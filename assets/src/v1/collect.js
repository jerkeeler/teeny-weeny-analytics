(function () {
  'use strict';

  var COOKIE_NAME = 'teeny_weeny_cookie';
  var TEENY_SCRIPT = 'teeny-weeny-analytics';
  var TOKEN_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('');
  var TOKEN_LENGTH = 16;

  function objToQueryString(obj) {
    var keys = Object.keys(obj);
    return '?' + keys.map(function(key) {
      return encodeURIComponent(key) + '=' + encodeURIComponent(obj[key])
    }).join('&');
  }

  function randomInt(n) {
    return Math.floor(Math.random() * n);
  }

  function randomVal(arr) {
    return arr[randomInt(arr.length)];
  }

  function genToken(n) {
    return Array(n).join().split(',').map(function() {
      return randomVal(TOKEN_CHARS)
    }).join('');
  }

  function getCookie(name) {
    var cookies = document.cookie ? document.cookie.split('; ') : [];

    for (var i = 0; i < cookies.length; i++) {
      var parts = cookies[i].split('=');
      if (decodeURIComponent(parts[0]) !== name) {
        continue;
      }

      var cookie = parts.slice(1).join('=');
      return decodeURIComponent(cookie);
    }

    return '';
  }

  function setCookie(name, data, expires) {
    name = encodeURIComponent(name);
    data = encodeURIComponent(JSON.stringify(data));

    var str = name + '=' + data;
    str += ';path=/';
    str += ';expires='+ expires.toUTCString();

    document.cookie = str;
  }

  function getBrowser() {
    if (!navigator.userAgent)
      return null;

    // Thank you https://stackoverflow.com/questions/5916900/how-can-you-detect-the-version-of-a-browser !!!!!
    var ua = navigator.userAgent;
    var match = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    var tem;
    if (/trident/i.test(match[1])){
        tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
        return 'IE ' + (tem[1] || '');
    }
    if (match[1]=== 'Chrome') {
        tem = ua.match(/\b(OPR|Edge)\/(\d+)/);
        if (tem != null)
          return tem.slice(1).join(' ').replace('OPR', 'Opera');
    }
    match = match[2] ? [match[1], match[2]] : [navigator.appName, navigator.appVersion, '-?'];
    if ((tem = ua.match(/version\/(\d+)/i))!= null)
      match.splice(1, 1, tem[1]);
    return match.join(' ');
  }

  function getLoadTime() {
    // This "should" get dom content loaded time (interactive) because if dom content is not loaded by the time
    // this script is called we add a listener for DOMContentLoaded and recall (all subsequent page view events
    // on the same page should have the same timing.
    if (!window.performance)
      return null;

    // Navigation 2 API
    var perfEntries = performance.getEntriesByType('navigation');
    if (perfEntries.length > 0)
      return perfEntries[0].domInteractive;

    // Navigation 1 API
    var perfData = window.performance.timing;
    return perfData.domInteractive - perfData.navigationStart;
  }

  function getNewUserData() {
    return  {
        isNewUser: true,
        isNewSession: true,
        pagesViewed: [],
        eventId: '',
        previousEventId: '',
        lastSeen: +new Date(),
        apiKey: '',
        previousApiKey: '',
    };
  }

  function getApiKey() {
    var el = document.getElementById(TEENY_SCRIPT);
    return el.dataset.key;
  }

  function getApiUrl() {
    var el = document.getElementById(TEENY_SCRIPT);
    return el.dataset.url;
  }

  function getPreviousData() {
    var cookie = getCookie(COOKIE_NAME);
    var minsAgo = new Date();
    minsAgo.setMinutes(minsAgo.getMinutes() - 30);

    if (!cookie)
        return getNewUserData();

    var data;
    try {
        data = JSON.parse(cookie);
    } catch (e) {
        console.error(e);
        return getNewUserData();
    }

    data.isNewSession = false;
    data.isNewUser = false;

    if(data.lastSeen < (+minsAgo)) {
      data.isNewSession = true;
    }

    return data;
  }

  function saveData(data) {
    var now = new Date();
    var twoDays = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 2, now.getHours(), now.getMinutes(),
      now.getSeconds());
    setCookie(COOKIE_NAME, data, twoDays);
  }

  function collect(eventName) {
    // Respect DNT
    if('doNotTrack' in navigator && navigator.doNotTrack === '1')
      return;

    // If we haven't loaded we should try again once we have.
    if(document.readyState !== 'complete'
       && document.readyState !== 'loaded'
       && document.readyState !== 'interactive') {
      window.addEventListener('load', function() {
        collect(eventName)
      });
      return;
    }

    var prevData = getPreviousData();
    var data = Object.assign({}, prevData);

    // Set cookie data
    var loc = window.location;
    var path = loc.pathname;
    data.pagesViewed.push(path);
    data.previousEventId = data.eventId;
    data.eventId = genToken(TOKEN_LENGTH);
    data.lastSeen = +new Date();
    data.previousApiKey = data.apiKey;
    data.apiKey = getApiKey();

    // Get data to be sent to server
    var hostname = loc.protocol + "//" + loc.hostname + (loc.port ? ':' + loc.port : '');

    // only set referrer if not internal
    var referrer = '';
    if(document.referrer.indexOf(hostname) < 0 && document.referrer !== '') {
      referrer = document.referrer;
    }

    var browser = getBrowser();
    var loadTime = getLoadTime();

    // Convert data to query string keys
    var queryData = {
        eid: data.eventId,
        en: eventName,
        pid: data.previousEventId,
        h: hostname,
        p: path,
        b: browser,
        lt: loadTime,
        ns: data.isNewSession ? '1' : '0',
        nu: data.isNewUser ? '1' : '0',
        r: referrer,
        sh: screen.height,
        sw: screen.width,
        ak: data.apiKey,
    };

    // Send data to the server using an image src attribute so it's handle by all browsers :)
    var apiUrl = getApiUrl();
    var img = document.createElement('img');
    img.addEventListener('load', function() {
      saveData(data);
    });
    img.src = apiUrl + objToQueryString(queryData);
    img.style.display = 'none';

    // Remove image and save cookie if success within 1sec
    window.setTimeout(function() {
      if(!img.parentNode)
        return;

      img.src = '';
      document.body.removeChild(img)
    }, 1000);

    // add to DOM to fire request
    document.body.appendChild(img);
  }

  var queue = window.tw.q || [];
  // now let's set the tw object and call everything that was waiting for us to load
  window.tw = function() {
    var args = [].slice.call(arguments);
    collect.apply(this, args);
  };

  // process existing queue
  queue.forEach(function(i) {
    window.tw.apply(this, i)
  });
})();

!function(){"use strict";var d="teeny_weeny_cookie",m="teeny-weeny-analytics",v="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".split(""),f=16;function w(e){return e[(n=e.length,Math.floor(Math.random()*n))];var n}function o(){return{isNewUser:!0,isNewSession:!0,pagesViewed:[],eventId:"",previousEventId:"",lastSeen:+new Date,apiKey:"",previousApiKey:""}}function g(){var e,n=function(e){for(var n=document.cookie?document.cookie.split("; "):[],t=0;t<n.length;t++){var o=n[t].split("=");if(decodeURIComponent(o[0])===e){var r=o.slice(1).join("=");return decodeURIComponent(r)}}return""}(d),t=new Date;if(t.setMinutes(t.getMinutes()-30),!n)return o();try{e=JSON.parse(n)}catch(e){return console.error(e),o()}return e.isNewSession=!1,e.isNewUser=!1,e.lastSeen<+t&&(e.isNewSession=!0),e}function y(e){var n,t,o,r,i=new Date,a=new Date(i.getFullYear(),i.getMonth(),i.getDate()+2,i.getHours(),i.getMinutes(),i.getSeconds());n=d,t=e,o=a,r=(n=encodeURIComponent(n))+"="+(t=encodeURIComponent(JSON.stringify(t))),r+=";path=/",r+=";expires="+o.toUTCString(),document.cookie=r}function h(e){if(!("doNotTrack"in navigator&&"1"===navigator.doNotTrack))if("complete"===document.readyState||"loaded"===document.readyState||"interactive"===document.readyState){var n=g(),t=Object.assign({},n),o=window.location,r=o.pathname;t.pagesViewed.push(r),t.previousEventId=t.eventId,t.eventId=Array(f).join().split(",").map(function(){return w(v)}).join(""),t.lastSeen=+new Date,t.previousApiKey=t.apiKey,t.apiKey=document.getElementById(m).dataset.key;var i=o.protocol+"//"+o.hostname+(o.port?":"+o.port:""),a="";document.referrer.indexOf(i)<0&&""!==document.referrer&&(a=document.referrer);var d,s=function(){if(!navigator.userAgent)return null;var e,n=navigator.userAgent,t=n.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i)||[];return/trident/i.test(t[1])?"IE "+((e=/\brv[ :]+(\d+)/g.exec(n)||[])[1]||""):"Chrome"===t[1]&&null!=(e=n.match(/\b(OPR|Edge)\/(\d+)/))?e.slice(1).join(" ").replace("OPR","Opera"):(t=t[2]?[t[1],t[2]]:[navigator.appName,navigator.appVersion,"-?"],null!=(e=n.match(/version\/(\d+)/i))&&t.splice(1,1,e[1]),t.join(" "))}(),c=function(){if(!window.performance)return null;var e=performance.getEntriesByType("navigation");if(0<e.length)return Math.round(e[0].domInteractive);var n=window.performance.timing;return Math.round(n.domInteractive-n.navigationStart)}(),u={eid:t.eventId,en:e,pid:t.previousEventId,h:i,p:r,b:s,lt:c,ns:t.isNewSession?"1":"0",nu:t.isNewUser?"1":"0",r:a,sh:screen.height,sw:screen.width,ak:t.apiKey},p=document.getElementById(m).dataset.url,l=document.createElement("img");l.addEventListener("load",function(){y(t)}),l.src=p+(d=u,"?"+Object.keys(d).map(function(e){return encodeURIComponent(e)+"="+encodeURIComponent(d[e])}).join("&")),l.style.display="none",window.setTimeout(function(){l.parentNode&&(l.src="",document.body.removeChild(l))},1e3),document.body.appendChild(l)}else window.addEventListener("load",function(){h(e)})}var e=window.tw.q||[];window.tw=function(){var e=[].slice.call(arguments);h.apply(this,e)},e.forEach(function(e){window.tw.apply(this,e)})}();
import React from 'react';
import { Route } from 'react-router-dom';

import Content from '../content';
import Footer from '../footer';
import Landing from '../landing';
import Navbar from '../navbar';

const App = () => (
  <div>
    <Navbar />
    <Content>
      <Route exact path='/' component={Landing} />
    </Content>
    <Footer />
  </div>
);

export default App;

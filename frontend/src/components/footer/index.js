import React from 'react';

import Divider from '../divider';

import './styles.css'

const currentYear = (new Date()).getFullYear();

const Footer = () => (
  <footer className="footer">
    <div className="container">
      <Divider />
      <p className="has-text-center">&copy; TeenyWeenyAnalytics 2018 - {currentYear}</p>
    </div>
  </footer>
);

export default Footer;

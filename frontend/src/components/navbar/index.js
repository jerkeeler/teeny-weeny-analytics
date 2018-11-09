import React from 'react';

import Link from '../link';

import './styles.css';

const Navbar = () => (
  <nav className='navbar'>
    <div className="container">
      <div className="navbar-start">
        <div className="navbar-brand">
          <Link className="navbar-item" to="/">TW</Link>
        </div>
      </div>
      <div className="navbar-end">
        <Link className="navbar-item" to="/events">Page Views</Link>
      </div>
    </div>
  </nav>
);

export default Navbar;

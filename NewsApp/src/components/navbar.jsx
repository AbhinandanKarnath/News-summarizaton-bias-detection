import React from 'react';
import './navbar.css';

const Navbar = () => (
  <nav className="navbar-glass">
    <div className="navbar-logo">
      <span role="img" aria-label="news" style={{marginRight: '0.5rem'}}>📰</span>
      <span className="navbar-title">India News Portal</span>
    </div>
    <ul className="navbar-links">
      <li><a href="/">Home</a></li>
      {/* Future: <li><a href="/about">About</a></li> */}
    </ul>
  </nav>
);

export default Navbar;

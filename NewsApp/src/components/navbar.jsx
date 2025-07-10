import React from 'react';

const Navbar = ({ onOpenSettings }) => (
  <div className="navbar bg-base-100 shadow-md">
    <div className="flex-1">
      <a className="btn btn-ghost normal-case text-xl">
        <span role="img" aria-label="news" style={{marginRight: '0.5rem'}}>📰</span>
        India News Portal
      </a>
    </div>
    <div className="flex-none">
      <ul className="menu menu-horizontal px-1">
        <li><a href="/">Home</a></li>
        <li>
          <button className="btn btn-outline btn-primary" onClick={onOpenSettings}>
            Settings
          </button>
        </li>
      </ul>
    </div>
  </div>
);

export default Navbar;

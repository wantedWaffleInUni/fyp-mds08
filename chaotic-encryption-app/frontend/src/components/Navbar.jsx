import React from 'react';
import { NavLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-brand">
          🔐 Chaotic Encryption
        </NavLink>
        <ul className="navbar-nav">
          <li>
            <NavLink 
              to="/" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              end
            >
              Home
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/encrypt" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Encrypt
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/decrypt" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Decrypt
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/results" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Results
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;

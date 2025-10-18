import React, { useEffect, useState }  from 'react';
import { NavLink } from 'react-router-dom';

const Navbar = () => {

  const [compact, setCompact] = useState(false);

  useEffect(() => {
    const onScroll = () => setCompact(window.scrollY > 12); // tweak threshold
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // set initial
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <nav className={`navbar ${compact ? 'navbar--compact' : ''}`}>

      <div className="navbar-container">
        
        <NavLink to="/" className="navbar-brand" aria-label="PEEKAPC Home">
          <span className="logo-text">PEEKAP</span>
          <span className="logo-emoji" aria-hidden>🔑</span>
          <span className="logo-text">C</span>
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
          {/* <li>
            <NavLink 
              to="/results" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Results
            </NavLink>
          </li> */}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;

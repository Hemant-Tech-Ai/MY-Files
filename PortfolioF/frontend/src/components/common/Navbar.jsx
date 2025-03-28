import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaBars, FaTimes } from 'react-icons/fa';
import { ROUTES } from '../../constants/routes';
import ThemeToggle from '../ThemeToggle';
import '../../styles/components/navbar.css';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="container navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-text">Hemant Singh Sidar</span>
        </Link>

        <div className="navbar-toggle" onClick={toggleMenu}>
          {isOpen ? <FaTimes /> : <FaBars />}
        </div>

        <ul className={`navbar-menu ${isOpen ? 'active' : ''}`}>
          <li className="navbar-item">
            <Link 
              to={ROUTES.HOME} 
              className={`navbar-link ${isActive(ROUTES.HOME) ? 'active' : ''}`} 
              onClick={() => setIsOpen(false)}
            >
              Home
            </Link>
          </li>
          <li className="navbar-item">
            <Link 
              to={ROUTES.ABOUT} 
              className={`navbar-link ${isActive(ROUTES.ABOUT) ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              About
            </Link>
          </li>
          <li className="navbar-item">
            <Link 
              to={ROUTES.SKILLS} 
              className={`navbar-link ${isActive(ROUTES.SKILLS) ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              Skills
            </Link>
          </li>
          <li className="navbar-item">
            <Link 
              to={ROUTES.PROJECTS} 
              className={`navbar-link ${isActive(ROUTES.PROJECTS) ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              Projects
            </Link>
          </li>
          <li className="navbar-item">
            <Link 
              to={ROUTES.EXPERIENCE} 
              className={`navbar-link ${isActive(ROUTES.EXPERIENCE) ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              Experience
            </Link>
          </li>
          <li className="navbar-item">
            <Link 
              to={ROUTES.CONTACT} 
              className={`navbar-link ${isActive(ROUTES.CONTACT) ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              Contact
            </Link>
          </li>
          <li className="navbar-item theme-toggle-item">
            <ThemeToggle />
          </li>
          <li className="navbar-item">
            <a
              href="/resume.pdf"
              className="btn btn-primary navbar-btn"
              target="_blank"
              rel="noopener noreferrer"
              download
            >
              Resume
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar; 
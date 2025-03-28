import React from 'react';
import { Link } from 'react-router-dom';
import { FaGithub, FaLinkedin, FaTwitter, FaEnvelope } from 'react-icons/fa';
import { ROUTES } from '../../constants/routes';
import '../../styles/components/footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="container footer-container">
        <div className="footer-content">
          <div className="footer-logo">
            <h3>John Doe</h3>
            <p>Senior Software Engineer</p>
          </div>

          <div className="footer-links">
            <h4>Quick Links</h4>
            <ul>
              <li><Link to={ROUTES.ABOUT}>About</Link></li>
              <li><Link to={ROUTES.SKILLS}>Skills</Link></li>
              <li><Link to={ROUTES.PROJECTS}>Projects</Link></li>
              <li><Link to={ROUTES.EXPERIENCE}>Experience</Link></li>
              <li><Link to={ROUTES.CONTACT}>Contact</Link></li>
            </ul>
          </div>

          <div className="footer-contact">
            <h4>Contact</h4>
            <p>
              <FaEnvelope className="footer-icon" />
              <a href="mailto:john.doe@example.com">john.doe@example.com</a>
            </p>
            <div className="footer-social">
              <a href="https://github.com/johndoe" target="_blank" rel="noopener noreferrer">
                <FaGithub className="footer-social-icon" />
              </a>
              <a href="https://linkedin.com/in/johndoe" target="_blank" rel="noopener noreferrer">
                <FaLinkedin className="footer-social-icon" />
              </a>
              <a href="https://twitter.com/johndoe" target="_blank" rel="noopener noreferrer">
                <FaTwitter className="footer-social-icon" />
              </a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; {currentYear} John Doe. All rights reserved.</p>
          <p>
            Built with <span className="heart">❤</span> using React and FastAPI
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 
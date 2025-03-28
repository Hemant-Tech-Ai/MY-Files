import React from 'react';
import { Link } from 'react-router-dom';
import { FaGithub, FaLinkedinIn, FaTwitter, FaReddit } from 'react-icons/fa';
import { SiOpenai } from 'react-icons/si';
import '../styles/pages/home.css';

const Home = () => {
  return (
    <section className="section home">
      <div className="container">
        <div className="home-content">
          <div className="home-text">
            <h1 className="section-title">
              <span className="greeting">Hi, I'm</span>
              <span className="name">Hemant Singh Sidar</span>
              <span className="role">Full Stack Developer & AI Enthusiast</span>
            </h1>
            
            <p className="section-description">
              I build exceptional digital experiences that combine cutting-edge technology 
              with elegant design. Specializing in full-stack development and AI integration.
            </p>

            <div className="home-cta">
              <Link to="/projects" className="btn btn-primary">View My Work</Link>
              <Link to="/contact" className="btn btn-outline">Get In Touch</Link>
            </div>

            <div className="tech-stack">
              <span>React</span>
              <span>Python</span>
              <span>FastAPI</span>
              <span>Node.js</span>
              <span>AI/ML</span>
              <span>Docker</span>
            </div>

            <div className="social-links">
              <a href="https://github.com/hemantsinghsidar" target="_blank" rel="noopener noreferrer" title="GitHub">
                <FaGithub />
              </a>
              <a href="https://linkedin.com/in/hemantsinghsidar" target="_blank" rel="noopener noreferrer" title="LinkedIn">
                <FaLinkedinIn />
              </a>
              <a href="https://twitter.com/hemantsinghsidar" target="_blank" rel="noopener noreferrer" title="X (Twitter)">
                <FaTwitter />
              </a>
              <a href="https://reddit.com/user/hemantsinghsidar" target="_blank" rel="noopener noreferrer" title="Reddit">
                <FaReddit />
              </a>
              <a href="https://huggingface.co/hemantsinghsidar" target="_blank" rel="noopener noreferrer" title="Hugging Face">
                <SiOpenai />
              </a>
            </div>
          </div>

          <div className="home-image">
            <img src="/images/profile.jpg" alt="Hemant Singh Sidar" className="profile-image" />
            <div className="image-overlay"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Home; 
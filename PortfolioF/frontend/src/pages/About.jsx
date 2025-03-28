import React from 'react';
import { FaDownload } from 'react-icons/fa';
import '../styles/pages/about.css';

const About = () => {
  return (
    <div className="about">
      <div className="container">
        <h1 className="section-title">About Me</h1>
        
        <div className="about-content grid grid-2">
          <div className="about-text">
            <p>
              Hello! I'm John, a passionate software engineer with over 5 years of experience in building
              web applications. My journey in software development started back in college when I built my
              first website, and I've been hooked ever since.
            </p>
            
            <p>
              Fast-forward to today, and I've had the privilege of working at a start-up, a large corporation,
              and a student-led design studio. My main focus these days is building accessible, inclusive products
              and digital experiences at a digital agency for a variety of clients.
            </p>
            
            <p>
              I also recently launched a course that covers everything you need to build a web app with the
              MERN stack. I'm always looking to learn new technologies and improve my skills. I'm currently
              exploring the world of serverless architecture and cloud computing.
            </p>
            
            <p>
              When I'm not at the computer, I'm usually rock climbing, hiking, or exploring new coffee shops
              in the city. I'm also a big fan of sci-fi books and movies.
            </p>
            
            <a href="/resume.pdf" className="btn btn-primary" download>
              <FaDownload className="btn-icon" /> Download Resume
            </a>
          </div>
        </div>
        
        <div className="about-education">
          <h2 className="about-subtitle">Education</h2>
          <div className="timeline">
            <div className="timeline-item">
              <div className="timeline-dot"></div>
              <div className="timeline-content">
                <h3>Master of Science in Computer Science</h3>
                <p className="timeline-place">Stanford University</p>
                <p className="timeline-date">2016 - 2018</p>
                <p className="timeline-description">
                  Specialized in Artificial Intelligence and Machine Learning. Thesis on "Deep Learning Approaches for Natural Language Processing".
                </p>
              </div>
            </div>
            
            <div className="timeline-item">
              <div className="timeline-dot"></div>
              <div className="timeline-content">
                <h3>Bachelor of Science in Computer Engineering</h3>
                <p className="timeline-place">Massachusetts Institute of Technology</p>
                <p className="timeline-date">2012 - 2016</p>
                <p className="timeline-description">
                  Graduated with honors. Participated in various hackathons and coding competitions.
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="about-experience">
          <h2 className="about-subtitle">Work Experience</h2>
          <div className="timeline">
            <div className="timeline-item">
              <div className="timeline-dot"></div>
              <div className="timeline-content">
                <h3>Senior Software Engineer</h3>
                <p className="timeline-place">Tech Innovations Inc.</p>
                <p className="timeline-date">2020 - Present</p>
                <p className="timeline-description">
                  Lead developer for client projects, mentoring junior developers, and implementing best practices for code quality and performance.
                </p>
              </div>
            </div>
            
            <div className="timeline-item">
              <div className="timeline-dot"></div>
              <div className="timeline-content">
                <h3>Full Stack Developer</h3>
                <p className="timeline-place">Digital Solutions LLC</p>
                <p className="timeline-date">2018 - 2020</p>
                <p className="timeline-description">
                  Developed and maintained multiple web applications using React, Node.js, and MongoDB. Implemented CI/CD pipelines and automated testing.
                </p>
              </div>
            </div>
            
            <div className="timeline-item">
              <div className="timeline-dot"></div>
              <div className="timeline-content">
                <h3>Software Engineering Intern</h3>
                <p className="timeline-place">Google</p>
                <p className="timeline-date">Summer 2017</p>
                <p className="timeline-description">
                  Worked on improving search algorithms and implementing new features for Google Maps.
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="about-interests">
          <h2 className="about-subtitle">Interests & Hobbies</h2>
          <div className="interests-grid grid grid-4">
            <div className="interest-item">
              <div className="interest-icon">🧗</div>
              <h3>Rock Climbing</h3>
            </div>
            <div className="interest-item">
              <div className="interest-icon">🏔️</div>
              <h3>Hiking</h3>
            </div>
            <div className="interest-item">
              <div className="interest-icon">📚</div>
              <h3>Reading</h3>
            </div>
            <div className="interest-item">
              <div className="interest-icon">☕</div>
              <h3>Coffee</h3>
            </div>
            <div className="interest-item">
              <div className="interest-icon">🎮</div>
              <h3>Gaming</h3>
            </div>
            <div className="interest-item">
              <div className="interest-icon">🎸</div>
              <h3>Music</h3>
            </div>
            <div className="interest-item">
              <div className="interest-icon">✈️</div>
              <h3>Travel</h3>
            </div>
            <div className="interest-item">
              <div className="interest-icon">🍳</div>
              <h3>Cooking</h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About; 
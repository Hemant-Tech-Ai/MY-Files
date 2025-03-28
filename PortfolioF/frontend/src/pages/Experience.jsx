import React, { useState } from 'react';
import { FaBriefcase, FaGraduationCap, FaBuilding, FaCalendarAlt, FaMapMarkerAlt } from 'react-icons/fa';
import '../styles/pages/experience.css';

const Experience = () => {
  const [activeTab, setActiveTab] = useState('work');

  const workExperience = [
    {
      id: 1,
      title: 'Senior Software Engineer',
      company: 'Tech Innovations Inc.',
      location: 'San Francisco, CA',
      period: 'Jan 2020 - Present',
      description: [
        'Lead developer for client projects, mentoring junior developers, and implementing best practices for code quality and performance.',
        'Architected and developed a scalable e-commerce platform using React, Node.js, and MongoDB, resulting in a 40% increase in conversion rates.',
        'Implemented CI/CD pipelines using GitHub Actions, reducing deployment time by 60% and improving team productivity.',
        'Collaborated with cross-functional teams to deliver high-quality software solutions that meet business requirements and user needs.',
      ],
      technologies: ['React', 'Node.js', 'MongoDB', 'Express', 'AWS', 'Docker', 'CI/CD'],
    },
    {
      id: 2,
      title: 'Full Stack Developer',
      company: 'Digital Solutions LLC',
      location: 'Boston, MA',
      period: 'Mar 2018 - Dec 2019',
      description: [
        'Developed and maintained multiple web applications using React, Node.js, and MongoDB.',
        'Implemented responsive designs and ensured cross-browser compatibility for all web applications.',
        'Collaborated with UX/UI designers to implement user-friendly interfaces and improve user experience.',
        'Participated in code reviews and provided constructive feedback to team members.',
      ],
      technologies: ['React', 'JavaScript', 'Node.js', 'Express', 'MongoDB', 'Redux', 'SASS'],
    },
    {
      id: 3,
      title: 'Software Engineering Intern',
      company: 'Google',
      location: 'Mountain View, CA',
      period: 'Summer 2017',
      description: [
        'Worked on improving search algorithms and implementing new features for Google Maps.',
        'Collaborated with senior engineers to optimize code performance and reduce loading times.',
        'Participated in daily stand-up meetings and weekly code reviews.',
        'Gained experience with large-scale software development and agile methodologies.',
      ],
      technologies: ['Python', 'JavaScript', 'Java', 'Google Cloud Platform'],
    },
  ];

  const education = [
    {
      id: 1,
      degree: 'Master of Science in Computer Science',
      institution: 'Stanford University',
      location: 'Stanford, CA',
      period: '2016 - 2018',
      description: [
        'Specialized in Artificial Intelligence and Machine Learning.',
        'Thesis: "Deep Learning Approaches for Natural Language Processing"',
        'GPA: 3.9/4.0',
        'Relevant coursework: Machine Learning, Deep Learning, Natural Language Processing, Algorithms, Data Structures.',
      ],
    },
    {
      id: 2,
      degree: 'Bachelor of Science in Computer Engineering',
      institution: 'Massachusetts Institute of Technology',
      location: 'Cambridge, MA',
      period: '2012 - 2016',
      description: [
        'Graduated with honors (cum laude).',
        'Participated in various hackathons and coding competitions.',
        'GPA: 3.8/4.0',
        'Relevant coursework: Computer Architecture, Operating Systems, Database Systems, Web Development, Software Engineering.',
      ],
    },
  ];

  return (
    <div className="experience">
      <div className="container">
        <h1 className="section-title">My Experience</h1>
        
        <div className="experience-tabs">
          <button 
            className={`tab-btn ${activeTab === 'work' ? 'active' : ''}`}
            onClick={() => setActiveTab('work')}
          >
            <FaBriefcase className="tab-icon" /> Work Experience
          </button>
          <button 
            className={`tab-btn ${activeTab === 'education' ? 'active' : ''}`}
            onClick={() => setActiveTab('education')}
          >
            <FaGraduationCap className="tab-icon" /> Education
          </button>
        </div>
        
        <div className="experience-content">
          {activeTab === 'work' ? (
            <div className="work-experience">
              {workExperience.map((job) => (
                <div key={job.id} className="experience-card">
                  <div className="experience-header">
                    <h2 className="experience-title">{job.title}</h2>
                    <div className="experience-company">
                      <FaBuilding className="experience-icon" />
                      <span>{job.company}</span>
                    </div>
                    <div className="experience-meta">
                      <div className="experience-location">
                        <FaMapMarkerAlt className="experience-icon" />
                        <span>{job.location}</span>
                      </div>
                      <div className="experience-period">
                        <FaCalendarAlt className="experience-icon" />
                        <span>{job.period}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="experience-body">
                    <ul className="experience-description">
                      {job.description.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                    
                    <div className="experience-technologies">
                      <h3>Technologies:</h3>
                      <div className="tech-tags">
                        {job.technologies.map((tech, index) => (
                          <span key={index} className="tech-tag">{tech}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="education-experience">
              {education.map((edu) => (
                <div key={edu.id} className="experience-card">
                  <div className="experience-header">
                    <h2 className="experience-title">{edu.degree}</h2>
                    <div className="experience-company">
                      <FaGraduationCap className="experience-icon" />
                      <span>{edu.institution}</span>
                    </div>
                    <div className="experience-meta">
                      <div className="experience-location">
                        <FaMapMarkerAlt className="experience-icon" />
                        <span>{edu.location}</span>
                      </div>
                      <div className="experience-period">
                        <FaCalendarAlt className="experience-icon" />
                        <span>{edu.period}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="experience-body">
                    <ul className="experience-description">
                      {edu.description.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="experience-download">
          <p>For a complete overview of my professional experience, please download my resume.</p>
          <a href="/resume.pdf" className="btn btn-primary" download>
            Download Resume
          </a>
        </div>
      </div>
    </div>
  );
};

export default Experience; 
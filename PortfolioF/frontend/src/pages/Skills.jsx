import React from 'react';
import { FaCode, FaServer, FaDatabase, FaTools, FaCloud } from 'react-icons/fa';
import '../styles/pages/skills.css';

const Skills = () => {
  const skillCategories = [
    {
      id: 'frontend',
      title: 'Frontend Development',
      icon: <FaCode />,
      skills: [
        { name: 'React', level: 90 },
        { name: 'JavaScript', level: 85 },
        { name: 'TypeScript', level: 80 },
        { name: 'HTML/CSS', level: 90 },
        { name: 'Redux', level: 75 },
        { name: 'Next.js', level: 70 },
        { name: 'Tailwind CSS', level: 85 },
        { name: 'SASS/SCSS', level: 80 },
      ],
    },
    {
      id: 'backend',
      title: 'Backend Development',
      icon: <FaServer />,
      skills: [
        { name: 'Node.js', level: 85 },
        { name: 'Python', level: 80 },
        { name: 'Django', level: 75 },
        { name: 'FastAPI', level: 80 },
        { name: 'Express', level: 85 },
        { name: 'GraphQL', level: 70 },
        { name: 'REST API', level: 90 },
      ],
    },
    {
      id: 'database',
      title: 'Database',
      icon: <FaDatabase />,
      skills: [
        { name: 'MongoDB', level: 85 },
        { name: 'PostgreSQL', level: 80 },
        { name: 'MySQL', level: 75 },
        { name: 'Redis', level: 70 },
        { name: 'Firebase', level: 75 },
      ],
    },
    {
      id: 'devops',
      title: 'DevOps & Tools',
      icon: <FaTools />,
      skills: [
        { name: 'Git', level: 90 },
        { name: 'Docker', level: 80 },
        { name: 'CI/CD', level: 75 },
        { name: 'Jest', level: 80 },
        { name: 'Webpack', level: 70 },
        { name: 'Agile/Scrum', level: 85 },
      ],
    },
    {
      id: 'cloud',
      title: 'Cloud Services',
      icon: <FaCloud />,
      skills: [
        { name: 'AWS', level: 75 },
        { name: 'Google Cloud', level: 70 },
        { name: 'Heroku', level: 85 },
        { name: 'Netlify', level: 90 },
        { name: 'Vercel', level: 85 },
      ],
    },
  ];

  return (
    <div className="skills">
      <div className="container">
        <h1 className="section-title">My Skills</h1>
        
        <div className="skills-intro">
          <p>
            I've worked with a variety of technologies and tools throughout my career.
            Here's a comprehensive overview of my technical skills and proficiency levels.
          </p>
        </div>
        
        <div className="skills-categories">
          {skillCategories.map((category) => (
            <div key={category.id} className="skill-category-section" id={category.id}>
              <div className="category-header">
                <div className="category-icon">{category.icon}</div>
                <h2 className="category-title">{category.title}</h2>
              </div>
              
              <div className="skills-list">
                {category.skills.map((skill) => (
                  <div key={skill.name} className="skill-item">
                    <div className="skill-info">
                      <h3 className="skill-name">{skill.name}</h3>
                      <span className="skill-percentage">{skill.level}%</span>
                    </div>
                    <div className="skill-bar">
                      <div 
                        className="skill-progress" 
                        style={{ width: `${skill.level}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        <div className="skills-additional">
          <h2 className="about-subtitle">Other Skills</h2>
          <div className="additional-skills">
            <div className="additional-skill">UI/UX Design</div>
            <div className="additional-skill">Responsive Design</div>
            <div className="additional-skill">SEO</div>
            <div className="additional-skill">Performance Optimization</div>
            <div className="additional-skill">Accessibility</div>
            <div className="additional-skill">Technical Writing</div>
            <div className="additional-skill">Problem Solving</div>
            <div className="additional-skill">Team Leadership</div>
            <div className="additional-skill">Project Management</div>
            <div className="additional-skill">Mentoring</div>
          </div>
        </div>
        
        <div className="skills-certifications">
          <h2 className="about-subtitle">Certifications</h2>
          <div className="certifications-list">
            <div className="certification">
              <h3>AWS Certified Developer - Associate</h3>
              <p className="certification-issuer">Amazon Web Services</p>
              <p className="certification-date">2022</p>
            </div>
            <div className="certification">
              <h3>Professional Scrum Master I (PSM I)</h3>
              <p className="certification-issuer">Scrum.org</p>
              <p className="certification-date">2021</p>
            </div>
            <div className="certification">
              <h3>MongoDB Certified Developer</h3>
              <p className="certification-issuer">MongoDB University</p>
              <p className="certification-date">2020</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Skills; 
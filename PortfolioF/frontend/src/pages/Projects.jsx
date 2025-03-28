import React, { useState } from 'react';
import { FaGithub, FaExternalLinkAlt, FaSearch } from 'react-icons/fa';
import '../styles/pages/projects.css';

const Projects = () => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const projects = [
    {
      id: 1,
      title: 'E-Commerce Platform',
      description: 'A full-stack e-commerce platform with user authentication, product management, cart functionality, and payment processing.',
      image: '/images/projects/project1.jpg',
      technologies: ['React', 'Node.js', 'MongoDB', 'Express', 'Redux'],
      category: 'fullstack',
      github: 'https://github.com',
      demo: 'https://project-demo.com',
      featured: true,
    },
    {
      id: 2,
      title: 'Task Management App',
      description: 'A collaborative task management application with real-time updates, team workspaces, and progress tracking.',
      image: '/images/projects/project2.jpg',
      technologies: ['React', 'Firebase', 'Redux', 'Material UI'],
      category: 'frontend',
      github: 'https://github.com',
      demo: 'https://project-demo.com',
      featured: true,
    },
    {
      id: 3,
      title: 'Personal Finance Tracker',
      description: 'An application to track personal finances, including expenses, income, budgeting, and financial goals.',
      image: '/images/projects/project3.jpg',
      technologies: ['React', 'Chart.js', 'Node.js', 'PostgreSQL'],
      category: 'fullstack',
      github: 'https://github.com',
      demo: 'https://project-demo.com',
      featured: false,
    },
    {
      id: 4,
      title: 'Weather Dashboard',
      description: 'A weather dashboard that displays current weather conditions and forecasts for multiple locations.',
      image: '/images/projects/project4.jpg',
      technologies: ['JavaScript', 'HTML', 'CSS', 'Weather API'],
      category: 'frontend',
      github: 'https://github.com',
      demo: 'https://project-demo.com',
      featured: false,
    },
    {
      id: 5,
      title: 'Recipe Sharing Platform',
      description: 'A platform for users to share, discover, and save recipes with social features and personalized recommendations.',
      image: '/images/projects/project5.jpg',
      technologies: ['React', 'Node.js', 'MongoDB', 'Express'],
      category: 'fullstack',
      github: 'https://github.com',
      demo: 'https://project-demo.com',
      featured: false,
    },
    {
      id: 6,
      title: 'Content Management System',
      description: 'A custom CMS for managing website content, user permissions, and media assets.',
      image: '/images/projects/project6.jpg',
      technologies: ['Python', 'Django', 'PostgreSQL', 'React'],
      category: 'backend',
      github: 'https://github.com',
      demo: 'https://project-demo.com',
      featured: false,
    },
  ];

  const filteredProjects = projects.filter((project) => {
    const matchesFilter = filter === 'all' || project.category === filter;
    const matchesSearch = project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.technologies.some(tech => tech.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="projects">
      <div className="container">
        <h1 className="section-title">My Projects</h1>
        
        <div className="projects-intro">
          <p>
            Here are some of the projects I've worked on. Each project represents a unique challenge
            and showcases different skills and technologies.
          </p>
        </div>
        
        <div className="projects-filter">
          <div className="filter-categories">
            <button 
              className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button 
              className={`filter-btn ${filter === 'frontend' ? 'active' : ''}`}
              onClick={() => setFilter('frontend')}
            >
              Frontend
            </button>
            <button 
              className={`filter-btn ${filter === 'backend' ? 'active' : ''}`}
              onClick={() => setFilter('backend')}
            >
              Backend
            </button>
            <button 
              className={`filter-btn ${filter === 'fullstack' ? 'active' : ''}`}
              onClick={() => setFilter('fullstack')}
            >
              Full Stack
            </button>
          </div>
          
          <div className="search-box">
            <FaSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        
        <div className="projects-grid">
          {filteredProjects.length > 0 ? (
            filteredProjects.map((project) => (
              <div key={project.id} className="project-card">
                <div className="project-image">
                  <img src={project.image} alt={project.title} />
                  <div className="project-links">
                    <a href={project.github} target="_blank" rel="noopener noreferrer" className="project-link">
                      <FaGithub />
                    </a>
                    <a href={project.demo} target="_blank" rel="noopener noreferrer" className="project-link">
                      <FaExternalLinkAlt />
                    </a>
                  </div>
                </div>
                <div className="project-content">
                  <h2 className="project-title">{project.title}</h2>
                  <p className="project-description">{project.description}</p>
                  <div className="project-tech">
                    {project.technologies.map((tech, index) => (
                      <span key={index} className="tech-tag">{tech}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="no-projects">
              <p>No projects found matching your criteria.</p>
              <button className="btn btn-secondary" onClick={() => {
                setFilter('all');
                setSearchTerm('');
              }}>
                Reset Filters
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Projects; 
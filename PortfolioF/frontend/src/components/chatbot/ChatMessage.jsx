import React from 'react';
import { FaRobot, FaUser } from 'react-icons/fa';

const ChatMessage = ({ message }) => {
  const { text, sender, timestamp, context } = message;
  const isBot = sender === 'bot';

  return (
    <div className={`chat-message ${isBot ? 'bot' : 'user'}`}>
      <div className="message-avatar">
        {isBot ? <FaRobot /> : <FaUser />}
      </div>
      <div className="message-content">
        <div className="message-text">{text}</div>
        
        {/* Render context data if available */}
        {isBot && context && context.type === 'skills' && context.data && (
          <div className="message-context">
            <h4>Top Skills:</h4>
            <ul>
              {context.data.top_skills.map((skill, index) => (
                <li key={index}>
                  {skill.name} - {skill.proficiency}%
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {isBot && context && context.type === 'projects' && context.data && (
          <div className="message-context">
            <h4>Featured Projects:</h4>
            <ul>
              {context.data.featured_projects.map((project, index) => (
                <li key={index}>
                  <strong>{project.title}</strong>: {project.description}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="message-time">
          {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage; 
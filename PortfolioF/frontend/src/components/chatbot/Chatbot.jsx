import React, { useContext } from 'react';
import { FaRobot, FaTimes } from 'react-icons/fa';
import { ChatbotContext } from '../../context/ChatbotContext';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import '../../styles/components/chatbot.css';

const Chatbot = () => {
  const { isOpen, toggleChatbot, messages, handleSendMessage, isTyping } = useContext(ChatbotContext);

  return (
    <>
      {/* Chatbot toggle button */}
      <button className="chatbot-toggle" onClick={toggleChatbot}>
        <FaRobot />
      </button>

      {/* Chatbot container */}
      <div className={`chatbot-container ${isOpen ? 'open' : ''}`}>
        <div className="chatbot-header">
          <div className="chatbot-title">
            <FaRobot className="chatbot-icon" />
            <h3>Portfolio Assistant</h3>
          </div>
          <button className="chatbot-close" onClick={toggleChatbot}>
            <FaTimes />
          </button>
        </div>

        <div className="chatbot-messages">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          
          {isTyping && (
            <div className="chatbot-typing">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>

        <ChatInput onSendMessage={handleSendMessage} />
      </div>
    </>
  );
};

export default Chatbot; 
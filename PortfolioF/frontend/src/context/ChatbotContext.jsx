import React, { createContext, useState, useEffect, useCallback } from 'react';
import { useChatbot } from '../hooks/useChatbot';

export const ChatbotContext = createContext();

export const ChatbotProvider = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const { sendMessage, getChatbotContext } = useChatbot();
  const [context, setContext] = useState(null);

  useEffect(() => {
    // Load chatbot context when the component mounts
    const loadContext = async () => {
      try {
        const contextData = await getChatbotContext();
        setContext(contextData);
        
        // Add initial greeting message
        setMessages([
          {
            id: 1,
            text: `👋 Hello! I'm your AI assistant for Hemant's portfolio. I can help you learn about his skills, projects, experience, and more. What would you like to know?`,
            sender: 'bot',
            timestamp: new Date().toISOString(),
          },
          {
            id: 2,
            text: `You can ask me about:\n• Hemant's technical skills\n• His projects and work\n• How to contact him\n• Download his resume`,
            sender: 'bot',
            timestamp: new Date().toISOString(),
          }
        ]);
      } catch (error) {
        console.error('Error loading chatbot context:', error);
      }
    };

    loadContext();
  }, [getChatbotContext]);

  const toggleChatbot = () => {
    setIsOpen((prev) => !prev);
  };

  const addMessage = useCallback((message) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        id: prevMessages.length + 1,
        ...message,
        timestamp: new Date().toISOString(),
      },
    ]);
  }, []);

  const handleSendMessage = useCallback(async (text) => {
    if (!text.trim()) return;

    // Add user message
    addMessage({
      text,
      sender: 'user',
    });

    // Show typing indicator
    setIsTyping(true);

    try {
      // Send message to API
      const response = await sendMessage(text);

      // Simulate typing delay
      setTimeout(() => {
        // Add bot response
        addMessage({
          text: response.response,
          sender: 'bot',
          context: response.context,
        });
        setIsTyping(false);
      }, 1000);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      setTimeout(() => {
        addMessage({
          text: 'Sorry, I encountered an error. Please try again later.',
          sender: 'bot',
        });
        setIsTyping(false);
      }, 1000);
    }
  }, [addMessage, sendMessage]);

  const clearMessages = useCallback(() => {
    // Keep only the initial greeting message
    setMessages((prevMessages) => prevMessages.slice(0, 1));
  }, []);

  return (
    <ChatbotContext.Provider
      value={{
        isOpen,
        toggleChatbot,
        messages,
        addMessage,
        handleSendMessage,
        clearMessages,
        isTyping,
        context,
      }}
    >
      {children}
    </ChatbotContext.Provider>
  );
}; 
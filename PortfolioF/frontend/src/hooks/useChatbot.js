import { useCallback } from 'react';
import api from '../services/api';

export const useChatbot = () => {
  const sendMessage = useCallback(async (message) => {
    try {
      const response = await api.post('/chatbot/query', { message });
      return response.data;
    } catch (error) {
      console.error('Error sending message to chatbot:', error);
      throw error;
    }
  }, []);

  const getChatbotContext = useCallback(async () => {
    try {
      const response = await api.get('/chatbot/context');
      return response.data;
    } catch (error) {
      console.error('Error getting chatbot context:', error);
      throw error;
    }
  }, []);

  return {
    sendMessage,
    getChatbotContext,
  };
}; 
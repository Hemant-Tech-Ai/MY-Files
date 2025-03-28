import { chatbotAPI } from './api';

export const sendChatMessage = async (message) => {
  try {
    const response = await chatbotAPI.sendMessage(message);
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

export const getChatbotContext = async () => {
  try {
    const response = await chatbotAPI.getContext();
    return response.data;
  } catch (error) {
    console.error('Error getting chatbot context:', error);
    throw error;
  }
}; 
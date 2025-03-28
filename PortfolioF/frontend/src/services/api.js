import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor
api.interceptors.request.use(
  (config) => {
    // You can add auth tokens or other headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors here
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Request error:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API functions for different endpoints
const portfolioAPI = {
  getOverview: () => api.get('/portfolio/overview'),
  getStats: () => api.get('/portfolio/stats'),
};

const projectsAPI = {
  getAll: (params) => api.get('/projects', { params }),
  getById: (id) => api.get(`/projects/${id}`),
};

const skillsAPI = {
  getAll: (params) => api.get('/skills', { params }),
  getTop: (limit) => api.get('/skills/top', { params: { limit } }),
};

const resumeAPI = {
  getAll: () => api.get('/resume'),
  getExperience: () => api.get('/resume/experience'),
  getEducation: () => api.get('/resume/education'),
  getCertifications: () => api.get('/resume/certifications'),
};

const chatbotAPI = {
  sendMessage: (message) => api.post('/chatbot/query', { message }),
  getContext: () => api.get('/chatbot/context'),
};

const contactAPI = {
  sendMessage: (formData) => api.post('/contact', formData),
};

export { portfolioAPI, projectsAPI, skillsAPI, resumeAPI, chatbotAPI, contactAPI };
export default api; 
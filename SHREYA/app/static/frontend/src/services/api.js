import axios from 'axios';

// API base URL
const API_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000';

// Create API instance with base URL
const api = axios.create({
  baseURL: API_URL
});

// Add request interceptor to attach token to all requests
api.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) {
            // Log the token being used (truncated for security)
            console.log(`Using token: ${token.substring(0, 15)}...`);
            console.log(`Token length: ${token.length}`);
            
            // Ensure the Authorization header format exactly matches what the backend expects
            config.headers['Authorization'] = `Bearer ${token}`;
            
            // Log the full authorization header for debugging
            console.log(`Authorization header sent: Bearer ${token.substring(0, 15)}...`);
        } else {
            console.warn('No token found in localStorage');
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// Add response interceptor to handle authentication errors
api.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        const originalRequest = error.config;
        
        // If the error is 401 and we haven't already tried to refresh
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            console.error('Authentication error:', error.response.data);
            
            // Clear localStorage and redirect to login
            localStorage.removeItem('token');
            localStorage.removeItem('userId');
            localStorage.removeItem('isAdmin');
            localStorage.removeItem('loginTime');
            
            // Redirect to login page
            window.location.href = '/login';
            return Promise.reject(error);
        }
        
        return Promise.reject(error);
    }
);

// Helper function to add cache-busting parameter to GET requests
const addCacheBuster = (url) => {
  const timestamp = new Date().getTime();
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}_=${timestamp}`;
};

export default {
  // Auth endpoints
  login(credentials) {
    return api.post('/auth/login', credentials);
  },
  register(userData) {
    return api.post('/auth/register', userData);
  },
  logout() {
    // Clear auth data from localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('isAdmin');
    localStorage.removeItem('loginTime');
    
    // Return a resolved promise to maintain API pattern
    return Promise.resolve({ success: true });
  },
  
  // User endpoints
  getAssignedQuizzes() {
    return api.get(addCacheBuster('/user/quizzes'));
  },
  getQuizQuestions(quizId) {
    return api.get(addCacheBuster(`/user/quizzes/${quizId}/questions`));
  },
  submitQuiz(data) {
    return api.post('/user/quizzes/submit', data);
  },
  getUserScores() {
    return api.get(addCacheBuster('/user/scores'));
  },
  getUserProfile() {
    return api.get(addCacheBuster('/user/profile'));
  },
  getUserSubjects() {
    return api.get(addCacheBuster('/user/subjects'));
  },
  getUserChapters(subjectId) {
    const url = subjectId ? `/user/chapters?subject_id=${subjectId}` : '/user/chapters';
    return api.get(addCacheBuster(url));
  },
  
  // New - User dashboard performance with fixed formatting
  getDashboardPerformance() {
    return api.get(addCacheBuster('/user/dashboard/performance'));
  },
  
  // Admin endpoints
  getSubjects() {
    return api.get('/admin/subjects');
  },
  createSubject(subjectData) {
    return api.post('/admin/subjects', subjectData);
  },
  updateSubject(id, subjectData) {
    return api.put(`/admin/subjects/${id}`, subjectData);
  },
  deleteSubject(id) {
    return api.delete(`/admin/subjects/${id}`);
  },
  
  // Chapters
  getChapters() {
    return api.get('/admin/chapters');
  },
  createChapter(chapterData) {
    return api.post('/admin/chapters', chapterData);
  },
  updateChapter(id, chapterData) {
    return api.put(`/admin/chapters/${id}`, chapterData);
  },
  deleteChapter(id) {
    return api.delete(`/admin/chapters/${id}`);
  },
  
  // Questions
  getQuestions(quizId) {
    return quizId 
      ? api.get(`/admin/quizzes/${quizId}/questions`) 
      : api.get('/admin/questions');
  },
  
  // Users
  getUsers() {
    return api.get('/admin/users');
  },
  
  // Quizzes
  getQuizzes() {
    return api.get('/admin/quizzes');
  },
  createQuiz(quizData) {
    return api.post('/admin/quizzes', quizData);
  },
  updateQuiz(id, quizData) {
    return api.put(`/admin/quizzes/${id}`, quizData);
  },
  deleteQuiz(id) {
    return api.delete(`/admin/quizzes/${id}`);
  },
  
  // Dashboard stats
  getDashboardStats() {
    return api.get('/admin/stats');
  },
  
  // Admin endpoints - Questions
  createQuestion(questionData) {
    return api.post('/admin/questions', questionData);
  },
  updateQuestion(id, questionData) {
    return api.put(`/admin/questions/${id}`, questionData);
  },
  deleteQuestion(id) {
    return api.delete(`/admin/questions/${id}`);
  },
  
  // Admin endpoints - Users
  createUser(userData) {
    return api.post('/admin/users', userData);
  },
  updateUser(id, userData) {
    return api.put(`/admin/users/${id}`, userData);
  },
  deleteUser(id) {
    return api.delete(`/admin/users/${id}`);
  },
  
  // Admin endpoints - Quiz Assignments
  getQuizAssignments() {
    return api.get('/admin/assignments');
  },
  getAssignments(quizId) {
    return api.get(`/admin/quizzes/${quizId}/assignments`);
  },
  assignQuiz(quizId, assignmentData) {
    return api.post(`/admin/quizzes/${quizId}/assign`, assignmentData);
  },
  removeAssignment(quizId, userId) {
    return api.delete(`/admin/quizzes/${quizId}/assignments/${userId}`);
  },

  // New - Report management
  getReportOptions() {
    return api.get('/admin/reports/monthly');
  },
  getReportStats() {
    return api.get('/admin/reports/stats');
  },
  triggerMonthlyReport(reportData) {
    return api.post('/admin/reports/monthly/trigger', reportData);
  },
  previewMonthlyReport(reportData) {
    return api.post('/admin/reports/monthly/preview', reportData);
  },

  // New - Export functionality
  exportQuizzes() {
    return api.post('/api/jobs/user/export/quiz');
  },
  exportUsers() {
    return api.post('/api/jobs/admin/export/users');
  },
  getJobStatus(jobId) {
    return api.get(`/api/jobs/status/${jobId}`);
  },
  getDownloadUrl(filename) {
    return `${API_URL}/api/jobs/download/${filename}`;
  }
}; 
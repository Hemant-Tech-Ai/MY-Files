<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Admin Dashboard</h1>
    </div>
    
    <!-- Alert for API errors -->
    <div v-if="errors.stats || errors.users || errors.quizzes" class="alert alert-warning mb-4">
      <strong>Warning:</strong> Some data could not be loaded from the server.
      <button class="btn btn-sm btn-outline-warning float-end" @click="fetchData">
        <i class="bi bi-arrow-clockwise"></i> Retry
      </button>
    </div>
    
    <div class="row">
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="card-title">Subjects</h4>
            <div v-if="loading.stats" class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p v-else class="card-text display-4">{{ stats.subjectCount }}</p>
            <p class="text-muted">Manage all subjects</p>
            <router-link to="/admin/subjects" class="btn btn-primary">Manage</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="card-title">Chapters</h4>
            <div v-if="loading.stats" class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p v-else class="card-text display-4">{{ stats.chapterCount }}</p>
            <p class="text-muted">Manage all chapters</p>
            <router-link to="/admin/chapters" class="btn btn-primary">Manage</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="card-title">Quizzes</h4>
            <div v-if="loading.stats" class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p v-else class="card-text display-4">{{ stats.quizCount }}</p>
            <p class="text-muted">Manage all quizzes</p>
            <router-link to="/admin/quizzes" class="btn btn-primary">Manage</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="card-title">Questions</h4>
            <div v-if="loading.stats" class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p v-else class="card-text display-4">{{ stats.questionCount }}</p>
            <p class="text-muted">Manage all questions</p>
            <router-link to="/admin/questions" class="btn btn-primary">Manage</router-link>
          </div>
        </div>
      </div>

      <!-- New Reports Card -->
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="card-title">Reports</h4>
            <div v-if="loading.stats" class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p v-else class="card-text display-4">
              <i class="bi bi-file-earmark-bar-graph"></i>
            </p>
            <p class="text-muted">Generate monthly reports</p>
            <router-link to="/admin/reports" class="btn btn-primary">Manage</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <div class="row mt-4">
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Recent Users</h5>
          </div>
          <div class="card-body">
            <div v-if="loading.users" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="errors.users" class="alert alert-danger">
              {{ errors.users }}
            </div>
            <div v-else-if="users.length === 0" class="text-center py-3">
              <p class="text-muted">No users found</p>
            </div>
            <table v-else class="table table-hover">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Full Name</th>
                  <th>Qualification</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users.slice(0, 5)" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.full_name }}</td>
                  <td>{{ user.qualification }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Recent Quizzes</h5>
          </div>
          <div class="card-body">
            <div v-if="loading.quizzes" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="errors.quizzes" class="alert alert-danger">
              {{ errors.quizzes }}
            </div>
            <div v-else-if="quizzes.length === 0" class="text-center py-3">
              <p class="text-muted">No quizzes found</p>
            </div>
            <table v-else class="table table-hover">
              <thead>
                <tr>
                  <th>Quiz</th>
                  <th>Date</th>
                  <th>Duration</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="quiz in quizzes.slice(0, 5)" :key="quiz.id">
                  <td>{{ quiz.subject_name || '' }} - {{ quiz.chapter_name || '' }}</td>
                  <td>{{ formatDate(quiz.date_of_quiz) }}</td>
                  <td>{{ quiz.time_duration }} min</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- New section for Quiz Assignments -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Quiz Assignments</h5>
            <button class="btn btn-sm btn-outline-primary" @click="fetchQuizAssignments">
              <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
          </div>
          <div class="card-body">
            <div v-if="loading.assignments" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="errors.assignments" class="alert alert-danger">
              {{ errors.assignments }}
            </div>
            <div v-else-if="quizAssignments.length === 0" class="text-center py-3">
              <p class="text-muted">No quiz assignments found</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Quiz</th>
                    <th>Student</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="assignment in quizAssignments" :key="assignment.id">
                    <td>{{ assignment.subject_name }} - {{ assignment.chapter_name }}</td>
                    <td>{{ assignment.student_name }}</td>
                    <td>{{ formatDate(assignment.date_of_quiz) }}</td>
                    <td>
                      <span v-if="assignment.completed" class="badge bg-success">Completed</span>
                      <span v-else class="badge bg-warning">Pending</span>
                    </td>
                    <td>
                      <router-link :to="`/admin/quizzes?assignQuiz=${assignment.quiz_id}`" class="btn btn-sm btn-primary">
                        <i class="bi bi-pencil me-1"></i> Assign
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {
        subjectCount: 0,
        chapterCount: 0,
        quizCount: 0,
        questionCount: 0,
        userCount: 0
      },
      users: [],
      quizzes: [],
      quizAssignments: [],
      loading: {
        stats: true,
        users: true,
        quizzes: true,
        assignments: true
      },
      errors: {
        stats: null,
        users: null,
        quizzes: null,
        assignments: null
      }
    }
  },
  mounted() {
    const token = localStorage.getItem('token');
    const isAdmin = localStorage.getItem('isAdmin');
    const loginTime = localStorage.getItem('loginTime');
    const now = new Date().getTime();
    
    // Calculate time since login if available
    const timeSinceLogin = loginTime ? Math.floor((now - parseInt(loginTime)) / 1000) : 'unknown';
    
    console.log('AdminDashboard mounted, auth state:', { 
      token: token ? `${token.substring(0, 15)}...` : null,
      isAdmin,
      timeSinceLogin: `${timeSinceLogin} seconds`
    });
    
    // Check token validity
    if (!token) {
      console.error('No token found, redirecting to login');
      this.$router.push('/login');
      return;
    }

    // Add a test API call to validate token before proceeding
    api.getDashboardStats()
      .then(() => {
        console.log('Token validated successfully');
        this.fetchData();
      })
      .catch(error => {
        console.error('Token validation failed:', error);
        if (error.response && error.response.status === 401) {
          console.log('Authentication failed, redirecting to login');
          this.$router.push('/login');
        } else {
          // Continue with other data even if stats endpoint fails
          this.fetchData();
        }
      });
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    fetchData() {
      this.fetchStats();
      this.fetchUsers();
      this.fetchQuizzes();
      this.fetchQuizAssignments();
    },
    
    async fetchStats() {
      try {
        this.loading.stats = true;
        this.errors.stats = null;
        
        // Try to fetch dashboard stats directly if endpoint exists
        try {
          const statsResponse = await api.getDashboardStats();
          this.stats = statsResponse.data;
        } catch (statsError) {
          // Fallback to individual counts if stats endpoint fails
          console.log('Falling back to individual API calls for stats');
          
          const subjectsResponse = await api.getSubjects();
          const chaptersResponse = await api.getChapters();
          const quizzesResponse = await api.getQuizzes();
          const questionsResponse = await api.getQuestions();
          
          // Update stats
          this.stats.subjectCount = subjectsResponse.data.length || 0;
          this.stats.chapterCount = chaptersResponse.data.length || 0;
          this.stats.quizCount = quizzesResponse.data.length || 0;
          this.stats.questionCount = questionsResponse.data.length || 0;
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
        this.errors.stats = 'Failed to load dashboard statistics';
      } finally {
        this.loading.stats = false;
      }
    },
    
    async fetchUsers() {
      try {
        this.loading.users = true;
        this.errors.users = null;
        
        const response = await api.getUsers();
        // Filter out admin users if needed
        this.users = response.data.filter(user => !user.is_admin);
      } catch (error) {
        console.error('Error fetching users:', error);
        this.errors.users = 'Failed to load users';
      } finally {
        this.loading.users = false;
      }
    },
    
    async fetchQuizzes() {
      try {
        this.loading.quizzes = true;
        this.errors.quizzes = null;
        
        const response = await api.getQuizzes();
        this.quizzes = response.data;
      } catch (error) {
        console.error('Error fetching quizzes:', error);
        this.errors.quizzes = 'Failed to load quizzes';
      } finally {
        this.loading.quizzes = false;
      }
    },
    
    async fetchQuizAssignments() {
      try {
        this.loading.assignments = true;
        this.errors.assignments = null;
        
        const response = await api.getQuizAssignments();
        this.quizAssignments = response.data;
      } catch (error) {
        console.error('Error fetching quiz assignments:', error);
        this.errors.assignments = 'Failed to load quiz assignments';
      } finally {
        this.loading.assignments = false;
      }
    },
    
    logout() {
      // Use the API service for logout
      api.logout().then(() => {
        console.log('Logout successful');
        this.$router.push('/login');
      }).catch(error => {
        console.error('Logout error:', error);
        // Still redirect to login even if there's an error
        this.$router.push('/login');
      });
    }
  }
}
</script> 
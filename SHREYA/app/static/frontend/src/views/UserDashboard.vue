<template>
  <div class="container mt-4">
    <h1 class="mb-4">User Dashboard</h1>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your dashboard...</p>
    </div>
    
    <div v-else>
      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="card h-100">
            <div class="card-header">
              <h5 class="mb-0">Available Quizzes</h5>
            </div>
            <div class="card-body">
              <div v-if="quizzes.length === 0" class="text-center py-5">
                <p class="text-muted">No quizzes available at the moment</p>
              </div>
              <div v-else class="list-group">
                <div v-for="quiz in quizzes" :key="quiz.id" class="list-group-item list-group-item-action">
                  <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">{{ quiz.title }}</h5>
                    <small>{{ formatDate(quiz.date_of_quiz) }}</small>
                  </div>
                  <p class="mb-1">{{ quiz.subject }} - {{ quiz.chapter }}</p>
                  <p class="mb-1"><small class="text-muted">Duration: {{ quiz.time_duration }} minutes</small></p>
                  <div class="mt-2">
                    <router-link :to="`/take-quiz/${quiz.id}`" class="btn btn-sm btn-primary">
                      Start Quiz
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 mb-4">
          <div class="card h-100">
            <div class="card-header">
              <h5 class="mb-0">Your Performance</h5>
            </div>
            <div class="card-body">
              <div v-if="scores.length === 0" class="text-center py-5">
                <p class="text-muted">No quiz attempts yet</p>
              </div>
              <div v-else>
                <div class="row text-center mb-4">
                  <div class="col-4">
                    <h2>{{ scores.length }}</h2>
                    <p class="text-muted">Quizzes Taken</p>
                  </div>
                  <div class="col-4">
                    <h2>{{ averageScore }}%</h2>
                    <p class="text-muted">Average Score</p>
                  </div>
                  <div class="col-4">
                    <h2>{{ highestScore }}%</h2>
                    <p class="text-muted">Highest Score</p>
                  </div>
                </div>
                
                <h6>Recent Attempts</h6>
                <div class="list-group">
                  <div v-for="score in scores.slice(0, 3)" :key="score.id" class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                      <h6 class="mb-1">{{ score.quiz_title }}</h6>
                      <small>{{ formatDate(score.time_stamp_of_attempt) }}</small>
                    </div>
                    <div class="progress mt-2" style="height: 10px;">
                      <div class="progress-bar" role="progressbar" 
                           :style="`width: ${(score.total_scored / score.total_questions) * 100}%`"
                           :class="getProgressBarClass(score.total_scored, score.total_questions)">
                      </div>
                    </div>
                    <small class="mt-1 d-block">Score: {{ score.total_scored }}/{{ score.total_questions }} 
                      ({{ Math.round((score.total_scored / score.total_questions) * 100) }}%)</small>
                  </div>
                </div>
                
                <div class="text-center mt-3">
                  <router-link to="/scores" class="btn btn-outline-primary btn-sm">
                    View All Scores
                  </router-link>
                </div>
              </div>
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
  name: 'UserDashboard',
  data() {
    return {
      quizzes: [],
      scores: [],
      loading: true,
      refreshTimer: null
    }
  },
  computed: {
    averageScore() {
      if (this.scores.length === 0) return 0;
      
      // Filter out any invalid scores
      const validScores = this.scores.filter(score => 
        score.total_questions > 0 && score.total_scored !== undefined && score.total_scored !== null
      );
      
      if (validScores.length === 0) return 0;
      
      const totalPercentage = validScores.reduce((sum, score) => {
        return sum + (score.total_scored / score.total_questions) * 100;
      }, 0);
      
      return Math.round(totalPercentage / validScores.length);
    },
    highestScore() {
      if (this.scores.length === 0) return 0;
      
      // Filter out any invalid scores
      const validScores = this.scores.filter(score => 
        score.total_questions > 0 && score.total_scored !== undefined && score.total_scored !== null
      );
      
      if (validScores.length === 0) return 0;
      
      const percentages = validScores.map(score => 
        (score.total_scored / score.total_questions) * 100
      );
      
      return Math.round(Math.max(...percentages));
    }
  },
  mounted() {
    this.fetchDashboardData();
  },
  watch: {
    // Watch for route changes to detect when returning from quiz
    '$route.query': {
      handler(newQuery) {
        // If there's a refresh parameter, refresh the data
        if (newQuery.refresh) {
          console.log('Dashboard refresh triggered by route query');
          this.fetchDashboardData();
        }
      },
      immediate: true
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    getProgressBarClass(scored, total) {
      if (!total || total <= 0 || scored === undefined || scored === null) return 'bg-secondary';
      const percentage = (scored / total) * 100;
      if (percentage >= 75) return 'bg-success';
      if (percentage >= 50) return 'bg-info';
      if (percentage >= 25) return 'bg-warning';
      return 'bg-danger';
    },
    async fetchDashboardData() {
      try {
        this.loading = true;
        
        // Clear any existing refresh timer
        if (this.refreshTimer) {
          clearTimeout(this.refreshTimer);
          this.refreshTimer = null;
        }
        
        // Fetch quizzes and scores in parallel using the API service
        const [quizzesResponse, scoresResponse, performanceResponse] = await Promise.all([
          api.getAssignedQuizzes(),
          api.getUserScores(),
          api.getDashboardPerformance()
        ]);
        
        console.log('Dashboard data from API:', { 
          quizzes: quizzesResponse.data,
          scores: scoresResponse.data,
          performance: performanceResponse?.data
        });
        
        this.quizzes = quizzesResponse.data.map(quiz => ({
          id: quiz.id,
          title: quiz.remarks || `Quiz #${quiz.id}`,
          subject: quiz.subject_name,
          chapter: quiz.chapter_name,
          date_of_quiz: quiz.date_of_quiz,
          time_duration: quiz.time_duration,
          completed: quiz.completed
        })).filter(quiz => !quiz.completed);
        
        this.scores = scoresResponse.data.map(score => {
          // Normalize score data
          const processed = {
            id: score.id,
            quiz_id: score.quiz_id,
            quiz_title: (score.subject_name || 'Unknown') + ': ' + (score.chapter_name || 'Quiz'),
            time_stamp_of_attempt: score.date || score.time_stamp_of_attempt,
            total_scored: 0,
            total_questions: 0
          };
          
          // Handle score value
          if (typeof score.score !== 'undefined' && score.score !== null) {
            processed.total_scored = Number(score.score);
          } else if (typeof score.total_scored !== 'undefined' && score.total_scored !== null) {
            processed.total_scored = Number(score.total_scored);
          }
          
          // Handle total value
          if (typeof score.total !== 'undefined' && score.total !== null) {
            processed.total_questions = Number(score.total);
          } else if (typeof score.total_questions !== 'undefined' && score.total_questions !== null) {
            processed.total_questions = Number(score.total_questions);
          }
          
          return processed;
        });
        
        console.log('Processed dashboard data:', {
          quizzes: this.quizzes,
          scores: this.scores
        });
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script> 
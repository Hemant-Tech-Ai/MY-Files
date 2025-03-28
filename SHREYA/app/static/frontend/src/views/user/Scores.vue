<template>
  <div class="container mt-4">
    <h1 class="mb-4">Quiz Reports</h1>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your score reports...</p>
    </div>
    
    <div v-else>
      <!-- Summary card -->
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Performance Summary</h5>
            <button class="btn btn-sm btn-light" @click="refreshScores" title="Refresh scores">
              <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="scores.length === 0" class="text-center py-5">
            <p class="text-muted">You haven't completed any quizzes yet</p>
            <router-link to="/user" class="btn btn-primary mt-2">Go to Dashboard</router-link>
          </div>
          <div v-else>
            <div class="row text-center">
              <div class="col-md-3 mb-3">
                <div class="performance-stat">
                  <h2>{{ scores.length }}</h2>
                  <p class="text-muted">Quizzes Completed</p>
                </div>
              </div>
              <div class="col-md-3 mb-3">
                <div class="performance-stat">
                  <h2>{{ averageScore }}%</h2>
                  <p class="text-muted">Average Score</p>
                </div>
              </div>
              <div class="col-md-3 mb-3">
                <div class="performance-stat">
                  <h2>{{ highestScore }}%</h2>
                  <p class="text-muted">Highest Score</p>
                </div>
              </div>
              <div class="col-md-3 mb-3">
                <div class="performance-stat">
                  <h2>{{ totalCorrect }}/{{ totalQuestions }}</h2>
                  <p class="text-muted">Total Correct Answers</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Score List -->
      <div v-if="scores.length > 0">
        <h4 class="mb-3">Quiz History</h4>
        
        <!-- Filter and Sort controls -->
        <div class="row mb-4">
          <div class="col-md-6">
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search by subject or chapter..." 
                v-model="searchQuery"
              >
              <button class="btn btn-outline-secondary" type="button" @click="searchQuery = ''">
                Clear
              </button>
            </div>
          </div>
          <div class="col-md-6 d-flex justify-content-end">
            <div class="btn-group">
              <button 
                class="btn" 
                :class="sortBy === 'date' ? 'btn-primary' : 'btn-outline-primary'"
                @click="setSortBy('date')"
              >
                Sort by Date
              </button>
              <button 
                class="btn" 
                :class="sortBy === 'score' ? 'btn-primary' : 'btn-outline-primary'"
                @click="setSortBy('score')"
              >
                Sort by Score
              </button>
            </div>
          </div>
        </div>
        
        <div class="table-responsive">
          <table class="table table-striped table-hover">
            <thead>
              <tr>
                <th>Date</th>
                <th>Subject</th>
                <th>Chapter</th>
                <th>Score</th>
                <th>Percentage</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="score in filteredAndSortedScores" :key="score.id">
                <td>{{ formatDate(score.date) }}</td>
                <td>{{ score.subject_name }}</td>
                <td>{{ score.chapter_name }}</td>
                <td>{{ score.score }}/{{ score.total }}</td>
                <td>
                  <div class="progress" style="height: 12px; min-width: 100px;">
                    <div 
                      class="progress-bar" 
                      role="progressbar" 
                      :style="`width: ${getPercentage(score.score, score.total)}%`"
                      :class="getProgressBarClass(score.score, score.total)"
                    ></div>
                  </div>
                  <small>{{ getPercentage(score.score, score.total) }}%</small>
                </td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary" 
                    @click="viewScoreDetails(score)"
                    data-bs-toggle="modal" 
                    data-bs-target="#scoreDetailsModal"
                  >
                    View Report
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Score Details Modal -->
    <div class="modal fade" id="scoreDetailsModal" tabindex="-1" aria-labelledby="scoreDetailsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedScore">
          <div class="modal-header">
            <h5 class="modal-title" id="scoreDetailsModalLabel">
              Quiz Report: {{ selectedScore.subject_name }} - {{ selectedScore.chapter_name }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="score-summary mb-4">
              <div class="row text-center">
                <div class="col-md-4">
                  <div class="stat-card">
                    <h2>{{ selectedScore.score }}/{{ selectedScore.total }}</h2>
                    <p>Score</p>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="stat-card">
                    <h2>{{ getPercentage(selectedScore.score, selectedScore.total) }}%</h2>
                    <p>Percentage</p>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="stat-card">
                    <h2>{{ formatDate(selectedScore.date) }}</h2>
                    <p>Date Taken</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="correct-wrong-summary mb-4">
              <div class="row">
                <div class="col-md-6">
                  <div class="card text-bg-success mb-3">
                    <div class="card-body text-center">
                      <h4 class="card-title">{{ selectedScore.score }}</h4>
                      <p class="card-text">Correct Answers</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="card text-bg-danger mb-3">
                    <div class="card-body text-center">
                      <h4 class="card-title">{{ selectedScore.total - selectedScore.score }}</h4>
                      <p class="card-text">Incorrect Answers</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <h6>Performance by Question</h6>
            <p class="text-muted small">Note: This is just a summary. Actual question details are not shown for security reasons.</p>
            
            <div class="question-summary">
              <div class="row">
                <div class="col-12">
                  <div class="progress" style="height: 30px;">
                    <div 
                      class="progress-bar bg-success" 
                      role="progressbar" 
                      :style="`width: ${getPercentage(selectedScore.score, selectedScore.total)}%`"
                    >
                      {{ selectedScore.score }} Correct
                    </div>
                    <div 
                      class="progress-bar bg-danger" 
                      role="progressbar" 
                      :style="`width: ${getPercentage(selectedScore.total - selectedScore.score, selectedScore.total)}%`"
                    >
                      {{ selectedScore.total - selectedScore.score }} Incorrect
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <router-link to="/user" class="btn btn-primary">Go to Dashboard</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'ScoresView',
  data() {
    return {
      scores: [],
      loading: true,
      selectedScore: null,
      searchQuery: '',
      sortBy: 'date', // 'date' or 'score'
      sortOrder: 'desc' // 'asc' or 'desc'
    }
  },
  computed: {
    filteredAndSortedScores() {
      // Filter scores based on search query
      let filtered = [...this.scores];
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(score => 
          (score.subject_name && score.subject_name.toLowerCase().includes(query)) || 
          (score.chapter_name && score.chapter_name.toLowerCase().includes(query))
        );
      }
      
      // Sort scores based on sort criteria
      filtered.sort((a, b) => {
        if (this.sortBy === 'date') {
          const dateA = new Date(a.date);
          const dateB = new Date(b.date);
          return this.sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
        } else if (this.sortBy === 'score') {
          const scorePercentA = this.getPercentage(a.score, a.total);
          const scorePercentB = this.getPercentage(b.score, b.total);
          return this.sortOrder === 'asc' ? scorePercentA - scorePercentB : scorePercentB - scorePercentA;
        }
        return 0;
      });
      
      return filtered;
    },
    averageScore() {
      if (this.scores.length === 0) return 0;
      let validScores = this.scores.filter(score => score.total > 0);
      if (validScores.length === 0) return 0;
      
      const totalPercentage = validScores.reduce((sum, score) => {
        return sum + this.getPercentage(score.score, score.total);
      }, 0);
      
      return Math.round(totalPercentage / validScores.length);
    },
    highestScore() {
      if (this.scores.length === 0) return 0;
      const percentages = this.scores
        .filter(score => score.total > 0)
        .map(score => this.getPercentage(score.score, score.total));
        
      return percentages.length > 0 ? Math.max(...percentages) : 0;
    },
    totalCorrect() {
      return this.scores.reduce((sum, score) => sum + (score.score || 0), 0);
    },
    totalQuestions() {
      return this.scores.reduce((sum, score) => sum + (score.total || 0), 0);
    }
  },
  mounted() {
    this.fetchScores();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    getPercentage(score, total) {
      if (!total || total <= 0 || !score) return 0;
      return Math.round((score / total) * 100);
    },
    getProgressBarClass(scored, total) {
      const percentage = this.getPercentage(scored, total);
      if (percentage >= 75) return 'bg-success';
      if (percentage >= 50) return 'bg-info';
      if (percentage >= 25) return 'bg-warning';
      return 'bg-danger';
    },
    setSortBy(sortType) {
      if (this.sortBy === sortType) {
        // Toggle sort order if clicking the same sort button
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortBy = sortType;
        // Default order: date - descending (newest first), score - descending (highest first)
        this.sortOrder = 'desc';
      }
    },
    viewScoreDetails(score) {
      this.selectedScore = score;
    },
    refreshScores() {
      console.log('Manually refreshing scores data');
      this.fetchScores();
    },
    async fetchScores() {
      try {
        this.loading = true;
        
        const response = await api.getUserScores();
        console.log('Scores API raw response:', response.data);
        
        // Normalize the API response to match our component's expected structure
        this.scores = response.data.map(score => {
          console.log('Processing score item:', score);
          
          // Handle various possible property names in the API response
          const mappedScore = {
            id: score.id,
            quiz_id: score.quiz_id,
            subject_name: score.subject_name || 'Unknown Subject',
            chapter_name: score.chapter_name || 'Unknown Chapter',
            score: 0,
            total: 0,
            date: score.date || score.time_stamp_of_attempt
          };
          
          // Handle score value
          if (typeof score.score !== 'undefined' && score.score !== null) {
            mappedScore.score = Number(score.score);
          } else if (typeof score.total_scored !== 'undefined' && score.total_scored !== null) {
            mappedScore.score = Number(score.total_scored);
          }
          
          // Handle total value
          if (typeof score.total !== 'undefined' && score.total !== null) {
            mappedScore.total = Number(score.total);
          } else if (typeof score.total_questions !== 'undefined' && score.total_questions !== null) {
            mappedScore.total = Number(score.total_questions);
          }
          
          console.log('Processed score item:', mappedScore);
          return mappedScore;
        });
        
        console.log('All processed scores:', this.scores);
        
      } catch (error) {
        console.error('Error fetching scores:', error);
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        }
        // Reset to empty array
        this.scores = [];
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.performance-stat {
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}
.performance-stat:hover {
  transform: translateY(-5px);
}
.performance-stat h2 {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.stat-card {
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 0.5rem;
  background-color: #f8f9fa;
}
.stat-card h2 {
  font-size: 1.75rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}
.stat-card p {
  margin-bottom: 0;
  color: #6c757d;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .performance-stat h2 {
    font-size: 1.5rem;
  }
  .stat-card h2 {
    font-size: 1.25rem;
  }
}
</style> 
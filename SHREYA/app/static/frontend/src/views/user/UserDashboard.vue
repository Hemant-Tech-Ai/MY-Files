<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>User Dashboard</h1>
    </div>

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
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">Take Quiz</h5>
            </div>
            <div class="card-body">
              <!-- Step 1: Select Subject -->
              <div v-if="currentStep === 1">
                <h6 class="mb-3">Step 1: Select a Subject</h6>
                <div v-if="subjects.length === 0" class="text-center py-4">
                  <p class="text-muted">No subjects available</p>
                </div>
                <div v-else class="list-group">
                  <button 
                    v-for="subject in subjects" 
                    :key="subject.id" 
                    class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                    @click="selectSubject(subject)"
                  >
                    {{ subject.name }}
                    <span class="badge bg-primary rounded-pill">{{ getChaptersCountForSubject(subject.id) }} chapters</span>
                  </button>
                </div>
              </div>

              <!-- Step 2: Select Chapter -->
              <div v-else-if="currentStep === 2">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h6 class="mb-0">Step 2: Select a Chapter</h6>
                  <button class="btn btn-sm btn-outline-secondary" @click="goBack">Back</button>
                </div>
                <p class="mb-3"><strong>Subject:</strong> {{ selectedSubject.name }}</p>
                
                <div v-if="chaptersForSubject.length === 0" class="text-center py-4">
                  <p class="text-muted">No chapters available for this subject</p>
                </div>
                <div v-else class="list-group">
                  <button 
                    v-for="chapter in chaptersForSubject" 
                    :key="chapter.id" 
                    class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                    @click="selectChapter(chapter)"
                  >
                    {{ chapter.name }}
                    <span class="badge bg-primary rounded-pill">{{ getQuizzesCountForChapter(chapter.id) }} quizzes</span>
                  </button>
                </div>
              </div>

              <!-- Step 3: Select Quiz -->
              <div v-else-if="currentStep === 3">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h6 class="mb-0">Step 3: Select a Quiz</h6>
                  <button class="btn btn-sm btn-outline-secondary" @click="goBack">Back</button>
                </div>
                <p class="mb-1"><strong>Subject:</strong> {{ selectedSubject.name }}</p>
                <p class="mb-3"><strong>Chapter:</strong> {{ selectedChapter.name }}</p>
                
                <div v-if="quizzesForChapter.length === 0" class="text-center py-4">
                  <p class="text-muted">No quizzes available for this chapter</p>
                </div>
                <div v-else class="list-group">
                  <div 
                    v-for="quiz in quizzesForChapter" 
                    :key="quiz.id" 
                    class="list-group-item list-group-item-action"
                  >
                    <div class="d-flex w-100 justify-content-between">
                      <h6 class="mb-1">Quiz #{{ quiz.id }}</h6>
                      <small>
                        <span v-if="quiz.completed" class="badge bg-success">Completed</span>
                        <span v-else class="badge bg-warning">Pending</span>
                      </small>
                    </div>
                    <p class="mb-1 small text-muted">
                      <span v-if="quiz.date_of_quiz">Date: {{ formatDate(quiz.date_of_quiz) }}</span>
                      <span v-else>No date specified</span>
                      | Duration: {{ quiz.time_duration }} minutes
                      | Questions: {{ quiz.question_count }}
                    </p>
                    <div class="mt-2">
                      <router-link 
                        v-if="!quiz.completed" 
                        :to="`/user/quiz/${quiz.id}`" 
                        class="btn btn-sm btn-primary"
                      >
                        Take Quiz
                      </router-link>
                      <button 
                        v-else 
                        class="btn btn-sm btn-outline-secondary"
                        @click="viewScore(quiz)"
                      >
                        View Results ({{ quiz.score }}/{{ quiz.total }})
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 mb-4">
          <div class="card h-100">
            <div class="card-header bg-info text-white">
              <h5 class="mb-0">Your Performance</h5>
            </div>
            <div class="card-body">
              <div v-if="performance.loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading performance data...</p>
              </div>
              <div v-else-if="performance.error" class="alert alert-warning">
                {{ performance.error }}
              </div>
              <div v-else>
                <div class="row text-center mb-4">
                  <div class="col-4">
                    <h2>{{ performance.data.quizzes_taken }}</h2>
                    <p class="text-muted">Quizzes Taken</p>
                  </div>
                  <div class="col-4">
                    <h2>{{ performance.data.average_score }}</h2>
                    <p class="text-muted">Average Score</p>
                  </div>
                  <div class="col-4">
                    <h2>{{ performance.data.highest_score }}</h2>
                    <p class="text-muted">Highest Score</p>
                  </div>
                </div>
                
                <h6>Recent Attempts</h6>
                <div v-if="performance.data.recent_attempts.length === 0" class="text-center py-4">
                  <p class="text-muted">No quiz attempts yet</p>
                </div>
                <div v-else class="list-group">
                  <div v-for="attempt in performance.data.recent_attempts" :key="attempt.id" class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                      <h6 class="mb-1">{{ attempt.title }}</h6>
                      <small>{{ attempt.date }}</small>
                    </div>
                    <div class="progress mt-2" style="height: 10px;">
                      <div class="progress-bar" role="progressbar" 
                           :style="`width: ${attempt.percentage.replace('%', '')}%`"
                           :class="getProgressBarClass(attempt.percentage)">
                      </div>
                    </div>
                    <small class="mt-1 d-block">Score: {{ attempt.score }} ({{ attempt.percentage }})</small>
                  </div>
                </div>
                
                <div class="text-center mt-3">
                  <router-link to="/user/scores" class="btn btn-outline-primary btn-sm">
                    View All Scores
                  </router-link>
                  <button class="btn btn-outline-success btn-sm ms-2" @click="exportQuizzes">
                    <i class="bi bi-download me-1"></i> Export Results
                  </button>
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
      loading: true,
      currentStep: 1,
      // Data for steps
      subjects: [],
      chapters: [],
      quizzes: [],
      scores: [],
      // Selected items
      selectedSubject: null,
      selectedChapter: null,
      performance: {
        loading: true,
        error: null,
        data: {
          quizzes_taken: 0,
          average_score: 0,
          highest_score: 0,
          recent_attempts: []
        }
      }
    }
  },
  computed: {
    chaptersForSubject() {
      if (!this.selectedSubject) return [];
      return this.chapters.filter(chapter => chapter.subject_id === this.selectedSubject.id);
    },
    quizzesForChapter() {
      if (!this.selectedChapter) return [];
      return this.quizzes.filter(quiz => quiz.chapter_id === this.selectedChapter.id);
    },
    averageScore() {
      if (this.scores.length === 0) return 0;
      const totalPercentage = this.scores.reduce((sum, score) => {
        return sum + (score.score / score.total) * 100;
      }, 0);
      return Math.round(totalPercentage / this.scores.length);
    },
    highestScore() {
      if (this.scores.length === 0) return 0;
      const percentages = this.scores.map(score => 
        (score.score / score.total) * 100
      );
      return Math.round(Math.max(...percentages));
    }
  },
  mounted() {
    this.fetchDashboardData();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    getProgressBarClass(percentage) {
      if (typeof percentage === 'string') {
        percentage = parseFloat(percentage);
      }
      
      if (percentage >= 75) return 'bg-success';
      if (percentage >= 50) return 'bg-info';
      if (percentage >= 25) return 'bg-warning';
      return 'bg-danger';
    },
    getChaptersCountForSubject(subjectId) {
      return this.chapters.filter(chapter => chapter.subject_id === subjectId).length;
    },
    getQuizzesCountForChapter(chapterId) {
      return this.quizzes.filter(quiz => quiz.chapter_id === chapterId).length;
    },
    selectSubject(subject) {
      this.selectedSubject = subject;
      this.currentStep = 2;
    },
    selectChapter(chapter) {
      this.selectedChapter = chapter;
      this.currentStep = 3;
    },
    goBack() {
      if (this.currentStep === 3) {
        this.currentStep = 2;
        this.selectedChapter = null;
      } else if (this.currentStep === 2) {
        this.currentStep = 1;
        this.selectedSubject = null;
      }
    },
    viewScore() {
      this.$router.push('/user/scores');
    },
    fetchDashboardData() {
      this.loading = true;
      
      // Fetch subjects
      api.getUserSubjects()
        .then(response => {
          this.subjects = response.data;
          return api.getUserChapters();
        })
        .then(response => {
          this.chapters = response.data;
          return api.getAssignedQuizzes();
        })
        .then(response => {
          this.quizzes = response.data;
          // Fetch performance data
          return this.fetchPerformanceData();
        })
        .catch(error => {
          console.error('Error loading dashboard data:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    async fetchPerformanceData() {
      try {
        this.performance.loading = true;
        this.performance.error = null;
        
        const response = await api.getDashboardPerformance();
        this.performance.data = response.data;
        
        console.log('Performance data loaded:', this.performance.data);
      } catch (error) {
        console.error('Error fetching performance data:', error);
        this.performance.error = 'Failed to load performance data. Please try refreshing the page.';
      } finally {
        this.performance.loading = false;
      }
    },
    async exportQuizzes() {
      try {
        const response = await api.exportQuizzes();
        const jobId = response.data.job_id;
        
        // Show success message
        alert(`Export started! Your file will be available shortly. Job ID: ${jobId}`);
        
        // You could implement job status checking here
        // or redirect to a page that shows job status
      } catch (error) {
        console.error('Error starting export:', error);
        alert('Failed to start export. Please try again later.');
      }
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}
.card:hover {
  transform: translateY(-5px);
}
</style> 
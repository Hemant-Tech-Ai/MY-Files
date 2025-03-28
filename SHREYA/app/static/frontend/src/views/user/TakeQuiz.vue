<template>
  <div class="container mt-4">
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading quiz...</p>
    </div>
    
    <div v-else-if="!quiz" class="alert alert-danger">
      <h4 class="alert-heading">Quiz Not Found</h4>
      <p>The quiz you requested does not exist or is not assigned to you.</p>
      <hr>
      <router-link to="/user" class="btn btn-primary">Back to Dashboard</router-link>
    </div>
    
    <div v-else>
      <div class="card mb-4">
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <h4 class="mb-0">Quiz #{{ quiz.id }}</h4>
          <div v-if="quizStarted && !quizSubmitted" class="timer-container">
            <div class="timer">
              <i class="bi bi-clock"></i> {{ formattedTimeRemaining }}
            </div>
          </div>
        </div>
        <div class="card-body">
          <div class="quiz-info mb-4">
            <h5>{{ quiz.subject_name }}: {{ quiz.chapter_name }}</h5>
            <div class="d-flex flex-wrap gap-3 mt-2 text-muted">
              <div><i class="bi bi-calendar"></i> {{ formatDate(quiz.date_of_quiz) || 'No date specified' }}</div>
              <div><i class="bi bi-hourglass"></i> {{ quiz.time_duration }} minutes</div>
              <div><i class="bi bi-list-ol"></i> {{ questions.length }} questions</div>
            </div>
          </div>
          
          <!-- Quiz start screen -->
          <div v-if="!quizStarted && !quizSubmitted" class="text-center p-4">
            <h5 class="mb-3">Ready to begin?</h5>
            <p class="mb-4">Once you start, you will have {{ quiz.time_duration }} minutes to complete the quiz.</p>
            <button class="btn btn-primary btn-lg" @click="startQuiz">Start Quiz</button>
          </div>
          
          <!-- Quiz in progress -->
          <div v-else-if="quizStarted && !quizSubmitted">
            <div class="progress mb-4" style="height: 8px;">
              <div 
                class="progress-bar bg-primary" 
                role="progressbar" 
                :style="`width: ${progress}%`"
              ></div>
            </div>
            
            <div class="d-flex justify-content-between mb-3">
              <span>Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}</span>
              <span>
                {{ Object.keys(answers).length }} of {{ questions.length }} answered
              </span>
            </div>
            
            <div class="question-container">
              <h5 class="question-text mb-4">{{ currentQuestion.question_statement }}</h5>
              
              <div class="options-list">
                <div 
                  v-for="(option, index) in currentQuestion.options || []" 
                  :key="index"
                  v-show="option"
                  class="form-check mb-3 p-0"
                >
                  <label class="form-check-label w-100">
                    <input 
                      type="radio" 
                      :name="`question-${currentQuestion.id}`" 
                      :value="index + 1" 
                      v-model="answers[currentQuestion.id]"
                      class="form-check-input me-2"
                    >
                    <span class="option-text">{{ option }}</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="navigation-buttons d-flex justify-content-between mt-4">
              <button 
                class="btn btn-outline-secondary" 
                @click="previousQuestion" 
                :disabled="currentQuestionIndex === 0"
              >
                <i class="bi bi-arrow-left"></i> Previous
              </button>
              
              <div>
                <button
                  v-if="currentQuestionIndex < questions.length - 1" 
                  class="btn btn-primary"
                  @click="nextQuestion"
                >
                  Next <i class="bi bi-arrow-right"></i>
                </button>
                <button 
                  v-else
                  class="btn btn-success"
                  @click="confirmSubmit"
                  :disabled="isSubmitting"
                >
                  <span v-if="isSubmitting">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Submitting...
                  </span>
                  <span v-else>Submit Quiz</span>
                </button>
              </div>
            </div>
            
            <!-- Question navigation pills -->
            <div class="question-pills mt-4">
              <button 
                v-for="(question, index) in questions" 
                :key="question.id"
                class="btn btn-sm me-2 mb-2" 
                :class="getQuestionPillClass(question.id, index)"
                @click="navigateToQuestion(index)"
              >
                {{ index + 1 }}
              </button>
            </div>
          </div>
          
          <!-- Quiz results -->
          <div v-else-if="quizSubmitted" class="quiz-results">
            <div class="text-center mb-4">
              <h4 class="mb-3">Quiz Completed!</h4>
              <div class="score-display">
                <div class="score-circle" :class="getScoreCircleClass()">
                  {{ getScorePercentage() }}%
                </div>
                <h5 class="mt-3">You scored {{ score.total_scored || 0 }} out of {{ score.total_questions || 0 }}</h5>
              </div>
            </div>
            
            <div class="score-breakdown p-3 mb-4 bg-light rounded">
              <h6>Your Performance</h6>
              <div class="row text-center">
                <div class="col-4">
                  <div class="stat-item">
                    <div class="stat-value text-success">{{ score.total_scored || 0 }}</div>
                    <div class="stat-label">Correct</div>
                  </div>
                </div>
                <div class="col-4">
                  <div class="stat-item">
                    <div class="stat-value text-danger">{{ (score.total_questions || 0) - (score.total_scored || 0) }}</div>
                    <div class="stat-label">Incorrect</div>
                  </div>
                </div>
                <div class="col-4">
                  <div class="stat-item">
                    <div class="stat-value text-warning">{{ questions.length - Object.keys(answers).length }}</div>
                    <div class="stat-label">Unanswered</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="text-center">
              <router-link to="/user" class="btn btn-primary me-2">Back to Dashboard</router-link>
              <router-link to="/user/scores" class="btn btn-outline-primary">View All Scores</router-link>
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
  name: 'TakeQuiz',
  data() {
    return {
      quizId: null,
      quiz: null,
      questions: [],
      loading: true,
      quizStarted: false,
      quizSubmitted: false,
      isSubmitting: false,
      currentQuestionIndex: 0,
      answers: {},
      timeRemaining: 0, // in seconds
      timer: null,
      score: {
        total_scored: 0,
        total_questions: 0
      }
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || {};
    },
    progress() {
      return this.questions.length > 0 
        ? ((this.currentQuestionIndex + 1) / this.questions.length) * 100 
        : 0;
    },
    formattedTimeRemaining() {
      const minutes = Math.floor(this.timeRemaining / 60);
      const seconds = this.timeRemaining % 60;
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
  },
  created() {
    this.quizId = parseInt(this.$route.params.id);
    this.fetchQuizData();
  },
  beforeUnmount() {
    this.clearTimer();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return null;
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    async fetchQuizData() {
      try {
        this.loading = true;
        
        console.log(`Fetching quiz data for quiz ID: ${this.quizId}`);
        
        // Get assigned quizzes to check if this quiz is assigned to the user
        const quizzesResponse = await api.getAssignedQuizzes();
        
        console.log(`Received ${quizzesResponse.data.length} assigned quizzes`);
        
        // Find the current quiz in the assigned quizzes
        this.quiz = quizzesResponse.data.find(q => q.id === this.quizId);
        
        if (!this.quiz) {
          console.error(`Quiz with ID ${this.quizId} not found in assigned quizzes`);
          this.loading = false;
          return;
        }
        
        console.log(`Found quiz: ${JSON.stringify(this.quiz)}`);
        
        // Get questions for this quiz
        try {
          const questionsResponse = await api.getQuizQuestions(this.quizId);
          
          this.questions = questionsResponse.data.questions;
          console.log(`Loaded ${this.questions.length} questions for quiz`);
        } catch (questionError) {
          console.error('Error fetching quiz questions:', questionError);
          
          if (questionError.response && questionError.response.status === 400) {
            // Quiz may have already been taken
            alert('You have already taken this quiz. Please go back to the dashboard.');
          }
        }
        
      } catch (error) {
        console.error('Error fetching quiz data:', error);
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        }
      } finally {
        this.loading = false;
      }
    },
    startQuiz() {
      this.quizStarted = true;
      
      // Set timer based on quiz duration (in minutes)
      this.timeRemaining = this.quiz.time_duration * 60;
      
      // Start the timer
      this.startTimer();
    },
    startTimer() {
      this.timer = setInterval(() => {
        if (this.timeRemaining > 0) {
          this.timeRemaining--;
        } else {
          // Time's up, submit the quiz
          this.submitQuiz();
        }
      }, 1000);
    },
    clearTimer() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
    },
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
      }
    },
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
      }
    },
    navigateToQuestion(index) {
      this.currentQuestionIndex = index;
    },
    getQuestionPillClass(questionId, index) {
      if (index === this.currentQuestionIndex) {
        return 'btn-primary';
      } else if (questionId in this.answers) {
        return 'btn-success';
      } else {
        return 'btn-outline-secondary';
      }
    },
    getScorePercentage() {
      if (!this.score.total_questions || this.score.total_questions <= 0) return 0;
      if (this.score.total_scored === undefined || this.score.total_scored === null) return 0;
      return Math.round((this.score.total_scored / this.score.total_questions) * 100);
    },
    getScoreCircleClass() {
      const percentage = this.getScorePercentage();
      if (percentage >= 75) return 'score-circle-success';
      if (percentage >= 50) return 'score-circle-info';
      if (percentage >= 25) return 'score-circle-warning';
      return 'score-circle-danger';
    },
    confirmSubmit() {
      const answeredCount = Object.keys(this.answers).length;
      const totalQuestions = this.questions.length;
      
      if (answeredCount < totalQuestions) {
        if (!confirm(`You've only answered ${answeredCount} out of ${totalQuestions} questions. Are you sure you want to submit?`)) {
          return;
        }
      }
      
      this.submitQuiz();
    },
    async submitQuiz() {
      try {
        this.isSubmitting = true;
        this.clearTimer();
        
        // Format answers as array of objects
        const formattedAnswers = Object.entries(this.answers).map(([questionId, selectedOption]) => ({
          question_id: parseInt(questionId),
          selected_option: selectedOption
        }));
        
        console.log('Submitting answers:', formattedAnswers);
        
        // Send answers to the server
        const response = await api.submitQuiz({
          quiz_id: this.quizId,
          answers: formattedAnswers
        });
        
        console.log('Quiz submission response:', response.data);
        
        // Check the response format and normalize the data
        this.score = {
          total_scored: response.data.score || response.data.total_scored || 0,
          total_questions: response.data.total_questions || response.data.questions || this.questions.length || 0
        };
        
        console.log('Processed score data:', this.score);
        
        this.quizSubmitted = true;
        
        // Set a timeout to redirect to dashboard after showing results
        setTimeout(() => {
          // Navigate to dashboard with a query parameter to force refresh
          this.$router.push({
            path: '/user',
            query: { refresh: new Date().getTime() }
          });
        }, 5000); // 5 seconds delay to show results before redirecting
        
      } catch (error) {
        console.error('Error submitting quiz:', error);
        alert('Failed to submit quiz. Please try again.');
      } finally {
        this.isSubmitting = false;
      }
    }
  }
}
</script>

<style scoped>
.timer-container {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 2rem;
}

.timer {
  color: white;
  font-weight: bold;
  font-size: 1.1rem;
}

.question-text {
  font-size: 1.2rem;
  font-weight: 500;
}

.options-list {
  margin-left: 1rem;
}

.option-text {
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  display: block;
  transition: all 0.15s ease;
}

.form-check-input:checked + .option-text {
  background-color: #f0f7ff;
  border-color: #0d6efd;
}

.option-text:hover {
  background-color: #f8f9fa;
}

.question-pills {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.score-display {
  margin: 2rem 0;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  font-size: 2rem;
  font-weight: bold;
  color: white;
}

.score-circle-success {
  background-color: #198754;
}

.score-circle-info {
  background-color: #0dcaf0;
}

.score-circle-warning {
  background-color: #ffc107;
}

.score-circle-danger {
  background-color: #dc3545;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
}
</style> 
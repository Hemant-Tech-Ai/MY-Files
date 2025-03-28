<template>
  <div class="manage-questions">
    <h1>Manage Questions</h1>
    
    <div class="mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <label for="quizFilter" class="form-label me-2">Filter by Quiz:</label>
          <select 
            class="form-select d-inline-block w-auto"
            id="quizFilter" 
            v-model="selectedQuizId"
            @change="filterQuestions"
          >
            <option value="">All Quizzes</option>
            <option 
              v-for="quiz in quizzes" 
              :key="quiz.id" 
              :value="quiz.id"
            >
              {{ quiz.chapter_name }} - {{ formatDate(quiz.date_of_quiz) }}
            </option>
          </select>
        </div>
        <button class="btn btn-primary" @click="showAddForm = !showAddForm">
          {{ showAddForm ? 'Hide Form' : 'Add New Question' }}
        </button>
      </div>
    </div>
    
    <!-- Create question form -->
    <div class="card mb-4" v-if="showAddForm">
      <div class="card-header">
        <h5 class="mb-0">Add New Question</h5>
      </div>
      <div class="card-body">
        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>
        <form @submit.prevent="createQuestion">
          <div class="mb-3">
            <label for="quizSelect" class="form-label">Quiz</label>
            <select 
              class="form-select" 
              id="quizSelect" 
              v-model="newQuestion.quiz_id"
              required
            >
              <option value="" disabled>Select a quiz</option>
              <option 
                v-for="quiz in quizzes" 
                :key="quiz.id" 
                :value="quiz.id"
              >
                {{ quiz.chapter_name }} - {{ formatDate(quiz.date_of_quiz) }}
              </option>
            </select>
          </div>
          <div class="mb-3">
            <label for="questionStatement" class="form-label">Question</label>
            <textarea 
              class="form-control" 
              id="questionStatement" 
              rows="3" 
              v-model="newQuestion.question_statement"
              required
            ></textarea>
          </div>
          <div class="mb-3">
            <label for="option1" class="form-label">Option 1</label>
            <input 
              type="text" 
              class="form-control" 
              id="option1" 
              v-model="newQuestion.option1" 
              required
            >
          </div>
          <div class="mb-3">
            <label for="option2" class="form-label">Option 2</label>
            <input 
              type="text" 
              class="form-control" 
              id="option2" 
              v-model="newQuestion.option2" 
              required
            >
          </div>
          <div class="mb-3">
            <label for="option3" class="form-label">Option 3</label>
            <input 
              type="text" 
              class="form-control" 
              id="option3" 
              v-model="newQuestion.option3" 
            >
          </div>
          <div class="mb-3">
            <label for="option4" class="form-label">Option 4</label>
            <input 
              type="text" 
              class="form-control" 
              id="option4" 
              v-model="newQuestion.option4" 
            >
          </div>
          <div class="mb-3">
            <label for="correctOption" class="form-label">Correct Option</label>
            <select 
              class="form-select" 
              id="correctOption" 
              v-model="newQuestion.correct_option"
              required
            >
              <option value="" disabled>Select correct option</option>
              <option value="1">Option 1</option>
              <option value="2">Option 2</option>
              <option value="3">Option 3</option>
              <option value="4">Option 4</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Add Question' }}
          </button>
        </form>
      </div>
    </div>
    
    <!-- Questions list -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">
          {{ selectedQuizId ? 'Questions for Selected Quiz' : 'All Questions' }}
        </h5>
      </div>
      <div class="card-body">
        <div v-if="loadingQuestions" class="text-center p-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="filteredQuestions.length === 0" class="alert alert-info">
          No questions found. Add new questions to get started.
        </div>
        <div v-else>
          <div v-for="question in filteredQuestions" :key="question.id" class="card mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <h5 class="card-title mb-0">{{ question.question_statement }}</h5>
                <div>
                  <button class="btn btn-sm btn-outline-primary me-2" @click="editQuestion(question)">Edit</button>
                  <button class="btn btn-sm btn-outline-danger" @click="deleteQuestion(question.id)">Delete</button>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="mb-1" :class="{'fw-bold text-success': question.correct_option === 1}">Option 1: {{ question.option1 }}</div>
                  <div class="mb-1" :class="{'fw-bold text-success': question.correct_option === 2}">Option 2: {{ question.option2 }}</div>
                </div>
                <div class="col">
                  <div class="mb-1" :class="{'fw-bold text-success': question.correct_option === 3}">Option 3: {{ question.option3 }}</div>
                  <div class="mb-1" :class="{'fw-bold text-success': question.correct_option === 4}">Option 4: {{ question.option4 }}</div>
                </div>
              </div>
              <div class="mt-2 text-muted small">
                Quiz: {{ getQuizName(question.quiz_id) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Edit Question Modal -->
    <div class="modal fade" id="editQuestionModal" tabindex="-1" aria-labelledby="editQuestionModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editQuestionModalLabel">Edit Question</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateQuestion">
              <div class="mb-3">
                <label for="editQuizSelect" class="form-label">Quiz</label>
                <select 
                  class="form-select" 
                  id="editQuizSelect" 
                  v-model="editingQuestion.quiz_id"
                  required
                >
                  <option value="" disabled>Select a quiz</option>
                  <option 
                    v-for="quiz in quizzes" 
                    :key="quiz.id" 
                    :value="quiz.id"
                  >
                    {{ quiz.chapter_name }}: {{ quiz.remarks || `Quiz ${quiz.id}` }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label for="editQuestionStatement" class="form-label">Question</label>
                <textarea 
                  class="form-control" 
                  id="editQuestionStatement" 
                  rows="2" 
                  v-model="editingQuestion.question_statement"
                  required
                ></textarea>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="editOption1" class="form-label">Option 1</label>
                  <div class="input-group mb-3">
                    <div class="input-group-text">
                      <input 
                        class="form-check-input mt-0" 
                        type="radio" 
                        name="editCorrectOption" 
                        value="1" 
                        v-model="editingQuestion.correct_option"
                        required
                      >
                    </div>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="editOption1" 
                      v-model="editingQuestion.option1"
                      required
                    >
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="editOption2" class="form-label">Option 2</label>
                  <div class="input-group mb-3">
                    <div class="input-group-text">
                      <input 
                        class="form-check-input mt-0" 
                        type="radio" 
                        name="editCorrectOption" 
                        value="2" 
                        v-model="editingQuestion.correct_option"
                        required
                      >
                    </div>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="editOption2" 
                      v-model="editingQuestion.option2"
                      required
                    >
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="editOption3" class="form-label">Option 3</label>
                  <div class="input-group mb-3">
                    <div class="input-group-text">
                      <input 
                        class="form-check-input mt-0" 
                        type="radio" 
                        name="editCorrectOption" 
                        value="3" 
                        v-model="editingQuestion.correct_option"
                        required
                      >
                    </div>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="editOption3" 
                      v-model="editingQuestion.option3"
                      required
                    >
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="editOption4" class="form-label">Option 4</label>
                  <div class="input-group mb-3">
                    <div class="input-group-text">
                      <input 
                        class="form-check-input mt-0" 
                        type="radio" 
                        name="editCorrectOption" 
                        value="4" 
                        v-model="editingQuestion.correct_option"
                        required
                      >
                    </div>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="editOption4" 
                      v-model="editingQuestion.option4"
                      required
                    >
                  </div>
                </div>
              </div>
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="updating">
                  {{ updating ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Navigation buttons -->
    <div class="mt-4 d-flex justify-content-center" v-if="selectedQuizId">
      <button class="btn btn-primary me-3" @click="goToDashboard">
        <i class="bi bi-house-door"></i> Return to Dashboard
      </button>
      <button class="btn btn-success" @click="assignQuiz">
        <i class="bi bi-people"></i> Assign Quiz to Students
      </button>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import { Modal } from 'bootstrap';

export default {
  name: 'ManageQuestions',
  data() {
    return {
      quizzes: [],
      questions: [],
      filteredQuestions: [],
      selectedQuizId: '',
      showAddForm: false,
      newQuestion: {
        quiz_id: '',
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: '1'
      },
      editingQuestion: {
        id: null,
        quiz_id: '',
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: '1'
      },
      error: null,
      loading: false,
      loadingQuestions: true,
      loadingQuizzes: true,
      updating: false,
      editModal: null
    }
  },
  computed: {
    quizOptions() {
      return this.quizzes.map(quiz => ({
        id: quiz.id,
        name: `${quiz.chapter_name}: ${quiz.remarks || `Quiz ${quiz.id}`}`
      }));
    }
  },
  mounted() {
    this.fetchQuizzes();
    this.fetchQuestions();
    
    // Check if there's a quiz parameter in the URL
    const quizId = this.$route.query.quiz;
    if (quizId) {
      this.selectedQuizId = parseInt(quizId);
      this.newQuestion.quiz_id = this.selectedQuizId;
      this.showAddForm = true;
    }
    
    // Initialize the edit modal
    this.editModal = new Modal(document.getElementById('editQuestionModal'));
  },
  methods: {
    async fetchQuizzes() {
      this.loadingQuizzes = true;
      try {
        const response = await api.getQuizzes();
        this.quizzes = response.data;
        
        // If a quiz was pre-selected from URL, pre-select it in the form
        if (this.selectedQuizId && !this.newQuestion.quiz_id) {
          this.newQuestion.quiz_id = this.selectedQuizId;
        }
      } catch (error) {
        console.error('Error fetching quizzes:', error);
        this.error = 'Failed to load quizzes. Please try again.';
      } finally {
        this.loadingQuizzes = false;
      }
    },
    async fetchQuestions() {
      this.loadingQuestions = true;
      try {
        const response = await api.getQuestions();
        this.questions = response.data;
        this.filterQuestions();
      } catch (error) {
        console.error('Error fetching questions:', error);
        this.error = 'Failed to load questions. Please try again.';
      } finally {
        this.loadingQuestions = false;
      }
    },
    filterQuestions() {
      if (this.selectedQuizId) {
        this.filteredQuestions = this.questions.filter(q => q.quiz_id === parseInt(this.selectedQuizId));
      } else {
        this.filteredQuestions = [...this.questions];
      }
    },
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    getQuizName(quizId) {
      const quiz = this.quizzes.find(q => q.id === quizId);
      return quiz ? `${quiz.chapter_name}: ${quiz.remarks || `Quiz ${quiz.id}`}` : `Quiz ${quizId}`;
    },
    async createQuestion() {
      this.loading = true;
      this.error = null;
      
      try {
        // Convert correct_option to integer
        const questionData = {
          ...this.newQuestion,
          correct_option: parseInt(this.newQuestion.correct_option)
        };
        
        const response = await api.createQuestion(questionData);
        this.questions.push(response.data);
        this.filterQuestions();
        
        // Reset form
        this.newQuestion = {
          quiz_id: this.selectedQuizId, // Keep the selected quiz
          question_statement: '',
          option1: '',
          option2: '',
          option3: '',
          option4: '',
          correct_option: '1'
        };
        
        // Hide form after submission
        this.showAddForm = false;
      } catch (error) {
        console.error('Error creating question:', error);
        this.error = 'Failed to create question. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    editQuestion(question) {
      this.editingQuestion = { ...question };
      // Convert quiz_id and correct_option to strings if they're numbers
      this.editingQuestion.quiz_id = String(question.quiz_id);
      this.editingQuestion.correct_option = String(question.correct_option);
      // Show the modal
      this.editModal.show();
    },
    async updateQuestion() {
      this.updating = true;
      this.error = null;
      
      try {
        // Convert correct_option to integer
        const questionData = {
          quiz_id: parseInt(this.editingQuestion.quiz_id),
          question_statement: this.editingQuestion.question_statement,
          option1: this.editingQuestion.option1,
          option2: this.editingQuestion.option2,
          option3: this.editingQuestion.option3,
          option4: this.editingQuestion.option4,
          correct_option: parseInt(this.editingQuestion.correct_option)
        };
        
        const response = await api.updateQuestion(this.editingQuestion.id, questionData);
        
        // Update the question in the list
        const index = this.questions.findIndex(q => q.id === this.editingQuestion.id);
        if (index !== -1) {
          this.questions[index] = response.data;
          this.filterQuestions();
        }
        
        // Close the modal
        this.editModal.hide();
      } catch (error) {
        console.error('Error updating question:', error);
        this.error = 'Failed to update question. Please try again.';
      } finally {
        this.updating = false;
      }
    },
    async deleteQuestion(id) {
      if (confirm('Are you sure you want to delete this question?')) {
        try {
          await api.deleteQuestion(id);
          this.questions = this.questions.filter(question => question.id !== id);
          this.filterQuestions();
        } catch (error) {
          console.error('Error deleting question:', error);
          this.error = 'Failed to delete question. Please try again.';
        }
      }
    },
    goToDashboard() {
      this.$router.push({ name: 'admin' });
    },
    assignQuiz() {
      if (this.selectedQuizId) {
        // Open the assignment modal for this quiz
        this.$router.push({
          name: 'quizzes',
          query: { assignQuiz: this.selectedQuizId }
        });
      }
    }
  }
}
</script>

<style scoped>
.manage-questions {
  padding: 20px;
}
.filter-form {
  max-width: 400px;
}
</style> 
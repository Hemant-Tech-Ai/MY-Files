<template>
  <div class="manage-quizzes">
    <h1>Manage Quizzes</h1>
    
    <!-- Create quiz form -->
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">Add New Quiz</h5>
      </div>
      <div class="card-body">
        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>
        <form @submit.prevent="createQuiz">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="chapterSelect" class="form-label">Chapter</label>
              <select 
                class="form-select" 
                id="chapterSelect" 
                v-model="newQuiz.chapter_id"
                required
              >
                <option value="" disabled>Select a chapter</option>
                <option 
                  v-for="chapter in chapters" 
                  :key="chapter.id" 
                  :value="chapter.id"
                >
                  {{ chapter.name }} ({{ chapter.subject_name }})
                </option>
              </select>
            </div>
            <div class="col-md-6 mb-3">
              <label for="quizDate" class="form-label">Date of Quiz</label>
              <input 
                type="date" 
                class="form-control" 
                id="quizDate" 
                v-model="newQuiz.date_of_quiz" 
                required
              >
            </div>
          </div>
          <div class="mb-3">
            <label for="quizName" class="form-label">Quiz Name</label>
            <input 
              type="text" 
              class="form-control" 
              id="quizName" 
              v-model="newQuiz.name" 
              placeholder="Enter a name for this quiz"
              required
            >
          </div>
          <div class="mb-3">
            <label for="quizDuration" class="form-label">Time Duration (minutes)</label>
            <input 
              type="number" 
              class="form-control" 
              id="quizDuration" 
              v-model="newQuiz.time_duration" 
              placeholder="30"
              min="1"
              required
            >
            <small class="form-text text-muted">Enter the duration in minutes (e.g., 30 for 30 minutes)</small>
          </div>
          <div class="mb-3">
            <label for="quizRemarks" class="form-label">Remarks (Optional)</label>
            <textarea 
              class="form-control" 
              id="quizRemarks" 
              rows="3" 
              v-model="newQuiz.remarks"
            ></textarea>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Add Quiz' }}
          </button>
        </form>
      </div>
    </div>
    
    <!-- Quizzes list -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">All Quizzes</h5>
      </div>
      <div class="card-body">
        <div v-if="loadingQuizzes" class="text-center p-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="quizzes.length === 0" class="alert alert-info">
          No quizzes found. Add a new quiz to get started.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Chapter</th>
                <th>Date</th>
                <th>Duration</th>
                <th>Questions</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quiz in quizzesWithChapters" :key="quiz.id">
                <td>{{ quiz.id }}</td>
                <td>{{ quiz.chapter_name }}</td>
                <td>{{ formatDate(quiz.date_of_quiz) }}</td>
                <td>{{ quiz.time_duration }} min</td>
                <td>{{ quiz.questions_count || 0 }}</td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="editQuiz(quiz)"
                  >
                    Edit
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-success me-2"
                    @click="manageQuestions(quiz.id)"
                  >
                    Add Questions
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="deleteQuiz(quiz.id)"
                  >
                    Delete
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-info me-2"
                    @click="manageAssignments(quiz.id)"
                  >
                    Assign
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Assign Quiz Modal -->
    <div class="modal fade" id="assignQuizModal" tabindex="-1" aria-labelledby="assignQuizModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="assignQuizModalLabel">Assign Quiz</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="assignError" class="alert alert-danger">
              {{ assignError }}
            </div>
            <div v-if="loadingUsers" class="text-center p-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading users...</span>
              </div>
            </div>
            <div v-else-if="users.length === 0" class="alert alert-info">
              No students found.
            </div>
            <div v-else>
              <div class="mb-3">
                <div class="form-check" v-for="user in users" :key="user.id">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    :id="'user-' + user.id" 
                    :value="user.id" 
                    v-model="selectedUsers"
                  >
                  <label class="form-check-label" :for="'user-' + user.id">
                    {{ user.full_name }} ({{ user.username }})
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="confirmAssignQuiz" 
              :disabled="assigningUsers || selectedUsers.length === 0"
            >
              <span v-if="assigningUsers" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Assign Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Edit Quiz Modal -->
    <div class="modal fade" id="editQuizModal" tabindex="-1" aria-labelledby="editQuizModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editQuizModalLabel">Edit Quiz</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateQuiz">
              <div class="mb-3">
                <label for="editChapterSelect" class="form-label">Chapter</label>
                <select 
                  class="form-select" 
                  id="editChapterSelect" 
                  v-model="editingQuiz.chapter_id"
                  required
                >
                  <option value="" disabled>Select a chapter</option>
                  <option 
                    v-for="chapter in chapters" 
                    :key="chapter.id" 
                    :value="chapter.id"
                  >
                    {{ chapter.name }} ({{ chapter.subject_name }})
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label for="editQuizDate" class="form-label">Date of Quiz</label>
                <input 
                  type="date" 
                  class="form-control" 
                  id="editQuizDate" 
                  v-model="editingQuiz.date_of_quiz" 
                  required
                >
              </div>
              <div class="mb-3">
                <label for="editQuizDuration" class="form-label">Time Duration (minutes)</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="editQuizDuration" 
                  v-model="editingQuiz.time_duration" 
                  placeholder="30"
                  min="1"
                  required
                >
                <small class="form-text text-muted">Enter the duration in minutes (e.g., 30 for 30 minutes)</small>
              </div>
              <div class="mb-3">
                <label for="editQuizRemarks" class="form-label">Remarks (Optional)</label>
                <textarea 
                  class="form-control" 
                  id="editQuizRemarks" 
                  rows="3" 
                  v-model="editingQuiz.remarks"
                ></textarea>
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
  </div>
</template>

<script>
import api from '@/services/api';
import { Modal } from 'bootstrap';

export default {
  name: 'ManageQuizzes',
  data() {
    return {
      chapters: [],
      quizzes: [],
      newQuiz: {
        chapter_id: '',
        name: '',
        date_of_quiz: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
        time_duration: 30,
        remarks: ''
      },
      loading: false,
      loadingQuizzes: true,
      selectedQuizId: null,
      users: [],
      loadingUsers: false,
      selectedUsers: [],
      assignments: [],
      loadingAssignments: false,
      assigningUsers: false,
      error: null,
      assignError: null,
      editingQuiz: {
        id: null,
        chapter_id: '',
        date_of_quiz: '',
        time_duration: 30,
        remarks: ''
      },
      editModal: null,
      assignModal: null,
      updating: false
    }
  },
  computed: {
    quizzesWithChapters() {
      return this.quizzes.map(quiz => {
        const chapter = this.chapters.find(c => c.id === quiz.chapter_id);
        return {
          ...quiz,
          chapter_name: chapter ? chapter.name : 'Unknown'
        };
      });
    },
    availableUsers() {
      // Ensure assignments is an array before trying to map
      const assignedUserIds = Array.isArray(this.assignments) 
        ? this.assignments.map(a => a.user_id) 
        : [];
      return this.users.filter(user => !assignedUserIds.includes(user.id));
    }
  },
  async mounted() {
    await this.fetchChapters();
    await this.fetchQuizzes();
    
    // Check for query parameter to pre-select a quiz for assignment
    const assignQuizId = this.$route.query.assignQuiz;
    if (assignQuizId) {
      this.selectedQuizId = assignQuizId;
      await this.fetchUsers();
      await this.fetchAssignments();
      // Show the assignment modal
      const assignModal = new Modal(document.getElementById('assignQuizModal'));
      assignModal.show();
    }
    
    // Initialize the modals
    this.assignModal = new Modal(document.getElementById('assignQuizModal'));
    this.editModal = new Modal(document.getElementById('editQuizModal'));
  },
  methods: {
    async fetchChapters() {
      try {
        const response = await api.getChapters();
        
        this.chapters = response.data;
        console.log('Chapters loaded:', this.chapters);
      } catch (error) {
        console.error('Error fetching chapters:', error);
        this.error = 'Failed to load chapters. Please try again.';
      }
    },
    async fetchQuizzes() {
      this.loadingQuizzes = true;
      this.error = null;
      
      try {
        const response = await api.getQuizzes();
        
        this.quizzes = response.data;
        console.log('Quizzes loaded:', this.quizzes);
      } catch (error) {
        console.error('Error fetching quizzes:', error);
        this.error = 'Failed to load quizzes. Please try again.';
      } finally {
        this.loadingQuizzes = false;
      }
    },
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    async createQuiz() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.createQuiz(this.newQuiz);
        
        console.log('Quiz created:', response.data);
        
        // Add to local state
        this.quizzes.push(response.data);
        
        // Reset form but keep the chapter_id
        const chapter_id = this.newQuiz.chapter_id;
        this.newQuiz = {
          chapter_id: chapter_id, // Keep the same chapter selected
          name: '',
          date_of_quiz: new Date().toISOString().split('T')[0],
          time_duration: 30,
          remarks: ''
        };
        
        // Refresh the quizzes list to ensure we have the latest data
        this.fetchQuizzes();
        
        // Offer to add questions immediately
        if (confirm('Quiz created successfully! Would you like to add questions now?')) {
          this.manageQuestions(response.data.id);
        }
        
      } catch (error) {
        console.error('Error creating quiz:', error);
        this.error = error.response?.data?.message || 'Failed to create quiz. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    editQuiz(quiz) {
      this.editingQuiz = { ...quiz };
      // Convert chapter_id to number if it's a string
      this.editingQuiz.chapter_id = Number(quiz.chapter_id);
      
      // Format date for input field (YYYY-MM-DD)
      if (quiz.date_of_quiz) {
        const date = new Date(quiz.date_of_quiz);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        this.editingQuiz.date_of_quiz = `${year}-${month}-${day}`;
      }
      
      // Show the modal
      this.editModal.show();
    },
    async updateQuiz() {
      this.updating = true;
      this.error = null;
      
      try {
        const response = await api.updateQuiz(this.editingQuiz.id, {
          chapter_id: this.editingQuiz.chapter_id,
          date_of_quiz: this.editingQuiz.date_of_quiz,
          time_duration: this.editingQuiz.time_duration,
          remarks: this.editingQuiz.remarks
        });
        
        // Update the quiz in the list
        const index = this.quizzes.findIndex(q => q.id === this.editingQuiz.id);
        if (index !== -1) {
          this.quizzes[index] = response.data;
        }
        
        // Close the modal
        this.editModal.hide();
      } catch (error) {
        console.error('Error updating quiz:', error);
        this.error = 'Failed to update quiz. Please try again.';
      } finally {
        this.updating = false;
      }
    },
    manageQuestions(quizId) {
      this.$router.push({
        name: 'questions',
        query: { quiz: quizId }
      });
    },
    deleteQuiz(id) {
      if (confirm('Are you sure you want to delete this quiz? All associated questions and scores will be lost.')) {
        // Simulate API call
        setTimeout(() => {
          this.quizzes = this.quizzes.filter(quiz => quiz.id !== id);
        }, 500);
      }
    },
    async openAssignModal(quizId) {
      this.selectedQuizId = quizId;
      this.selectedUsers = [];
      
      // Reset modal state
      this.loadingUsers = true;
      this.loadingAssignments = true;
      
      // Create Modal instance using the imported Modal class
      const modal = new Modal(document.getElementById('assignQuizModal'));
      modal.show();
      
      // Load users and current assignments
      this.fetchUsers();
      this.fetchAssignments();
    },
    
    async fetchUsers() {
      try {
        const response = await api.getUsers();
        this.users = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
      } finally {
        this.loadingUsers = false;
      }
    },
    
    async fetchAssignments() {
      try {
        const response = await api.getAssignments(this.selectedQuizId);
        
        // Make sure assignments is always an array
        this.assignments = response.data.assignments || [];
        console.log('Assignments loaded:', this.assignments);
      } catch (error) {
        console.error('Error fetching assignments:', error);
        this.assignments = []; // Initialize as empty array on error
      } finally {
        this.loadingAssignments = false;
      }
    },
    
    async assignQuizToUsers() {
      if (this.selectedUsers.length === 0) {
        return;
      }
      
      this.assigningUsers = true;
      this.error = null;
      
      try {
        const response = await api.assignQuiz(this.selectedQuizId, { userIds: this.selectedUsers });
        
        console.log('Assignment response:', response.data);
        
        // Refresh assignments
        this.fetchAssignments();
        
        // Clear selection
        this.selectedUsers = [];
        
        // Close the modal
        const modal = Modal.getInstance(document.getElementById('assignQuizModal'));
        if (modal) modal.hide();
        
        // Redirect to admin dashboard
        this.$router.push('/admin');
        
      } catch (error) {
        console.error('Error assigning quiz:', error);
        this.error = error.response?.data?.message || 'Failed to assign quiz. Please try again.';
      } finally {
        this.assigningUsers = false;
      }
    },
    
    async removeAssignment(userId) {
      if (!confirm('Are you sure you want to remove this assignment?')) {
        return;
      }
      
      try {
        await api.removeAssignment(this.selectedQuizId, userId);
        
        // Refresh assignments
        this.fetchAssignments();
        
      } catch (error) {
        console.error('Error removing assignment:', error);
        this.error = error.response?.data?.message || 'Failed to remove assignment. Please try again.';
      }
    },
    
    manageAssignments(quizId) {
      this.openAssignModal(quizId);
    },
    confirmAssignQuiz() {
      // Call assignQuizToUsers if users are selected
      if (this.selectedUsers.length > 0) {
        this.assignQuizToUsers();
      }
    }
  }
}
</script> 
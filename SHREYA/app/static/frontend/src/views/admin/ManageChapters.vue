<template>
  <div class="manage-chapters">
    <h1>Manage Chapters</h1>
    
    <!-- Create chapter form -->
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">Add New Chapter</h5>
      </div>
      <div class="card-body">
        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>
        <form @submit.prevent="createChapter">
          <div class="mb-3">
            <label for="subjectSelect" class="form-label">Subject</label>
            <select 
              class="form-select" 
              id="subjectSelect" 
              v-model="newChapter.subject_id"
              required
            >
              <option value="" disabled>Select a subject</option>
              <option 
                v-for="subject in subjects" 
                :key="subject.id" 
                :value="subject.id"
              >
                {{ subject.name }}
              </option>
            </select>
          </div>
          <div class="mb-3">
            <label for="chapterName" class="form-label">Chapter Name</label>
            <input 
              type="text" 
              class="form-control" 
              id="chapterName" 
              v-model="newChapter.name" 
              required
            >
          </div>
          <div class="mb-3">
            <label for="chapterDescription" class="form-label">Description</label>
            <textarea 
              class="form-control" 
              id="chapterDescription" 
              rows="3" 
              v-model="newChapter.description"
            ></textarea>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Add Chapter' }}
          </button>
        </form>
      </div>
    </div>
    
    <!-- Chapters list -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">All Chapters</h5>
      </div>
      <div class="card-body">
        <div v-if="loadingSubjects" class="text-center p-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading subjects...</span>
          </div>
        </div>
        <div v-if="loadingChapters" class="text-center p-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="chapters.length === 0" class="alert alert-info">
          No chapters found. Add a new chapter to get started.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Subject</th>
                <th>Name</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="chapter in chaptersWithSubjects" :key="chapter.id">
                <td>{{ chapter.id }}</td>
                <td>{{ chapter.subject_name }}</td>
                <td>{{ chapter.name }}</td>
                <td>{{ chapter.description }}</td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="editChapter(chapter)"
                  >
                    Edit
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger me-2"
                    @click="deleteChapter(chapter.id)"
                  >
                    Delete
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-success"
                    @click="addQuiz(chapter)"
                  >
                    Add Quiz
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Edit Chapter Modal -->
    <div class="modal fade" id="editChapterModal" tabindex="-1" aria-labelledby="editChapterModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editChapterModalLabel">Edit Chapter</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateChapter">
              <div class="mb-3">
                <label for="editSubjectSelect" class="form-label">Subject</label>
                <select 
                  class="form-select" 
                  id="editSubjectSelect" 
                  v-model="editingChapter.subject_id"
                  required
                >
                  <option value="" disabled>Select a subject</option>
                  <option 
                    v-for="subject in subjects" 
                    :key="subject.id" 
                    :value="subject.id"
                  >
                    {{ subject.name }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label for="editChapterName" class="form-label">Chapter Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="editChapterName" 
                  v-model="editingChapter.name" 
                  required
                >
              </div>
              <div class="mb-3">
                <label for="editChapterDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="editChapterDescription" 
                  rows="3" 
                  v-model="editingChapter.description"
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
  name: 'ManageChapters',
  data() {
    return {
      subjects: [],
      chapters: [],
      newChapter: {
        subject_id: '',
        name: '',
        description: ''
      },
      error: null,
      loading: false,
      loadingSubjects: true,
      loadingChapters: true,
      editingChapter: {
        id: null,
        subject_id: '',
        name: '',
        description: ''
      },
      updating: false,
      editModal: null
    };
  },
  computed: {
    chaptersWithSubjects() {
      return this.chapters.map(chapter => {
        const subject = this.subjects.find(s => s.id === chapter.subject_id);
        return {
          ...chapter,
          subject_name: subject ? subject.name : 'Unknown'
        };
      });
    }
  },
  async mounted() {
    await this.fetchSubjects();
    await this.fetchChapters();
    // Initialize Bootstrap modal
    this.editModal = new Modal(document.getElementById('editChapterModal'));
  },
  methods: {
    async fetchSubjects() {
      this.loadingSubjects = true;
      try {
        const token = localStorage.getItem('token');
        const response = await api.getSubjects(token);
        this.subjects = response.data;
      } catch (error) {
        console.error('Error fetching subjects:', error);
        this.error = 'Failed to load subjects. Please try refreshing the page.';
      } finally {
        this.loadingSubjects = false;
      }
    },
    async fetchChapters() {
      this.loadingChapters = true;
      try {
        const token = localStorage.getItem('token');
        const response = await api.getChapters(token);
        this.chapters = response.data;
      } catch (error) {
        console.error('Error fetching chapters:', error);
        this.error = 'Failed to load chapters. Please try refreshing the page.';
      } finally {
        this.loadingChapters = false;
      }
    },
    async createChapter() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.createChapter(this.newChapter);
        this.chapters.push(response.data);
        
        // Reset form
        this.newChapter = {
          subject_id: '',
          name: '',
          description: ''
        };
      } catch (error) {
        console.error('Error creating chapter:', error);
        this.error = 'Failed to create chapter. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    editChapter(chapter) {
      this.editingChapter = { ...chapter };
      // Convert subject_id to number if it's a string
      this.editingChapter.subject_id = Number(chapter.subject_id);
      // Show the modal
      this.editModal.show();
    },
    async updateChapter() {
      this.updating = true;
      this.error = null;
      
      try {
        const response = await api.updateChapter(this.editingChapter.id, {
          subject_id: this.editingChapter.subject_id,
          name: this.editingChapter.name,
          description: this.editingChapter.description
        });
        
        // Update the chapter in the list
        const index = this.chapters.findIndex(c => c.id === this.editingChapter.id);
        if (index !== -1) {
          this.chapters[index] = response.data;
        }
        
        // Close the modal
        this.editModal.hide();
      } catch (error) {
        console.error('Error updating chapter:', error);
        this.error = 'Failed to update chapter. Please try again.';
      } finally {
        this.updating = false;
      }
    },
    async deleteChapter(id) {
      if (confirm('Are you sure you want to delete this chapter?')) {
        try {
          await api.deleteChapter(id);
          this.chapters = this.chapters.filter(chapter => chapter.id !== id);
        } catch (error) {
          console.error('Error deleting chapter:', error);
          this.error = 'Failed to delete chapter. Please try again.';
        }
      }
    },
    addQuiz(chapter) {
      // Navigate to the quizzes page with the chapter pre-selected
      this.$router.push({
        name: 'quizzes',
        query: { chapter: chapter.id }
      });
    }
  }
};
</script>

<style scoped>
.manage-chapters {
  padding: 20px;
}
</style> 
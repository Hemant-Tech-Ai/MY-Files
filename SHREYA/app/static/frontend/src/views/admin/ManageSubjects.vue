<template>
  <div class="manage-subjects">
    <h1>Manage Subjects</h1>
    
    <!-- Create subject form -->
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">Add New Subject</h5>
      </div>
      <div class="card-body">
        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>
        <form @submit.prevent="createSubject">
          <div class="mb-3">
            <label for="subjectName" class="form-label">Subject Name</label>
            <input 
              type="text" 
              class="form-control" 
              id="subjectName" 
              v-model="newSubject.name" 
              required
            >
          </div>
          <div class="mb-3">
            <label for="subjectDescription" class="form-label">Description</label>
            <textarea 
              class="form-control" 
              id="subjectDescription" 
              rows="3" 
              v-model="newSubject.description"
            ></textarea>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Add Subject' }}
          </button>
        </form>
      </div>
    </div>
    
    <!-- Subjects list -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">All Subjects</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="subjects.length === 0" class="alert alert-info">
          No subjects found. Add a new subject to get started.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Chapters</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="subject in subjects" :key="subject.id">
                <td>{{ subject.id }}</td>
                <td>{{ subject.name }}</td>
                <td>{{ subject.description }}</td>
                <td>{{ subject.chapters_count || 0 }}</td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="editSubject(subject)"
                  >
                    Edit
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger me-2"
                    @click="deleteSubject(subject.id)"
                  >
                    Delete
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-success"
                    @click="addChapter(subject)"
                  >
                    Add Chapter
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Edit Subject Modal -->
    <div class="modal fade" id="editSubjectModal" tabindex="-1" aria-labelledby="editSubjectModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editSubjectModalLabel">Edit Subject</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateSubject">
              <div class="mb-3">
                <label for="editSubjectName" class="form-label">Subject Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="editSubjectName" 
                  v-model="editingSubject.name" 
                  required
                >
              </div>
              <div class="mb-3">
                <label for="editSubjectDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="editSubjectDescription" 
                  rows="3" 
                  v-model="editingSubject.description"
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
  name: 'ManageSubjects',
  data() {
    return {
      subjects: [],
      newSubject: {
        name: '',
        description: ''
      },
      editingSubject: {
        id: null,
        name: '',
        description: ''
      },
      error: null,
      loading: false,
      updating: false,
      editModal: null
    };
  },
  async mounted() {
    await this.fetchSubjects();
    // Initialize Bootstrap modal
    this.editModal = new Modal(document.getElementById('editSubjectModal'));
  },
  methods: {
    async fetchSubjects() {
      this.loading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await api.getSubjects(token);
        this.subjects = response.data;
      } catch (error) {
        console.error('Error fetching subjects:', error);
        this.error = 'Failed to load subjects. Please try refreshing the page.';
      } finally {
        this.loading = false;
      }
    },
    async createSubject() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.createSubject(this.newSubject);
        this.subjects.push(response.data);
        
        // Reset form
        this.newSubject = {
          name: '',
          description: ''
        };
      } catch (error) {
        console.error('Error creating subject:', error);
        this.error = 'Failed to create subject. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    editSubject(subject) {
      this.editingSubject = { ...subject };
      // Show the modal
      this.editModal.show();
    },
    async updateSubject() {
      this.updating = true;
      this.error = null;
      
      try {
        const response = await api.updateSubject(this.editingSubject.id, {
          name: this.editingSubject.name,
          description: this.editingSubject.description
        });
        
        // Update the subject in the list
        const index = this.subjects.findIndex(s => s.id === this.editingSubject.id);
        if (index !== -1) {
          this.subjects[index] = response.data;
        }
        
        // Close the modal
        this.editModal.hide();
      } catch (error) {
        console.error('Error updating subject:', error);
        this.error = 'Failed to update subject. Please try again.';
      } finally {
        this.updating = false;
      }
    },
    async deleteSubject(id) {
      if (confirm('Are you sure you want to delete this subject?')) {
        try {
          await api.deleteSubject(id);
          this.subjects = this.subjects.filter(subject => subject.id !== id);
        } catch (error) {
          console.error('Error deleting subject:', error);
          this.error = 'Failed to delete subject. Please try again.';
        }
      }
    },
    addChapter(subject) {
      // Navigate to the chapters page with the subject pre-selected
      this.$router.push({
        name: 'chapters',
        query: { subject: subject.id }
      });
    }
  }
};
</script>

<style scoped>
.manage-subjects {
  padding: 20px;
}
</style> 
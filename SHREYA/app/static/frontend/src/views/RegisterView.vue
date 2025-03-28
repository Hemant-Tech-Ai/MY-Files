<template>
  <div class="register-container">
    <div class="card register-card">
      <div class="card-header text-center">
        <h4>Quiz Master - Register</h4>
      </div>
      <div class="card-body">
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        <div v-if="success" class="alert alert-success">
          {{ success }}
        </div>
        
        <form @submit.prevent="handleRegister" v-if="!success">
          <div class="mb-3">
            <label for="username" class="form-label">Email (Username)</label>
            <input 
              type="email" 
              class="form-control" 
              id="username" 
              v-model="userData.username" 
              required
            >
          </div>
          
          <div class="mb-3">
            <label for="fullName" class="form-label">Full Name</label>
            <input 
              type="text" 
              class="form-control" 
              id="fullName" 
              v-model="userData.full_name" 
              required
            >
          </div>
          
          <div class="mb-3">
            <label for="qualification" class="form-label">Qualification</label>
            <input 
              type="text" 
              class="form-control" 
              id="qualification" 
              v-model="userData.qualification"
            >
          </div>
          
          <div class="mb-3">
            <label for="dob" class="form-label">Date of Birth</label>
            <input 
              type="date" 
              class="form-control" 
              id="dob" 
              v-model="userData.dob"
            >
          </div>
          
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="password" 
              v-model="userData.password" 
              required
              minlength="6"
            >
            <small class="form-text text-muted">Password must be at least 6 characters</small>
          </div>
          
          <div class="mb-3">
            <label for="confirmPassword" class="form-label">Confirm Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="confirmPassword" 
              v-model="confirmPassword" 
              required
            >
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary w-100"
            :disabled="loading || !passwordsMatch"
          >
            {{ loading ? 'Registering...' : 'Register' }}
          </button>
          
          <div v-if="confirmPassword && !passwordsMatch" class="alert alert-warning mt-3">
            Passwords do not match
          </div>
        </form>
        
        <div class="mt-3 text-center">
          <p>Already have an account? <router-link to="/login">Login</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RegisterView',
  data() {
    return {
      userData: {
        username: '',
        full_name: '',
        qualification: '',
        dob: '',
        password: ''
      },
      confirmPassword: '',
      loading: false,
      error: null,
      success: null
    }
  },
  computed: {
    passwordsMatch() {
      return this.userData.password === this.confirmPassword;
    }
  },
  methods: {
    async handleRegister() {
      if (!this.passwordsMatch) {
        this.error = 'Passwords do not match';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        // Make an actual API call to the backend
        const response = await axios.post('http://localhost:5000/auth/register', this.userData);
        
        console.log('Registration response:', response.data);
        this.success = 'Registration successful! You can now login.';
        
        // Reset form
        this.userData = {
          username: '',
          full_name: '',
          qualification: '',
          dob: '',
          password: ''
        };
        this.confirmPassword = '';
        
      } catch (error) {
        console.error('Registration error:', error.response?.data || error.message);
        this.error = error.response?.data?.message || 'Registration failed. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem 0;
}

.register-card {
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style> 
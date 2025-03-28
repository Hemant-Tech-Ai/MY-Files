<template>
  <div class="login-container">
    <div class="card login-card">
      <div class="card-header text-center">
        <h4>Quiz Master - Login</h4>
      </div>
      <div class="card-body">
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        <form @submit.prevent="handleLogin">
          <div class="form-group mb-3">
            <label for="username">Username (Email)</label>
            <input 
              type="email" 
              class="form-control" 
              id="username" 
              v-model="credentials.username" 
              required
            >
          </div>
          <div class="form-group mb-3">
            <label for="password">Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="password" 
              v-model="credentials.password" 
              required
            >
          </div>
          <button 
            type="submit" 
            class="btn btn-primary w-100"
            :disabled="loading"
          >
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>
        <div class="mt-3 text-center">
          <p>Don't have an account? <router-link to="/register">Register</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import jwtDecode from 'vue-jwt-decode';

export default {
  name: 'Login',
  data() {
    return {
      credentials: {
        username: '',
        password: ''
      },
      loading: false,
      error: null
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.login(this.credentials);
        const token = response.data.access_token;
        
        // Store token
        localStorage.setItem('token', token);
        
        // Decode token to get user info
        const decoded = jwtDecode.decode(token);
        const isAdmin = decoded.is_admin || false;
        
        // Store user role
        localStorage.setItem('isAdmin', isAdmin);
        
        // Redirect based on role
        if (isAdmin) {
          this.$router.push('/admin');
        } else {
          this.$router.push('/user/dashboard');
        }
      } catch (error) {
        console.error('Login error:', error);
        this.error = error.response?.data?.message || 'Login failed. Please check your credentials.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style> 
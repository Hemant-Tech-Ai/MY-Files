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
// We'll use fetch directly for now instead of the api service
export default {
  name: 'LoginView',
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
        const response = await fetch('http://localhost:5000/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.credentials)
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Login failed');
        }
        
        const data = await response.json();
        console.log('Login response:', {
          token: data.token ? `${data.token.substring(0, 15)}...` : null,
          isAdmin: data.isAdmin,
          userId: data.userId
        });
        
        // Get values from response with correct property names
        const token = data.token;
        const isAdmin = data.isAdmin;
        const userId = data.userId;
        
        if (!token) {
          throw new Error('No token received from server');
        }
        
        // Store in localStorage and Vuex with timestamps
        const now = new Date().getTime();
        
        // Clean storage before setting new values
        localStorage.removeItem('token');
        localStorage.removeItem('userId');
        localStorage.removeItem('isAdmin');
        localStorage.removeItem('loginTime');
        
        // Set new values
        localStorage.setItem('token', token);
        localStorage.setItem('userId', userId);
        localStorage.setItem('isAdmin', isAdmin ? 'true' : 'false');
        localStorage.setItem('loginTime', now);
        
        console.log('Stored auth data:', {
          tokenLength: token.length,
          tokenPrefix: token.substring(0, 10) + '...',
          isAdmin,
          userId,
          loginTime: new Date(now).toISOString()
        });
        
        // Dispatch to Vuex
        this.$store.dispatch('login', { token, isAdmin, userId });
        
        // Redirect based on role
        if (isAdmin) {
          this.$router.push('/admin');
        } else {
          this.$router.push('/user');
        }
      } catch (error) {
        console.error('Login error:', error);
        this.error = error.message || 'Login failed. Please check your credentials.';
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
  min-height: 80vh;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style> 
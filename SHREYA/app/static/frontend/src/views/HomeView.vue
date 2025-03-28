<template>
  <div class="home">
    <h1>Welcome to Quiz Master</h1>
    <div class="actions">
      <router-link to="/login" class="btn btn-primary">Login</router-link>
      <router-link to="/register" class="btn btn-outline-primary ms-2">Register</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home {
  text-align: center;
  margin-top: 100px;
}
.actions {
  margin-top: 30px;
}
</style> 
import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    isAdmin: false,
    token: localStorage.getItem('token') || null
  },
  getters: {
    isLoggedIn: state => !!state.token,
    isAdmin: state => state.isAdmin
  },
  mutations: {
    setToken(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    setUser(state, user) {
      state.user = user
    },
    setIsAdmin(state, isAdmin) {
      state.isAdmin = isAdmin
      localStorage.setItem('isAdmin', isAdmin ? 'true' : 'false')
    },
    logout(state) {
      state.token = null
      state.user = null
      state.isAdmin = false
      localStorage.removeItem('token')
      localStorage.removeItem('isAdmin')
    }
  },
  actions: {
    login({ commit }, authData) {
      const token = authData.token;
      const isAdmin = authData.isAdmin;
      const userId = authData.userId;
      
      console.log('Login success:', { token: !!token, isAdmin, userId });
      
      // Store in state
      commit('setToken', token);
      commit('setUser', userId);
      commit('setIsAdmin', isAdmin);
      
      // Store in localStorage for persistence
      localStorage.setItem('token', token);
      localStorage.setItem('userId', userId);
      localStorage.setItem('isAdmin', isAdmin ? 'true' : 'false');
    },
    logout({ commit }) {
      commit('logout')
    }
  },
  modules: {
  }
}) 
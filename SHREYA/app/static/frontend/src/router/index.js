import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  // Admin routes with lazy loading
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects',
    name: 'subjects',
    component: () => import('../views/admin/ManageSubjects.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/chapters',
    name: 'chapters',
    component: () => import('../views/admin/ManageChapters.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes',
    name: 'quizzes',
    component: () => import('../views/admin/ManageQuizzes.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/questions',
    name: 'questions',
    component: () => import('../views/admin/ManageQuestions.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // New Reports Route
  {
    path: '/admin/reports',
    name: 'reports',
    component: () => import('../views/admin/ReportsManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // User routes
  {
    path: '/user',
    name: 'user',
    component: () => import('../views/user/UserDashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/quiz/:id',
    name: 'take-quiz',
    component: () => import('../views/user/TakeQuiz.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/scores',
    name: 'scores',
    component: () => import('../views/user/Scores.vue'),
    meta: { requiresAuth: true }
  },
  // Registration route
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue')
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// Navigation guards
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const isAdmin = localStorage.getItem('isAdmin');
  
  // Debug information (can be removed in production)
  console.log('Route navigation:', to.path);
  console.log('Auth state:', { token: !!token, isAdmin });

  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else if (to.meta.requiresAdmin && isAdmin !== 'true') {
    next('/user');
  } else {
    next();
  }
});

export default router; 
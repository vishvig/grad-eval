import { createRouter, createWebHistory } from 'vue-router'
import AuthPage from '@/components/AuthPage.vue'
import IntroductionPage from '@/components/IntroductionPage.vue'
import MCQSection from '@/components/MCQSection.vue'
import CodingTask from '@/components/CodingTask.vue'
import CongratulationsPage from '@/components/CongratulationsPage.vue'

const routes = [
  {
    path: '/',
    name: 'Auth',
    component: AuthPage,
    meta: { 
      title: 'Login - Grad Evaluator'
    }
  },
  {
    path: '/introduction',
    name: 'Introduction',
    component: IntroductionPage,
    meta: { 
      requiresAuth: true,
      title: 'Introduction - Grad Evaluator'
    }
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: MCQSection,
    meta: { 
      requiresAuth: true,
      title: 'MCQ Assessment - Grad Evaluator'
    }
  },
  {
    path: '/congratulations',
    name: 'Congratulations',
    component: CongratulationsPage,
    meta: { 
      requiresAuth: true,
      title: 'Congratulations - Grad Evaluator'
    }
  },
  {
    path: '/coding',
    name: 'Coding',
    component: CodingTask,
    meta: { 
      requiresAuth: true,
      title: 'Coding Challenge - Grad Evaluator'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  // Update document title
  document.title = to.meta.title || 'Grad Evaluator'
  
  // Auth check
  const token = localStorage.getItem('auth_token')
  if (to.meta.requiresAuth && !token) {
    next('/')
  } else if (to.path === '/' && token) {
    next('/introduction')
  } else {
    next()
  }
})

export default router 
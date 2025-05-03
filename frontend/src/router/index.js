import { createRouter, createWebHistory } from 'vue-router'
import AuthPage from '@/components/AuthPage.vue'
import IntroductionPage from '@/components/IntroductionPage.vue'
import MCQSection from '@/components/MCQSection.vue'
import CodingTask from '@/components/CodingTask.vue'
import CongratulationsPage from '@/components/CongratulationsPage.vue'
import TimeExpiredPage from '@/components/TimeExpiredPage.vue'

const routes = [
  {
    path: '/',
    name: 'Auth',
    component: AuthPage,
    meta: { 
      title: 'Login - ThinkGrade'
    }
  },
  {
    path: '/introduction',
    name: 'Introduction',
    component: IntroductionPage,
    meta: { 
      requiresAuth: true,
      title: 'Introduction - ThinkGrade'
    }
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: MCQSection,
    meta: { 
      requiresAuth: true,
      title: 'MCQ Assessment - ThinkGrade'
    }
  },
  {
    path: '/congratulations',
    name: 'Congratulations',
    component: CongratulationsPage,
    meta: { 
      requiresAuth: true,
      title: 'Congratulations - ThinkGrade'
    }
  },
  {
    path: '/coding',
    name: 'Coding',
    component: CodingTask,
    meta: { 
      requiresAuth: true,
      title: 'Coding Challenge - ThinkGrade'
    }
  },
  {
    path: '/time-expired',
    name: 'TimeExpired',
    component: TimeExpiredPage,
    meta: { 
      requiresAuth: true,
      title: 'Time Expired - ThinkGrade'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('user_id')
  const assessmentStarted = localStorage.getItem('assessment_status') === 'true'
  
  // If trying to access auth page while authenticated
  if (to.name === 'auth' && isAuthenticated) {
    if (assessmentStarted) {
      next('/coding') // Go directly to coding if assessment was started
    } else {
      next('/introduction') // Show introduction if assessment not started
    }
    return
  }
  
  // If not authenticated and trying to access protected route
  if (!isAuthenticated && to.meta.requiresAuth) {
    next('/')
    return
  }
  
  // If authenticated and trying to access introduction
  if (to.name === 'introduction' && assessmentStarted) {
    next('/coding') // Skip introduction if assessment was started
    return
  }
  
  // Update document title
  document.title = to.meta.title || 'ThinkGrade'
  
  next()
})

export default router 
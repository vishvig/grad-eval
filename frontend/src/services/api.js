import axios from 'axios'
import { ROUTES } from '@/constants/api'

const handleError = (error) => {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.message || 'Server error occurred'
    const enhancedError = new Error(message)
    enhancedError.response = error.response
    throw enhancedError
  } else if (error.request) {
    // Request made but no response
    throw new Error('No response from server. Please check your connection.')
  } else {
    // Request setup error
    throw new Error('Failed to make request. Please try again.')
  }
}

export const mcqService = {
  startAssessment: async () => {
    try {
      const userId = localStorage.getItem('user_id')
      const response = await axios.post(ROUTES.MCQ.START_ASSESSMENT, {
        user_id: userId
      })
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  getNextQuestion: async () => {
    try {
      const response = await axios.get(ROUTES.MCQ.NEXT_QUESTION)
      return response.data.body
    } catch (error) {
      handleError(error)
    }
  },

  submitAnswer: async (questionId, selectedAnswers) => {
    try {
      return await axios.post(ROUTES.MCQ.SUBMIT_ANSWER, {
        questionId,
        selectedAnswers
      })
    } catch (error) {
      handleError(error)
    }
  }
}

export const authService = {
  getCaptcha: async () => {
    try {
      const response = await axios.get(ROUTES.AUTH.GET_CAPTCHA)
      const sessionId = response.data.body.session_id
      
      // Store session ID in localStorage
      localStorage.setItem('captcha_session_id', sessionId)
      
      return {
        image: response.data.body.image,
        sessionId: sessionId
      }
    } catch (error) {
      handleError(error)
    }
  },

  login: async (credentials) => {
    try {
      const sessionId = localStorage.getItem('captcha_session_id')
      
      const response = await axios.post(ROUTES.AUTH.VERIFY, {
        full_name: credentials.fullName,
        token: credentials.token,
        captcha_session_id: sessionId,
        captcha_text: credentials.captchaResponse
      })
      
      // Store user data in localStorage
      localStorage.setItem('auth_token', credentials.token)
      localStorage.setItem('username', credentials.fullName)
      localStorage.setItem('user_id', response.data.body.user_id) // Access user_id from body
      
      // Add token to axios defaults
      axios.defaults.headers.common['Authorization'] = `Bearer ${credentials.token}`
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  clearUserData: () => {
    localStorage.removeItem('user_id')
    localStorage.removeItem('auth_token')
    localStorage.removeItem('username')
    localStorage.removeItem('captcha_session_id')
    delete axios.defaults.headers.common['Authorization']
  }
} 
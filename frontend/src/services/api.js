import axios from 'axios'
import { ROUTES } from '@/constants/api'

let router;

// Initialize router - this should be called in the main app setup
export const initializeApiService = (routerInstance) => {
  router = routerInstance;
}

const TIME_EXPIRED_STATUS = 440 // Special status code for time expired

const handleError = (error) => {
  if (error.response) {
    // Check for time expired status
    if (error.response.status === TIME_EXPIRED_STATUS) {
      // If router is available, navigate to time-expired page
      if (router) {
        router.push('/time-expired')
        return // Prevent further error handling
      }
    }
    
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

// Helper to get current epoch timestamp
const getCurrentEpoch = () => {
  return Math.floor(Date.now() / 1000)
}

// Helper to get assessment start time from localStorage
const getStartEpoch = () => {
  const startTime = localStorage.getItem('assessment_start_time')
  return startTime ? parseInt(startTime) : null
}

export const mcqService = {
  startAssessment: async () => {
    try {
      const userId = localStorage.getItem('user_id')
      const currentEpoch = getCurrentEpoch()
      
      // Store start time in localStorage
      localStorage.setItem('assessment_start_time', currentEpoch.toString())
      
      const response = await axios.post(ROUTES.MCQ.START_ASSESSMENT, {
        user_id: userId,
        current_epoch: currentEpoch
      })
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  getNextQuestion: async () => {
    try {
      const userId = localStorage.getItem('user_id')
      const startEpoch = getStartEpoch()
      const currentEpoch = getCurrentEpoch()
      
      const response = await axios.post(ROUTES.MCQ.NEXT_QUESTION, {
        user_id: userId,
        current_epoch: currentEpoch,
        start_epoch: startEpoch
      })
      return response.data.body
    } catch (error) {
      handleError(error)
    }
  },

  submitAnswer: async (question_id, selected_answers) => {
    try {
      const user_id = localStorage.getItem('user_id')
      const startEpoch = getStartEpoch()
      const currentEpoch = getCurrentEpoch()
      
      return await axios.post(ROUTES.MCQ.SUBMIT_ANSWER, {
        question_id,
        selected_answers,
        user_id,
        current_epoch: currentEpoch,
        start_epoch: startEpoch
      })
    } catch (error) {
      handleError(error)
    }
  }
}

// Helper function to prepare common request data
const prepareNextTaskData = () => {
  const userId = localStorage.getItem('user_id')
  const startEpoch = localStorage.getItem('assessment_start_time')
  const currentEpoch = getCurrentEpoch()

  return {
    user_id: userId,
    current_epoch: parseInt(currentEpoch),
    start_epoch: parseInt(startEpoch)
  }
}

export const codingService = {
  submitTask: async (taskData) => {
    try {
      const userId = localStorage.getItem('user_id')
      const startEpoch = getStartEpoch()
      const currentEpoch = getCurrentEpoch()
      
      const formData = new FormData()
      formData.append('notebook', taskData.notebook)
      formData.append('output', taskData.output)
      formData.append('task_id', taskData.taskId)
      formData.append('user_id', userId)
      formData.append('current_epoch', currentEpoch)
      formData.append('start_epoch', startEpoch)
      
      const response = await axios.post(ROUTES.CODING.SUBMIT_TASK, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      handleError(error)
    }
  },
  
  downloadTaskFiles: async (taskData) => {
    try {
      const userId = localStorage.getItem('user_id')
      const startEpoch = getStartEpoch()
      const currentEpoch = getCurrentEpoch()
      
      const response = await axios.post(ROUTES.CODING.DOWNLOAD_TASK_FILES, {
        user_id: userId,
        question_id: taskData.question_id,
        current_epoch: currentEpoch,
        start_epoch: startEpoch
      }, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      handleError(error)
      throw error
    }
  },

  startCodingAssessment: async () => {
    try {
      const startTime = Date.now()
      localStorage.setItem('assessment_start_time', startTime.toString())
      
      // First call the start assessment API
      await axios.post(ROUTES.CODING.START_ASSESSMENT, {
        ...prepareNextTaskData(),
        start_epoch: startTime
      })

      // Then call next-task API to get the first task
      const formData = new FormData()
      const jsonData = {
        ...prepareNextTaskData(),
        start_epoch: startTime,
        question_id: null
      }
      
      const nextTaskResponse = await axios.post(
        ROUTES.CODING.NEXT_TASK,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          params: {
            request_data: JSON.stringify(jsonData)
          }
        }
      )
      
      return nextTaskResponse.data
    } catch (error) {
      handleError(error)
      throw error
    }
  },

  nextTask: async (taskData) => {
    try {
      const formData = new FormData()
      
      // Add files if they exist
      if (taskData.notebook) {
        formData.append('notebook_file', taskData.notebook)
      }
      if (taskData.output) {
        formData.append('solution_file', taskData.output)
      }
      
      // Add the JSON data
      const jsonData = {
        ...prepareNextTaskData(),
        question_id: taskData.question_id
      }
      
      const response = await axios.post(
        ROUTES.CODING.NEXT_TASK,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          params: {
            request_data: JSON.stringify(jsonData)
          }
        }
      )
      return response.data
    } catch (error) {
      handleError(error)
      throw error
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
      
      if (handleAuthResponse(response)) {
        // Store additional user data in localStorage
        localStorage.setItem('auth_token', credentials.token)
        localStorage.setItem('username', credentials.fullName)
        
        // Add token to axios defaults
        axios.defaults.headers.common['Authorization'] = `Bearer ${credentials.token}`

        // If assessment was already started, get the next task
        if (response.data.body.assessment_status) {
          // Call next task API to resume the assessment
          const formData = new FormData()
          const jsonData = {
            ...prepareNextTaskData(),
            question_id: null
          }
          
          const nextTaskResponse = await axios.post(
            ROUTES.CODING.NEXT_TASK,
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              },
              params: {
                request_data: JSON.stringify(jsonData)
              }
            }
          )
          
          // Return with a flag indicating assessment was already started and include next task data
          return {
            ...response.data,
            resumeAssessment: true,
            nextTaskData: nextTaskResponse.data
          }
        }
      }
      
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
    localStorage.removeItem('assessment_start_time')
    localStorage.removeItem('assessment_timer_value')
    localStorage.removeItem('assessment_status')
    delete axios.defaults.headers.common['Authorization']
  }
}

// Move handleAuthResponse before it's used
const handleAuthResponse = (response) => {
  if (response.data.body.authenticated) {
    localStorage.setItem('user_id', response.data.body.user_id)
    localStorage.setItem('assessment_status', response.data.body.assessment_status)
    if (response.data.body.assessment_start_time) {
      localStorage.setItem('assessment_start_time', response.data.body.assessment_start_time.toString())
    }
    return true
  }
  return false
} 
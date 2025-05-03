// Environment variable access with fallbacks and validation
const getEnvVar = (key, defaultValue) => {
  const value = import.meta.env?.[key]
  if (value === undefined) {
    console.warn(`Environment variable ${key} not found, using default:`, defaultValue)
    return defaultValue
  }
  return value
}

// Get base URL with fallback
export const BASE_URL = getEnvVar('VITE_API_BASE_URL', 'http://localhost:3000')

// API Routes
export const ROUTES = {
  MCQ: {
    NEXT_QUESTION: `${BASE_URL}/api/mcq/next`,
    SUBMIT_ANSWER: `${BASE_URL}/api/mcq/submit`,
    START_ASSESSMENT: `${BASE_URL}/mcq/start-assessment`
  },
  CODING: {
    SUBMIT_TASK: `${BASE_URL}/coding/submit-task`,
    DOWNLOAD_TASK: `${BASE_URL}/coding-task/download-task-file`,
    DOWNLOAD_TASK_FILES: `${BASE_URL}/coding/download`,
    NEXT_TASK: `${BASE_URL}/coding-task/next-task`,
    START_ASSESSMENT: `${BASE_URL}/coding-task/start-assessment`,
    GET_NEXT_TASK: `${BASE_URL}/coding/next`
  },
  AUTH: {
    VERIFY: `${BASE_URL}/auth/verify`,
    GET_CAPTCHA: `${BASE_URL}/auth/captcha`,
    LOGIN: `${BASE_URL}/api/auth/login`,
    CAPTCHA: `${BASE_URL}/api/auth/captcha`
  },
  CHAT: {
    CHAT: `${BASE_URL}/chat/chat`
  }
}

// Status Codes
export const STATUS_CODES = {
  TIME_EXPIRED: 440
}

// Validate API configuration
const validateConfig = () => {
  if (!BASE_URL.startsWith('http')) {
    console.error('Invalid API configuration:', BASE_URL)
    throw new Error('Invalid API configuration')
  }
}

// Run validation
validateConfig() 
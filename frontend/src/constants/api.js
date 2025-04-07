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
    NEXT_QUESTION: `${BASE_URL}/mcq/next_question`,
    SUBMIT_ANSWER: `${BASE_URL}/api/submit-answer`,
    START_ASSESSMENT: `${BASE_URL}/mcq/start-assessment`
  },
  AUTH: {
    VERIFY: `${BASE_URL}/auth/verify`,
    GET_CAPTCHA: `${BASE_URL}/auth/captcha`
  }
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
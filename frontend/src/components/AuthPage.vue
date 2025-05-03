<template>
  <div class="auth-container">
    <div class="theme-toggle-wrapper">
      <ThemeToggle />
    </div>
    <div class="auth-card">
      <div class="auth-header">
        <h1>ThinkGrade</h1>
        <p>Please enter your credentials to continue</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="input-group">
          <label for="fullName">Full Name</label>
          <input 
            type="text"
            id="fullName"
            v-model="fullName"
            placeholder="Enter your full name"
            :class="{ 'error': errors.fullName }"
          />
          <span v-if="errors.fullName" class="error-text">{{ errors.fullName }}</span>
        </div>

        <div class="input-group">
          <label for="token">Access Token</label>
          <input 
            type="password"
            id="token"
            v-model="token"
            placeholder="Enter your access token"
            :class="{ 'error': errors.token }"
          />
          <span v-if="errors.token" class="error-text">{{ errors.token }}</span>
        </div>

        <div v-if="showCaptcha" class="captcha-section">
          <div class="captcha-image">
            <img :src="captchaImage" alt="Captcha" />
            <button 
              type="button" 
              class="refresh-captcha" 
              @click="refreshCaptcha"
              :disabled="isLoading"
            >
              🔄
            </button>
          </div>
          <div class="input-group">
            <label for="captcha">Enter Captcha</label>
            <input 
              type="text"
              id="captcha"
              v-model="captchaResponse"
              placeholder="Enter the text shown above"
              :class="{ 'error': errors.captcha }"
            />
            <span v-if="errors.captcha" class="error-text">{{ errors.captcha }}</span>
          </div>
        </div>
        
        <button 
          type="submit" 
          class="login-button"
          :disabled="isLoading || !isFormValid"
        >
          <img src="@/assets/gitlab.svg" alt="GitLab" class="gitlab-icon" />
          <span>{{ isLoading ? 'Authenticating...' : 'Login with GitLab' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'
import { useToast } from '@/composables/useToast'
import ThemeToggle from './common/ThemeToggle.vue'

const router = useRouter()
const { addToast } = useToast()

const fullName = ref('')
const token = ref('')
const captchaResponse = ref('')
const captchaImage = ref('')
const captchaId = ref('')
const showCaptcha = ref(false)
const isLoading = ref(false)
const errors = ref({
  fullName: '',
  token: '',
  captcha: ''
})

const isFormValid = computed(() => {
  if (!showCaptcha.value) {
    return fullName.value.trim() && token.value.trim()
  }
  return fullName.value.trim() && token.value.trim() && captchaResponse.value.trim()
})

const loadCaptcha = async () => {
  try {
    const response = await authService.getCaptcha()
    captchaImage.value = response.image
    captchaId.value = response.id
    showCaptcha.value = true
  } catch (err) {
    addToast('Failed to load captcha', 'error')
  }
}

const refreshCaptcha = () => {
  loadCaptcha()
  captchaResponse.value = ''
}

const validateForm = () => {
  errors.value = {}
  
  if (!fullName.value.trim()) {
    errors.value.fullName = 'Full name is required'
  } else if (fullName.value.trim().length < 3) {
    errors.value.fullName = 'Full name must be at least 3 characters'
  }
  
  if (!token.value.trim()) {
    errors.value.token = 'Access token is required'
  }
  
  if (showCaptcha.value && !captchaResponse.value.trim()) {
    errors.value.captcha = 'Please enter the captcha'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleLogin = async () => {
  if (!validateForm()) return
  
  isLoading.value = true
  errors.value = {}
  
  try {
    const response = await authService.login({
      fullName: fullName.value,
      token: token.value,
      captchaId: captchaId.value,
      captchaResponse: captchaResponse.value
    })

    // Check if authentication was successful
    if (response.status === 'success' && response.body.authenticated) {
      addToast('Authentication successful', 'success')

      // Store user ID in localStorage
      localStorage.setItem('user_id', response.body.user_id)

      // Check assessment status and redirect accordingly
      if (response.body.assessment_status) {
        // Store assessment start time if it exists
        if (response.body.assessment_start_time) {
          localStorage.setItem('assessment_start_time', response.body.assessment_start_time.toString())
        }
        router.push('/coding')
      } else {
        router.push('/introduction')
      }
    } else {
      throw new Error('Authentication failed')
    }
  } catch (err) {
    const errorMessage = err.response?.data?.message || 'Invalid credentials'
    if (err.response?.status === 401) {
      errors.value.token = errorMessage
    } else {
      errors.value.captcha = errorMessage
      refreshCaptcha()
    }
    addToast(errorMessage, 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadCaptcha()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';

.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: var(--color-background);
  position: relative;
}

.theme-toggle-wrapper {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
}

.auth-card {
  background: var(--color-surface);
  border-radius: $border-radius-lg;
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px var(--color-shadow);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;

  h1 {
    color: var(--color-text);
    font-size: 2rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
  }

  p {
    color: var(--color-text-secondary);
    font-size: 1rem;
  }
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  label {
    color: var(--color-text);
    font-size: 0.9rem;
    font-weight: 500;
  }

  input {
    padding: 0.75rem 1rem;
    border: 2px solid var(--color-border);
    border-radius: $border-radius-md;
    background: var(--color-surface);
    color: var(--color-text);
    font-size: 1rem;
    transition: $transition-default;

    &:focus {
      outline: none;
      border-color: var(--color-primary);
    }

    &.error {
      border-color: #f44336;
    }

    &::placeholder {
      color: var(--color-text-secondary);
      opacity: 0.7;
    }
  }
}

.error-text {
  color: #f44336;
  font-size: 0.8rem;
}

.login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  background: #6b4fbb;
  color: white;
  border: none;
  border-radius: $border-radius-md;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: $transition-default;

  &:hover:not(:disabled) {
    background: #5c3ea8;
    transform: translateY(-2px);
    box-shadow: 0 2px 4px var(--color-shadow);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .gitlab-icon {
    width: 20px;
    height: 20px;
  }
}

.captcha-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.captcha-image {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  padding: 1rem;
  border: 2px solid var(--color-border);
  border-radius: $border-radius-md;

  img {
    max-width: 100%;
    height: auto;
  }

  .refresh-captcha {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.5rem;
    opacity: 0.7;
    transition: $transition-default;

    &:hover:not(:disabled) {
      opacity: 1;
    }

    &:disabled {
      cursor: not-allowed;
    }
  }
}

@media (max-width: $breakpoint-mobile) {
  .theme-toggle-wrapper {
    top: 0.5rem;
    right: 0.5rem;
  }

  .auth-card {
    padding: 1.5rem;
  }

  .auth-header h1 {
    font-size: 1.3rem;
  }
}
</style> 
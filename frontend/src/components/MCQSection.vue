<template>
  <div class="main-content">
    <div class="quiz-container" :class="{ 'chat-minimized': isChatMinimized }">
      <div class="quiz-layout">
        <div class="quiz-main" :class="{ 'chat-minimized': isChatMinimized }">
          <ErrorPage
            v-if="error"
            :message="error"
            @retry="retryFetch"
          />
          <div v-else-if="!quizCompleted" class="quiz-content">
            <MCQQuestion
              v-if="currentQuestion"
              :question="currentQuestion"
              :selected-answers="selectedAnswers"
              @answer-updated="updateSelectedAnswers"
            />
            <div class="button-container">
              <button 
                class="next-button" 
                @click="handleNext"
                :disabled="!hasSelection"
                :title="!hasSelection ? 'Please select an option to continue' : ''"
              >
                {{ isLastQuestion ? 'Submit' : 'Next' }} 
                <span class="arrow">→</span>
              </button>
            </div>
          </div>
        
          <div v-else class="completion-message">
            <h2>✅ Quiz Completed</h2>
            <p>Thank you for participating.</p>
          </div>
        </div>
        
        <ChatInterface @minimize-changed="handleChatMinimize" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import MCQQuestion from './MCQQuestion.vue'
import ErrorPage from './ErrorPage.vue'
import { mcqService } from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useRouter } from 'vue-router'
import ChatInterface from '@/components/ChatInterface.vue'

const { addToast } = useToast()
const router = useRouter()

const questions = ref([])
const currentIndex = ref(0)
const selectedAnswers = ref([])
const quizCompleted = ref(false)
const error = ref(null)
const timerPaused = ref(false)
const isChatMinimized = ref(false)

const DEFAULT_TIMER = 300 // 5 minutes in seconds
const TIMER_STORAGE_KEY = 'quiz_timer_value'

// Initialize timer value from env or default
const timerValue = (() => {
  try {
    const envValue = import.meta.env?.VITE_QUIZ_TIMER_SECONDS
    const parsedValue = envValue ? parseInt(envValue) : DEFAULT_TIMER
    return Math.max(parsedValue, 0) // Ensure non-negative value
  } catch (error) {
    console.warn('Failed to read environment variable, using default timer:', DEFAULT_TIMER)
    return DEFAULT_TIMER
  }
})()

// Initialize timeLeft with stored value or default
const timeLeft = ref(() => {
  const storedValue = localStorage.getItem(TIMER_STORAGE_KEY)
  if (storedValue) {
    const parsedValue = parseInt(storedValue)
    return parsedValue > 0 ? parsedValue : timerValue
  }
  return timerValue
})

// Update timer storage on changes
watch(timeLeft, (newValue) => {
  if (newValue > 0) {
    localStorage.setItem(TIMER_STORAGE_KEY, newValue.toString())
  } else {
    localStorage.removeItem(TIMER_STORAGE_KEY)
  }
})

const currentQuestion = computed(() => questions.value[currentIndex.value])

// Watch error state to pause/resume timer
watch(error, (newError) => {
  timerPaused.value = !!newError
  emit('timer-state-change', timerPaused.value)
})

const updateFormattedTime = () => {
  const value = Math.max(timeLeft.value, 0) // Ensure non-negative value
  const minutes = Math.floor(value / 60)
  const seconds = value % 60
  emit('time-update', `${minutes}:${seconds.toString().padStart(2, '0')}`)
}

const emit = defineEmits(['time-update', 'quiz-completed', 'timer-state-change'])

let timer = null

const startTimer = () => {
  if (timer) clearInterval(timer)
  
  // Ensure initial value is positive
  if (timeLeft.value <= 0) {
    timeLeft.value = timerValue
  }
  
  updateFormattedTime() // Initial update
  
  timer = setInterval(() => {
    if (!timerPaused.value && timeLeft.value > 0) {
      timeLeft.value = timeLeft.value - 1
      updateFormattedTime()
      
      if (timeLeft.value <= 0) {
        clearInterval(timer)
        completeQuiz()
      }
    }
  }, 1000)
}

// Start timer when component mounts
onMounted(async () => {
  await fetchQuestions()
  startTimer()
})

const retryFetch = async () => {
  error.value = null
  await fetchQuestions()
}

const fetchQuestions = async () => {
  const userId = localStorage.getItem('user_id') // Retrieve user ID from localStorage
  try {
    const response = await mcqService.getNextQuestion({
      userId: userId // Send user ID in the request body
    })
    questions.value = [response]
    error.value = null // Clear any existing error
    addToast('Question loaded successfully', 'success')
  } catch (err) {
    console.error('Error fetching questions:', err)
    const errorMessage = err.response?.data?.message || 'Failed to load question'
    error.value = errorMessage
    addToast(errorMessage, 'error')
  }
}

const updateSelectedAnswers = (answers) => {
  selectedAnswers.value = answers
}

const completeQuiz = () => {
  clearInterval(timer)
  quizCompleted.value = true
  localStorage.removeItem(TIMER_STORAGE_KEY) // Clear timer on quiz completion
  emit('quiz-completed')
}

const isLastQuestion = computed(() => currentIndex.value === 4) // 5th question

const handleNext = async () => {
  try {
    await mcqService.submitAnswer(currentQuestion.value.id, selectedAnswers.value)
    const response = await mcqService.getNextQuestion()
    console.log(response)
    console.log(response.quizFinished)
    console.log(response.value)
    if (response.quizFinished) {
      addToast('Quiz completed successfully', 'success')
      router.push('/congratulations')
    } else {
      addToast('Response recorded. Loading next question.', 'success')
      setTimeout(() => {
        questions.value = [response]
        selectedAnswers.value = []
      }, 300)
    }
    // if (isLastQuestion.value) {
    //   // Handle final submission
    //   addToast('MCQ section completed successfully', 'success')
    //   router.push('/congratulations') // Redirect to congratulations page instead of coding
    // } else {
    //   // Get next question
    //   const response = await mcqService.getNextQuestion()
    //   if (response) {
    //     addToast('Response recorded. Loading next question.', 'success')
        
    //     setTimeout(() => {
    //       questions.value = [response]
    //       selectedAnswers.value = []
    //     }, 300)
    //   }
    // }
  } catch (err) {
    console.error('Error:', err)
    const errorMessage = err.response?.data?.message || 'Failed to process request'
    error.value = errorMessage
    addToast(errorMessage, 'error')
  }
}

// Add computed property to check if an option is selected
const hasSelection = computed(() => selectedAnswers.value.length > 0)

// Clear timer when component unmounts
onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})

const handleChatMinimize = (minimized) => {
  isChatMinimized.value = minimized
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';

.main-content {
  padding-top: 84px;
  height: calc(100vh - 84px);
  overflow: hidden;
  position: relative;
}

.quiz-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  height: 100%;
  padding-right: 20px;
  transition: padding-right 0.3s ease;
  
  &.chat-minimized {
    padding-right: 20px;
  }
}

.quiz-layout {
  display: flex;
  gap: 0;
  height: 100%;
  position: relative;
}

.quiz-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  margin-right: 20px;
  transition: margin-right 0.3s ease;
  
  &.chat-minimized {
    margin-right: 20px;
  }
}

.quiz-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
  padding: 0 1rem;
}

.next-button {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 1rem 3rem;
  border-radius: $border-radius-md;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: $transition-default;
  width: 100%;
  max-width: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  .arrow {
    font-size: 1.2em;
    transition: transform 0.2s ease;
  }

  &:disabled {
    background: var(--color-text-secondary);
    cursor: not-allowed;
    transform: none;
    opacity: 0.7;

    &:hover {
      background: var(--color-text-secondary);
      transform: none;
      box-shadow: none;

      .arrow {
        transform: none;
      }
    }
  }

  &:hover:not(:disabled) {
    background: var(--color-primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 2px 4px var(--color-shadow);

    .arrow {
      transform: translateX(4px);
    }
  }
}

.completion-message {
  text-align: center;
  padding: 2rem;
  background: var(--color-surface);
  border-radius: $border-radius-lg;
  margin-top: 2rem;

  h2 {
    color: var(--color-primary);
    margin: 0;
    font-size: clamp(1.5rem, 4vw, 2rem);
  }

  p {
    color: var(--color-text-secondary);
    margin-top: 1rem;
  }
}

/* Media queries for responsive design */
@media (max-width: $breakpoint-tablet) {
  .quiz-container {
    padding-right: 1rem;
  }

  .quiz-main {
    margin-right: 0;
  }
}

@media (max-width: $breakpoint-mobile) {
  .main-content {
    padding-top: 76px; // Adjusted for mobile title bar height
  }

  .quiz-container {
    margin: 1rem auto; // Adjusted for mobile
    padding: 0.25rem;
  }

  .quiz-content {
    gap: 1rem;
  }

  .completion-message {
    padding: 1.5rem;
    margin-top: 1rem;
  }
}
</style>
  
<template>
  <div class="main-content">
    <div class="quiz-container" :class="{ 'chat-minimized': isChatMinimized }">
      <div class="quiz-layout">
        <div class="quiz-main" :class="{ 'chat-minimized': isChatMinimized }">
          <div class="timer-header">
            <CountdownTimer :time="formattedTime" />
          </div>
          
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
import { useTimer } from '@/composables/useTimer'
import { useRouter } from 'vue-router'
import ChatInterface from '@/components/ChatInterface.vue'
import CountdownTimer from '@/components/common/CountdownTimer.vue'

const { addToast } = useToast()
const router = useRouter()

// Use the timer composable
const { 
  formattedTime, 
  initializeTimer, 
  startTimer, 
  pauseTimer, 
  resumeTimer, 
  stopTimer
} = useTimer()

const questions = ref([])
const currentIndex = ref(0)
const selectedAnswers = ref([])
const quizCompleted = ref(false)
const error = ref(null)
const isChatMinimized = ref(false)

// Watch error state to pause/resume timer
watch(error, (newError) => {
  if (newError) {
    pauseTimer()
  } else {
    resumeTimer()
  }
})

const emit = defineEmits(['quiz-completed'])

const currentQuestion = computed(() => questions.value[currentIndex.value])

// Start timer when component mounts
onMounted(async () => {
  await fetchQuestions()
  
  // Initialize the timer - if this is the first screen of the assessment,
  // this will record the start time
  initializeTimer()
  startTimer()
})

const retryFetch = async () => {
  error.value = null
  await fetchQuestions()
}

const fetchQuestions = async () => {
  try {
    const response = await mcqService.getNextQuestion()
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

// eslint-disable-next-line no-unused-vars
const completeQuiz = () => {
  stopTimer()
  quizCompleted.value = true
  emit('quiz-completed')
}

const isLastQuestion = computed(() => currentIndex.value === 4) // 5th question

const handleNext = async () => {
  try {
    await mcqService.submitAnswer(currentQuestion.value.id, selectedAnswers.value)
    const response = await mcqService.getNextQuestion()
    
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
  stopTimer()
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

.timer-header {
  display: flex;
  justify-content: flex-end;
  padding: 1rem;
  position: absolute;
  top: 0;
  right: 0;
  z-index: 100;
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
  
  .timer-header {
    position: static;
    justify-content: center;
    margin-bottom: 1rem;
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
  
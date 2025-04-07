<template>
  <div class="main-content">
    <div class="intro-container">
      <BaseCard class="intro-card">
        <div class="intro-header">
          <h1>Welcome to the Assessment</h1>
          <p class="subtitle">Please read the following instructions carefully</p>
        </div>

        <div class="intro-content">
          <div class="section">
            <h2>Overview</h2>
            <p>{{ introText[0] }}</p>
          </div>

          <div class="section mcq-section">
            <h3>Part 1: Multiple Choice Questions</h3>
            <div class="section-content">
              <div class="info-item">
                <span class="info-icon">📝</span>
                <p>5 questions to answer</p>
              </div>
              <div class="info-item">
                <span class="info-icon">⏱️</span>
                <p>Time-limited assessment</p>
              </div>
              <div class="info-item">
                <span class="info-icon">✅</span>
                <p>Select the best answer(s) for each question</p>
              </div>
            </div>
          </div>

          <div class="section coding-section">
            <h3>Part 2: Coding Challenge</h3>
            <div class="section-content">
              <div class="info-item">
                <span class="info-icon">💻</span>
                <p>Practical programming task</p>
              </div>
              <div class="info-item">
                <span class="info-icon">📊</span>
                <p>Write and test your solution</p>
              </div>
              <div class="info-item">
                <span class="info-icon">🎯</span>
                <p>Focus on code quality and efficiency</p>
              </div>
            </div>
          </div>

          <div class="section important-notes">
            <h3>Important Notes</h3>
            <ul class="notes-list">
              <li>Ensure stable internet connection throughout the assessment</li>
              <li>Your progress is automatically saved</li>
              <li>Do not refresh or close the browser during the assessment</li>
              <li>Complete all sections in one sitting</li>
            </ul>
          </div>
        </div>

        <div class="acknowledgment-section">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="hasAcknowledged"
              class="checkbox-input"
            >
            <span class="checkbox-text">I have read and understood all instructions</span>
          </label>
        </div>

        <div class="button-container">
          <button 
            class="start-button" 
            @click="proceedToQuiz"
            :disabled="!hasAcknowledged || isStarting"
          >
            {{ isStarting ? 'Starting Assessment...' : 'Start Assessment' }}
            <span class="arrow" v-if="!isStarting">→</span>
          </button>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from './common/BaseCard.vue'
import { mcqService } from '@/services/api'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const { addToast } = useToast()
const hasAcknowledged = ref(false)
const isStarting = ref(false)

const introText = [
  'This assessment is designed to evaluate your technical knowledge and problem-solving abilities through a combination of multiple choice questions and practical coding challenges.'
]

const proceedToQuiz = async () => {
  if (!hasAcknowledged.value || isStarting.value) return
  
  isStarting.value = true
  try {
    await mcqService.startAssessment()
    router.push('/quiz')
  } catch (error) {
    addToast(error.message || 'Failed to start assessment', 'error')
  } finally {
    isStarting.value = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';

.main-content {
  padding-top: 84px;
  min-height: 100vh;
  background: var(--color-background);
}

.intro-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.intro-card {
  background: var(--color-surface);
  border-radius: $border-radius-lg;
  padding: 2.5rem;
  box-shadow: 0 4px 6px var(--color-shadow);
}

.intro-header {
  text-align: center;
  margin-bottom: 3rem;

  h1 {
    color: var(--color-text);
    font-size: clamp(1.5rem, 3vw, 2rem);
    margin-bottom: 0.5rem;
  }

  .subtitle {
    color: var(--color-text-secondary);
    font-size: 1.1rem;
  }
}

.intro-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section {
  h2, h3 {
    color: var(--color-text);
    margin-bottom: 1rem;
    font-weight: 600;
  }

  h2 {
    font-size: 1.4rem;
  }

  h3 {
    font-size: 1.2rem;
    color: var(--color-primary);
  }

  p {
    color: var(--color-text);
    line-height: 1.6;
    margin-bottom: 1rem;
  }
}

.section-content {
  background: var(--color-background);
  border-radius: $border-radius-md;
  padding: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;

  &:last-child {
    margin-bottom: 0;
  }

  .info-icon {
    font-size: 1.5rem;
    min-width: 2rem;
    text-align: center;
  }

  p {
    margin: 0;
    font-size: 1rem;
  }
}

.notes-list {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.75rem;
    color: var(--color-text);
    line-height: 1.5;

    &:before {
      content: "•";
      color: var(--color-primary);
      font-weight: bold;
      position: absolute;
      left: 0.5rem;
    }
  }
}

.acknowledgment-section {
  margin: 2rem 0;
  padding: 1.5rem;
  border-radius: $border-radius-md;
  background: var(--color-background);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;

  .checkbox-input {
    width: 1.2rem;
    height: 1.2rem;
    cursor: pointer;
  }

  .checkbox-text {
    color: var(--color-text);
    font-weight: 500;
  }
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.start-button {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: $border-radius-md;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: $transition-default;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 200px;

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  &:hover:not(:disabled) {
    background: var(--color-primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 2px 4px var(--color-shadow);

    .arrow {
      transform: translateX(4px);
    }
  }

  .arrow {
    transition: transform 0.2s ease;
  }
}

@media (max-width: $breakpoint-tablet) {
  .intro-card {
    padding: 2rem;
  }

  .section-content {
    padding: 1.25rem;
  }
}

@media (max-width: $breakpoint-mobile) {
  .intro-container {
    margin: 1rem auto;
  }

  .intro-card {
    padding: 1.5rem;
  }

  .intro-header {
    margin-bottom: 2rem;
  }

  .section-content {
    padding: 1rem;
  }

  .info-item {
    gap: 0.75rem;

    .info-icon {
      font-size: 1.25rem;
      min-width: 1.5rem;
    }
  }
}
</style> 
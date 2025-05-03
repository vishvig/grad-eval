<template>
  <div class="main-content">
    <div class="intro-container">
      <BaseCard class="intro-card">
        <div class="intro-header">
          <h1>Welcome to the Assessment</h1>
          <p class="subtitle">Please read the following instructions carefully</p>
        </div>

        <div class="intro-content">
          <div v-if="isLoading" class="loading">
            <p>Loading content...</p>
          </div>
          <div v-else-if="error" class="error">
            <p>{{ error }}</p>
            <button @click="fetchContent" class="retry-button">Try Again</button>
          </div>
          <div v-else class="markdown-content" v-html="parsedContent"></div>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from './common/BaseCard.vue'
// import { mcqService } from '@/services/api'
import { markdownService } from '@/services/markdownService'
import { useToast } from '@/composables/useToast'
import MarkdownIt from 'markdown-it'

const router = useRouter()
const { addToast } = useToast()
const hasAcknowledged = ref(false)
const isStarting = ref(false)
const isLoading = ref(true)
const markdownContent = ref('')
const error = ref(null)

const md = new MarkdownIt()

const parsedContent = computed(() => {
  return md.render(markdownContent.value)
})

const fetchContent = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    markdownContent.value = await markdownService.getMarkdownContent('/markdown/introduction.md')
  } catch (err) {
    console.error('Failed to fetch introduction content:', err)
    error.value = 'Failed to load content. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const proceedToQuiz = async () => {
  if (!hasAcknowledged.value || isStarting.value) return
  
  isStarting.value = true
  try {
    // await mcqService.startAssessment()
    router.push('/coding')
  } catch (error) {
    addToast(error.message || 'Failed to start assessment', 'error')
  } finally {
    isStarting.value = false
  }
}

onMounted(() => {
  fetchContent()
})
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
  border-radius: 8px;
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
  margin-bottom: 2rem;
}

.markdown-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 1rem;
  border-radius: 8px;
  background: var(--color-background);
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1);
  
  /* Add styling for markdown content */
  :deep(h1) {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    color: var(--color-primary);
  }
  
  :deep(h2) {
    font-size: 1.4rem;
    margin: 1.5rem 0 1rem;
    color: var(--color-text);
  }
  
  :deep(h3) {
    font-size: 1.2rem;
    margin: 1.2rem 0 0.8rem;
    color: var(--color-primary);
  }
  
  :deep(p) {
    margin-bottom: 1rem;
    line-height: 1.6;
    color: var(--color-text);
  }
  
  :deep(ul), :deep(ol) {
    margin: 1rem 0;
    padding-left: 2rem;
  }
  
  :deep(li) {
    margin-bottom: 0.5rem;
    line-height: 1.6;
  }
  
  :deep(strong) {
    font-weight: 600;
    color: var(--color-text);
  }
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--color-background);
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: 4px;
    
    &:hover {
      background: var(--color-primary);
    }
  }
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--color-background);
  border-radius: 8px;
  
  p {
    color: var(--color-text);
    margin-bottom: 1rem;
  }
}

.retry-button {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  
  &:hover {
    background: var(--color-primary-dark);
  }
}

.acknowledgment-section {
  margin: 2rem 0;
  padding: 1.5rem;
  border-radius: 8px;
  background: var(--color-background);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
}

.checkbox-input {
  appearance: none;
  width: 1.5rem;
  height: 1.5rem;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 4px;
  position: relative;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:checked {
    background: var(--color-primary);
    border-color: var(--color-primary);
    
    &:after {
      content: "✓";
      color: white;
      font-size: 1rem;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }
  }
}

.checkbox-text {
  color: var(--color-text);
  font-weight: 500;
}

.button-container {
  display: flex;
  justify-content: center;
}

.start-button {
  padding: 0.75rem 2rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s ease;
  
  &:hover:not(:disabled) {
    background: var(--color-primary-dark);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  .arrow {
    margin-left: 0.5rem;
    font-size: 1.2rem;
  }
}

@media (max-width: 768px) {
  .intro-container {
    margin-top: 1rem;
  }
  
  .intro-card {
    padding: 1.5rem;
  }
  
  .intro-header {
    margin-bottom: 2rem;
  }
  
  .markdown-content {
    max-height: 350px;
  }
}
</style> 
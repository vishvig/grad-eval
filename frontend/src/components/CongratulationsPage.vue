<template>
  <div class="main-content">
    <div class="congrats-container">
      <div class="congrats-card">
        <div class="congrats-header">
          <h1>Congratulations!</h1>
          <p class="subtitle">You have successfully completed the assessment</p>
        </div>
        
        <div class="content-container">
          <div v-if="isLoading" class="loading">
            <p>Loading content...</p>
          </div>
          <div v-else-if="error" class="error">
            <p>{{ error }}</p>
            <button @click="fetchContent" class="retry-button">Try Again</button>
          </div>
          <div v-else class="markdown-content" v-html="parsedContent"></div>
        </div>
        
        <div class="button-container">
          <button @click="finishAssessment" class="finish-button">
            Finish Assessment
            <span class="arrow">→</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { markdownService } from '@/services/markdownService'
import { authService } from '@/services/api'
import MarkdownIt from 'markdown-it'

const router = useRouter()
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
    markdownContent.value = await markdownService.getMarkdownContent('/markdown/congratulations.md')
  } catch (err) {
    console.error('Failed to fetch congratulations content:', err)
    error.value = 'Failed to load content. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const finishAssessment = () => {
  // Clear user data and logout
  authService.clearUserData()
  // Redirect to login page
  router.push('/')
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
  min-height: calc(100vh - 84px);
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--color-background);
}

.congrats-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.congrats-card {
  background-color: var(--color-surface);
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  text-align: center;
}

.congrats-header {
  margin-bottom: 2rem;
  
  h1 {
    font-size: 2.5rem;
    color: var(--color-primary);
    margin-bottom: 1rem;
  }
  
  .subtitle {
    font-size: 1.25rem;
    color: var(--color-text-secondary);
  }
}

.content-container {
  margin-bottom: 2rem;
}

.markdown-content {
  max-height: 350px;
  overflow-y: auto;
  padding: 1rem;
  border-radius: 8px;
  background: var(--color-background);
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1);
  text-align: left;
  
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
    text-align: left;
  }
  
  :deep(li) {
    margin-bottom: 0.5rem;
    line-height: 1.6;
    text-align: left;
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

.button-container {
  margin-top: 2rem;
}

.finish-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: inline-flex;
  align-items: center;
  
  &:hover {
    background-color: var(--color-primary-dark);
  }
  
  .arrow {
    margin-left: 0.5rem;
    font-size: 1.25rem;
  }
}

@media (max-width: 768px) {
  .congrats-container {
    padding: 1rem;
  }
  
  .congrats-card {
    padding: 1.5rem;
  }
  
  .congrats-header h1 {
    font-size: 2rem;
  }
  
  .markdown-content {
    max-height: 300px;
  }
}
</style> 
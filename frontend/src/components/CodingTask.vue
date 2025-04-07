<template>
  <div class="main-content">
    <div class="coding-container">
      <BaseCard class="coding-card">
        <div class="question-section">
          <h2 class="question-title">Coding Challenge</h2>
          <div class="question-content">
            {{ question }}
          </div>
        </div>
        
        <div class="editor-section">
          <textarea
            v-model="code"
            class="code-editor"
            placeholder="Write your code here..."
            :rows="15"
          ></textarea>
        </div>

        <div class="button-container">
          <button 
            class="submit-button"
            @click="handleSubmit"
            :disabled="!code.trim() || isSubmitting"
          >
            {{ isSubmitting ? 'Submitting...' : 'Submit Solution' }}
          </button>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BaseCard from './common/BaseCard.vue'
import { useToast } from '@/composables/useToast'

const { addToast } = useToast()

const question = ref('Your coding challenge question will appear here...')
const code = ref('')
const isSubmitting = ref(false)

const handleSubmit = async () => {
  if (!code.value.trim()) return
  
  isSubmitting.value = true
  try {
    // API call to submit code will go here
    addToast('Solution submitted successfully', 'success')
    // Handle completion
  } catch (err) {
    addToast(err.message || 'Failed to submit solution', 'error')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style lang="scss" scoped>
// ... styling similar to other components with appropriate modifications ...
</style> 
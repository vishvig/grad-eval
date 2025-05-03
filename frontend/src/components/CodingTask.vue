<template>
  <div class="main-content">
    <div class="coding-container">
      <div class="coding-card">
        <div v-if="isLoading" class="loading-state">
          Loading task...
        </div>
        <template v-else>
          <div class="task-header">
            <h2 class="task-number">Coding Task {{ currentTask }}</h2>
          </div>
          
          <div class="task-description" v-html="parsedTaskDescription"></div>
          
          <div class="task-resources">
            <button @click="downloadTaskFiles" class="download-button">
              <span class="icon">📥</span>
              Download Task Files
            </button>
            
            <div class="upload-section">
              <div class="upload-item">
                <label for="notebook-upload">Upload Jupyter Notebook:</label>
                <div class="upload-control">
                  <input 
                    type="file" 
                    id="notebook-upload" 
                    ref="notebookUpload"
                    @change="handleNotebookUpload" 
                    accept=".ipynb"
                  />
                  <div class="file-info">
                    {{ notebookFile ? notebookFile.name : 'No file selected' }}
                  </div>
                </div>
              </div>
              
              <div class="upload-item">
                <label for="output-upload">Upload Output File (Optional):</label>
                <div class="upload-control">
                  <input 
                    type="file" 
                    id="output-upload" 
                    ref="outputUpload"
                    @change="handleOutputUpload"
                    accept=".csv,.txt,.pkl,.doc,.docx, .json, .pdf"
                  />
                  <div class="file-info">
                    {{ outputFile ? outputFile.name : 'No file selected' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="button-container">
            <button 
              @click="goToNextTask" 
              class="next-button"
              :disabled="!canSubmit || isSubmitting"
            >
              {{ isSubmitting ? 'Submitting...' : 'Next Task' }} <span class="arrow">→</span>
            </button>
          </div>
        </template>
      </div>
    </div>

    <ChatInterface />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useTimer } from '@/composables/useTimer'
import { codingService } from '@/services/api'
import ChatInterface from '@/components/ChatInterface.vue'
import axios from 'axios'
import { ROUTES } from '@/constants/api'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const router = useRouter()
const { addToast } = useToast()
const { 
  formattedTime, 
  initializeTimer, 
  startTimer,
  timerPaused
} = useTimer()

// Helper function to prepare common request data
const prepareNextTaskData = () => {
  const userId = localStorage.getItem('user_id')
  const startEpoch = localStorage.getItem('assessment_start_time')
  const currentEpoch = Math.floor(Date.now() / 1000)

  return {
    user_id: userId,
    current_epoch: parseInt(currentEpoch),
    start_epoch: parseInt(startEpoch)
  }
}

const emit = defineEmits(['time-update', 'timer-state-change'])

// Watch the formatted time to emit time-update events
watch(formattedTime, (newTime) => {
  emit('time-update', newTime)
})

// Watch timer paused state to emit timer-state-change events
watch(timerPaused, (isPaused) => {
  emit('timer-state-change', isPaused)
})

const currentTask = ref(null)
const notebookFile = ref(null)
const outputFile = ref(null)
const isSubmitting = ref(false)
const taskDescription = ref('')
const isLoading = ref(true)

const canSubmit = computed(() => {
  // Only require notebook file for submission
  return notebookFile.value
})

const parsedTaskDescription = computed(() => {
  return taskDescription.value ? md.render(taskDescription.value) : ''
})

const downloadTaskFiles = async () => {
  try {
    // Prepare request data according to DownloadTaskFileRequest model
    const requestData = {
      user_id: localStorage.getItem('user_id'),
      question_id: `coding_task_${currentTask.value}`
    }

    // Make the API call with proper headers and responseType
    const response = await axios.post(
      ROUTES.CODING.DOWNLOAD_TASK,
      requestData,
      {
        responseType: 'blob' // Important for handling binary data
      }
    )

    // Create a blob from the response data
    const blob = new Blob([response.data], { type: 'application/zip' })
    const url = window.URL.createObjectURL(blob)
    
    // Create a temporary link and trigger download
    const link = document.createElement('a')
    link.href = url
    link.download = `task_${currentTask.value}_files.zip`
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    addToast('Files downloaded successfully', 'success')
  } catch (err) {
    console.error('Failed to download task files:', err)
    addToast('Failed to download task files', 'error')
  }
}

onMounted(async () => {
  try {
    isLoading.value = true
    let taskData
    
    // Check if we have stored task data from login
    const storedTaskData = localStorage.getItem('current_task_data')
    if (storedTaskData) {
      taskData = JSON.parse(storedTaskData)
      localStorage.removeItem('current_task_data') // Clear it after use
    } else {
      // Check if assessment was already started
      const assessmentStarted = localStorage.getItem('assessment_status') === 'true'
      if (assessmentStarted) {
        // If already started, just get the next task
        const formData = new FormData()
        const jsonData = {
          ...prepareNextTaskData(),
          question_id: null
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
        taskData = response.data
      } else {
        // If not started, start the assessment
        taskData = await codingService.startCodingAssessment()
        localStorage.setItem('assessment_status', 'true')
      }
    }
    
    // Only redirect if we explicitly get a null question_id
    if (!taskData || !taskData.question_id) {
      addToast('No tasks available', 'info')
      router.push('/congratulations')
      return
    }

    // Store question_id in sessionStorage for chat
    sessionStorage.setItem('question_id', taskData.question_id)

    // Update the component with the task data
    currentTask.value = taskData.question_id.replace('coding_task_', '')
    taskDescription.value = taskData.body || '' // Use body instead of description
    
    // Initialize and start the timer
    initializeTimer()
    startTimer()
  } catch (err) {
    console.error('Failed to start coding assessment:', err)
    addToast('Failed to start coding assessment. Please try again.', 'error')
    router.push('/congratulations') // Redirect on error
  } finally {
    isLoading.value = false
  }
})

const handleNotebookUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    notebookFile.value = file
    addToast(`Notebook file selected: ${file.name}`, 'success')
  }
}

const handleOutputUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    outputFile.value = file
    addToast(`Output file selected: ${file.name}`, 'success')
  }
}

const goToNextTask = async () => {
  if (!canSubmit.value) return
  
  isLoading.value = true
  isSubmitting.value = true
  try {
    const taskData = await codingService.nextTask({
      notebook: notebookFile.value,
      output: outputFile.value || null, // Make output optional
      question_id: `coding_task_${currentTask.value}`
    })
    
    // Only redirect if we explicitly get a null question_id
    if (!taskData || !taskData.question_id) {
      addToast('All tasks completed!', 'success')
      router.push('/congratulations')
      return
    }
    
    // Store the new question_id in sessionStorage for chat
    sessionStorage.setItem('question_id', taskData.question_id)
    
    // Update task data
    currentTask.value = taskData.question_id.replace('coding_task_', '')
    taskDescription.value = taskData.body || '' // Use body instead of description
    
    // Reset file inputs
    notebookFile.value = null
    outputFile.value = null
    if (document.getElementById('notebook-upload')) {
      document.getElementById('notebook-upload').value = ''
    }
    if (document.getElementById('output-upload')) {
      document.getElementById('output-upload').value = ''
    }

    // Force chat reload by removing and setting the trigger with a small delay
    sessionStorage.removeItem('chat_reload_trigger')
    setTimeout(() => {
      sessionStorage.setItem('chat_reload_trigger', Date.now().toString())
    }, 100)
    
    addToast('Solution submitted successfully', 'success')
  } catch (err) {
    console.error('Failed to move to next task:', err)
    addToast('Failed to submit solution. Please try again.', 'error')
  } finally {
    isSubmitting.value = false
    isLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';

.main-content {
  padding-top: 84px;
  min-height: calc(100vh - 84px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background-color: var(--color-background);
  padding-bottom: 2rem;
}

.coding-container {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.coding-card {
  background-color: var(--color-surface);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
  position: relative;
  
  .task-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
  }
}

.task-description {
  margin-bottom: 2rem;
  line-height: 1.6;
  
  :deep(p) {
    margin-bottom: 1rem;
  }

  :deep(pre) {
    background-color: var(--color-background);
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    margin: 1rem 0;
  }

  :deep(code) {
    font-family: monospace;
    background-color: var(--color-background);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
  }

  :deep(ul), :deep(ol) {
    margin: 1rem 0;
    padding-left: 2rem;
  }

  :deep(li) {
    margin-bottom: 0.5rem;
  }

  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    margin: 1.5rem 0 1rem;
    color: var(--color-text);
  }
}

.task-resources {
  margin-bottom: 2rem;
}

.download-button {
  display: flex;
  align-items: center;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 1.25rem;
  cursor: pointer;
  font-weight: 600;
  margin-bottom: 1.5rem;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: var(--color-primary-dark);
  }
  
  .icon {
    margin-right: 0.5rem;
    font-size: 1.25rem;
  }
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1.5rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 1.5rem;
  background-color: var(--color-surface);
}

.upload-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
  label {
    font-weight: 600;
    color: var(--color-text);
  }
  
  .upload-control {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    
    input[type="file"] {
      background-color: var(--color-background);
      padding: 0.5rem;
      border: 1px solid var(--color-border);
      border-radius: 4px;
      width: 100%;
      color: var(--color-text);
    }
    
    .file-info {
      font-size: 0.875rem;
      color: var(--color-text-secondary);
      margin-top: 0.25rem;
    }
  }
}

.button-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.next-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    background-color: var(--color-primary-dark);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .arrow {
    margin-left: 0.5rem;
  }
}

@media (max-width: 768px) {
  .button-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .next-button {
    width: 100%;
  }
  
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  font-size: 1.2rem;
  color: var(--color-text-secondary);
}
</style> 
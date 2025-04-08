<template>
  <div class="main-content">
    <div class="coding-container">
      <div class="coding-card">
        <div class="task-header">
          <h2 class="task-number">Coding Task {{ currentTask }}</h2>
          <div class="progress-indicator">
            Task {{ currentTask }} of {{ totalTasks }}
          </div>
        </div>
        
        <div class="task-description">
          <p>{{ taskDescription }}</p>
        </div>
        
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
              <label for="output-upload">Upload Output File:</label>
              <div class="upload-control">
                <input 
                  type="file" 
                  id="output-upload" 
                  ref="outputUpload"
                  @change="handleOutputUpload"
                  accept=".csv,.json,.txt"
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
            @click="submitTask" 
            class="submit-button"
            :disabled="!canSubmit || isSubmitting"
          >
            {{ isSubmitting ? 'Submitting...' : 'Submit Task' }}
          </button>
          
          <button 
            v-if="!isLastTask"
            @click="goToNextTask" 
            class="next-button"
            :disabled="!taskCompleted"
          >
            Next Task <span class="arrow">→</span>
          </button>
          
          <button 
            v-else
            @click="finishCodingSection" 
            class="finish-button"
            :disabled="!taskCompleted"
          >
            Finish <span class="arrow">→</span>
          </button>

          <!-- Cancel Button to go back to the Congratulations page -->
          <button 
            @click="goToCongratulations" 
            class="cancel-button"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Include the ChatInterface component -->
    <ChatInterface />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import ChatInterface from '@/components/ChatInterface.vue'; // Import the ChatInterface component

const router = useRouter()
const { addToast } = useToast()

// Mock tasks data - in a real app, this would come from an API
const tasks = [
  {
    id: 1,
    description: 'In this task, you will analyze a dataset of customer transactions to identify patterns and anomalies. The dataset contains information about purchases, timestamps, and customer demographics. Your goal is to implement a clustering algorithm to segment customers based on their purchasing behavior.',
    downloadUrl: '/api/tasks/1/download',
    completed: false
  },
  {
    id: 2,
    description: 'For this task, you will build a predictive model to forecast sales for the next quarter based on historical data. The dataset includes sales figures, marketing spend, seasonality factors, and external economic indicators. You will need to preprocess the data, engineer relevant features, and implement a regression model.',
    downloadUrl: '/api/tasks/2/download',
    completed: false
  },
  {
    id: 3,
    description: 'In this final task, you will implement a natural language processing solution to classify customer reviews into positive, negative, or neutral sentiment. The dataset contains product reviews with text and star ratings. You will need to clean the text data, extract relevant features, and build a classification model.',
    downloadUrl: '/api/tasks/3/download',
    completed: false
  }
]

const currentTask = ref(1)
const totalTasks = tasks.length
const notebookFile = ref(null)
const outputFile = ref(null)
const isSubmitting = ref(false)
const taskCompleted = ref(false)

const taskDescription = computed(() => {
  const task = tasks.find(t => t.id === currentTask.value)
  return task?.description || 'Task description not available.'
})

const isLastTask = computed(() => {
  return currentTask.value === totalTasks
})

const canSubmit = computed(() => {
  return notebookFile.value && outputFile.value
})

const downloadTaskFiles = async () => {
  try {
    // In a real app, this would download the task files based on the current task
    // For demo purposes, just show a toast
    addToast('Downloading task files...', 'info')
    setTimeout(() => {
      addToast('Task files downloaded successfully', 'success')
    }, 1500)
  } catch (err) {
    addToast('Failed to download task files', 'error')
  }
}

const handleNotebookUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    notebookFile.value = file
    addToast(`Notebook file selected: ${file.name}`, 'info')
  }
}

const handleOutputUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    outputFile.value = file
    addToast(`Output file selected: ${file.name}`, 'info')
  }
}

const submitTask = async () => {
  if (!canSubmit.value) return
  
  isSubmitting.value = true
  try {
    // In a real app, this would upload the files to the server
    // const formData = new FormData()
    // formData.append('notebook', notebookFile.value)
    // formData.append('output', outputFile.value)
    // const response = await apiService.submitTaskFiles(currentTask.value, formData)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Update task status
    tasks[currentTask.value - 1].completed = true
    taskCompleted.value = true
    
    addToast('Task submitted successfully', 'success')
  } catch (err) {
    addToast('Failed to submit task', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const goToNextTask = () => {
  if (currentTask.value < totalTasks) {
    currentTask.value += 1
    notebookFile.value = null
    outputFile.value = null
    taskCompleted.value = tasks[currentTask.value - 1].completed
    
    // Reset file inputs
    if (document.getElementById('notebook-upload')) {
      document.getElementById('notebook-upload').value = ''
    }
    if (document.getElementById('output-upload')) {
      document.getElementById('output-upload').value = ''
    }
  }
}

const finishCodingSection = () => {
  addToast('Coding section completed!', 'success')
  // In a real app, you might redirect to a completion page
  router.push('/')
}

const goToCongratulations = () => {
  router.push('/congratulations'); // Navigate to the congratulations page
}

onMounted(() => {
  // Check if there's a task number in the URL
  const taskParam = new URLSearchParams(window.location.search).get('task')
  if (taskParam && !isNaN(parseInt(taskParam))) {
    const taskNumber = parseInt(taskParam)
    if (taskNumber >= 1 && taskNumber <= totalTasks) {
      currentTask.value = taskNumber
    }
  }
  
  // Check if the current task is already completed
  taskCompleted.value = tasks[currentTask.value - 1].completed
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
  
  .task-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
  }
  
  .progress-indicator {
    color: var(--color-text-secondary);
    font-size: 0.875rem;
  }
}

.task-description {
  margin-bottom: 2rem;
  line-height: 1.6;
  
  p {
    margin-bottom: 1rem;
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
  justify-content: space-between;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.submit-button, .next-button, .finish-button, .cancel-button {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.submit-button {
  background-color: var(--color-success);
  color: white;
  border: none;
  
  &:hover:not(:disabled) {
    background-color: var(--color-success-dark);
  }
}

.next-button, .finish-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  
  &:hover:not(:disabled) {
    background-color: var(--color-primary-dark);
  }
  
  .arrow {
    margin-left: 0.5rem;
  }
}

.cancel-button {
  background-color: var(--color-danger);
  color: white;
  border: none;
  
  &:hover {
    background-color: var(--color-danger-dark);
  }
}

@media (max-width: 768px) {
  .button-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .submit-button, .next-button, .finish-button, .cancel-button {
    width: 100%;
  }
}
</style> 
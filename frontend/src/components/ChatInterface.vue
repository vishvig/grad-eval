<template>
  <div 
    class="chat-container" 
    :class="{ 'minimized': isMinimized }"
    :style="{ width: `${width}px` }"
  >
    <div class="resize-handle" @mousedown="startResize"></div>
    <div class="chat-header" @click="expandChat">
      <h3>Chat Assistant</h3>
      <button class="minimize-btn" @click.stop="toggleMinimize">
        {{ isMinimized ? '←' : '→' }}
      </button>
    </div>

    <div class="chat-content">
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(message, index) in messages" 
             :key="index" 
             :class="['message', message.type, { 'error': message.isError }]">
          <div v-if="message.isMarkdown" v-html="md.render(message.content)" class="markdown-content"></div>
          <div v-else>{{ message.content }}</div>
        </div>
        
        <!-- Thinking Loader -->
        <div v-if="isThinking" class="message system thinking">
          <div class="thinking-loader">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <!-- Quick actions hidden but code preserved -->
      <div class="quick-actions" style="display: none;">
        <button 
          v-for="action in quickActions" 
          :key="action"
          class="quick-action-btn"
          @click="handleQuickAction(action)"
        >
          {{ action }}
        </button>
      </div>

      <div class="chat-input-container">
        <textarea 
          v-model="userInput"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.enter.shift.exact="userInput += '\n'"
          placeholder="Type your message here... (Shift + Enter for new line)"
          class="chat-input"
          rows="1"
        ></textarea>
        <button @click="sendMessage" class="send-button">Send</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import axios from 'axios'
import { ROUTES } from '@/constants/api'
import { useToast } from '@/composables/useToast'

const md = new MarkdownIt()
const { addToast } = useToast()

const isMinimized = ref(false)
const userInput = ref('')
const messages = ref([])
const isThinking = ref(false)
const messagesContainer = ref(null)
const width = ref(320) // Default width
const isResizing = ref(false)
const startX = ref(0)
const startWidth = ref(0)

const emit = defineEmits(['minimize-changed', 'width-changed'])

const quickActions = [
  'Explain this question',
  'Give me a hint',
  'Time remaining?',
  'Questions left?'
]

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
  emit('minimize-changed', isMinimized.value)
}

const expandChat = () => {
  if (isMinimized.value) {
    isMinimized.value = false
    emit('minimize-changed', false)
  }
}

const sendMessage = async () => {
  if (!userInput.value.trim()) return
  
  // Add user message
  messages.value.push({
    type: 'user',
    content: userInput.value
  })
  
  const userMessage = userInput.value
  userInput.value = ''
  
  // Show thinking loader
  isThinking.value = true
  await scrollToBottom()
  
  try {
    // Get user_id and question_id from localStorage/sessionStorage
    const userId = localStorage.getItem('user_id')
    const questionId = sessionStorage.getItem('question_id')

    if (!userId || !questionId) {
      throw new Error('Missing user or question information')
    }

    // Make API call
    const response = await axios.post(ROUTES.CHAT.CHAT, {
      user_id: userId,
      question_id: questionId,
      prompt: userMessage
    })

    // Add system response with markdown rendering
    messages.value.push({
      type: 'system',
      content: response.data.response,
      isMarkdown: true
    })

    addToast('Response received', 'success')
  } catch (err) {
    console.error('Error sending message:', err)
    addToast('Failed to send message', 'error')
    messages.value.push({
      type: 'system',
      content: 'Sorry, I encountered an error. Please try again.',
      isError: true
    })
  } finally {
    isThinking.value = false
    await scrollToBottom()
  }
}

const handleQuickAction = (action) => {
  userInput.value = action
  sendMessage()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const startResize = (e) => {
  isResizing.value = true
  startX.value = e.clientX
  startWidth.value = width.value
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
}

const handleResize = (e) => {
  if (!isResizing.value) return
  const diff = startX.value - e.clientX
  const newWidth = Math.min(Math.max(startWidth.value + diff, 280), 800) // Min 280px, Max 800px
  width.value = newWidth
  document.documentElement.style.setProperty('--chat-width', `${newWidth}px`)
  emit('width-changed', newWidth)
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// Watch for chat reload trigger
watch(() => sessionStorage.getItem('chat_reload_trigger'), (newValue, oldValue) => {
  // Only reload if the value has actually changed and is not null
  if (newValue && newValue !== oldValue) {
    console.log('Chat reload triggered')
    messages.value = []
    nextTick(() => {
      messages.value = [{
        type: 'system',
        content: 'Hello! How can I help you with your assessment?',
        isMarkdown: true
      }]
      scrollToBottom()
    })
  }
}, { immediate: true })

onMounted(() => {
  document.documentElement.style.setProperty('--chat-width', `${width.value}px`)
  // Remove the initial message push since the watcher will handle it
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
})
</script>

<style scoped>
.chat-container {
  position: fixed;
  right: 0;
  top: 84px;
  bottom: 0;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  transition: transform 0.3s ease;
  transform-origin: right;

  &.minimized {
    transform: translateX(calc(100% - 40px));
    box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
    
    .chat-content {
      display: none;
    }
    
    .chat-header {
      background: var(--color-primary);
      width: 40px;
      padding: 12px 8px;
      justify-content: center;
      
      h3 {
        display: none;
      }
      
      .minimize-btn {
        margin: 0;
        padding: 4px;
      }
    }

    .resize-handle {
      display: none;
    }
  }
}

.resize-handle {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  cursor: col-resize;
  background: transparent;
  transition: background-color 0.2s ease;

  &:hover {
    background: var(--color-primary);
    opacity: 0.2;
  }

  &:active {
    background: var(--color-primary);
    opacity: 0.4;
  }
}

.chat-header {
  padding: 12px 20px;
  background: var(--color-primary);
  color: var(--color-text);
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 48px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.minimize-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 4px 12px;
  font-size: 1.2rem;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
  }
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100% - 48px);
  background: var(--color-surface);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--color-background);
}

.message {
  max-width: 90%;
  padding: 14px 18px;
  border-radius: 8px;
  word-break: break-word;
  font-size: 15px;
  line-height: 1.4;
  white-space: pre-wrap;
}

.message.user {
  align-self: flex-end;
  background: var(--color-primary);
  color: white;
}

.message.system {
  align-self: flex-start;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.thinking {
  background: var(--color-background);
  border: none !important;
}

.thinking-loader {
  display: flex;
  gap: 4px;
  padding: 4px;
}

.thinking-loader span {
  width: 8px;
  height: 8px;
  background: var(--color-primary);
  border-radius: 50%;
  display: inline-block;
  animation: bounce 1.4s infinite ease-in-out both;
}

.thinking-loader span:nth-child(1) { animation-delay: -0.32s; }
.thinking-loader span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { 
    transform: scale(0);
  } 
  40% { 
    transform: scale(1.0);
  }
}

.quick-actions {
  padding: 12px;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: var(--color-surface);
}

.quick-action-btn {
  padding: 6px 12px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text);
  transition: all 0.2s ease;
}

.quick-action-btn:hover {
  background: var(--color-primary-dark);
  border-color: var(--color-primary);
}

.chat-input-container {
  padding: 12px;
  border-top: 1px solid var(--color-border);
  display: flex;
  gap: 8px;
  background: var(--color-surface);
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  resize: none;
  min-height: 40px;
  max-height: 120px;
  overflow-y: auto;
  line-height: 1.4;
  font-family: inherit;
  background: var(--color-background);
  color: var(--color-text);
}

.chat-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.send-button {
  padding: 8px 16px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  min-width: 80px;
  transition: background-color 0.2s ease;
}

.send-button:hover {
  background: var(--color-primary-dark);
}

.markdown-content {
  width: 100%;
}

.markdown-content :deep(p) {
  margin: 0.5em 0;
}

.markdown-content :deep(code) {
  background: var(--color-background);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: monospace;
}

.markdown-content :deep(pre) {
  background: var(--color-background);
  padding: 1em;
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-content :deep(ul), 
.markdown-content :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.markdown-content :deep(blockquote) {
  margin: 0.5em 0;
  padding-left: 1em;
  border-left: 3px solid var(--color-border);
  color: var(--color-text-secondary);
}

.message.error {
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid #f44336;
}
</style> 
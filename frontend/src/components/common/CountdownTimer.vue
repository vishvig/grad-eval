<template>
  <div class="timer-container" :class="{ 'warning': isWarning, 'danger': isDanger }">
    <div class="timer-label">Time Remaining:</div>
    <div class="timer-icon">⏱️</div>
    <div class="timer-display">{{ formattedTime }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  time: {
    type: String,
    required: true
  },
  warningThreshold: {
    type: Number,
    default: 300 // 5 minutes in seconds
  },
  dangerThreshold: {
    type: Number,
    default: 60 // 1 minute in seconds
  }
})

// Calculate if we should show warning or danger states
const timeInSeconds = computed(() => {
  if (!props.time) return 0
  
  const [minutes, seconds] = props.time.split(':').map(Number)
  return (minutes * 60) + seconds
})

const isWarning = computed(() => {
  return timeInSeconds.value <= props.warningThreshold && timeInSeconds.value > props.dangerThreshold
})

const isDanger = computed(() => {
  return timeInSeconds.value <= props.dangerThreshold
})

const formattedTime = computed(() => {
  if (!props.time) return "00:00"
  
  // Ensure proper format with leading zeros
  const [minutes, seconds] = props.time.split(':')
  return `${minutes.padStart(2, '0')}:${seconds.padStart(2, '0')}`
})
</script>

<style lang="scss" scoped>
.timer-container {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  gap: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  
  &.warning {
    border-color: #f0ad4e;
    background-color: rgba(240, 173, 78, 0.1);
    animation: pulse 2s infinite;
  }
  
  &.danger {
    border-color: #d9534f;
    background-color: rgba(217, 83, 79, 0.1);
    animation: pulse 1s infinite;
  }
}

.timer-label {
  font-size: 1rem;
  font-weight: 500;
  margin-right: 0.3rem;
}

.timer-icon {
  font-size: 1.2rem;
}

.timer-display {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
  
  .warning & {
    color: #f0ad4e;
  }
  
  .danger & {
    color: #d9534f;
  }
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 1;
  }
}
</style> 
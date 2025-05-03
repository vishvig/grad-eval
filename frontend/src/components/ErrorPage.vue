<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-icon">
        <span class="robot">🤖</span>
        <span class="spark">⚡</span>
      </div>
      <h2 class="error-title">Oops! Something went wrong</h2>
      <p class="error-message">{{ message }}</p>
      <button class="retry-button" @click="handleRetry">
        Try Again
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'An unexpected error occurred.'
  }
})

const emit = defineEmits(['retry'])

const handleRetry = () => {
  emit('retry')
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';

.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  width: 100%;
}

.error-content {
  text-align: center;
  padding: 2rem;
  background: var(--color-surface);
  border-radius: $border-radius-lg;
  box-shadow: 0 4px 6px var(--color-shadow);
  max-width: 500px;
  width: 90%;
}

.error-icon {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;

  .robot {
    font-size: 4rem;
    display: inline-block;
    transform: rotate(-10deg);
    filter: grayscale(0.3);
    animation: shake 2s ease-in-out infinite;
  }

  .spark {
    position: absolute;
    top: -0.5rem;
    right: -0.5rem;
    font-size: 1.5rem;
    animation: spark 1s ease-in-out infinite;
  }
}

@keyframes shake {
  0%, 100% {
    transform: rotate(-10deg);
  }
  25% {
    transform: rotate(-15deg);
  }
  75% {
    transform: rotate(-5deg);
  }
}

@keyframes spark {
  0%, 100% {
    opacity: 0;
    transform: scale(0.8) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1.2) rotate(15deg);
  }
}

.error-title {
  color: var(--color-text);
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.error-message {
  color: var(--color-text-secondary);
  margin-bottom: 2rem;
  line-height: 1.5;
}

.retry-button {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: $border-radius-md;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: $transition-default;

  &:hover {
    background: var(--color-primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 2px 4px var(--color-shadow);
  }
}

@media (max-width: $breakpoint-mobile) {
  .error-content {
    padding: 1.5rem;
  }

  .error-icon .robot {
    font-size: 3rem;
  }

  .error-icon .spark {
    font-size: 1.2rem;
  }

  .error-title {
    font-size: 1.2rem;
  }
}
</style> 
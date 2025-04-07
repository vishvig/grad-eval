<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast--${toast.type}`]"
      >
        <span class="toast__icon">
          {{ toast.type === 'success' ? '✅' : '❌' }}
        </span>
        <span class="toast__message">{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '@/composables/useToast'

const { toasts } = useToast()
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';

.toast-container {
  position: fixed;
  top: 80px; // Below title bar
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: $border-radius-md;
  background: var(--color-surface);
  box-shadow: 0 4px 6px var(--color-shadow);
  min-width: 300px;
  max-width: 400px;
  
  &--success {
    border-left: 4px solid #4caf50;
  }
  
  &--error {
    border-left: 4px solid #f44336;
  }

  &__icon {
    font-size: 1.2rem;
  }

  &__message {
    color: var(--color-text);
    font-size: 0.95rem;
    line-height: 1.4;
  }
}

// Toast animations
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

@media (max-width: $breakpoint-mobile) {
  .toast-container {
    right: 0.5rem;
    left: 0.5rem;
  }

  .toast {
    min-width: unset;
    width: 100%;
  }
}
</style> 
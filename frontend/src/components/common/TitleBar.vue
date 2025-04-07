<template>
  <header class="title-bar">
    <div class="title-section">
      <h1>Grad Evaluator</h1>
      <span class="page-subtitle" v-if="pageSubtitle">{{ pageSubtitle }}</span>
    </div>
    <div class="status-section">
      <div v-if="showTimer" class="timer" :class="{ 'timer--paused': isPaused }">
        <span class="timer__icon">{{ isPaused ? '⏸️' : '⏱️' }}</span>
        <span class="timer__text">
          {{ isPaused ? 'Timer Paused: ' : 'Time Left: ' }}{{ formattedTime }}
        </span>
      </div>
      
      <div class="profile-menu" v-click-outside="closeDropdown">
        <button class="profile-button" @click="toggleDropdown">
          <span class="profile-icon">👤</span>
          <span class="profile-name">{{ username }}</span>
          <span class="dropdown-arrow" :class="{ 'open': isDropdownOpen }">▼</span>
        </button>
        
        <div class="dropdown-menu" v-if="isDropdownOpen">
          <div class="dropdown-item theme-item">
            <span class="item-icon">{{ isDarkTheme ? '🌙' : '☀️' }}</span>
            <span class="item-text">Theme</span>
            <ThemeToggle class="theme-toggle-compact" />
          </div>
          <button class="dropdown-item" @click="handleLogout">
            <span class="item-icon">🚪</span>
            <span class="item-text">Logout</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'
import { authService } from '@/services/api'

defineProps({
  formattedTime: {
    type: String,
    required: true
  },
  isPaused: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()
const route = useRoute()

const isDropdownOpen = ref(false)
const username = ref('')
const isDarkTheme = ref(document.documentElement.getAttribute('data-theme') === 'dark')

const showTimer = computed(() => route.name === 'Quiz')

// Compute page subtitle based on current route
const pageSubtitle = computed(() => {
  switch (route.name) {
    case 'Introduction':
      return 'Introduction'
    case 'Quiz':
      return 'Multiple Choice Questions'
    case 'Coding':
      return 'Coding Challenge'
    default:
      return null
  }
})

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const handleLogout = () => {
  authService.clearUserData()
  router.push('/')
}

onMounted(() => {
  username.value = localStorage.getItem('username') || 'User'
})

// Custom directive for clicking outside
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';

.title-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--color-surface);
  box-shadow: 0 2px 4px var(--color-shadow);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 clamp(1rem, 5vw, 2rem);
  z-index: 100;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 1rem;

  h1 {
    color: var(--color-text);
    font-size: clamp(1.2rem, 3vw, 1.5rem);
    margin: 0;
    font-weight: 600;
  }

  .page-subtitle {
    color: var(--color-text-secondary);
    font-size: clamp(0.9rem, 2vw, 1.1rem);
    padding-left: 1rem;
    border-left: 2px solid var(--color-border);
  }
}

.status-section {
  display: flex;
  align-items: center;
  gap: clamp(1.5rem, 4vw, 3rem);
  margin-left: auto;
}

.timer {
  font-size: clamp(0.9rem, 2.5vw, 1.1rem);
  font-weight: 600;
  color: var(--color-primary);
  padding: 0.5rem clamp(0.75rem, 2vw, 1rem);
  background: var(--color-selected);
  border-radius: 8px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;

  &--paused {
    background: var(--color-surface);
    border: 2px solid var(--color-primary);
    animation: pulse 2s infinite;
  }

  &__icon {
    display: inline-flex;
    align-items: center;
  }

  &__text {
    display: inline-flex;
    align-items: center;
  }
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
}

.profile-menu {
  position: relative;
}

.profile-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: $border-radius-md;
  color: var(--color-text);
  cursor: pointer;
  transition: $transition-default;

  &:hover {
    border-color: var(--color-primary);
    box-shadow: 0 2px 4px var(--color-shadow);
  }

  .profile-icon {
    font-size: 1.2rem;
  }

  .profile-name {
    font-size: 0.9rem;
    font-weight: 500;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .dropdown-arrow {
    font-size: 0.8rem;
    transition: transform 0.3s ease;

    &.open {
      transform: rotate(180deg);
    }
  }
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: $border-radius-md;
  box-shadow: 0 4px 6px var(--color-shadow);
  min-width: 220px;
  z-index: 1000;
  padding: 0.25rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  width: 100%;
  border: none;
  background: none;
  color: var(--color-text);
  cursor: pointer;
  transition: $transition-default;
  text-align: left;
  box-sizing: border-box;

  &:hover {
    background: var(--color-selected);
  }

  &:not(:last-child) {
    border-bottom: 1px solid var(--color-border);
  }

  .item-icon {
    font-size: 1.1rem;
  }

  .item-text {
    font-size: 0.9rem;
  }
}

.theme-item {
  justify-content: space-between;
  cursor: default;
  padding-right: 0.5rem;
  gap: 0.5rem;

  &:hover {
    background: none;
  }
}

.theme-toggle-compact {
  position: static;
  width: 46px;
  height: 24px;
  margin-right: 0.25rem;

  :deep(.toggle-slider) {
    width: 18px;
    height: 18px;
  }

  :deep(.toggle-icon) {
    font-size: 0.75rem;
  }
}

@media (max-width: $breakpoint-tablet) {
  .status-section {
    gap: clamp(1rem, 3vw, 2rem);
  }
}

@media (max-width: $breakpoint-mobile) {
  .title-bar {
    height: 56px;
  }

  .status-section {
    gap: 1rem;
  }

  .profile-button {
    padding: 0.4rem 0.75rem;

    .profile-name {
      max-width: 100px;
    }
  }

  .dropdown-menu {
    min-width: 180px;
  }

  .timer {
    font-size: 0.9rem;
    padding: 0.4rem 0.8rem;
  }

  .title-section {
    gap: 0.5rem;
    flex-direction: column;
    align-items: flex-start;

    .page-subtitle {
      padding-left: 0;
      border-left: none;
      font-size: 0.9rem;
    }
  }
}
</style> 
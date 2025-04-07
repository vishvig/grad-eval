<template>
  <button 
    class="theme-toggle" 
    @click="toggleTheme" 
    :title="isLightTheme ? 'Switch to dark mode' : 'Switch to light mode'"
    :class="{ 'theme-toggle--dark': !isLightTheme }"
  >
    <div class="toggle-slider">
      <span class="toggle-icon">{{ isLightTheme ? '☀️' : '🌙' }}</span>
    </div>
  </button>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const theme = ref(null); // null means system preference

const systemPrefersDark = computed(() => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
});

const isLightTheme = computed(() => {
  if (theme.value === null) {
    return !systemPrefersDark.value;
  }
  return theme.value === 'light';
});

const toggleTheme = () => {
  theme.value = isLightTheme.value ? 'dark' : 'light';
  updateTheme();
};

const updateTheme = () => {
  if (theme.value === null) {
    document.documentElement.removeAttribute('data-theme');
  } else {
    document.documentElement.setAttribute('data-theme', theme.value);
  }
  localStorage.setItem('theme-preference', theme.value || 'system');
};

// Listen for system theme changes
onMounted(() => {
  const savedTheme = localStorage.getItem('theme-preference');
  theme.value = savedTheme === 'system' ? null : savedTheme;
  updateTheme();

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (theme.value === null) {
      updateTheme();
    }
  });
});
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';

.theme-toggle {
  position: fixed;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem;
  border-radius: 2rem;
  border: 2px solid var(--color-border);
  background: var(--color-surface);
  cursor: pointer;
  transition: $transition-default;
  width: 70px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  z-index: 1000;
  overflow: hidden;
  
  &:hover {
    border-color: var(--color-primary);
    box-shadow: 0 2px 8px var(--color-shadow);
  }

  &--dark {
    justify-content: flex-end;
    background: var(--color-surface);
    
    .toggle-slider {
      background: var(--color-selected);
    }
  }
}

.toggle-slider {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: $transition-default;
}

.toggle-icon {
  font-size: 1rem;
  line-height: 1;
  transition: $transition-default;
}

@media (max-width: $breakpoint-mobile) {
  .theme-toggle {
    top: 0.5rem;
    right: 0.5rem;
    width: 60px;
    height: 30px;
  }

  .toggle-slider {
    width: 24px;
    height: 24px;
  }

  .toggle-icon {
    font-size: 0.875rem;
  }
}
</style> 
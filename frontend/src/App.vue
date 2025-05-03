<template>
  <TitleBar 
    v-if="showTitleBar"
    :formatted-time="formattedTime" 
    :is-paused="timerPaused"
  />
  <router-view @time-update="updateTime" @quiz-completed="onQuizCompleted" @timer-state-change="updateTimerState"></router-view>
  <ToastNotification />
</template>

<script>
import ToastNotification from './components/common/ToastNotification.vue'
import TitleBar from './components/common/TitleBar.vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'

export default {
  name: 'App',
  components: {
    ToastNotification,
    TitleBar
  },
  data() {
    return {
      formattedTime: '--:--',
      quizCompleted: false,
      timerPaused: false
    }
  },
  setup() {
    const route = useRoute()
    const showTitleBar = computed(() => {
      // Show title bar on all authenticated routes except login
      return route.meta.requiresAuth
    })
    return {
      showTitleBar
    }
  },
  methods: {
    updateTime(time) {
      this.formattedTime = time
    },
    onQuizCompleted() {
      this.quizCompleted = true
    },
    updateTimerState(isPaused) {
      this.timerPaused = isPaused
    }
  }
}
</script>

<style lang="scss">
@import '@/styles/mixins.scss';
@import '@/styles/themes.scss';

/* Add global styles to html and body */
html, 
body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background: var(--color-background);
  transition: background-color 0.3s ease;
}

body {
  overflow-x: hidden; /* Prevent horizontal scrollbar */
}

#app {
  font-family: 'Inter', Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--color-text);
  margin: 0;
  min-height: 100vh;
  background: var(--color-background);
  transition: background-color 0.3s ease, color 0.3s ease;
  width: 100%;
  position: relative;
}

.main-content {
  padding-top: 84px; // title bar height + spacing
  min-height: 100vh;
  box-sizing: border-box;
  background: var(--color-background);
}

.app-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Media queries for responsive design */
@media (max-width: $breakpoint-mobile) {
  .main-content {
    padding-top: 76px;
  }
  
  .app-container {
    padding: 0 0.5rem;
  }
}
</style>

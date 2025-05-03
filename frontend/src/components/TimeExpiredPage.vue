<template>
  <div class="main-content">
    <div class="expired-container">
      <div class="expired-card">
        <div class="icon">⏱️</div>
        <h1>Time's Up!</h1>
        <p>Your assessment time has expired.</p>
        <p>Thank you for your participation.</p>
        <div class="button-container">
          <button @click="goToHome" class="home-button">
            Return to Home
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToHome = () => {
  router.push('/')
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
  align-items: center;
  background-color: var(--color-background);
}

.expired-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}

.expired-card {
  background-color: var(--color-surface);
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  text-align: center;
}

.icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

h1 {
  font-size: 2.5rem;
  color: var(--color-primary);
  margin-bottom: 1.5rem;
}

p {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.button-container {
  margin-top: 2.5rem;
}

.home-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: var(--color-primary-dark);
  }
}

@media (max-width: 768px) {
  .expired-container {
    padding: 1rem;
  }
  
  .expired-card {
    padding: 2rem;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  p {
    font-size: 1rem;
  }
}
</style> 
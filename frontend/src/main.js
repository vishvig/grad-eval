import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initializeApiService } from './services/api'

// Initialize API service with router instance for redirection
initializeApiService(router)

const app = createApp(App)
app.use(router)
app.mount('#app')

import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initializeAuth } from '@/stores/auth'

// Initialize auth before mounting app
initializeAuth().then(() => {
  const app = createApp(App)
  app.use(router)
  app.mount('#app')
})

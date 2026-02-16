import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Performance monitoring in production
if (import.meta.env.PROD) {
  app.config.performance = true
  app.config.errorHandler = (err) => {
    // Silent error handling in production
    if (import.meta.env.DEV) console.error(err)
  }
}

app.mount('#app')

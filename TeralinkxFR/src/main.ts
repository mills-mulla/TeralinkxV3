import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Vue3Toastify from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'
import App from './App.vue'
import router from './router'
// import './assets/main.css'
import './styles.css'
import store from './components/store'
import FontAwesomeIcon from './plugins/font-awesome'
import { useTheme } from './composables/useTheme'

// Import the enhanced HotSpot plugin
import hotspotPlugin from './plugins/hotspot'

const app = createApp(App)
const pinia = createPinia()

// Initialize theme before mounting
const { updateTheme } = useTheme()
updateTheme()

// Configure Toast
app.use(Vue3Toastify, {
  autoClose: 3000,
  position: 'top-right',
  theme: 'light'
})

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Install plugins with proper type safety
app.use(store)
app.use(pinia)
app.use(router)

// Install HotSpot plugin with initialization check
if (window.hotspotContext) {
  app.use(hotspotPlugin)
} else {
  // Initialize with fallback data if needed
  window.hotspotContext = {
    mac: '',
    ip: '',
    
  }
  app.use(hotspotPlugin)
}

// Initialize auth store after pinia is set up
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.initialize()

app.mount('#app')

// Type augmentation for TypeScript support
declare global {
  interface Window {
    hotspotContext?: {
      mac: string
      ip: string
      
    }
  }
}
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

// Import the enhanced HotSpot plugin
import hotspotPlugin from './plugins/hotspot'

const app = createApp(App)

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
app.use(createPinia())
app.use(router)

// Install HotSpot plugin with initialization check
if (window.hotspotContext) {
  app.use(hotspotPlugin)
  // console.log('Hotspot context check if available in main.ts page:',window.hotspotContext)
} else {
  console.warn('HotSpot data not detected - running in fallback mode')
  // Initialize with fallback data if needed
  window.hotspotContext = {
    mac: '',
    ip: '',
    
  }
  app.use(hotspotPlugin)
}

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
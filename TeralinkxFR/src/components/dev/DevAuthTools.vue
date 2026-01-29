<template>
  <div class="space-y-3 border border-gray-300 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-900/30">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
        </svg>
        <span class="text-xs font-mono text-gray-700 dark:text-gray-300">DEV TOOLS</span>
      </div>
      <button
        @click="expanded = !expanded"
        class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
      >
        <svg 
          class="w-4 h-4 transition-transform" 
          :class="{ 'rotate-180': expanded }" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div v-if="expanded" class="space-y-4">
      <!-- Quick Test Credentials -->
      <div class="space-y-2">
        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Test Credentials</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="(cred, index) in testCredentials"
            :key="index"
            @click="loadTestCredentials(cred)"
            class="text-xs px-3 py-2 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition text-left"
          >
            <div class="font-mono">{{ cred.phone }}</div>
            <div class="text-gray-500 dark:text-gray-400 text-xs">pass: {{ cred.password }}</div>
          </button>
        </div>
      </div>

      <!-- Authentication Tests -->
      <div class="space-y-2">
        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Auth Tests</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="$emit('test', 'success')"
            class="text-xs px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded transition flex items-center justify-center"
          >
            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Test Success
          </button>
          <button
            @click="$emit('test', 'error')"
            class="text-xs px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition flex items-center justify-center"
          >
            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            Test Error
          </button>
        </div>
      </div>

      <!-- Network Simulation -->
      <div class="space-y-2">
        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Network Simulation</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="simulateConnected"
            class="text-xs px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition"
          >
            Simulate Connected
          </button>
          <button
            @click="simulateDisconnected"
            class="text-xs px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded transition"
          >
            Simulate Disconnected
          </button>
        </div>
      </div>

      <!-- API Endpoints -->
      <div class="space-y-2">
        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">API Endpoints</label>
        <div class="space-y-1">
          <button
            v-for="endpoint in apiEndpoints"
            :key="endpoint.name"
            @click="testEndpoint(endpoint)"
            class="w-full text-xs px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition text-left flex items-center justify-between"
          >
            <span class="font-mono">{{ endpoint.name }}</span>
            <span class="text-gray-500 dark:text-gray-400">{{ endpoint.method }}</span>
          </button>
        </div>
      </div>

      <!-- Token Operations -->
      <div class="space-y-2">
        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Token Operations</label>
        <div class="grid grid-cols-3 gap-1">
          <button
            @click="inspectToken"
            class="text-xs px-2 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded transition"
          >
            Inspect
          </button>
          <button
            @click="copyToken"
            class="text-xs px-2 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded transition"
          >
            Copy
          </button>
          <button
            @click="clearTokens"
            class="text-xs px-2 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded transition"
          >
            Clear
          </button>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="space-y-2">
        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Quick Actions</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="clearLocalStorage"
            class="text-xs px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 text-white rounded transition"
          >
            Clear Storage
          </button>
          <button
            @click="showConsole"
            class="text-xs px-3 py-1.5 bg-gray-600 hover:bg-gray-700 text-white rounded transition flex items-center justify-center"
          >
            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            Console
          </button>
        </div>
      </div>

      <!-- Environment Info -->
      <div class="pt-2 border-t border-gray-300 dark:border-gray-700">
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div class="text-gray-600 dark:text-gray-400">Env:</div>
          <div class="font-mono text-gray-900 dark:text-gray-100">{{ envName }}</div>
          
          <div class="text-gray-600 dark:text-gray-400">API Base:</div>
          <div class="font-mono text-gray-900 dark:text-gray-100 truncate">{{ apiBaseUrl }}</div>
          
          <div class="text-gray-600 dark:text-gray-400">Version:</div>
          <div class="font-mono text-gray-900 dark:text-gray-100">{{ appVersion }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useDevStore } from '@/stores/dev'

const emit = defineEmits(['test'])

const { showSuccess, showError, showInfo } = useToast()
const authStore = useAuthStore()
const devStore = useDevStore()

const expanded = ref(true)

// Test data
const testCredentials = ref([
  { phone: '712345678', password: 'password123' },
  { phone: '723456789', password: 'password456' },
  { phone: '734567890', password: 'password789' },
  { phone: '745678901', password: 'password012' }
])

const apiEndpoints = ref([
  { name: '/api/client/', method: 'GET', action: 'health' },
  { name: '/api/network-info/', method: 'GET', action: 'network' },
  { name: '/api/session/validate/', method: 'POST', action: 'session' }
])

// Environment info
const envName = computed(() => import.meta.env.VITE_ENV_NAME || 'development')
const apiBaseUrl = computed(() => import.meta.env.VITE_API_BASE_URL || 'not-set')
const appVersion = computed(() => import.meta.env.VITE_APP_VERSION || '1.0.0-dev')

// Methods
const loadTestCredentials = (cred) => {
  emit('test', 'load', cred)
  showInfo(`Loaded: ${cred.phone}`)
}

const simulateConnected = () => {
  // This would interact with network store
  showInfo('Network connected (simulated)')
}

const simulateDisconnected = () => {
  showInfo('Network disconnected (simulated)')
}

const testEndpoint = async (endpoint) => {
  try {
    // TODO: Call the endpoint
    showInfo(`Testing ${endpoint.name}...`)
  } catch (error) {
    showError(`Test failed: ${error.message}`)
  }
}

const inspectToken = () => {
  if (authStore.token) {
    devStore.addLog('TOKEN', `Token: ${authStore.token.slice(0, 50)}...`)
    showInfo('Token logged to console')
  } else {
    showError('No token found')
  }
}

const copyToken = async () => {
  if (authStore.token) {
    try {
      await navigator.clipboard.writeText(authStore.token)
      showSuccess('Token copied to clipboard')
    } catch (err) {
      showError('Failed to copy token')
    }
  } else {
    showError('No token to copy')
  }
}

const clearTokens = () => {
  authStore.clearAuth()
  showSuccess('Tokens cleared')
}

const clearLocalStorage = () => {
  localStorage.clear()
  sessionStorage.clear()
  showSuccess('Local storage cleared')
}

const showConsole = () => {
  devStore.toggleConsole()
}
</script>
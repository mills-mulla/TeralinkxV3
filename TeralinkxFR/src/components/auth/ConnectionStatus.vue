<template>
  <div class="space-y-3">
    <!-- Connection Status Card -->
    <div 
      class="rounded-lg border p-4 transition-all duration-300"
      :class="{
        'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800': !isConnected,
        'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800': isConnected && connectionTested,
        'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800': isConnected && !connectionTested
      }"
    >
      <div class="flex items-center justify-between">
        <!-- Status Indicator -->
        <div class="flex items-center space-x-3">
          <!-- Status Icon -->
          <div class="relative">
            <div 
              class="w-3 h-3 rounded-full"
              :class="{
                'bg-yellow-500 animate-pulse': !isConnected,
                'bg-green-500': isConnected && connectionTested,
                'bg-blue-500': isConnected && !connectionTested
              }"
            ></div>
            <!-- Ping Animation -->
            <div 
              v-if="isConnected && connectionTested"
              class="absolute inset-0 rounded-full bg-green-500 animate-ping opacity-75"
            ></div>
          </div>

          <!-- Status Text -->
          <div>
            <h3 class="text-sm font-medium">
              <span v-if="!isConnected">Connecting to Network...</span>
              <span v-if="isConnected && !connectionTested">Connected to Network</span>
              <span v-if="isConnected && connectionTested">Network Ready</span>
            </h3>
            <p class="text-xs opacity-75 mt-0.5">
              <span v-if="!isConnected">Waiting for network information</span>
              <span v-if="isConnected && !connectionTested">Checking backend connection...</span>
              <span v-if="isConnected && connectionTested">Ready for authentication</span>
            </p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <!-- Test Button -->
          <button
            v-if="isConnected && !connectionTested"
            @click="testConnection"
            class="text-xs px-3 py-1 rounded transition-colors bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-800 dark:text-blue-300 dark:hover:bg-blue-700"
            :disabled="testing"
          >
            <span v-if="testing">Testing...</span>
            <span v-else>Test</span>
          </button>

          <!-- Details Button -->
          <button
            @click="showDetails = !showDetails"
            class="text-xs px-3 py-1 rounded transition-colors bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            {{ showDetails ? 'Hide' : 'Details' }}
          </button>
        </div>
      </div>

      <!-- Connection Details -->
      <div v-if="showDetails" class="mt-3 pt-3 border-t border-current border-opacity-20">
        <div class="grid grid-cols-2 gap-2 text-xs">
          <!-- IP Address -->
          <div class="text-gray-600 dark:text-gray-400">IP Address:</div>
          <div class="font-mono text-gray-900 dark:text-gray-100 truncate">
            {{ ip || 'Not detected' }}
            <button
              v-if="ip"
              @click="copyToClipboard(ip, 'IP address')"
              class="ml-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
              title="Copy IP"
            >
              📋
            </button>
          </div>

          <!-- MAC Address -->
          <div class="text-gray-600 dark:text-gray-400">MAC Address:</div>
          <div class="font-mono text-gray-900 dark:text-gray-100 truncate">
            {{ mac || 'Not detected' }}
            <button
              v-if="mac"
              @click="copyToClipboard(mac, 'MAC address')"
              class="ml-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
              title="Copy MAC"
            >
              📋
            </button>
          </div>

          <!-- Source -->
          <div class="text-gray-600 dark:text-gray-400">Detection Source:</div>
          <div class="flex items-center">
            <span class="font-mono text-gray-900 dark:text-gray-100">{{ formatSource(source) }}</span>
            <span
              v-if="source === 'mikrotik_hotspot'"
              class="ml-2 px-1.5 py-0.5 text-xs bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100 rounded"
            >
              Hotspot
            </span>
            <span
              v-if="source === 'simulated'"
              class="ml-2 px-1.5 py-0.5 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100 rounded"
            >
              Simulated
            </span>
          </div>

          <!-- Last Test -->
          <div v-if="lastTest" class="text-gray-600 dark:text-gray-400">Last Test:</div>
          <div v-if="lastTest" class="text-gray-900 dark:text-gray-100">
            {{ formatTime(lastTest) }}
          </div>
        </div>

        <!-- Dev Actions -->
        <div v-if="devMode" class="mt-3 pt-3 border-t border-current border-opacity-20">
          <div class="flex space-x-2">
            <button
              @click="simulateNetwork"
              class="flex-1 text-xs px-3 py-1.5 rounded transition-colors bg-yellow-100 text-yellow-800 hover:bg-yellow-200 dark:bg-yellow-800 dark:text-yellow-100 dark:hover:bg-yellow-700"
            >
              Simulate Network
            </button>
            <button
              @click="refreshDetection"
              class="flex-1 text-xs px-3 py-1.5 rounded transition-colors bg-blue-100 text-blue-800 hover:bg-blue-200 dark:bg-blue-800 dark:text-blue-100 dark:hover:bg-blue-700"
            >
              Refresh Detection
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Connection Steps -->
    <div class="flex items-center justify-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
      <div class="flex items-center space-x-1">
        <div 
          class="w-2 h-2 rounded-full"
          :class="{
            'bg-green-500': ip,
            'bg-gray-300 dark:bg-gray-600': !ip
          }"
        ></div>
        <span>IP Detected</span>
      </div>
      <div class="text-gray-300 dark:text-gray-600">→</div>
      <div class="flex items-center space-x-1">
        <div 
          class="w-2 h-2 rounded-full"
          :class="{
            'bg-green-500': mac,
            'bg-gray-300 dark:bg-gray-600': !mac
          }"
        ></div>
        <span>MAC Detected</span>
      </div>
      <div class="text-gray-300 dark:text-gray-600">→</div>
      <div class="flex items-center space-x-1">
        <div 
          class="w-2 h-2 rounded-full"
          :class="{
            'bg-green-500': connectionTested,
            'bg-gray-300 dark:bg-gray-600': !connectionTested
          }"
        ></div>
        <span>Backend Ready</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from '@/composables/useToast'
import { useDevStore } from '@/stores/dev'

const props = defineProps({
  ip: {
    type: String,
    default: ''
  },
  mac: {
    type: String,
    default: ''
  },
  source: {
    type: String,
    default: 'unknown'
  },
  isConnected: {
    type: Boolean,
    default: false
  },
  connectionTested: {
    type: Boolean,
    default: false
  },
  lastTest: {
    type: [String, Date, null],
    default: null
  }
})

const emit = defineEmits(['simulate', 'test'])

const { showSuccess, showError } = useToast()
const devStore = useDevStore()

const showDetails = ref(false)
const testing = ref(false)

const devMode = computed(() => devStore.showDevTools)

const formatSource = (source) => {
  const sources = {
    'mikrotik_hotspot': 'Mikrotik Hotspot',
    'webrtc_fallback': 'WebRTC Detection',
    'simulated': 'Simulated Data',
    'detection_failed': 'Detection Failed',
    'unknown': 'Unknown'
  }
  return sources[source] || source
}

const formatTime = (date) => {
  if (!date) return 'Never'
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const copyToClipboard = async (text, label) => {
  try {
    await navigator.clipboard.writeText(text)
    showSuccess(`${label} copied to clipboard`)
  } catch (err) {
    showError('Failed to copy to clipboard')
  }
}

const testConnection = async () => {
  testing.value = true
  try {
    await emit('test')
    showSuccess('Backend connection successful')
  } catch (error) {
    showError('Backend connection failed')
  } finally {
    testing.value = false
  }
}

const simulateNetwork = () => {
  emit('simulate')
  showSuccess('Network data simulated')
}

const refreshDetection = () => {
  window.location.reload()
}
</script>

<style scoped>
.animate-ping {
  animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
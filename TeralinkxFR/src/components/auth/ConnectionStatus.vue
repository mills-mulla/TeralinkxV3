<template>
  <div class="space-y-1">
    <div 
      class="rounded border p-1 transition-all duration-300"
      :class="{
        'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800': !isConnected,
        'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800': isConnected
      }"
    >
      <div class="flex items-center justify-center space-x-2">
        <div 
          class="w-1.5 h-1.5 rounded-full"
          :class="{
            'bg-yellow-500 animate-pulse': !isConnected,
            'bg-green-500': isConnected
          }"
        ></div>
        <h3 class="text-xs font-medium">
          <span v-if="!isConnected">Connecting...</span>
          <span v-if="isConnected">Ready</span>
        </h3>
      </div>
    </div>
    <div class="flex items-center justify-center space-x-2">
      <div 
        class="w-1 h-1 rounded-full"
        :class="{
          'bg-green-500': ip,
          'bg-gray-300 dark:bg-gray-600': !ip
        }"
      ></div>
      <div 
        class="w-1 h-1 rounded-full"
        :class="{
          'bg-green-500': mac,
          'bg-gray-300 dark:bg-gray-600': !mac
        }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from '@/composables/useToast'


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


const showDetails = ref(false)
const testing = ref(false)

const devMode = computed(() => false)

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
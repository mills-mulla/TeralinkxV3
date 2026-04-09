<template>
  <div class="space-y-1">
    <div 
      class="rounded border p-1 transition-all duration-300"
      :class="{
        'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800': !backendConnected,
        'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800': backendConnected
      }"
    >
      <div class="flex items-center justify-center space-x-2">
        <div 
          class="w-1.5 h-1.5 rounded-full"
          :class="{
            'bg-yellow-500 animate-pulse': !backendConnected,
            'bg-green-500': backendConnected
          }"
        ></div>
        <h3 class="text-xs font-medium">
          <span v-if="!backendConnected">Connecting...</span>
          <span v-if="backendConnected">Ready</span>
        </h3>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'

const backendConnected = ref(false)

const checkBackendHealth = async () => {
  try {
    const response = await api.get('/api/health/', { timeout: 5000 })
    
    if (response.status === 200) {
      backendConnected.value = true
    } else {
      backendConnected.value = false
    }
  } catch (error) {
    console.warn('Backend health check failed:', error)
    backendConnected.value = false
  }
}

onMounted(() => {
  checkBackendHealth()
})
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
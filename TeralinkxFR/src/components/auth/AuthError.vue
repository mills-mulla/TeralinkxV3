<template>
  <div 
    v-if="error"
    class="rounded-lg border p-4 transition-all duration-300 animate-fadeIn"
    :class="{
      'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800': errorSeverity === 'error',
      'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800': errorSeverity === 'warning',
      'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800': errorSeverity === 'info'
    }"
  >
    <div class="flex items-start space-x-3">
      <!-- Icon -->
      <div class="flex-shrink-0">
        <svg 
          class="w-5 h-5" 
          :class="{
            'text-red-600 dark:text-red-400': errorSeverity === 'error',
            'text-yellow-600 dark:text-yellow-400': errorSeverity === 'warning',
            'text-blue-600 dark:text-blue-400': errorSeverity === 'info'
          }" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            v-if="errorSeverity === 'error'" 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
          <path 
            v-if="errorSeverity === 'warning'" 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.284 16.5c-.77.833.192 2.5 1.732 2.5z"
          />
          <path 
            v-if="errorSeverity === 'info'" 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      <!-- Error Message -->
      <div class="flex-1 min-w-0">
        <p 
          class="text-sm font-medium"
          :class="{
            'text-red-800 dark:text-red-300': errorSeverity === 'error',
            'text-yellow-800 dark:text-yellow-300': errorSeverity === 'warning',
            'text-blue-800 dark:text-blue-300': errorSeverity === 'info'
          }"
        >
          {{ error }}
        </p>
        
        <!-- Action/Suggestion -->
        <p 
          v-if="suggestion" 
          class="text-xs mt-1"
          :class="{
            'text-red-600 dark:text-red-400': errorSeverity === 'error',
            'text-yellow-600 dark:text-yellow-400': errorSeverity === 'warning',
            'text-blue-600 dark:text-blue-400': errorSeverity === 'info'
          }"
        >
          {{ suggestion }}
        </p>
        
        <!-- Retry Button (for retryable errors) -->
        <button
          v-if="showRetry"
          @click="$emit('retry')"
          class="mt-2 text-xs px-3 py-1 rounded transition"
          :class="{
            'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-800 dark:text-red-300 dark:hover:bg-red-700': errorSeverity === 'error',
            'bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-800 dark:text-yellow-300 dark:hover:bg-yellow-700': errorSeverity === 'warning',
            'bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-800 dark:text-blue-300 dark:hover:bg-blue-700': errorSeverity === 'info'
          }"
        >
          Try Again
        </button>
      </div>

      <!-- Close Button -->
      <button
        v-if="showClose"
        @click="$emit('clear')"
        class="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        title="Dismiss"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- Auto-dismiss progress bar -->
    <div 
      v-if="autoDismiss && !manuallyClosed" 
      class="mt-2 h-0.5 bg-current opacity-20 rounded-full overflow-hidden"
    >
      <div 
        class="h-full bg-current transition-all duration-500 ease-linear"
        :style="{ width: `${dismissProgress}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  error: {
    type: String,
    default: ''
  },
  severity: {
    type: String,
    default: 'error', // 'error' | 'warning' | 'info'
    validator: (value) => ['error', 'warning', 'info'].includes(value)
  },
  suggestion: {
    type: String,
    default: ''
  },
  autoDismiss: {
    type: Boolean,
    default: true
  },
  dismissTime: {
    type: Number,
    default: 5000 // milliseconds
  },
  showClose: {
    type: Boolean,
    default: true
  },
  showRetry: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['clear', 'retry'])

const dismissProgress = ref(0)
const manuallyClosed = ref(false)
let dismissInterval = null

const errorSeverity = computed(() => props.severity)

// Auto-dismiss logic
const startAutoDismiss = () => {
  if (!props.autoDismiss || manuallyClosed.value) return
  
  const intervalTime = 50 // Update every 50ms for smooth animation
  const totalSteps = props.dismissTime / intervalTime
  const stepPercentage = 100 / totalSteps
  
  let steps = 0
  
  dismissInterval = setInterval(() => {
    steps++
    dismissProgress.value = steps * stepPercentage
    
    if (steps >= totalSteps) {
      clearInterval(dismissInterval)
      emit('clear')
    }
  }, intervalTime)
}

const stopAutoDismiss = () => {
  if (dismissInterval) {
    clearInterval(dismissInterval)
    dismissInterval = null
  }
}

const handleClose = () => {
  manuallyClosed.value = true
  stopAutoDismiss()
  emit('clear')
}

// Watch for error changes
watch(() => props.error, (newError, oldError) => {
  if (newError && !oldError) {
    // New error appeared
    dismissProgress.value = 0
    manuallyClosed.value = false
    startAutoDismiss()
  } else if (!newError && oldError) {
    // Error cleared
    stopAutoDismiss()
  }
})

// Lifecycle
onMounted(() => {
  if (props.error && props.autoDismiss) {
    startAutoDismiss()
  }
})

onUnmounted(() => {
  stopAutoDismiss()
})
</script>

<style scoped>
.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
<template>
  <div class="mt-1">
    <!-- Strength Indicator -->
    <div class="flex items-center space-x-1 mb-1">
      <div
        v-for="i in 4"
        :key="i"
        class="h-1 flex-1 rounded-full transition-all duration-300"
        :class="{
          'bg-red-500': strength < i,
          'bg-yellow-500': strength === i,
          'bg-green-500': strength > i,
          'bg-gray-200 dark:bg-gray-700': password.length === 0
        }"
      ></div>
    </div>
    
    <!-- Strength Text -->
    <p class="text-xs" :class="strengthClass">
      {{ strengthText }}
    </p>
    
    <!-- Requirements -->
    <ul v-if="password.length > 0" class="mt-2 space-y-1 text-xs">
      <li 
        v-for="req in requirements" 
        :key="req.text"
        class="flex items-center"
        :class="req.met ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'"
      >
        <svg 
          class="w-3 h-3 mr-1.5" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            v-if="req.met" 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="3" 
            d="M5 13l4 4L19 7"
          />
          <path 
            v-else 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
        {{ req.text }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  password: {
    type: String,
    default: ''
  }
})

// Calculate password strength
const strength = computed(() => {
  if (props.password.length === 0) return 0
  
  let score = 0
  
  // Length check
  if (props.password.length >= 8) score++
  if (props.password.length >= 12) score++
  
  // Complexity checks
  if (/[A-Z]/.test(props.password)) score++
  if (/[a-z]/.test(props.password)) score++
  if (/[0-9]/.test(props.password)) score++
  if (/[^A-Za-z0-9]/.test(props.password)) score++
  
  return Math.min(score, 4)
})

// Strength text and class
const strengthText = computed(() => {
  switch (strength.value) {
    case 0: return 'Enter a password'
    case 1: return 'Very weak'
    case 2: return 'Weak'
    case 3: return 'Good'
    case 4: return 'Strong'
    default: return ''
  }
})

const strengthClass = computed(() => {
  switch (strength.value) {
    case 0: return 'text-gray-500 dark:text-gray-400'
    case 1: return 'text-red-600 dark:text-red-400'
    case 2: return 'text-orange-600 dark:text-orange-400'
    case 3: return 'text-yellow-600 dark:text-yellow-400'
    case 4: return 'text-green-600 dark:text-green-400'
    default: return 'text-gray-500'
  }
})

// Password requirements
const requirements = computed(() => [
  {
    text: 'At least 8 characters',
    met: props.password.length >= 8
  },
  {
    text: 'Contains uppercase letter',
    met: /[A-Z]/.test(props.password)
  },
  {
    text: 'Contains lowercase letter',
    met: /[a-z]/.test(props.password)
  },
  {
    text: 'Contains number',
    met: /[0-9]/.test(props.password)
  },
  {
    text: 'Contains special character',
    met: /[^A-Za-z0-9]/.test(props.password)
  }
])
</script>
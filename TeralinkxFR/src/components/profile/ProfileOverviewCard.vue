<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <!-- Loading State -->
    <div v-if="loading" class="animate-pulse">
      <div class="flex flex-col items-center space-y-4">
        <div class="w-24 h-24 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
        <div class="space-y-2 text-center">
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-32"></div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-24"></div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="flex flex-col items-center space-y-4">
      <!-- Profile Image -->
      <div class="relative group">
        <div class="w-24 h-24 rounded-full overflow-hidden border-4 border-blue-500 shadow-lg">
          <img
            v-if="user.profileImage"
            :src="user.profileImage"
            :alt="user.displayName"
            class="w-full h-full object-cover"
          />
          <div
            v-else
            class="w-full h-full bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center"
          >
            <svg class="w-12 h-12 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
        </div>
        
        <!-- Upload Button -->
        <label class="absolute -bottom-2 -right-2 bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full cursor-pointer shadow-lg transition-colors group-hover:scale-110 transform duration-200">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <input
            type="file"
            accept="image/*"
            @change="handleFileSelect"
            class="hidden"
          />
        </label>
      </div>

      <!-- User Info -->
      <div class="text-center space-y-2">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">
          {{ user.displayName }}
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ user.phone }}
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-500">
          {{ user.accountNumber }}
        </p>
        
        <!-- Status Badge -->
        <span :class="statusClasses" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
          <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="statusDotClasses"></span>
          {{ user.status }}
        </span>
      </div>

      <!-- Quick Stats -->
      <div class="w-full pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-2 gap-4 text-center">
          <div>
            <p class="text-lg font-semibold text-gray-900 dark:text-white">
              KSh {{ formatCurrency(user.balance) }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">Balance</p>
          </div>
          <div>
            <p class="text-lg font-semibold text-gray-900 dark:text-white capitalize">
              {{ user.tier }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">Account Tier</p>
          </div>
        </div>
      </div>

      <!-- Member Since -->
      <div class="text-center pt-2">
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Member since {{ formatDate(user.createdAt) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['upload-image'])

const statusClasses = computed(() => {
  const status = props.user.status
  return {
    'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': status === 'active',
    'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': status === 'suspended',
    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400': status === 'pending'
  }
})

const statusDotClasses = computed(() => {
  const status = props.user.status
  return {
    'bg-green-500': status === 'active',
    'bg-red-500': status === 'suspended',
    'bg-yellow-500': status === 'pending'
  }
})

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    emit('upload-image', file)
    event.target.value = '' // Reset input
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long'
  })
}
</script>
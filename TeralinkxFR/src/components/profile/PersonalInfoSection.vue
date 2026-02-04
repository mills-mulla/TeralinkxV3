<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center space-x-3 mb-6">
      <div class="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
        <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Personal Information</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">Update your personal details</p>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Display Name -->
      <FormField
        label="Display Name"
        :value="localUser.displayName"
        @update="updateField('displayName', $event)"
        :loading="loading"
        placeholder="Enter your display name"
      />

      <!-- Email -->
      <FormField
        label="Email Address"
        type="email"
        :value="localUser.email"
        @update="updateField('email', $event)"
        :loading="loading"
        placeholder="Enter your email address"
      />

      <!-- Phone Number -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Phone Number
        </label>
        <div class="relative">
          <input
            :value="user.phone"
            type="tel"
            readonly
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
          />
          <div class="absolute inset-y-0 right-0 flex items-center pr-3">
            <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Phone number cannot be changed. Contact support if needed.
        </p>
      </div>

      <!-- Account Number -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Account Number
        </label>
        <input
          :value="user.accountNumber"
          type="text"
          readonly
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import FormField from '@/components/ui/FormField.vue'

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

const emit = defineEmits(['update'])

// Local state for form fields
const localUser = ref({
  displayName: props.user.displayName || '',
  email: props.user.email || ''
})

// Watch for prop changes
watch(() => props.user, (newUser) => {
  localUser.value.displayName = newUser.displayName || ''
  localUser.value.email = newUser.email || ''
}, { deep: true })

// Debounced update function
let updateTimeout = null
const updateField = (field, value) => {
  localUser.value[field] = value
  
  // Clear existing timeout
  if (updateTimeout) {
    clearTimeout(updateTimeout)
  }
  
  // Set new timeout for debounced update
  updateTimeout = setTimeout(() => {
    const apiField = field === 'displayName' ? 'display_name' : field
    emit('update', apiField, value)
  }, 1000)
}
</script>
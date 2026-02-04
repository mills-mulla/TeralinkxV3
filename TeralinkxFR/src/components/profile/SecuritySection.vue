<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center space-x-3 mb-6">
      <div class="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
        <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11H16V16H8V11H9.2V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.4,8.7 10.4,10V11H13.6V10C13.6,8.7 12.8,8.2 12,8.2Z"/>
        </svg>
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Security Settings</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">Manage your account security</p>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Password Change -->
      <div class="space-y-4">
        <h4 class="text-sm font-medium text-gray-900 dark:text-white">Change Password</h4>
        
        <div class="space-y-4">
          <div class="relative">
            <input
              v-model="passwordData.newPassword"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Enter new password"
              class="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              @click="showPassword = !showPassword"
              type="button"
              class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg v-if="showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
          </div>
          
          <div class="relative">
            <input
              v-model="passwordData.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="Confirm new password"
              class="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              @click="showConfirmPassword = !showConfirmPassword"
              type="button"
              class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg v-if="showConfirmPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
          </div>

          <!-- Password Strength Indicator -->
          <div v-if="passwordData.newPassword" class="space-y-2">
            <div class="flex items-center space-x-2">
              <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  :class="passwordStrengthColor"
                  class="h-2 rounded-full transition-all duration-300"
                  :style="{ width: passwordStrengthWidth }"
                ></div>
              </div>
              <span :class="passwordStrengthColor" class="text-xs font-medium">
                {{ passwordStrengthText }}
              </span>
            </div>
            <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <li :class="{ 'text-green-600 dark:text-green-400': passwordData.newPassword.length >= 8 }">
                ✓ At least 8 characters
              </li>
              <li :class="{ 'text-green-600 dark:text-green-400': /[A-Z]/.test(passwordData.newPassword) }">
                ✓ One uppercase letter
              </li>
              <li :class="{ 'text-green-600 dark:text-green-400': /[0-9]/.test(passwordData.newPassword) }">
                ✓ One number
              </li>
            </ul>
          </div>

          <button
            @click="updatePassword"
            :disabled="!canUpdatePassword || loading"
            class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors font-medium"
          >
            {{ loading ? 'Updating...' : 'Update Password' }}
          </button>
        </div>
      </div>

      <!-- Two-Factor Authentication -->
      <div class="pt-6 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M10,17L6,13L7.41,11.59L10,14.17L16.59,7.58L18,9L10,17Z"/>
              </svg>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-900 dark:text-white">Two-Factor Authentication</h4>
              <p class="text-xs text-gray-600 dark:text-gray-400">Add extra security to your account</p>
            </div>
          </div>
          
          <ToggleSwitch
            :enabled="user.twoFactorEnabled"
            @toggle="toggle2FA"
            :loading="loading"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ToggleSwitch from '@/components/ui/ToggleSwitch.vue'

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

// Password state
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const passwordData = ref({
  newPassword: '',
  confirmPassword: ''
})

// Password validation
const passwordStrength = computed(() => {
  const password = passwordData.value.newPassword
  let score = 0
  
  if (password.length >= 8) score++
  if (/[A-Z]/.test(password)) score++
  if (/[a-z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^A-Za-z0-9]/.test(password)) score++
  
  return score
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength < 2) return 'Weak'
  if (strength < 4) return 'Medium'
  return 'Strong'
})

const passwordStrengthColor = computed(() => {
  const strength = passwordStrength.value
  if (strength < 2) return 'text-red-600 bg-red-500'
  if (strength < 4) return 'text-yellow-600 bg-yellow-500'
  return 'text-green-600 bg-green-500'
})

const passwordStrengthWidth = computed(() => {
  return `${(passwordStrength.value / 5) * 100}%`
})

const canUpdatePassword = computed(() => {
  return passwordData.value.newPassword.length >= 8 &&
         passwordData.value.newPassword === passwordData.value.confirmPassword &&
         passwordStrength.value >= 3
})

// Methods
const updatePassword = () => {
  if (canUpdatePassword.value) {
    emit('update', 'password', passwordData.value.newPassword)
    passwordData.value.newPassword = ''
    passwordData.value.confirmPassword = ''
  }
}

const toggle2FA = () => {
  emit('update', 'two_factor_enabled', !props.user.twoFactorEnabled)
}
</script>
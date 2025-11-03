<template>
  <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
  <div class="max-w-3xl mx-auto p-4 pt-20">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Settings</h1>

    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md space-y-6">
      <!-- Theme Setting -->
      <div>
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Theme</h3>
        <div class="flex items-center space-x-4">
          <button
            @click="setTheme('light')"
            class="px-4 py-2 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
          >
            Light
          </button>
          <button
            @click="setTheme('dark')"
            class="px-4 py-2 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
          >
            Dark
          </button>
        </div>
      </div>

      <!-- Notifications Setting -->
      <div>
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Notifications</h3>
        <label class="inline-flex items-center space-x-2">
          <input
            type="checkbox"
            v-model="notificationsEnabled"
            class="form-checkbox h-5 w-5 text-green-600"
          />
          <span class="text-gray-700 dark:text-gray-300">Enable Notifications</span>
        </label>
      </div>

      <!-- Save Button -->
      <div>
        <button
          @click="saveSettings"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
        >
          Save Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NavBar from '@/components/NavBar.vue'

const notificationsEnabled = ref(true)

function setTheme(mode) {
  const root = document.documentElement
  if (mode === 'dark') {
    root.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    root.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

function saveSettings() {
  alert('Settings saved successfully!')
}
</script>

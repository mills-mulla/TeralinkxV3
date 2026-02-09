<template>
  <!-- App wrapper with Connected page gradient theme -->
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 text-gray-800 dark:text-white transition-all duration-300 flex flex-col" id="app">
    
    <NotificationHandler />
    <ToastContainer />
    
    <!-- Main content area -->
    <div class="flex-1">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import NotificationHandler from './components/NotificationHandler.vue'
import ToastContainer from './components/ToastContainer.vue'
import { useTheme } from './composables/useTheme'

// Initialize theme on app mount
const { updateTheme } = useTheme()

onMounted(() => {
  updateTheme()
})
</script>

<style>
#app {
  overflow-x: hidden;
}
</style>

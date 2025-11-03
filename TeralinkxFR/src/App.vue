<template>
  <!-- App wrapper with responsive dark/light background -->
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-white transition-colors duration-300" id="app">
    
    <NotificationHandler />
    <router-view />
  </div>
</template>

<script>
import NotificationHandler from './components/NotificationHandler.vue'


export default {
  name: 'App',
  components: {
    NotificationHandler,
    
  }
}
</script>

<style>
#app {
  overflow-x: hidden;
}
</style>

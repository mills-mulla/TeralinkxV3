<template>
  <footer class="w-full bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 text-gray-800 dark:text-white py-2 px-2 text-sm transition-colors duration-300 border-t border-blue-100 dark:border-gray-600">
    <div class="max-w-md mx-auto flex flex-col space-y-2 items-center text-center">
      
     

      <!-- Phone/whatsapp Contact -->
      <div class="flex text-2xs items-center space-x-2">
        <font-awesome-icon :icon="['fas', 'phone']" class="hover:text-blue-400 transition-colors duration-200" />
        <span>Call Us: 0113 209 751 / 0714 787 999</span>
        <font-awesome-icon :icon="['fab', 'whatsapp']" class="hover:text-green-500 transition-colors duration-200" />
        <span>0113 209 751</span>
      </div>

      <!-- Copyright -->
      <p class="text-gray-600 dark:text-gray-400 text-xs mt-2">
        &copy; {{ currentYear }}
        <span class="text-black dark:text-white font-medium">Teralinkx Waves</span>.
        All rights reserved.
      </p>
    </div>
  </footer>
</template>
<script>
export default {
  name: 'FooTr',
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
}
</script>
<style scoped>
footer svg {
  transition: color 0.3s ease;
}
footer svg:hover {
  color: #10b981; /* Tailwind green-500 */
}
</style>

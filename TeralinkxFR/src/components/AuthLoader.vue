<template>
  <div class="h-screen flex items-start justify-center pt-20 bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
    <div class="text-center">
      <!-- Logo -->
      <div class="mb-4">
        <img :src="logoSrc" alt="TeralinkX" class="h-80 w-auto mx-auto drop-shadow-2xl" />
      </div>
      
      <!-- Welcome Message -->
      <h1 class="text-2xl font-bold text-white mb-2 drop-shadow-lg">Welcome Back</h1>
      <p class="text-blue-100 dark:text-gray-300 mb-6 text-base">Checking your credentials...</p>
      
      <!-- Fancy Spinner -->
      <div class="flex justify-center">
        <div class="relative">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-transparent border-t-white border-r-white/50 shadow-lg"></div>
          <div class="absolute inset-0 animate-pulse rounded-full h-12 w-12 border-2 border-blue-300/30"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logoImage from '@/assets/teralinkx2.png'

const logoSrc = logoImage
</script>
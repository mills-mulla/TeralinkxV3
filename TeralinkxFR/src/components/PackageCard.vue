<template>
  <Loader v-if="isloading"/>
  <div class="sm:max-w-md md:max-w-lg lg:max-w-xl mx-auto p-4 font-sans dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300 rounded-md shadow-sm">
    <!-- Title -->
    <h2 class="text-center text-sm font-bold text-gray-800 dark:text-white mb-4">DATA PACKAGES</h2>

    <!-- Skeleton Loader -->
    <div v-if="packageStore.loading" class="grid grid-cols-2 gap-3 animate-pulse">
      <div v-for="n in 4" :key="n" class="bg-gray-200 dark:bg-gray-700 rounded-lg h-28"></div>
    </div>

    <!-- Grid layout -->
    <div v-else class="grid grid-cols-2 gap-3">
      <div
        v-for="(pkg, index) in packageStore.packages"
        :key="index"
        class="bg-white dark:bg-gray-800 p-2 rounded-lg shadow dark:shadow-gray-700 flex flex-col justify-between transition"
      >
        <!-- Title -->
        <div class="mb-1">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ pkg.package }}</h3>
        </div>

        <!-- Info -->
        <div class="flex flex-row justify-between">
          <p class="text-xs text-gray-700 dark:text-gray-300 mt-auto">{{ pkg.devices }}</p>
          <p class="text-xs text-gray-700 dark:text-gray-300 mt-auto hidden">{{ pkg.package_code }}</p>
          <p class="text-sm text-black dark:text-white font-bold mt-0">
            <span class="text-xs font-semibold">@KES</span> {{ pkg.price }}
          </p>
        </div>

        <!-- Buy Button -->
        <div class="mt-3">
          <button
            class="w-full bg-green-600 text-white text-sm font-bold py-2 rounded hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loadingId === pkg.id"
            @click="buy(pkg)"
          >
            {{ loadingId === pkg.id ? 'Processing...' : 'BUY' }}
          </button>
          <p v-if="errorMessage && loadingId === pkg.id" class="text-red-600 text-xs mt-1">{{ errorMessage }}</p>
        </div>

        <!-- Modal -->
        <BuyComponent
          v-if="showBuyComponent"
          @close="showBuyComponent = false"
          :packageDetails="selectedPackage"
        />
        
      </div>
    </div>

    
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import BuyComponent from './BuyComponent.vue'
import { usePackageStore } from '@/stores/usePackageStore'
import { useBuyPackage } from '@/composables/useBuyPackage'
import Loader from '@/views/Loader.vue'

const packageStore = usePackageStore()

const {
  buy,
  loadingId,
  errorMessage,
  showBuyComponent,
  selectedPackage,
  isloading
} = useBuyPackage()

onMounted(() => {
  packageStore.fetchPackages()
})
</script>

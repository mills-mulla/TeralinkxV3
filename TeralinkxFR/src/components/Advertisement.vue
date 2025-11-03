<template>
  <div class="w-full max-w-xs mx-auto py-2">
    <div class="relative overflow-hidden rounded-lg shadow-lg">
      <!-- Render ad only if available -->
      <img
        v-if="ads.length > 0"
        :src="ads[currentIndex].image"
        :alt="ads[currentIndex].alt"
        class="w-full h-40 object-contain transition-all duration-700 ease-in-out"
      />


      <!-- Caption -->
<div
  v-if="ads.length > 0"
  class="absolute bottom-2 left-1/2 -translate-x-1/2 transform bg-black/40 text-white px-2 py-0.5 rounded text-[10px]"
>
  {{ ads[currentIndex].caption }}
</div>


      <!-- Controls -->
      <div
        v-if="ads.length > 0"
        class="absolute bottom-0.5 left-1/2 transform -translate-x-1/2 flex space-x-1"
      >
        <button
          v-for="(ad, index) in ads"
          :key="index"
          @click="currentIndex = index"
          class="w-2 h-2 rounded-full border border-white"
          :class="{
            'bg-blue-600': index === currentIndex,
            'bg-white': index !== currentIndex
          }"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const ads = ref([])
const currentIndex = ref(0)
let intervalId = null

// Base domain for images from .env
const IMAGE_BASE_URL = import.meta.env.VITE_API_PROD_ADS_URL?.replace(/\/+$/, '')

async function fetchAds() {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/activeads/`, {
      headers: {
        Authorization: `Token ${localStorage.getItem('authToken')}`
      }
    })

    ads.value = response.data.map(ad => {
      let imagePath = ''
      try {
        const parsed = new URL(ad.image)
        imagePath = parsed.pathname + parsed.search // keep query if any
      } catch {
        imagePath = ad.image.startsWith('/') ? ad.image : '/' + ad.image
      }

      return {
        image: `${IMAGE_BASE_URL}${imagePath}`,
        alt: ad.title,
        caption: ad.caption
      }
    })

    // console.log("✅ Ads fetched successfully:", ads.value)
  } catch (err) {
    console.error("❌ Failed to fetch ads:", err)
  }
}

onMounted(async () => {
  await fetchAds()
  if (ads.value.length > 0) {
    intervalId = setInterval(() => {
      currentIndex.value = (currentIndex.value + 1) % ads.value.length
    }, 5000)
  }
})

onUnmounted(() => {
  clearInterval(intervalId)
})
</script>


<style scoped>
img {
  border-radius: 1rem;
}
</style>

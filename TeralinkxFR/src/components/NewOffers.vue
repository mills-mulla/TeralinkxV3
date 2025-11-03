<template>
  <div class="sm:max-w-md md:max-w-lg lg:max-w-xl px-2 mx-auto  dark:bg-gray-900 text-text-light dark:text-text-dark transition-colors duration-300">
    <h2 class="text-center text-sm font-bold text-gray-800 dark:text-white mb-4">OFFERS FOR YOU</h2>

    <!-- Skeleton Loader -->
    <div v-if="offerStore.loading" class="grid grid-cols-2 gap-3 animate-pulse">
      <div v-for="n in 4" :key="n" class="bg-gray-200 dark:bg-gray-800 rounded-lg h-28"></div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="text-red-500 text-sm text-center mb-2">
      {{ error }}
    </div>

    <!-- Offer Cards -->
    <div v-else class="grid grid-cols-2 gap-3">
      <div
        v-for="offer in offerStore.offers"
        :key="offer.id"
        class="relative bg-white dark:bg-gray-800 shadow-md dark:shadow-gray-700 rounded-lg px-4 py-2 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition duration-300 overflow-hidden"
      >
        <!-- Banner -->
        <div
          v-if="offer.banner"
          class="absolute top-0 left-0 w-full bg-gradient-to-r from-red-500 to-yellow-400 text-white text-[10px] font-bold text-center py-0.5 animate-pulse z-10 flex items-center justify-center space-x-1"
        >
          <span v-if="offer.banner === 'HOT'">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
              <path d="M13.763 2.5s1.187 1.902.73 3.99c-.34 1.522-1.422 2.375-1.826 3.563-.454 1.337-.132 3.238-.132 3.238s-.404-.624-.615-1.042c-.286-.57-.51-1.325-.686-2.27-.257-1.387.292-2.877.736-3.832.445-.955.793-1.498.793-1.498zM10 12.004c.413 1.332 1.316 2.73 2.375 3.324 1.445.796 2.53-.112 2.53-.112s.64 2.234-.587 3.847c-.846 1.143-2.356 1.599-3.655 1.074-1.236-.5-2.225-1.58-2.55-2.84-.375-1.448.087-2.992.887-4.133z" />
            </svg>
          </span>
          <span v-else-if="offer.banner === 'NEW'">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a1 1 0 01.894.553l2.382 4.823 5.322.774a1 1 0 01.554 1.706l-3.85 3.754.909 5.304a1 1 0 01-1.451 1.054L10 17.347l-4.76 2.5a1 1 0 01-1.451-1.054l.909-5.304-3.85-3.754a1 1 0 01.554-1.706l5.322-.774 2.382-4.823A1 1 0 0110 2z" />
            </svg>
          </span>
          <span>{{ offer.banner }}</span>
        </div>

        <!-- Offer Details -->
        <p class="font-semibold text-sm text-gray-800 dark:text-white mt-4">{{ offer.package }}</p>
        <p class="text-xs text-gray-600 dark:text-gray-300">{{ offer.devices }}</p>
        <p class="text-xs text-gray-600 dark:text-gray-300">{{ offer.limit }} remaining</p>
        <p class="text-sm text-black dark:text-gray-200 font-bold mb-2">
          <span class="text-xs text-gray-700 dark:text-gray-400 font-semibold">@KES</span> {{ offer.price }}
        </p>

        <!-- Buy Button -->
        <button
          v-if="offer.status === 'available'"
          @click="handleBuy(offer)"
          :disabled="loading"
          class="relative w-full inline-flex items-center justify-center text-white bg-blue-700 hover:bg-blue-800 px-3 py-1 text-xs rounded shadow-lg animate-pulse disabled:opacity-50 disabled:cursor-not-allowed
                before:absolute before:inset-0 before:rounded before:blur-md before:bg-blue-600 before:opacity-40 before:animate-ping before:z-[-1]"
        >
          <span v-if="loading">Processing...</span>
          <span v-else>Buy Now</span>
        </button>


        <!-- Sold Out -->
        <div
          v-if="offer.status === 'soldout'"
          class="absolute inset-0 bg-white dark:bg-black bg-opacity-20 dark:bg-opacity-30 flex flex-col justify-center items-center text-center p-2"
        >
          <span class="sold-out-stamp font-bold">SOLD OUT</span>
        </div>
      </div>

      <!-- Buy Modal -->
      <BuyComponent
        v-if="showBuyComponent"
        @close="showBuyComponent = false"
        :packageDetails="selectedPackage"
      />
      <Loader v-if="isloading"   />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useOfferStore } from '@/stores/useOfferStore'
import { useBuyOffer } from '@/composables/useBuyOffer'
import BuyComponent from './BuyComponent.vue'
import Loader from '@/views/Loader.vue'

const offerStore = useOfferStore()
const showBuyComponent = ref(false)
const selectedPackage = ref(null)

const { buyOffer, loading, error ,isloading } = useBuyOffer()

function openBuyComponent(offer) {
  selectedPackage.value = offer
  showBuyComponent.value = true
}

function handleBuy(offer) {
  if (!loading.value) {
    buyOffer(offer, openBuyComponent)
  }
}

onMounted(() => {
  offerStore.fetchOffers()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Wallpoet&display=swap');

@keyframes stampPop {
  0% {
    transform: scale(0.5) rotate(-30deg);
    opacity: 0;
  }
  100% {
    transform: scale(1) rotate(-30deg);
    opacity: 0.7;
  }
}

.sold-out-stamp {
  font-family: 'Wallpoet', sans-serif;
  position: absolute;
  top: 50px;
  left: 50%;
  transform: translateX(-50%) rotate(-30deg);
  color: #b91c1c;
  border: 2px solid #b91c1c;
  padding: 6px 12px;
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  opacity: 0.8;
  animation: stampPop 0.6s ease-out;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}
</style>

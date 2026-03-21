<template>
  <div class="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
      
      <!-- Header with Status -->
      <div class="bg-gradient-to-r from-blue-600 to-purple-600 p-4 text-white">
        <div class="flex items-center justify-center space-x-3">
          <div v-if="!showActionButtons" class="relative">
            <div class="w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
            <div class="absolute inset-0 w-8 h-8 border-4 border-blue-200 rounded-full animate-ping opacity-30"></div>
          </div>
          <div v-else class="w-8 h-8 flex items-center justify-center">
            <svg class="w-6 h-6 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="text-center">
            <h3 class="font-semibold text-lg">{{ statusTitle }}</h3>
            <p class="text-blue-100 text-sm">{{ statusMessage }}</p>
          </div>
        </div>
        
        <!-- Timer -->
        <div class="text-center mt-2 text-blue-100 text-xs">
          {{ formatTime(elapsedTime) }} elapsed
        </div>
      </div>

      <!-- Revenue Ad Space -->
      <div class="p-4 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-3">
          <span class="text-xs text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded-full">
            Sponsored
          </span>
          <div class="flex items-center space-x-2">
            <button 
              v-if="currentAd.type === 'audio' || currentAd.type === 'video'"
              @click="toggleMute"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <svg v-if="isMuted" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L4.828 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.828l3.555-3.793a1 1 0 011.617.793zM12 8a1 1 0 012 0v4a1 1 0 11-2 0V8z" clip-rule="evenodd" />
              </svg>
              <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L4.828 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.828l3.555-3.793a1 1 0 011.617.793zM12 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm4-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
            <span class="text-xs text-green-600 dark:text-green-400 font-medium">+KES {{ currentAd.revenue }}</span>
          </div>
        </div>
        
        <!-- Ad Container -->
        <div class="relative h-56 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 rounded-lg overflow-hidden">
          <TransitionGroup name="ad-slide" tag="div" class="relative h-full">
            <div
              v-for="(ad, index) in ads"
              :key="ad.id"
              v-show="currentAdIndex === index"
              class="absolute inset-0 cursor-pointer"
              @click="handleAdClick(ad)"
            >
              <!-- Video Ad -->
              <div v-if="ad.type === 'video'" class="w-full h-full relative">
                <video 
                  ref="videoPlayer"
                  :src="ad.video"
                  :muted="isMuted"
                  autoplay
                  loop
                  class="w-full h-full object-cover rounded-lg"
                  @loadeddata="trackAdView(ad)"
                  @error="handleAdError(ad)"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                <div class="absolute bottom-0 left-0 right-0 p-3">
                  <h4 class="text-white font-semibold text-sm mb-1">{{ ad.title }}</h4>
                  <p class="text-gray-200 text-xs">{{ ad.description }}</p>
                </div>
                <div class="absolute top-2 right-2 bg-red-600 text-white px-2 py-1 rounded text-xs font-bold">
                  LIVE
                </div>
              </div>
              
              <!-- Audio Ad -->
              <div v-else-if="ad.type === 'audio'" class="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-600 text-white relative">
                <audio 
                  ref="audioPlayer"
                  :src="ad.audio"
                  :muted="isMuted"
                  autoplay
                  loop
                  @loadeddata="trackAdView(ad)"
                  @error="handleAdError(ad)"
                ></audio>
                <div class="text-center p-4">
                  <div class="w-16 h-16 mx-auto mb-4 bg-white/20 rounded-full flex items-center justify-center">
                    <svg class="w-8 h-8 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L4.828 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.828l3.555-3.793a1 1 0 011.617.793zM12 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm4-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <h4 class="font-bold text-lg mb-2">{{ ad.title }}</h4>
                  <p class="text-sm opacity-90 mb-3">{{ ad.description }}</p>
                  <div class="flex justify-center space-x-1">
                    <div v-for="i in 5" :key="i" class="w-1 h-4 bg-white/60 rounded animate-pulse" :style="{ animationDelay: `${i * 0.1}s` }"></div>
                  </div>
                </div>
                <div class="absolute top-2 right-2 bg-purple-700 text-white px-2 py-1 rounded text-xs font-bold">
                  AUDIO
                </div>
              </div>
              
              <!-- Image Ad -->
              <div v-else-if="ad.type === 'image'" class="w-full h-full relative">
                <img 
                  :src="ad.image" 
                  :alt="ad.title"
                  class="w-full h-full object-cover rounded-lg"
                  @load="trackAdView(ad)"
                  @error="handleAdError(ad)"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                <div class="absolute bottom-0 left-0 right-0 p-3">
                  <h4 class="text-white font-semibold text-sm mb-1">{{ ad.title }}</h4>
                  <p class="text-gray-200 text-xs">{{ ad.description }}</p>
                </div>
              </div>
              
              <!-- Text Ad -->
              <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                <div class="text-center p-4">
                  <h4 class="font-bold text-lg mb-2">{{ ad.title }}</h4>
                  <p class="text-sm opacity-90 mb-4">{{ ad.description }}</p>
                  <button class="bg-white text-blue-600 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-100 transition-colors">
                    {{ ad.cta || 'Learn More' }}
                  </button>
                </div>
              </div>
            </div>
          </TransitionGroup>
          
          <!-- Ad Progress Bar -->
          <div class="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
            <div 
              class="h-full bg-white transition-all duration-1000 ease-linear"
              :style="{ width: `${adProgress}%` }"
            ></div>
          </div>
          
          <!-- Skip Ad Button (after 5 seconds) -->
          <button
            v-if="canSkipAd"
            @click="skipAd"
            class="absolute top-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-xs hover:bg-black/80 transition-colors"
          >
            Skip Ad
          </button>
        </div>
        
        <!-- Ad Controls -->
        <div class="flex justify-between items-center mt-3">
          <div class="flex space-x-1">
            <button
              v-for="(ad, index) in ads"
              :key="`dot-${ad.id}`"
              @click="switchToAd(index)"
              :class="[
                'w-2 h-2 rounded-full transition-colors',
                currentAdIndex === index ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
              ]"
            ></button>
          </div>
          <div class="text-xs text-gray-500 dark:text-gray-400">
            {{ currentAdIndex + 1 }} / {{ ads.length }}
          </div>
        </div>
      </div>

      <!-- Payment Info -->
      <div class="p-4 space-y-3">
        <div class="flex justify-between items-center text-sm">
          <span class="text-gray-600 dark:text-gray-400">Transaction ID:</span>
          <span class="font-mono text-gray-800 dark:text-white text-xs">{{ checkoutId || 'N/A' }}</span>
        </div>
        
        <div class="flex justify-between items-center text-sm">
          <span class="text-gray-600 dark:text-gray-400">Amount:</span>
          <span class="font-semibold text-gray-800 dark:text-white">KES {{ amount }}</span>
        </div>
        
        <!-- Tips -->
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
          <div class="flex items-start space-x-2">
            <svg class="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <div>
              <p class="text-xs font-medium text-blue-800 dark:text-blue-200">{{ currentTip.title }}</p>
              <p class="text-xs text-blue-600 dark:text-blue-300 mt-1">{{ currentTip.message }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons (show when timed out, failed, or refunded) -->
      <div v-if="showActionButtons" class="p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
        <!-- Refunded state: different CTA -->
        <div v-if="isRefunded" class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3 mb-3">
          <p class="text-xs text-amber-800 dark:text-amber-200 leading-relaxed">
            💰 Your account balance has been credited. You can use it to purchase any package.
          </p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="isRefunded ? buyWithBalance() : retryPayment()"
            class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors"
          >
            {{ isRefunded ? 'Buy with Balance' : 'Retry Payment' }}
          </button>
          <button
            @click="cancelPayment"
            class="flex-1 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 py-2 px-4 rounded-lg text-sm font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
      
      <!-- Cancel Button (show during processing) -->
      <div v-else class="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="cancelPayment"
          class="w-full bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 py-2 px-4 rounded-lg text-sm font-medium transition-colors"
        >
          Cancel Payment
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import { toast } from '@/composables/useCustomToast'

const props = defineProps({
  checkoutId: String,
  amount: [String, Number],
  phoneNumber: String
})

const emit = defineEmits(['success', 'error', 'cancel', 'retry', 'buyWithBalance'])

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()

// State
const polling = ref(null)
const elapsedTime = ref(0)
const timer = ref(null)
const currentAdIndex = ref(0)
const adTimer = ref(null)
const currentTipIndex = ref(0)
const tipTimer = ref(null)
const isMuted = ref(false)
const adProgress = ref(0)
const adProgressTimer = ref(null)
const canSkipAd = ref(false)
const adViewTime = ref(0)
const totalRevenue = ref(0)
const showActionButtons = ref(false)
const successShown = ref(false)
const isRefunded = ref(false)

// Status
const statusTitle = ref('Processing Payment')
const statusMessage = ref('Please complete payment on your phone...')

// Revenue-generating ads data (fetched from API)
const ads = ref([])
const adsLoaded = ref(false)

// Tips for users
const tips = ref([
  {
    title: 'Payment Tip',
    message: 'Check your phone for the M-Pesa prompt and enter your PIN.'
  },
  {
    title: 'Network Tip',
    message: 'Ensure you have good network coverage for faster processing.'
  },
  {
    title: 'Security Tip',
    message: 'Never share your M-Pesa PIN with anyone for security.'
  },
  {
    title: 'Speed Tip',
    message: 'Payment usually completes within 30-60 seconds.'
  }
])

const fetchAds = async () => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/ads/activeads/`, {
      headers: authStore.authHeaders
    })
    
    const data = await response.json()
    
    if (response.ok && data.success && data.ads.length > 0) {
      ads.value = data.ads.map(ad => ({
        id: ad.id,
        type: ad.type,
        title: ad.title,
        description: ad.description,
        cta: ad.cta,
        url: ad.url,
        revenue: ad.revenue,
        duration: ad.duration,
        video: ad.media.video,
        audio: ad.media.audio,
        image: ad.media.image,
        thumbnail: ad.media.thumbnail,
        brand: ad.brand
      }))
    } else {
      ads.value = getDefaultAds()
    }
    adsLoaded.value = true
  } catch (error) {
    console.error('Failed to fetch ads:', error)
    ads.value = getDefaultAds()
    adsLoaded.value = true
  }
}

const getDefaultAds = () => [
  {
    id: 'default-1',
    type: 'banner',
    title: 'Upgrade Your Internet',
    description: 'Get faster speeds with our premium packages',
    cta: 'View Packages',
    url: '/packages',
    revenue: 1.50,
    duration: 15
  }
]

const currentTip = computed(() => tips.value[currentTipIndex.value])
const currentAd = computed(() => ads.value[currentAdIndex.value] || {})
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleAdClick = (ad) => {
  trackAdInteraction(ad, 'click')
  totalRevenue.value += ad.revenue
  
  if (ad.url) {
    window.open(ad.url, '_blank')
  }
}

const toggleMute = () => {
  isMuted.value = !isMuted.value
  
  // Apply to current media
  const video = document.querySelector('video')
  const audio = document.querySelector('audio')
  
  if (video) video.muted = isMuted.value
  if (audio) audio.muted = isMuted.value
}

const trackAdView = (ad) => {
  trackAdInteraction(ad, 'view')
  totalRevenue.value += ad.revenue * 0.3 // 30% of click revenue for views
}

const skipAd = () => {
  nextAd()
}

const switchToAd = (index) => {
  currentAdIndex.value = index
  resetAdProgress()
}

const nextAd = () => {
  currentAdIndex.value = (currentAdIndex.value + 1) % ads.value.length
  resetAdProgress()
}

const resetAdProgress = () => {
  adProgress.value = 0
  adViewTime.value = 0
  canSkipAd.value = false
  
  clearInterval(adProgressTimer.value)
  startAdProgress()
}

const startAdProgress = () => {
  const duration = currentAd.value.duration || 15
  const interval = 100 // Update every 100ms
  
  adProgressTimer.value = setInterval(() => {
    adViewTime.value += interval / 1000
    adProgress.value = (adViewTime.value / duration) * 100
    
    // Allow skipping after 5 seconds
    if (adViewTime.value >= 5) {
      canSkipAd.value = true
    }
    
    // Auto advance when complete
    if (adProgress.value >= 100) {
      nextAd()
    }
  }, interval)
}

const handleAdError = (ad) => {
  console.warn('Ad failed to load:', ad)
}

const trackAdInteraction = async (ad, type) => {
  // Skip tracking for default ads
  if (typeof ad.id === 'string' && ad.id.startsWith('default-')) {
    console.log(`Skipping tracking for default ad: ${ad.id}`)
    return
  }
  
  try {
    await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/ads/track/`, {
      method: 'POST',
      headers: {
        ...authStore.authHeaders,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ad_id: ad.id,
        interaction_type: type
      })
    })
    console.log(`Ad ${type}: ${ad.title}`)
  } catch (error) {
    console.warn('Failed to track ad interaction:', error)
  }
}

const startPolling = () => {
  if (!props.checkoutId) {
    statusTitle.value = 'Payment Error'
    statusMessage.value = 'No checkout ID provided'
    showActionButtons.value = true
    return
  }

  const startTime = Date.now()
  const timeout = 60000 // 1 minute

  polling.value = setInterval(async () => {
    if (Date.now() - startTime >= timeout) {
      stopAllTimers()
      statusTitle.value = 'Payment Timed Out'
      statusMessage.value = 'The payment request has expired'
      showActionButtons.value = true
      toast.warning('Payment timed out. Please try again.')
      return
    }

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/payment-status/${props.checkoutId}/`,
        { headers: authStore.authHeaders }
      )

      const data = await response.json()
      const paymentStatus = data.payment?.payment_status || data.payment?.status
      const isTerminal = data.payment?.terminal === true

      // ── Completed ────────────────────────────────────────────────────────
      if (paymentStatus === 'completed' && !successShown.value) {
        successShown.value = true
        stopAllTimers()
        statusTitle.value = 'Payment Successful!'
        statusMessage.value = 'Your internet package is now active'
        toast.success('🎉 Payment completed! Your voucher is now active.')
        setTimeout(() => {
          emit('success', data)
          dashboardStore.fetchDashboardData()
        }, 2000)
        return
      }

      // ── Refunded (M-Pesa OK, voucher activation failed) ──────────────────
      if (paymentStatus === 'refunded') {
        stopAllTimers()
        isRefunded.value = true
        statusTitle.value = 'Activation Unsuccessful'
        statusMessage.value = 'Your balance has been credited'
        showActionButtons.value = true
        // Update store balance immediately from fresh server value
        const freshBalance = data.payment?.fresh_balance
        if (freshBalance !== null && freshBalance !== undefined) {
          dashboardStore.balance = freshBalance
        }
        toast.info(
          'Payment received but activation failed. Amount credited to your balance.',
          null,
          8000
        )
        return
      }

      // ── Hard payment failure (user cancelled, insufficient funds, etc.) ──
      if (paymentStatus === 'failed' || isTerminal) {
        stopAllTimers()
        statusTitle.value = 'Payment Failed'
        statusMessage.value = data.payment?.description || 'Please try again'
        showActionButtons.value = true
        toast.error(data.payment?.description || 'Payment failed. Please try again.')
        return
      }

      // ── Still in progress — keep polling ─────────────────────────────────
      // (pending / processing / no terminal flag)

    } catch (error) {
      console.error('Payment status check failed:', error)
    }
  }, 3000)
}

const startTimers = () => {
  // Elapsed time timer
  timer.value = setInterval(() => {
    elapsedTime.value++
  }, 1000)

  // Start ad progress tracking
  startAdProgress()
  
  // Track initial ad view
  trackAdView(ads.value[0])

  // Tip rotation timer
  tipTimer.value = setInterval(() => {
    currentTipIndex.value = (currentTipIndex.value + 1) % tips.value.length
  }, 6000) // Change tip every 6 seconds
}

const stopAllTimers = () => {
  clearInterval(polling.value)
  clearInterval(timer.value)
  clearInterval(adTimer.value)
  clearInterval(tipTimer.value)
  clearInterval(adProgressTimer.value)
  
  // Stop all media
  const videos = document.querySelectorAll('video')
  const audios = document.querySelectorAll('audio')
  
  videos.forEach(video => {
    video.pause()
    video.currentTime = 0
  })
  
  audios.forEach(audio => {
    audio.pause()
    audio.currentTime = 0
  })
}

const retryPayment = () => {
  showActionButtons.value = false
  successShown.value = false
  isRefunded.value = false
  statusTitle.value = 'Processing Payment'
  statusMessage.value = 'Please complete payment on your phone...'
  elapsedTime.value = 0
  startPolling()
  startTimers()
  toast.info('Retrying payment...')
}

const buyWithBalance = () => {
  stopAllTimers()
  emit('buyWithBalance')
}

const cancelPayment = () => {
  stopAllTimers()
  emit('cancel')
}

// Lifecycle
onMounted(async () => {
  await fetchAds()
  startPolling()
  startTimers()
  
  console.log(`Payment loader started. Loaded ${ads.value.length} ads`)
})

onBeforeUnmount(() => {
  stopAllTimers()
})
</script>

<style scoped>
.ad-slide-enter-active,
.ad-slide-leave-active {
  transition: all 0.5s ease-in-out;
}

.ad-slide-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.ad-slide-leave-to {
  opacity: 0;
  transform: translateX(-100%);
}
</style>
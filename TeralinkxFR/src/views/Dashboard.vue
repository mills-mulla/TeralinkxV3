<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 pt-16">
    <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
    
    <!-- Animated Dashboard Components -->
    <div class="space-y-4 animate-fade-in">
      <div class="transform transition-all duration-500 animate-slide-in-up" style="animation-delay: 0.1s">
        <AccountCard/>
      </div>
      
      <div class="transform transition-all duration-500 animate-slide-in-up" style="animation-delay: 0.2s">
        <Advertisement />
      </div>
      
      <div class="transform transition-all duration-500 animate-slide-in-up" style="animation-delay: 0.3s">
        <VoucherCard @openRenewModal="openRenewModal"/>
      </div>
      
      <div class="transform transition-all duration-500 animate-slide-in-up mb-8" style="animation-delay: 0.4s">
        <PackagesSection @openPaymentModal="openPaymentModal" @openBuyModal="openBuyModal"/>
      </div>
    </div>
   
    <!-- <fooTr/> -->
    <WelcomeMessage v-if="isNewU" @close="isNewU = false"/>
  </div>
  
  <!-- Payment Modals - Outside main container -->
  <PaymentOptionsModal
    v-if="showPaymentModal"
    @close="showPaymentModal = false"
    @paymentSelected="handlePaymentSelected"
    :packageDetails="selectedPackage"
  />
  
  <BuyComponent
    v-if="showBuyComponent"
    @close="showBuyComponent = false"
    :packageDetails="selectedPackage"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useDashboardStore } from '../stores/dashboard'
import { useToast } from '../composables/useToast'

// Components
import fooTr from '../components/Footer.vue' 
import WelcomeMessage from '../components/New.vue'
import NavBar from '../components/NavBar.vue'
import AccountCard from '@/components/AccountCard.vue'
import Advertisement from '@/components/Advertisement.vue'
import VoucherCard from '@/components/VoucherCard.vue'
import PackagesSection from '@/components/PackagesSection.vue'
import PaymentOptionsModal from '@/components/PaymentOptionsModal.vue'
import BuyComponent from '@/components/BuyComponent.vue'

// Stores and composables
const router = useRouter()
const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const { showError } = useToast()

// State
const isNewU = ref(false)
const showPaymentModal = ref(false)
const showBuyComponent = ref(false)
const selectedPackage = ref(null)

// Check authentication and load dashboard data
onMounted(async () => {
  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    router.push({ name: 'home' })
    return
  }

  // Check for new user flag
  isNewU.value = localStorage.getItem('isNewUser') === 'true'
  localStorage.removeItem('isNewUser')

  // Load dashboard data
  try {
    await dashboardStore.fetchDashboardData()
  } catch (error) {
    showError('Failed to load dashboard data')
    console.error('Dashboard load error:', error)
  }
})

// Modal handlers
const handlePaymentSelected = (paymentInfo) => {
  showPaymentModal.value = false
  
  if (paymentInfo.method === 'credit') {
    // Credit payment is handled directly in PaymentOptionsModal
    return
  }
  
  // For M-Pesa and mixed payments, open BuyComponent
  selectedPackage.value = {
    ...paymentInfo.packageDetails,
    paymentData: paymentInfo.paymentData || null
  }
  
  // Set the useCredit flag based on payment method
  selectedPackage.value.defaultUseCredit = paymentInfo.useCredit
  
  showBuyComponent.value = true
}

// Provide modal functions to child components
const openPaymentModal = (pkg) => {
  selectedPackage.value = pkg
  showPaymentModal.value = true
}

const openBuyModal = (pkg) => {
  selectedPackage.value = pkg
  showBuyComponent.value = true
}

// Handle renewal from VoucherCard
const openRenewModal = (packageDetails) => {
  selectedPackage.value = packageDetails
  showBuyComponent.value = true
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slide-in-up {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}

.animate-slide-in-up {
  animation: slide-in-up 0.6s ease-out;
  animation-fill-mode: both;
}
</style>

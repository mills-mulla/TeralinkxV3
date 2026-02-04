<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800 pt-16">
    <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
    
    <div class="sm:max-w-md md:max-w-lg lg:max-w-4xl mx-auto px-4 mt-4 mb-8">
      <!-- Page Header -->
      <header class="mb-8 transform transition-all duration-500 animate-fade-in">
        <div class="flex items-center space-x-3 mb-2">
          <div class="p-2 bg-orange-500 rounded-lg transition-all duration-300 hover:bg-orange-600 hover:scale-110 hover:rotate-3">
            <svg class="w-6 h-6 text-white transition-transform duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,17A1.5,1.5 0 0,1 10.5,15.5A1.5,1.5 0 0,1 12,14A1.5,1.5 0 0,1 13.5,15.5A1.5,1.5 0 0,1 12,17M12,10.5C12.8,10.5 13.5,9.8 13.5,9C13.5,8.2 12.8,7.5 12,7.5C11.2,7.5 10.5,8.2 10.5,9C10.5,9.8 11.2,10.5 12,10.5Z"/>
            </svg>
          </div>
          <div class="transition-all duration-300 hover:translate-x-1">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Frequently Asked Questions</h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Find answers to common questions</p>
          </div>
        </div>
      </header>

      <!-- Search Bar -->
      <div class="mb-6">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search FAQs..."
            class="w-full px-4 py-3 pl-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 transition-all duration-300"
          />
          <svg class="absolute left-3 top-3.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
      </div>

      <!-- FAQ Categories -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Category Navigation -->
        <div class="lg:col-span-1">
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sticky top-20">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Categories</h3>
            <nav class="space-y-2">
              <button
                v-for="category in faqCategories"
                :key="category.id"
                @click="activeCategory = category.id"
                :class="[
                  'w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-all duration-200 text-sm',
                  activeCategory === category.id
                    ? 'bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 border border-orange-200 dark:border-orange-800'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
              >
                <span class="font-medium">{{ category.name }}</span>
                <span class="text-xs bg-gray-200 dark:bg-gray-600 px-2 py-1 rounded-full">{{ category.count }}</span>
              </button>
            </nav>
          </div>
        </div>

        <!-- FAQ Content -->
        <div class="lg:col-span-3">
          <div class="space-y-4">
            <div
              v-for="faq in filteredFAQs"
              :key="faq.id"
              class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <button
                @click="toggleFAQ(faq.id)"
                class="w-full px-6 py-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
              >
                <div class="flex items-center justify-between">
                  <h3 class="font-medium text-gray-900 dark:text-white pr-4">{{ faq.question }}</h3>
                  <svg
                    :class="[
                      'w-5 h-5 text-gray-500 transition-transform duration-200',
                      faq.isOpen ? 'rotate-180' : ''
                    ]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </div>
              </button>
              
              <Transition
                enter-active-class="transition-all duration-300 ease-out"
                enter-from-class="opacity-0 max-h-0"
                enter-to-class="opacity-100 max-h-96"
                leave-active-class="transition-all duration-200 ease-in"
                leave-from-class="opacity-100 max-h-96"
                leave-to-class="opacity-0 max-h-0"
              >
                <div v-if="faq.isOpen" class="px-6 pb-4">
                  <div class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed" v-html="faq.answer"></div>
                </div>
              </Transition>
            </div>

            <!-- No Results -->
            <div v-if="filteredFAQs.length === 0" class="text-center py-8">
              <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 20a7.962 7.962 0 01-5-1.709M15 11V9a6 6 0 00-12 0v2"/>
              </svg>
              <p class="text-gray-500 dark:text-gray-400">No FAQs found matching your search.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Support -->
      <div class="mt-8 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl p-6 border border-orange-200 dark:border-orange-800">
        <div class="flex items-center space-x-3 mb-3">
          <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z"/>
          </svg>
          <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-200">Still Need Help?</h3>
        </div>
        <p class="text-orange-800 dark:text-orange-300 mb-4">Can't find what you're looking for? Our support team is here to help!</p>
        <button class="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium transition-all duration-300 hover:scale-105">
          Contact Support
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import NavBar from '@/components/NavBar.vue'

const searchQuery = ref('')
const activeCategory = ref('all')

const faqCategories = [
  { id: 'all', name: 'All Questions', count: 15 },
  { id: 'account', name: 'Account & Billing', count: 5 },
  { id: 'technical', name: 'Technical Issues', count: 4 },
  { id: 'packages', name: 'Packages & Data', count: 3 },
  { id: 'devices', name: 'Device Management', count: 3 }
]

const faqs = ref([
  {
    id: 1,
    category: 'account',
    question: 'How do I create a new account?',
    answer: 'To create a new account, visit our registration page and provide your phone number. You\'ll receive an SMS with a verification code. Enter the code to complete your registration.',
    isOpen: false
  },
  {
    id: 2,
    category: 'account',
    question: 'How can I check my account balance?',
    answer: 'You can check your account balance by logging into your dashboard. Your current balance is displayed prominently on the main page, along with your data usage statistics.',
    isOpen: false
  },
  {
    id: 3,
    category: 'technical',
    question: 'Why is my internet connection slow?',
    answer: 'Slow internet can be caused by several factors:<br>• High network traffic during peak hours<br>• Multiple devices connected to your account<br>• Reaching your data limit (speed may be throttled)<br>• Distance from the access point<br><br>Try disconnecting unused devices or contact support for assistance.',
    isOpen: false
  },
  {
    id: 4,
    category: 'packages',
    question: 'What data packages are available?',
    answer: 'We offer various data packages to suit different needs:<br>• Daily packages (1GB-5GB)<br>• Weekly packages (5GB-20GB)<br>• Monthly packages (20GB-100GB)<br>• Unlimited packages<br><br>Visit the "Buy" section to see current packages and pricing.',
    isOpen: false
  },
  {
    id: 5,
    category: 'devices',
    question: 'How many devices can I connect?',
    answer: 'The number of devices you can connect depends on your package:<br>• Basic packages: 2-3 devices<br>• Standard packages: 4-5 devices<br>• Premium packages: 6-10 devices<br>• Unlimited packages: Up to 15 devices',
    isOpen: false
  },
  {
    id: 6,
    category: 'technical',
    question: 'I can\'t connect to the internet. What should I do?',
    answer: 'If you can\'t connect, try these steps:<br>1. Check if your voucher is still active<br>2. Verify you haven\'t exceeded device limits<br>3. Clear your browser cache and cookies<br>4. Try a different browser or device<br>5. Restart your network connection<br><br>If the problem persists, contact our support team.',
    isOpen: false
  },
  {
    id: 7,
    category: 'account',
    question: 'How do I change my password?',
    answer: 'To change your password:<br>1. Go to Settings > Security Settings<br>2. Enter your new password<br>3. Click "Update Password"<br><br>For security, we recommend using a strong password with a mix of letters, numbers, and symbols.',
    isOpen: false
  },
  {
    id: 8,
    category: 'packages',
    question: 'Do data packages expire?',
    answer: 'Yes, all data packages have expiration dates:<br>• Daily packages: 24 hours<br>• Weekly packages: 7 days<br>• Monthly packages: 30 days<br><br>Unused data expires at the end of the validity period and cannot be carried forward.',
    isOpen: false
  },
  {
    id: 9,
    category: 'devices',
    question: 'How do I disconnect a device?',
    answer: 'To disconnect a device:<br>1. Go to your Profile page<br>2. Scroll to "Connected Devices"<br>3. Find the device you want to disconnect<br>4. Click the menu button (three dots)<br>5. Select "Disconnect Device"<br><br>The device will be immediately disconnected from the network.',
    isOpen: false
  },
  {
    id: 10,
    category: 'technical',
    question: 'What browsers are supported?',
    answer: 'TeralinkX works with all modern browsers:<br>• Chrome (recommended)<br>• Firefox<br>• Safari<br>• Microsoft Edge<br>• Opera<br><br>For the best experience, keep your browser updated to the latest version.',
    isOpen: false
  },
  {
    id: 11,
    category: 'account',
    question: 'How do I enable two-factor authentication?',
    answer: 'To enable 2FA:<br>1. Go to Settings > Security Settings<br>2. Find "Two-Factor Authentication"<br>3. Toggle the switch to enable<br>4. Follow the setup instructions<br><br>2FA adds an extra layer of security to your account.',
    isOpen: false
  },
  {
    id: 12,
    category: 'packages',
    question: 'Can I upgrade my package mid-cycle?',
    answer: 'Yes, you can purchase additional packages at any time. The new package will be added to your account and can be used immediately. Multiple active packages can run simultaneously.',
    isOpen: false
  },
  {
    id: 13,
    category: 'devices',
    question: 'Why was my device blocked?',
    answer: 'Devices may be blocked for several reasons:<br>• Suspicious activity detected<br>• Violation of terms of service<br>• Security concerns<br>• Manual blocking by account owner<br><br>Contact support if you believe your device was blocked in error.',
    isOpen: false
  },
  {
    id: 14,
    category: 'technical',
    question: 'How do I check my data usage?',
    answer: 'You can monitor your data usage in several ways:<br>• Dashboard shows real-time usage<br>• Profile page displays detailed statistics<br>• Voucher section shows per-voucher usage<br>• Enable usage alerts in Settings<br><br>Usage is updated every few minutes.',
    isOpen: false
  },
  {
    id: 15,
    category: 'account',
    question: 'How do I contact customer support?',
    answer: 'You can reach our support team through:<br>• Live chat (available 24/7)<br>• Email: support@teralinkx.com<br>• Phone: +254 XXX XXX XXX<br>• WhatsApp: +254 XXX XXX XXX<br><br>For faster service, have your account number ready when contacting us.',
    isOpen: false
  }
])

const filteredFAQs = computed(() => {
  let filtered = faqs.value

  // Filter by category
  if (activeCategory.value !== 'all') {
    filtered = filtered.filter(faq => faq.category === activeCategory.value)
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(faq => 
      faq.question.toLowerCase().includes(query) || 
      faq.answer.toLowerCase().includes(query)
    )
  }

  return filtered
})

const toggleFAQ = (id) => {
  const faq = faqs.value.find(f => f.id === id)
  if (faq) {
    faq.isOpen = !faq.isOpen
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>
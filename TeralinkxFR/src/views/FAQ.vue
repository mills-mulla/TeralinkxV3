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

    <fooTr />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import NavBar from '@/components/NavBar.vue'
import fooTr from '@/components/Footer.vue'

const searchQuery = ref('')
const activeCategory = ref('all')

const faqCategories = [
  { id: 'all', name: 'All Questions', count: 35 },
  { id: 'account', name: 'Account & Billing', count: 8 },
  { id: 'technical', name: 'Technical Issues', count: 9 },
  { id: 'packages', name: 'Packages & Data', count: 7 },
  { id: 'devices', name: 'Device Management', count: 6 },
  { id: 'security', name: 'Security & Privacy', count: 5 }
]

const faqs = ref([
  // Account & Billing
  {
    id: 1,
    category: 'account',
    question: 'How do I create a new account?',
    answer: 'To create a new account:<br>1. Connect to Teralinkx WiFi hotspot<br>2. Open your browser and enter your phone number<br>3. Verify your number via SMS code<br>4. Complete your profile setup<br><br>Your account is created instantly and you can start purchasing packages immediately.',
    isOpen: false
  },
  {
    id: 2,
    category: 'account',
    question: 'How can I check my account balance?',
    answer: 'You can check your account balance by:<br>• Logging into your dashboard - balance is displayed prominently<br>• Viewing the Account Card on the main page<br>• Checking the Profile section for detailed balance history<br>• Receiving SMS notifications when balance is low',
    isOpen: false
  },
  {
    id: 3,
    category: 'account',
    question: 'What payment methods do you accept?',
    answer: 'We accept multiple payment methods:<br>• M-Pesa (Safaricom)<br>• Airtel Money<br>• Account Credit Balance<br>• Bank Cards (Visa, Mastercard)<br>• PayPal<br><br>All payments are processed securely through encrypted channels.',
    isOpen: false
  },
  {
    id: 4,
    category: 'account',
    question: 'How do I add credit to my account?',
    answer: 'To add credit:<br>1. Go to Dashboard > Buy Packages<br>2. Select "Add Credit" option<br>3. Enter amount (minimum KSh 50)<br>4. Choose payment method<br>5. Complete payment<br><br>Credit is added instantly and can be used for any package purchase.',
    isOpen: false
  },
  {
    id: 5,
    category: 'account',
    question: 'Can I get a refund for unused data?',
    answer: 'Refund eligibility depends on several factors:<br>• Unused packages (80%+ data remaining): Eligible within 7 days<br>• Service issues: Full refund if service unavailable for 12+ hours<br>• Billing errors: Immediate refund<br>• Expired packages: Not eligible<br><br>Contact support with your request and we\'ll review your case.',
    isOpen: false
  },
  {
    id: 6,
    category: 'account',
    question: 'How do I view my transaction history?',
    answer: 'Access your transaction history:<br>1. Go to Profile page<br>2. Scroll to "Transaction History" section<br>3. Filter by date range or transaction type<br>4. Export to PDF or CSV for records<br><br>All transactions are stored for 12 months.',
    isOpen: false
  },
  {
    id: 7,
    category: 'account',
    question: 'Can I transfer credit to another account?',
    answer: 'Yes! Credit transfers are available:<br>• Minimum transfer: KSh 50<br>• Maximum per day: KSh 5,000<br>• Transfer fee: 2% of amount<br>• Instant processing<br><br>Go to Dashboard > Transfer Credit and enter recipient\'s phone number.',
    isOpen: false
  },
  {
    id: 8,
    category: 'account',
    question: 'What happens if my account is suspended?',
    answer: 'Account suspension reasons:<br>• Policy violations<br>• Payment disputes<br>• Suspicious activity<br>• Terms of service breach<br><br>Contact support immediately to resolve. Most suspensions are temporary and can be lifted after verification.',
    isOpen: false
  },

  // Technical Issues
  {
    id: 9,
    category: 'technical',
    question: 'Why is my internet connection slow?',
    answer: 'Slow internet can be caused by:<br>• <strong>Network congestion:</strong> Peak hours (6-10 PM) may have slower speeds<br>• <strong>Multiple devices:</strong> Too many connected devices sharing bandwidth<br>• <strong>Data limit:</strong> Speed throttled after reaching package limit<br>• <strong>Distance:</strong> Too far from access point<br>• <strong>Device issues:</strong> Outdated software or hardware<br><br>Try disconnecting unused devices, moving closer to the access point, or upgrading your package.',
    isOpen: false
  },
  {
    id: 10,
    category: 'technical',
    question: 'I can\'t connect to the internet. What should I do?',
    answer: 'Troubleshooting steps:<br>1. <strong>Check voucher status:</strong> Ensure it\'s active and not expired<br>2. <strong>Verify device limit:</strong> You may have reached maximum devices<br>3. <strong>Clear cache:</strong> Clear browser cache and cookies<br>4. <strong>Try different browser:</strong> Use Chrome, Firefox, or Safari<br>5. <strong>Restart connection:</strong> Disconnect and reconnect to WiFi<br>6. <strong>Check balance:</strong> Ensure you have active data<br><br>If problem persists, contact support with error details.',
    isOpen: false
  },
  {
    id: 11,
    category: 'technical',
    question: 'What browsers are supported?',
    answer: 'TeralinkX works with all modern browsers:<br>• <strong>Chrome</strong> (recommended) - Version 90+<br>• <strong>Firefox</strong> - Version 88+<br>• <strong>Safari</strong> - Version 14+<br>• <strong>Microsoft Edge</strong> - Version 90+<br>• <strong>Opera</strong> - Version 76+<br><br>For best experience, keep your browser updated. Mobile browsers are fully supported.',
    isOpen: false
  },
  {
    id: 12,
    category: 'technical',
    question: 'How do I check my data usage?',
    answer: 'Monitor your data usage:<br>• <strong>Dashboard:</strong> Real-time usage displayed on main page<br>• <strong>Profile:</strong> Detailed statistics (daily, weekly, monthly)<br>• <strong>Voucher section:</strong> Per-voucher usage breakdown<br>• <strong>SMS alerts:</strong> Enable in Settings for usage notifications<br>• <strong>Mobile app:</strong> Track usage on the go<br><br>Usage updates every 5 minutes.',
    isOpen: false
  },
  {
    id: 13,
    category: 'technical',
    question: 'Why do I keep getting disconnected?',
    answer: 'Frequent disconnections may be due to:<br>• <strong>Weak signal:</strong> Move closer to access point<br>• <strong>Network switching:</strong> Disable auto-connect to other networks<br>• <strong>Session timeout:</strong> Inactive for 30+ minutes<br>• <strong>Device sleep mode:</strong> Adjust power settings<br>• <strong>VPN conflicts:</strong> Disable VPN temporarily<br><br>Enable "Keep me connected" in settings to maintain session.',
    isOpen: false
  },
  {
    id: 14,
    category: 'technical',
    question: 'Can I use a VPN with TeralinkX?',
    answer: 'Yes, VPNs are allowed:<br>• Most VPN services work seamlessly<br>• May slightly reduce connection speed<br>• Recommended for enhanced privacy<br>• Some VPNs may require initial connection without VPN<br><br>Popular VPNs tested: NordVPN, ExpressVPN, ProtonVPN, Surfshark.',
    isOpen: false
  },
  {
    id: 15,
    category: 'technical',
    question: 'What ports are blocked?',
    answer: 'For security and network stability:<br>• <strong>Blocked:</strong> Port 25 (SMTP), Port 445 (SMB)<br>• <strong>Restricted:</strong> Torrent ports during peak hours<br>• <strong>Open:</strong> HTTP (80), HTTPS (443), FTP (21), SSH (22)<br>• <strong>Gaming ports:</strong> Fully open and optimized<br><br>Business packages have unrestricted port access.',
    isOpen: false
  },
  {
    id: 16,
    category: 'technical',
    question: 'How do I improve my connection speed?',
    answer: 'Speed optimization tips:<br>• Use 5GHz WiFi band if available<br>• Position device closer to router<br>• Close bandwidth-heavy applications<br>• Update device network drivers<br>• Use Ethernet cable for best performance<br>• Upgrade to higher-tier package<br>• Schedule large downloads during off-peak hours',
    isOpen: false
  },
  {
    id: 17,
    category: 'technical',
    question: 'Does weather affect my connection?',
    answer: 'Weather impact on connection:<br>• <strong>Rain:</strong> Minimal impact on fiber connections<br>• <strong>Heavy storms:</strong> May cause temporary disruptions<br>• <strong>Lightning:</strong> Equipment protection in place<br>• <strong>Extreme heat:</strong> Rare equipment overheating<br><br>Our infrastructure is weather-resistant. Outages are rare and quickly resolved.',
    isOpen: false
  },

  // Packages & Data
  {
    id: 18,
    category: 'packages',
    question: 'What data packages are available?',
    answer: 'We offer flexible packages:<br><strong>Daily Packages:</strong><br>• 1GB - KSh 50 (24 hours)<br>• 3GB - KSh 120 (24 hours)<br>• 5GB - KSh 180 (24 hours)<br><br><strong>Weekly Packages:</strong><br>• 10GB - KSh 350 (7 days)<br>• 20GB - KSh 650 (7 days)<br><br><strong>Monthly Packages:</strong><br>• 50GB - KSh 1,500 (30 days)<br>• 100GB - KSh 2,800 (30 days)<br>• Unlimited - KSh 5,000 (30 days)<br><br>All packages include unlimited local content access.',
    isOpen: false
  },
  {
    id: 19,
    category: 'packages',
    question: 'Do data packages expire?',
    answer: 'Yes, all packages have validity periods:<br>• <strong>Daily:</strong> 24 hours from activation<br>• <strong>Weekly:</strong> 7 days from activation<br>• <strong>Monthly:</strong> 30 days from activation<br><br>Unused data expires and cannot be carried forward. Set reminders or enable auto-renewal to avoid expiration.',
    isOpen: false
  },
  {
    id: 20,
    category: 'packages',
    question: 'Can I upgrade my package mid-cycle?',
    answer: 'Yes! Package upgrades are flexible:<br>• Purchase additional packages anytime<br>• Multiple packages can run simultaneously<br>• New package activates immediately<br>• No loss of existing package data<br>• Upgrade to higher tier for better rates<br><br>Example: Add 10GB weekly to your existing 50GB monthly package.',
    isOpen: false
  },
  {
    id: 21,
    category: 'packages',
    question: 'What is the unlimited package fair usage policy?',
    answer: 'Unlimited package details:<br>• <strong>Daily limit:</strong> 100GB at full speed<br>• <strong>After 100GB:</strong> Speed reduced to 5 Mbps<br>• <strong>Resets:</strong> Daily at midnight<br>• <strong>Streaming:</strong> HD quality supported<br>• <strong>Gaming:</strong> Low latency maintained<br><br>99% of users never reach the daily limit. Perfect for heavy users.',
    isOpen: false
  },
  {
    id: 22,
    category: 'packages',
    question: 'Can I share my package with family?',
    answer: 'Yes! Package sharing options:<br>• Connect multiple devices (up to package limit)<br>• Family members can use same voucher<br>• Monitor usage per device<br>• Set device priorities<br>• Block/unblock devices anytime<br><br>Premium packages support up to 15 simultaneous devices.',
    isOpen: false
  },
  {
    id: 23,
    category: 'packages',
    question: 'Are there student or corporate discounts?',
    answer: 'Special discounts available:<br><strong>Student Discount:</strong><br>• 20% off all packages<br>• Valid student ID required<br>• Educational content free<br><br><strong>Corporate Plans:</strong><br>• Custom packages for businesses<br>• Volume discounts (10+ users)<br>• Dedicated support<br>• Priority bandwidth<br><br>Contact sales@teralinkx.com for details.',
    isOpen: false
  },
  {
    id: 24,
    category: 'packages',
    question: 'What happens when my data runs out?',
    answer: 'When data is exhausted:<br>• Connection automatically pauses<br>• SMS notification sent<br>• Dashboard shows "Out of Data" status<br>• Can purchase new package immediately<br>• Previous session restored after purchase<br>• No disconnection of devices<br><br>Enable auto-renewal to avoid interruptions.',
    isOpen: false
  },

  // Device Management
  {
    id: 25,
    category: 'devices',
    question: 'How many devices can I connect?',
    answer: 'Device limits by package:<br>• <strong>Basic (1-5GB):</strong> 2-3 devices<br>• <strong>Standard (10-20GB):</strong> 4-5 devices<br>• <strong>Premium (50GB+):</strong> 6-10 devices<br>• <strong>Unlimited:</strong> Up to 15 devices<br><br>Devices include phones, tablets, laptops, smart TVs, and IoT devices.',
    isOpen: false
  },
  {
    id: 26,
    category: 'devices',
    question: 'How do I disconnect a device?',
    answer: 'To disconnect a device:<br>1. Go to Profile > Connected Devices<br>2. Find the device in the list<br>3. Click menu (three dots)<br>4. Select "Disconnect Device"<br>5. Confirm action<br><br>Device is immediately disconnected. It can reconnect using the voucher code.',
    isOpen: false
  },
  {
    id: 27,
    category: 'devices',
    question: 'Why was my device blocked?',
    answer: 'Devices may be blocked for:<br>• <strong>Suspicious activity:</strong> Unusual traffic patterns<br>• <strong>Policy violations:</strong> Prohibited content access<br>• <strong>Security threats:</strong> Malware or virus detected<br>• <strong>Manual block:</strong> Account owner action<br>• <strong>Excessive usage:</strong> Abnormal data consumption<br><br>Contact support to appeal or resolve security issues.',
    isOpen: false
  },
  {
    id: 28,
    category: 'devices',
    question: 'Can I rename my devices?',
    answer: 'Yes! Device naming helps identification:<br>1. Go to Profile > Connected Devices<br>2. Click device name or edit icon<br>3. Enter new name (e.g., "John\'s iPhone")<br>4. Press Enter or click Save<br><br>Names are private and only visible to you. Helps manage family devices.',
    isOpen: false
  },
  {
    id: 29,
    category: 'devices',
    question: 'What is device trust and how does it work?',
    answer: 'Trusted devices feature:<br>• <strong>Auto-login:</strong> No voucher code needed<br>• <strong>Priority access:</strong> Faster connection<br>• <strong>Security:</strong> Device fingerprint stored<br>• <strong>Convenience:</strong> Seamless reconnection<br><br>To trust a device: Profile > Devices > Trust Device. Untrust anytime for security.',
    isOpen: false
  },
  {
    id: 30,
    category: 'devices',
    question: 'How do I connect a smart TV or gaming console?',
    answer: 'Connecting non-browser devices:<br>1. Connect device to Teralinkx WiFi<br>2. On phone/laptop, login to your account<br>3. Go to Profile > Add Device<br>4. Enter device MAC address (found in device settings)<br>5. Authorize device<br><br>Device connects automatically. Works for PS5, Xbox, Smart TVs, etc.',
    isOpen: false
  },

  // Security & Privacy
  {
    id: 31,
    category: 'security',
    question: 'How do I enable two-factor authentication?',
    answer: 'Enable 2FA for enhanced security:<br>1. Go to Settings > Security<br>2. Toggle "Two-Factor Authentication"<br>3. Choose method (SMS or Authenticator App)<br>4. Verify with code<br>5. Save backup codes<br><br>2FA adds extra protection. Required for high-value accounts.',
    isOpen: false
  },
  {
    id: 32,
    category: 'security',
    question: 'Is my browsing data private?',
    answer: 'Your privacy is protected:<br>• <strong>No logging:</strong> We don\'t track browsing history<br>• <strong>Encrypted:</strong> HTTPS traffic is end-to-end encrypted<br>• <strong>No selling:</strong> We never sell user data<br>• <strong>Compliance:</strong> GDPR and local privacy laws<br>• <strong>VPN friendly:</strong> Use VPN for extra privacy<br><br>We only collect connection metadata for service quality.',
    isOpen: false
  },
  {
    id: 33,
    category: 'security',
    question: 'How do I change my password?',
    answer: 'Change password securely:<br>1. Go to Settings > Security Settings<br>2. Click "Change Password"<br>3. Enter current password<br>4. Enter new password (min 8 characters)<br>5. Confirm new password<br>6. Click "Update Password"<br><br>Use strong passwords with letters, numbers, and symbols.',
    isOpen: false
  },
  {
    id: 34,
    category: 'security',
    question: 'What should I do if my account is hacked?',
    answer: 'If you suspect unauthorized access:<br>1. <strong>Immediately:</strong> Change your password<br>2. <strong>Review:</strong> Check connected devices and disconnect unknown ones<br>3. <strong>Enable:</strong> Two-factor authentication<br>4. <strong>Contact:</strong> Support team immediately<br>5. <strong>Monitor:</strong> Transaction history for unauthorized purchases<br><br>We\'ll investigate and secure your account within 1 hour.',
    isOpen: false
  },
  {
    id: 35,
    category: 'security',
    question: 'Are public WiFi connections safe?',
    answer: 'TeralinkX public WiFi security:<br>• <strong>WPA3 encryption:</strong> Latest security standard<br>• <strong>Isolated sessions:</strong> Users can\'t see each other<br>• <strong>Firewall protection:</strong> Malicious traffic blocked<br>• <strong>Regular monitoring:</strong> 24/7 security team<br>• <strong>Recommendation:</strong> Use HTTPS sites and VPN for sensitive transactions<br><br>Our network is safer than most public WiFi.',
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
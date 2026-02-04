<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800 pt-16">
    <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
    
    <div class="sm:max-w-md md:max-w-lg lg:max-w-4xl mx-auto px-4 mt-4 mb-8">
      <!-- Page Header -->
      <header class="mb-8 transform transition-all duration-500 animate-fade-in">
        <div class="flex items-center space-x-3 mb-2">
          <div class="p-2 bg-green-500 rounded-lg transition-all duration-300 hover:bg-green-600 hover:scale-110 hover:rotate-3">
            <svg class="w-6 h-6 text-white transition-transform duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </div>
          <div class="transition-all duration-300 hover:translate-x-1">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors duration-300">User Guide</h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Complete guide to using TeralinkX services</p>
          </div>
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Navigation Sidebar -->
        <div class="lg:col-span-1">
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sticky top-20">
            <nav class="space-y-2">
              <button
                v-for="section in guideSections"
                :key="section.id"
                @click="activeSection = section.id"
                :class="[
                  'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-all duration-200 text-sm',
                  activeSection === section.id
                    ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border border-green-200 dark:border-green-800'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
              >
                <component :is="section.icon" class="w-4 h-4" />
                <span class="font-medium">{{ section.name }}</span>
              </button>
            </nav>
          </div>
        </div>

        <!-- Content Area -->
        <div class="lg:col-span-3">
          <!-- Getting Started -->
          <div v-if="activeSection === 'getting-started'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Getting Started</h2>
            
            <div class="space-y-6">
              <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 class="font-semibold text-blue-900 dark:text-blue-200 mb-2">Welcome to TeralinkX</h3>
                <p class="text-blue-800 dark:text-blue-300 text-sm">Your complete internet service provider solution. Follow these steps to get started with your account.</p>
              </div>

              <div class="space-y-4">
                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white">Account Setup</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Create your account using your phone number and verify your identity.</p>
                  </div>
                </div>

                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white">Choose a Package</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Browse our data packages and select one that fits your needs.</p>
                  </div>
                </div>

                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white">Connect Your Device</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Use your voucher code to connect your device to our network.</p>
                  </div>
                </div>

                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">4</div>
                  <div>
                    <h4 class="font-medium text-gray-900 dark:text-white">Start Browsing</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Enjoy high-speed internet access across all your devices.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Packages & Vouchers -->
          <div v-if="activeSection === 'packages'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Packages & Vouchers</h2>
            
            <div class="space-y-6">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">How to Purchase Packages</h3>
                <ol class="list-decimal list-inside space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>Navigate to the "Buy" section in your dashboard</li>
                  <li>Browse available data packages</li>
                  <li>Select a package that suits your needs</li>
                  <li>Choose your payment method (M-Pesa, Airtel Money, etc.)</li>
                  <li>Complete the payment process</li>
                  <li>Receive your voucher code via SMS</li>
                </ol>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Using Voucher Codes</h3>
                <ul class="list-disc list-inside space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>Each voucher code is unique and can be used on multiple devices (up to the package limit)</li>
                  <li>Voucher codes have expiration dates - use them before they expire</li>
                  <li>You can view all your vouchers in the "Vouchers" section</li>
                  <li>Active vouchers show real-time data usage</li>
                </ul>
              </div>

              <div class="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <h4 class="font-medium text-yellow-800 dark:text-yellow-200 mb-2">Important Notes</h4>
                <ul class="list-disc list-inside space-y-1 text-sm text-yellow-700 dark:text-yellow-300">
                  <li>Voucher codes are case-sensitive</li>
                  <li>Keep your voucher codes secure</li>
                  <li>Contact support if you lose a voucher code</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Device Management -->
          <div v-if="activeSection === 'devices'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Device Management</h2>
            
            <div class="space-y-6">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Connecting Devices</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">To connect a new device to your account:</p>
                <ol class="list-decimal list-inside space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>Open your web browser on the device</li>
                  <li>Navigate to any website (you'll be redirected to our login page)</li>
                  <li>Enter your voucher code</li>
                  <li>Click "Connect" to authenticate your device</li>
                </ol>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Managing Connected Devices</h3>
                <ul class="list-disc list-inside space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>View all connected devices in your Profile page</li>
                  <li>Rename devices for easy identification</li>
                  <li>Disconnect devices you no longer use</li>
                  <li>Block suspicious or unauthorized devices</li>
                </ul>
              </div>

              <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">Device Limits</h4>
                <p class="text-sm text-blue-700 dark:text-blue-300">Each package has a device connection limit. Premium packages allow more simultaneous connections.</p>
              </div>
            </div>
          </div>

          <!-- Account Settings -->
          <div v-if="activeSection === 'account'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Account Settings</h2>
            
            <div class="space-y-6">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Profile Management</h3>
                <ul class="list-disc list-inside space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>Update your display name and profile picture</li>
                  <li>Manage notification preferences</li>
                  <li>Set up two-factor authentication for enhanced security</li>
                  <li>Configure data usage alerts</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Security Features</h3>
                <ul class="list-disc list-inside space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>Change your password regularly</li>
                  <li>Enable two-factor authentication</li>
                  <li>Monitor device connections</li>
                  <li>Review login activity</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Troubleshooting -->
          <div v-if="activeSection === 'troubleshooting'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Troubleshooting</h2>
            
            <div class="space-y-6">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Common Issues</h3>
                
                <div class="space-y-4">
                  <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Cannot Connect to Internet</h4>
                    <ul class="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                      <li>Check if your voucher is still active</li>
                      <li>Verify you haven't exceeded device limits</li>
                      <li>Clear your browser cache and cookies</li>
                      <li>Try connecting from a different browser</li>
                    </ul>
                  </div>

                  <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Slow Internet Speed</h4>
                    <ul class="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                      <li>Check your data usage - you might be near your limit</li>
                      <li>Disconnect unused devices</li>
                      <li>Move closer to the access point</li>
                      <li>Restart your device's network connection</li>
                    </ul>
                  </div>

                  <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 dark:text-white mb-2">Voucher Code Not Working</h4>
                    <ul class="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                      <li>Double-check the voucher code for typos</li>
                      <li>Ensure the voucher hasn't expired</li>
                      <li>Verify you haven't reached the device limit</li>
                      <li>Contact support if the issue persists</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NavBar from '@/components/NavBar.vue'

const activeSection = ref('getting-started')

const guideSections = [
  { id: 'getting-started', name: 'Getting Started', icon: 'svg' },
  { id: 'packages', name: 'Packages & Vouchers', icon: 'svg' },
  { id: 'devices', name: 'Device Management', icon: 'svg' },
  { id: 'account', name: 'Account Settings', icon: 'svg' },
  { id: 'troubleshooting', name: 'Troubleshooting', icon: 'svg' }
]
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
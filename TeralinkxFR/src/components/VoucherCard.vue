<template>
  <div class="sm:max-w-md md:max-w-lg lg:max-w-xl w-full max-w-sm mx-auto mb-2 text-text-light dark:text-text-dark">
    <!-- Loading Skeleton -->
    <div v-if="dashboardStore.loading" class="space-y-3">
      <div v-for="n in 2" :key="n" class="bg-white/60 dark:bg-gray-700/60 backdrop-blur-sm rounded-lg h-28 animate-pulse"></div>
    </div>

    <!-- No Vouchers Message -->
    <div
      v-else-if="dashboardStore.vouchers.length === 0"
      class="text-center text-sm text-text-light dark:text-text-dark mt-4 shadow-lg rounded-lg p-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm"
    >
      <div class="flex justify-center items-center space-x-2">
        <svg
          class="w-5 h-5 text-gray-400 dark:text-gray-500"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span>You don't have any vouchers.</span>
      </div>
    </div>

    <!-- Vouchers Container -->
    <div v-else class="space-y-4">
      <!-- Active Vouchers Section -->
      <div v-if="activeVouchers.length > 0" class="relative">
        <div class="sticky top-0 z-10 text-xs text-gray-700 dark:text-gray-300 px-3 py-2 font-medium mb-2 bg-white/10 dark:bg-gray-800/10 backdrop-blur-md rounded-lg border border-white/20 dark:border-gray-600/20">Active Vouchers</div>
        <div class="max-h-64 overflow-y-auto space-y-3" style="scrollbar-width: none; -ms-overflow-style: none;">
          <div
            v-for="voucher in activeVouchers"
            :key="voucher.voucher_code"
            class="flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 backdrop-blur-sm shadow-md rounded-lg px-4 py-2 relative transition-all duration-300 border border-blue-100 dark:border-gray-600"
          >
            <div>
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span class="font-mono text-sm">{{ voucher.voucher_code }}</span>
                <!-- Copy Button -->
                <button
                  @click="copyVoucherCode(voucher.voucher_code)"
                  class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  title="Copy voucher code"
                >
                  <svg class="w-4 h-4 text-gray-500 hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                </button>
                <!-- Connected Devices Icons -->
                <div v-if="voucher.sessions?.active_devices?.length" class="flex space-x-1 ml-2">
                  <div 
                    v-for="device in voucher.sessions.active_devices" 
                    :key="device.session_id"
                    @click="showDeviceInfo(device)"
                    class="relative cursor-pointer group"
                  >
                    <!-- Device Icon -->
                    <svg class="w-5 h-5 transition-transform group-hover:scale-110" :class="device.is_current_device ? 'text-green-500' : 'text-red-400'" fill="currentColor" viewBox="0 0 24 24">
                      <!-- Phone -->
                      <path v-if="device.device_type === 'phone'" d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/>
                      <!-- Tablet -->
                      <path v-else-if="device.device_type === 'tablet'" d="M21 4H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H3V6h18v12z"/>
                      <!-- Laptop -->
                      <path v-else-if="device.device_type === 'laptop'" d="M20 18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H0v2h24v-2h-4zM4 6h16v10H4V6z"/>
                      <!-- Desktop -->
                      <path v-else-if="device.device_type === 'desktop'" d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7v2H8v2h8v-2h-2v-2h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H3V4h18v12z"/>
                      <!-- TV -->
                      <path v-else-if="device.device_type === 'tv'" d="M21 3H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h5v2h8v-2h5c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 14H3V5h18v12z"/>
                      <!-- Default/Other -->
                      <path v-else d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                    <!-- Tooltip on hover (desktop) -->
                    <div class="hidden group-hover:block absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-2xs rounded whitespace-nowrap z-10">
                      {{ device.device_name }}<br>
                      {{ device.device_manufacturer }} {{ device.device_model }}<br>
                      {{ device.ip_address }}
                    </div>
                  </div>
                </div>
              </div>
              <p class="text-2xs text-gray-600 dark:text-gray-300">{{ voucher.package_name }}</p>
              <p class="text-2xs text-gray-700 dark:text-gray-400">
                <span class="text-3xs text-blue-600">USAGE: </span>
                <span class="font-semibold text-orange-600">
                  {{ formatBytes(voucher.usage?.total_bytes || 0) }}
                  <span v-if="!voucher.usage?.is_unlimited"> / {{ formatBytes((voucher.usage?.data_limit_bytes || 0)) }}</span>
                  <span v-else> / Unlimited</span>
                </span>
              </p>
              <p class="text-2xs text-gray-700 dark:text-gray-400">
                <span class="text-3xs text-purple-600">SESSIONS: </span>
                <span class="font-semibold" :class="voucher.sessions?.is_session_limit_reached ? 'text-red-600' : 'text-green-600'">
                  {{ voucher.sessions?.current_sessions || 0 }} / {{ voucher.sessions?.device_limit || 1 }}
                </span>
              </p>
              <p class="text-2xs text-gray-700 dark:text-gray-400">
                <span class="text-3xs text-red-600">EXPIRES:</span> {{ formatDate(voucher.expires_at) }}
              </p>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col space-y-1">
              <!-- Smart Connect/Disconnect Button -->
              <button
                @click="() => toggleConnection(voucher)"
                :disabled="reconnectingVouchers.has(voucher.voucher_code)"
                :class="[
                  'px-3 py-1 text-xs rounded text-white flex items-center justify-center',
                  reconnectingVouchers.has(voucher.voucher_code)
                    ? 'bg-gray-400 cursor-wait'
                    : voucher.sessions?.is_current_device_connected
                      ? 'bg-red-600 hover:bg-red-700'
                      : voucher.sessions?.is_session_limit_reached
                        ? 'bg-orange-500 hover:bg-orange-600'
                        : 'bg-green-600 hover:bg-green-700'
                ]"
              >
                <!-- Loading Spinner -->
                <svg v-if="reconnectingVouchers.has(voucher.voucher_code)" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                
                <span v-else-if="voucher.sessions?.is_current_device_connected">
                  DISCONNECT
                </span>
                <span v-else>
                  RECONNECT
                </span>
              </button>
            </div>
          </div>
        </div>
        <!-- Fade overlay for smooth transition -->
        <div v-if="activeVouchers.length > 3" class="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-blue-50 to-transparent dark:from-gray-900 pointer-events-none"></div>
      </div>

      <!-- Expired Vouchers Section -->
      <div v-if="expiredVouchers.length > 0" class="relative">
        <div class="sticky top-0 z-10 text-xs text-gray-700 dark:text-gray-300 px-3 py-2 font-medium mb-2 bg-white/10 dark:bg-gray-800/10 backdrop-blur-md rounded-lg border border-white/20 dark:border-gray-600/20">Expired Vouchers</div>
        <div class="max-h-24 overflow-y-auto space-y-2" style="scrollbar-width: none; -ms-overflow-style: none;">
          <div
            v-for="voucher in expiredVouchers"
            :key="voucher.voucher_code"
            class="flex items-center justify-between bg-gradient-to-r from-red-50 to-orange-50 dark:from-gray-800 dark:to-gray-700 backdrop-blur-sm shadow-md rounded-lg px-4 py-2 relative transition-all duration-300 border border-red-200 dark:border-red-800 opacity-60"
          >
            <div>
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span class="font-mono text-sm">{{ voucher.voucher_code }}</span>
                <!-- Copy Button -->
                <button
                  @click="copyVoucherCode(voucher.voucher_code)"
                  class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  title="Copy voucher code"
                >
                  <svg class="w-4 h-4 text-gray-500 hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                </button>
              </div>
              <p class="text-2xs text-gray-600 dark:text-gray-300">{{ voucher.package_name }}</p>
              <p class="text-2xs text-gray-700 dark:text-gray-400">
                <span class="text-3xs text-blue-600">USAGE: </span>
                <span class="font-semibold text-orange-600">
                  {{ formatBytes(voucher.usage?.total_bytes || 0) }}
                  <span v-if="!voucher.usage?.is_unlimited"> / {{ formatBytes((voucher.usage?.data_limit_bytes || 0)) }}</span>
                  <span v-else> / Unlimited</span>
                </span>
              </p>
              <p class="text-2xs text-gray-700 dark:text-gray-400">
                <span class="text-3xs text-red-600">EXPIRED:</span> {{ formatDate(voucher.expires_at) }}
              </p>
            </div>

            <!-- Renew Button -->
            <button
              @click="() => renewVoucher(voucher)"
              class="text-white bg-blue-500 hover:bg-blue-600 px-3 py-1 text-xs rounded"
            >
              RENEW
            </button>

            <!-- Expired Stamp -->
            <span
              class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 rotate-[-20deg] text-red-600 font-bold text-xl pointer-events-none"
            >
              EXPIRED
            </span>
          </div>
        </div>
        <!-- Fade overlay for smooth transition -->
        <div v-if="expiredVouchers.length > 2" class="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-red-50 to-transparent dark:from-gray-900 pointer-events-none"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { useNetworkStore } from '@/stores/network'
import { useCustomToast } from '@/composables/useCustomToast'
import { useHotspot } from '@/plugins/hotspot'

// Define emits to communicate with parent Dashboard
const emit = defineEmits(['openRenewModal'])

const dashboardStore = useDashboardStore()
const authStore = useAuthStore()
const networkStore = useNetworkStore()
const { success: showSuccess, error: showError, warning: showWarning } = useCustomToast()

// Loading state for reconnect button
const reconnectingVouchers = ref(new Set())

// Show device info on touch/click
const showDeviceInfo = (device) => {
  const info = `${device.device_name}\n${device.device_manufacturer} ${device.device_model}\nIP: ${device.ip_address}`
  showSuccess(info)
}

// Separate active and expired vouchers
const activeVouchers = computed(() => 
  dashboardStore.vouchers.filter(voucher => !voucher.is_expired)
)

const expiredVouchers = computed(() => 
  dashboardStore.vouchers.filter(voucher => voucher.is_expired)
)

const formatBytes = (bytes) => {
  const num = Number(bytes) || 0
  if (num === 0) return '0 B'
  if (num < 1024) return num + ' B'
  if (num < 1024 * 1024) return (num / 1024).toFixed(1) + ' KB'
  if (num < 1024 * 1024 * 1024) return (num / (1024 * 1024)).toFixed(1) + ' MB'
  return (num / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}

const toggleConnection = async (voucher) => {
  if (reconnectingVouchers.value.has(voucher.voucher_code)) return
  
  if (voucher.sessions?.is_current_device_connected) {
    await disconnectCurrentDevice(voucher)
  } else {
    await reconnect(voucher)
  }
}

const disconnectCurrentDevice = async (voucher) => {
  try {
    reconnectingVouchers.value.add(voucher.voucher_code)
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/disconnect/`, {
      method: 'POST',
      headers: {
        ...authStore.authHeaders,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mac_address: hotspot.mac
      })
    })

    if (response.ok) {
      showSuccess('Disconnected successfully!')
      await dashboardStore.fetchDashboardData()
    } else {
      const data = await response.json()
      showError(data.error || 'Failed to disconnect')
    }
  } catch (error) {
    console.error('Disconnect error:', error)
    showError('Failed to disconnect. Try again later.')
  } finally {
    reconnectingVouchers.value.delete(voucher.voucher_code)
  }
}

const hotspot = useHotspot()

const reconnect = async (voucher) => {
  try {
    reconnectingVouchers.value.add(voucher.voucher_code)
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/reconnect/`, {
      method: 'POST',
      headers: {
        ...authStore.authHeaders,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        voucher_code: voucher.voucher_code,
        bound_ip: hotspot.ip,
        bound_mac: hotspot.mac
      })
    })

    const data = await response.json()

    if (response.ok) {
      showSuccess('Reconnected successfully!')
      // Fetch dashboard data in background (don't block redirect)
      dashboardStore.fetchDashboardData()
      setTimeout(() => {
        window.location = 'https://login.teralinkxwaves.uk/htm.html#/connected'
      }, 1000)
    } else if (response.status === 403) {
      showWarning(data.error || 'Session limit reached. Cannot reconnect.')
    } else {
      showError(data.error || 'Reconnect failed')
    }
  } catch (error) {
    console.error('Reconnect error:', error)
    showError('Reconnect failed. Try again later.')
  } finally {
    reconnectingVouchers.value.delete(voucher.voucher_code)
  }
}

const renewVoucher = async (voucher) => {
  const matchingPackage = dashboardStore.packages.find(pkg => 
    pkg.name === voucher.package_name
  )
  
  if (!matchingPackage) {
    showError('Package not found for renewal')
    return
  }
  
  const packagePrice = matchingPackage.price?.parsedValue?.parsedValue || 
                      matchingPackage.price?.parsedValue || 
                      matchingPackage.price
  
  const renewPackageDetails = {
    id: matchingPackage.id,
    name: matchingPackage.name,
    code: matchingPackage.code,
    price: packagePrice,
    package_code: matchingPackage.code
  }
  
  // Emit event to parent Dashboard to open BuyComponent for fresh data
  emit('openRenewModal', renewPackageDetails)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const copyVoucherCode = async (voucherCode) => {
  try {
    await navigator.clipboard.writeText(voucherCode)
    showSuccess('Voucher code copied to clipboard!')
  } catch (error) {
    const textArea = document.createElement('textarea')
    textArea.value = voucherCode
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    showSuccess('Voucher code copied to clipboard!')
  }
}
</script>

<style scoped>
/* Hide scrollbars completely */
.max-h-64::-webkit-scrollbar,
.max-h-24::-webkit-scrollbar {
  display: none;
}
</style>
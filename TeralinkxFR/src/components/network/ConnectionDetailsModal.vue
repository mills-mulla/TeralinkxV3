<template>
  <!-- Modal Overlay -->
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Background Overlay -->
    <div 
      class="fixed inset-0 bg-black bg-opacity-75 transition-opacity"
      @click="closeModal"
    ></div>

    <!-- Modal Container -->
    <div class="flex min-h-full items-center justify-center p-4">
      <!-- Modal Content -->
      <div 
        class="relative w-full max-w-2xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden transform transition-all"
        @click.stop
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-800 dark:to-blue-900 px-6 py-5">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="p-2 bg-white/10 rounded-lg">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"></path>
                </svg>
              </div>
              <div>
                <h2 class="text-xl font-bold text-white">Connection Details</h2>
                <p class="text-blue-100 text-sm mt-1">Network information and diagnostics</p>
              </div>
            </div>
            <button
              @click="closeModal"
              class="text-white hover:text-blue-200 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="p-6 space-y-6">
          <!-- Connection Status -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Status Card -->
            <div class="col-span-1 md:col-span-2">
              <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Connection Status</h3>
                  <div class="flex items-center space-x-2">
                    <div 
                      class="w-3 h-3 rounded-full animate-pulse"
                      :class="{
                        'bg-green-500': network.isConnected,
                        'bg-yellow-500': !network.isConnected && network.ip,
                        'bg-red-500': !network.ip
                      }"
                    ></div>
                    <span class="text-sm font-medium">
                      <span v-if="!network.ip">Disconnected</span>
                      <span v-if="network.ip && !network.mac">Connecting</span>
                      <span v-if="network.isConnected">Connected</span>
                    </span>
                  </div>
                </div>
                
                <!-- Status Indicators -->
                <div class="space-y-3">
                  <div class="flex items-center justify-between">
                    <span class="text-gray-600 dark:text-gray-400">Network Detection</span>
                    <span class="font-mono text-sm">{{ formatSource(network.source) }}</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-gray-600 dark:text-gray-400">Backend Connection</span>
                    <span class="flex items-center">
                      <span 
                        class="w-2 h-2 rounded-full mr-2"
                        :class="{
                          'bg-green-500': network.connectionTested,
                          'bg-yellow-500': !network.connectionTested && network.isConnected,
                          'bg-gray-400': !network.isConnected
                        }"
                      ></span>
                      <span v-if="network.connectionTested">Connected</span>
                      <span v-if="!network.connectionTested && network.isConnected">Testing...</span>
                      <span v-if="!network.isConnected">Not tested</span>
                    </span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-gray-600 dark:text-gray-400">Hotspot Data</span>
                    <span class="font-mono text-sm">
                      {{ network.hasHotspotData ? 'Available' : 'Not available' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="space-y-4">
              <button
                @click="refreshDetection"
                class="w-full p-4 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-800/30 rounded-xl border border-blue-200 dark:border-blue-800 transition flex flex-col items-center justify-center"
              >
                <svg class="w-8 h-8 text-blue-600 dark:text-blue-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <span class="text-sm font-medium text-blue-700 dark:text-blue-300">Refresh Detection</span>
              </button>
              
              <button
                @click="testConnection"
                class="w-full p-4 bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-800/30 rounded-xl border border-green-200 dark:border-green-800 transition flex flex-col items-center justify-center"
              >
                <svg class="w-8 h-8 text-green-600 dark:text-green-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                <span class="text-sm font-medium text-green-700 dark:text-green-300">Test Backend</span>
              </button>
            </div>
          </div>

          <!-- Network Details -->
          <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-5">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Network Information</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- IP Address -->
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-600 dark:text-gray-400">IP Address</label>
                <div class="flex items-center space-x-2">
                  <code class="flex-1 font-mono text-lg bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-lg truncate">
                    {{ network.ip || 'Not detected' }}
                  </code>
                  <button
                    v-if="network.ip"
                    @click="copyToClipboard(network.ip, 'IP address')"
                    class="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition"
                    title="Copy IP"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- MAC Address -->
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-600 dark:text-gray-400">MAC Address</label>
                <div class="flex items-center space-x-2">
                  <code class="flex-1 font-mono text-lg bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-lg truncate">
                    {{ network.mac || 'Not detected' }}
                  </code>
                  <button
                    v-if="network.mac"
                    @click="copyToClipboard(network.mac, 'MAC address')"
                    class="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition"
                    title="Copy MAC"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Detection Source -->
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Detection Source</label>
                <div class="flex items-center space-x-2">
                  <span class="flex-1 font-medium px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700">
                    {{ formatSource(network.source) }}
                  </span>
                  <span
                    v-if="network.source === 'mikrotik_hotspot'"
                    class="px-3 py-1 bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100 rounded-full text-sm font-medium"
                  >
                    Hotspot
                  </span>
                  <span
                    v-if="network.source === 'simulated'"
                    class="px-3 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100 rounded-full text-sm font-medium"
                  >
                    Simulated
                  </span>
                </div>
              </div>

              <!-- Last Test -->
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Last Backend Test</label>
                <div class="px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700">
                  <span class="font-medium">
                    {{ network.lastTest ? formatTime(network.lastTest) : 'Never' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Network Diagnostics -->
          <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-5">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Network Diagnostics</h3>
            
            <div class="space-y-4">
              <!-- DNS Test -->
              <div class="flex items-center justify-between p-3 bg-white dark:bg-gray-900 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div 
                    class="w-3 h-3 rounded-full"
                    :class="{
                      'bg-green-500': dnsStatus === 'success',
                      'bg-yellow-500': dnsStatus === 'testing',
                      'bg-red-500': dnsStatus === 'failed'
                    }"
                  ></div>
                  <div>
                    <span class="font-medium">DNS Resolution</span>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Can resolve domain names</p>
                  </div>
                </div>
                <button
                  @click="testDNS"
                  :disabled="testingDNS"
                  class="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ testingDNS ? 'Testing...' : 'Test' }}
                </button>
              </div>

              <!-- Connectivity Test -->
              <div class="flex items-center justify-between p-3 bg-white dark:bg-gray-900 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div 
                    class="w-3 h-3 rounded-full"
                    :class="{
                      'bg-green-500': connectivityStatus === 'success',
                      'bg-yellow-500': connectivityStatus === 'testing',
                      'bg-red-500': connectivityStatus === 'failed'
                    }"
                  ></div>
                  <div>
                    <span class="font-medium">Internet Connectivity</span>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Can reach external servers</p>
                  </div>
                </div>
                <button
                  @click="testConnectivity"
                  :disabled="testingConnectivity"
                  class="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ testingConnectivity ? 'Testing...' : 'Test' }}
                </button>
              </div>

              <!-- Latency Test -->
              <div class="flex items-center justify-between p-3 bg-white dark:bg-gray-900 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div 
                    class="w-3 h-3 rounded-full"
                    :class="{
                      'bg-green-500': latency !== null && latency < 100,
                      'bg-yellow-500': latency !== null && latency >= 100 && latency < 300,
                      'bg-red-500': latency !== null && latency >= 300,
                      'bg-gray-400': latency === null
                    }"
                  ></div>
                  <div>
                    <span class="font-medium">Network Latency</span>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                      {{ latency !== null ? `${latency}ms` : 'Not tested' }}
                    </p>
                  </div>
                </div>
                <button
                  @click="testLatency"
                  :disabled="testingLatency"
                  class="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ testingLatency ? 'Testing...' : 'Test' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Advanced Settings -->
          <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-5">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Advanced Settings</h3>
            
            <div class="space-y-3">
              <!-- Manual Override -->
              <div class="flex items-center justify-between">
                <div>
                  <span class="font-medium">Manual Network Override</span>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Set custom network values</p>
                </div>
                <button
                  @click="showManualOverride = !showManualOverride"
                  class="px-4 py-1.5 text-sm bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition"
                >
                  {{ showManualOverride ? 'Hide' : 'Show' }}
                </button>
              </div>

              <!-- Manual Input Form -->
              <div v-if="showManualOverride" class="p-4 bg-white dark:bg-gray-900 rounded-lg space-y-3">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label class="block text-sm font-medium mb-1">Custom IP</label>
                    <input
                      v-model="manualIP"
                      type="text"
                      placeholder="192.168.1.100"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1">Custom MAC</label>
                    <input
                      v-model="manualMAC"
                      type="text"
                      placeholder="00:11:22:33:44:55"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                    />
                  </div>
                </div>
                <div class="flex justify-end space-x-2">
                  <button
                    @click="applyManualOverride"
                    class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
                  >
                    Apply
                  </button>
                  <button
                    @click="resetManualOverride"
                    class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition"
                  >
                    Reset
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center">
            <div class="text-sm text-gray-500 dark:text-gray-400">
              Network information updated in real-time
            </div>
            <div class="flex space-x-3">
              <button
                @click="exportData"
                class="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition"
              >
                Export Data
              </button>
              <button
                @click="closeModal"
                class="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  network: {
    type: Object,
    required: true,
    default: () => ({
      ip: '',
      mac: '',
      source: 'unknown',
      isConnected: false,
      hasHotspotData: false,
      connectionTested: false,
      lastTest: null
    })
  }
})

const emit = defineEmits(['close'])

const { showSuccess, showError, showInfo } = useToast()

// State
const showManualOverride = ref(false)
const manualIP = ref('')
const manualMAC = ref('')
const dnsStatus = ref(null) // 'success', 'testing', 'failed'
const connectivityStatus = ref(null)
const latency = ref(null)
const testingDNS = ref(false)
const testingConnectivity = ref(false)
const testingLatency = ref(false)

// Methods
const formatSource = (source) => {
  const sources = {
    'mikrotik_hotspot': 'Mikrotik Hotspot',
    'webrtc_fallback': 'WebRTC Detection',
    'simulated': 'Simulated Data',
    'detection_failed': 'Detection Failed',
    'unknown': 'Unknown'
  }
  return sources[source] || source
}

const formatTime = (date) => {
  if (!date) return 'Never'
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`
  return d.toLocaleString([], { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const copyToClipboard = async (text, label) => {
  try {
    await navigator.clipboard.writeText(text)
    showSuccess(`${label} copied to clipboard`)
  } catch (err) {
    showError('Failed to copy to clipboard')
  }
}

const refreshDetection = () => {
  // This would call network store's detectNetwork method
  showInfo('Refreshing network detection...')
  window.location.reload()
}

const testConnection = () => {
  // This would call network store's testConnection method
  showInfo('Testing backend connection...')
}

const testDNS = async () => {
  testingDNS.value = true
  dnsStatus.value = 'testing'
  
  try {
    // Test DNS resolution
    await fetch('https://api.ipify.org?format=json', { mode: 'no-cors' })
    dnsStatus.value = 'success'
    showSuccess('DNS resolution successful')
  } catch (error) {
    dnsStatus.value = 'failed'
    showError('DNS resolution failed')
  } finally {
    testingDNS.value = false
  }
}

const testConnectivity = async () => {
  testingConnectivity.value = true
  connectivityStatus.value = 'testing'
  
  try {
    const start = performance.now()
    const response = await fetch('https://httpbin.org/get', { 
      mode: 'cors',
      cache: 'no-cache'
    })
    const end = performance.now()
    
    if (response.ok) {
      connectivityStatus.value = 'success'
      showSuccess(`Internet connectivity: ${Math.round(end - start)}ms`)
    } else {
      throw new Error('Response not OK')
    }
  } catch (error) {
    connectivityStatus.value = 'failed'
    showError('Internet connectivity test failed')
  } finally {
    testingConnectivity.value = false
  }
}

const testLatency = async () => {
  testingLatency.value = true
  
  try {
    const times = []
    
    // Test multiple times for accuracy
    for (let i = 0; i < 3; i++) {
      const start = performance.now()
      await fetch('https://httpbin.org/delay/0', { 
        mode: 'no-cors',
        cache: 'no-store'
      })
      const end = performance.now()
      times.push(end - start)
      
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    // Calculate average
    const avg = times.reduce((a, b) => a + b, 0) / times.length
    latency.value = Math.round(avg)
    
    showSuccess(`Average latency: ${latency.value}ms`)
  } catch (error) {
    showError('Latency test failed')
  } finally {
    testingLatency.value = false
  }
}

const applyManualOverride = () => {
  if (manualIP.value || manualMAC.value) {
    // This would update the network store
    showSuccess('Manual override applied')
    showManualOverride.value = false
  }
}

const resetManualOverride = () => {
  manualIP.value = ''
  manualMAC.value = ''
  showInfo('Manual override reset')
}

const exportData = () => {
  const data = {
    timestamp: new Date().toISOString(),
    network: props.network,
    diagnostics: {
      dns: dnsStatus.value,
      connectivity: connectivityStatus.value,
      latency: latency.value
    }
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `teralinkx-network-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  showSuccess('Network data exported')
}

const closeModal = () => {
  emit('close')
}
</script>

<style scoped>
/* Custom animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">
            💰 Downtime Refund Management
          </h1>
          <p class="text-slate-600 font-light">Compensate clients for service downtime</p>
        </div>
        <div class="flex items-center space-x-3">
          <div class="relative">
            <div class="w-3 h-3 bg-emerald-500 rounded-full animate-ping absolute -top-1 -right-1"></div>
            <div class="w-2 h-2 bg-emerald-500 rounded-full absolute -top-0.5 -right-0.5"></div>
            <button @click="refreshData" class="p-2 hover:bg-white/50 rounded-xl transition-all duration-300 backdrop-blur-sm" title="Refresh data">
              <ArrowPathIcon class="w-6 h-6 text-slate-600" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Debug Panel (Remove in production) -->
    <div v-if="debugMode" class="bg-yellow-50 border border-yellow-200 rounded-2xl p-4 mb-6">
      <div class="flex items-center justify-between">
        <h3 class="text-yellow-800 font-semibold flex items-center">
          <WrenchScrewdriverIcon class="w-4 h-4 mr-2" />
          Debug Mode
        </h3>
        <button @click="debugMode = false" class="text-yellow-600 hover:text-yellow-800">
          <XCircleIcon class="w-4 h-4" />
        </button>
      </div>
      <div class="mt-2 text-sm text-yellow-700 space-y-1">
        <div>Auth Status: {{ authStatus }}</div>
        <div>Token: {{ tokenStatus }}</div>
        <div>Last Error: {{ lastError }}</div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <ExclamationTriangleIcon class="w-6 h-6 text-rose-600" />
          <div>
            <h3 class="text-rose-800 font-semibold">Failed to load refunds data</h3>
            <p class="text-rose-600 text-sm">{{ error }}</p>
            <button 
              v-if="error.includes('403')"
              @click="enableDebugMode"
              class="text-xs text-rose-700 underline mt-1"
            >
              Debug 403 Error
            </button>
          </div>
        </div>
        <button 
          @click="fetchAllData"
          class="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition-colors duration-200 flex items-center space-x-2"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span>Retry</span>
        </button>
      </div>
    </div>

    <!-- User Manual Section -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 mb-8 overflow-hidden">
      <div class="p-6 border-b border-slate-200/60 cursor-pointer" @click="toggleManual">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-800 flex items-center">
            <BookOpenIcon class="w-5 h-5 text-slate-600 mr-2" />
            REFUND RULES & USER MANUAL
          </h3>
          <span class="text-slate-500">{{ manualExpanded ? '−' : '+' }}</span>
        </div>
      </div>
      <div v-if="manualExpanded" class="p-6 bg-gradient-to-br from-slate-50 to-blue-50/30">
        <!-- Manual content remains the same -->
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !error" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
          <div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div>
        </div>
        <p class="mt-4 text-slate-500 font-light">Loading refunds data...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="!loading" class="space-y-8">
      <!-- Quick Stats -->
      <section>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-slate-800 flex items-center">
            <div class="w-2 h-8 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full mr-3"></div>
            Refund Overview
          </h2>
          <div class="flex items-center space-x-2">
            <div class="text-sm text-slate-500 bg-white/50 px-3 py-1 rounded-full backdrop-blur-sm">
              {{ formatDate(new Date()) }}
            </div>
            <button 
              @click="enableDebugMode"
              class="text-xs text-slate-400 hover:text-slate-600 p-1"
              title="Debug Mode"
            >
              <WrenchScrewdriverIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <ModernMetricCard
            title="Eligible Clients"
            :value="stats.eligibleClients || 0"
            trend="up"
            trendValue="12.5%"
            icon="👥"
            color="blue"
            :formatted="true"
          />
          
          <ModernMetricCard
            title="Total Refunded"
            :value="`KSh ${formatNumber(stats.totalRefunded || 0)}`"
            trend="up"
            trendValue="18.7%"
            icon="💰"
            color="emerald"
            :formatted="false"
          />
          
          <ModernMetricCard
            title="Pending Refunds"
            :value="stats.pendingRefunds || 0"
            trend="down"
            trendValue="5.3%"
            icon="⏳"
            color="amber"
            :formatted="true"
          />
          
          <ModernMetricCard
            title="Avg. Refund"
            :value="`KSh ${formatNumber(stats.averageRefund || 0)}`"
            trend="stable"
            trendValue="2.1%"
            icon="📊"
            color="purple"
            :formatted="false"
          />
        </div>
      </section>

      <!-- Tab Navigation -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
        <div class="flex border-b border-slate-200/60">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            :class="[
              'flex-1 px-6 py-4 text-sm font-medium transition-all duration-300 border-b-2',
              activeTab === tab.id 
                ? 'border-blue-500 text-blue-600 bg-blue-50/50' 
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50/50'
            ]"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab Content -->
        <div class="p-6">
          <!-- Individual Refund Tab -->
          <div v-if="activeTab === 'individual'" class="space-y-6">
            <h3 class="text-lg font-semibold text-slate-800 mb-6 flex items-center">
              <UserIcon class="w-5 h-5 text-slate-600 mr-2" />
              Individual Client Refund
            </h3>
            
            <div v-if="loading.eligibleClients" class="flex items-center justify-center py-12">
              <div class="text-center">
                <div class="relative">
                  <div class="w-12 h-12 border-4 border-blue-200 rounded-full"></div>
                  <div class="w-12 h-12 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div>
                </div>
                <p class="mt-4 text-slate-500 font-light">Loading eligible clients...</p>
              </div>
            </div>
            
            <div v-else-if="eligibleClients.length === 0" class="text-center py-12">
              <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <UserGroupIcon class="w-8 h-8 text-slate-400" />
              </div>
              <h3 class="text-lg font-semibold text-slate-600 mb-2">No eligible clients found</h3>
              <p class="text-slate-500">No clients meet the refund eligibility criteria.</p>
            </div>
            
            <div v-else class="space-y-6">
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-3">Select Client</label>
                  <select 
                    v-model="selectedClient" 
                    @change="onClientChange"
                    class="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 bg-white"
                  >
                    <option value="">Choose a client...</option>
                    <option 
                      v-for="client in eligibleClients" 
                      :key="client.dispatch_account"
                      :value="client.dispatch_account"
                    >
                      {{ client.dispatch_account }} - {{ client.username }} - KES {{ client.dispatch_price }}
                    </option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-3">Downtime Minutes</label>
                  <input 
                    type="number" 
                    v-model.number="individualDowntime"
                    min="0"
                    max="1440"
                    step="1"
                    class="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  />
                  <p class="text-xs text-slate-500 mt-2">Total downtime minutes to compensate</p>
                </div>
              </div>

              <!-- Client Details -->
              <div v-if="selectedClientDetails" class="bg-gradient-to-br from-slate-50 to-blue-50/30 rounded-2xl p-6 border border-slate-200/60">
                <h4 class="text-lg font-semibold text-slate-800 mb-4">Client Details</h4>
                
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div class="bg-white rounded-xl p-4 text-center border border-slate-200/60">
                    <div class="text-sm text-slate-600 mb-1">Current Balance</div>
                    <div class="text-lg font-semibold text-slate-800">KES {{ selectedClientDetails.current_balance?.toFixed(2) }}</div>
                  </div>
                  
                  <div class="bg-white rounded-xl p-4 text-center border border-slate-200/60">
                    <div class="text-sm text-slate-600 mb-1">Package Price</div>
                    <div class="text-lg font-semibold text-slate-800">KES {{ selectedClientDetails.dispatch_price?.toFixed(2) }}</div>
                  </div>
                  
                  <div class="bg-white rounded-xl p-4 text-center border border-slate-200/60">
                    <div class="text-sm text-slate-600 mb-1">Package Duration</div>
                    <div class="text-lg font-semibold text-slate-800">{{ selectedClientDetails.dispatch_package_duration || 'N/A' }}</div>
                  </div>
                  
                  <div class="bg-white rounded-xl p-4 text-center border border-slate-200/60">
                    <div class="text-sm text-slate-600 mb-1">Status</div>
                    <div class="text-lg font-semibold" :class="getStatusClass(selectedClientStatus)">
                      {{ selectedClientStatus.replace('✅', '').replace('❌', '').trim() }}
                    </div>
                  </div>
                </div>

                <!-- Usage Progress -->
                <div v-if="selectedClientDetails.usage_limit > 0" class="mb-6">
                  <div class="flex justify-between text-sm text-slate-600 mb-2">
                    <span>Data Usage</span>
                    <span>{{ totalUsage.toFixed(2) }} / {{ selectedClientDetails.usage_limit.toFixed(2) }} ({{ Math.min(usagePercentage, 100).toFixed(1) }}%)</span>
                  </div>
                  <div class="w-full bg-slate-200 rounded-full h-3">
                    <div 
                      class="bg-gradient-to-r from-emerald-500 to-teal-600 h-3 rounded-full transition-all duration-500"
                      :style="{ width: Math.min(usagePercentage, 100) + '%' }"
                    ></div>
                  </div>
                </div>
                
                <div v-else class="mb-6">
                  <div class="bg-emerald-100 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl text-center">
                    <span class="font-medium">Unlimited usage package</span>
                  </div>
                </div>

                <!-- Estimated Refund -->
                <div class="bg-blue-100 border border-blue-200 text-blue-800 px-4 py-3 rounded-xl mb-4">
                  <div class="flex items-center justify-between">
                    <span class="font-medium">📍 Estimated Refund</span>
                    <span class="text-xl font-bold">KES {{ estimatedRefund.toFixed(2) }}</span>
                  </div>
                </div>

                <!-- Eligibility Warning -->
                <div v-if="!isClientEligible" class="bg-rose-100 border border-rose-200 text-rose-800 px-4 py-3 rounded-xl mb-4">
                  <div class="flex items-center">
                    <XCircleIcon class="w-5 h-5 mr-2" />
                    <span>This client is not eligible for refund: {{ selectedClientStatus.replace('❌', '').trim() }}</span>
                  </div>
                </div>

                <!-- Process Refund Button -->
                <button 
                  class="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-500 hover:to-purple-500 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center space-x-2 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!canProcessIndividualRefund"
                  @click="processIndividualRefund"
                >
                  <ArrowPathIcon class="w-5 h-5" />
                  <span>Process Individual Refund</span>
                </button>

                <!-- Debug Info -->
                <div v-if="debugMode" class="mt-4 p-3 bg-slate-100 rounded-lg text-xs">
                  <div>Endpoint: POST /suapi/refunds/process-individual/</div>
                  <div>Payload: {{ JSON.stringify({
                    account: this.selectedClient,
                    downtime_minutes: this.individualDowntime,
                    refund_type: 'individual'
                  }) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Other tabs remain the same -->
          <!-- ... -->
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="processingRefund" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-8 shadow-2xl text-center">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
          <div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div>
        </div>
        <p class="mt-4 text-slate-600 font-medium">Processing refund...</p>
      </div>
    </div>
  </div>
</template>

<script>
import ModernMetricCard from '../components/MetricCard.vue'
import { useApi } from '../composables/useApi'
import axios from 'axios'

import { 
  BellIcon,
  BookOpenIcon,
  UserIcon,
  UserGroupIcon,
  TableCellsIcon,
  ClockIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CalendarIcon,
  DocumentPlusIcon,
  RocketLaunchIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  CalculatorIcon,
  WrenchScrewdriverIcon,
  EyeIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'Refunds',
  components: {
    ModernMetricCard,
    BellIcon,
    BookOpenIcon,
    UserIcon,
    UserGroupIcon,
    TableCellsIcon,
    ClockIcon,
    DocumentTextIcon,
    ChartBarIcon,
    CalendarIcon,
    DocumentPlusIcon,
    RocketLaunchIcon,
    ArrowPathIcon,
    ArrowDownTrayIcon,
    CheckCircleIcon,
    XCircleIcon,
    ExclamationTriangleIcon,
    CalculatorIcon,
    WrenchScrewdriverIcon,
    EyeIcon
  },
  setup() {
    const { loading, error, makeRequest } = useApi()
    return { loading, error, makeRequest }
  },
  data() {
    return {
      activeTab: 'individual',
      manualExpanded: false,
      showClientsDetails: false,
      processingRefund: false,
      debugMode: false,
      authStatus: 'Unknown',
      tokenStatus: 'Unknown',
      lastError: '',
      
      tabs: [
        { id: 'individual', label: '🧍 Individual Refund' },
        { id: 'batch', label: '👥 Batch Refund' },
        { id: 'history', label: '📊 Refund History' },
        { id: 'insights', label: '🔍 Eligibility Insights' }
      ],
      
      stats: {
        eligibleClients: 0,
        totalRefunded: 0,
        pendingRefunds: 0,
        averageRefund: 0
      },
      
      // Individual Refund Data
      eligibleClients: [],
      selectedClient: '',
      selectedClientDetails: null,
      individualDowntime: 15,
      
      // Batch Refund Data
      batchDowntime: 15,
      batchResults: [],
      totalRefunded: 0,
      
      // Refund History Data
      refundHistory: [],
      
      // Downtime Management Data
      recentDowntimes: [],
      newDowntime: {
        name: '',
        startTime: '',
        endTime: '',
        reason: '',
        affectedServices: 'all',
        severity: 'medium'
      }
    }
  },
  computed: {
    // ... existing computed properties remain the same
  },
  async mounted() {
    await this.fetchAllData()
    await this.checkAuthStatus()
  },
  methods: {
    async checkAuthStatus() {
      try {
        const token = localStorage.getItem('access_token')
        this.tokenStatus = token ? 'Present' : 'Missing'
        
        const response = await axios.get('/suapi/auth/verify/')
        this.authStatus = response.data.authenticated ? 'Authenticated' : 'Not Authenticated'
        
        console.log('🔐 Auth Status:', {
          token: this.tokenStatus,
          auth: this.authStatus,
          user: response.data.user
        })
      } catch (error) {
        this.authStatus = 'Failed'
        console.error('Auth check failed:', error)
      }
    },

    async fetchAllData() {
      try {
        this.error = null
        
        await Promise.all([
          this.fetchRefundStats(),
          this.fetchEligibleClients(),
          this.fetchRefundHistory(),
          this.fetchRecentDowntimes()
        ])
        
      } catch (error) {
        console.error('Error fetching refunds data:', error)
        this.lastError = error.message
        this.error = this.getErrorMessage(error)
      }
    },

    getErrorMessage(error) {
      if (error.response?.status === 403) {
        return 'Access forbidden. Please check your permissions or contact administrator.'
      }
      if (error.response?.status === 401) {
        return 'Authentication failed. Please log in again.'
      }
      return error.response?.data?.error || 'Failed to load refunds data'
    },

    async fetchRefundStats() {
      try {
        const data = await this.makeRequest('get', 'suapi/refunds/stats/')
        this.stats = data
      } catch (error) {
        console.error('Error fetching refund stats:', error)
        throw error
      }
    },

    async fetchEligibleClients() {
      try {
        const data = await this.makeRequest('get', 'suapi/refunds/eligible-clients/')
        this.eligibleClients = data
      } catch (error) {
        console.error('Error fetching eligible clients:', error)
        throw error
      }
    },

    async fetchRefundHistory() {
      try {
        const data = await this.makeRequest('get', 'suapi/refunds/history/')
        this.refundHistory = data
      } catch (error) {
        console.error('Error fetching refund history:', error)
        throw error
      }
    },

    async fetchRecentDowntimes() {
      try {
        const data = await this.makeRequest('get', 'suapi/refunds/recent-downtimes/')
        this.recentDowntimes = data
      } catch (error) {
        console.error('Error fetching recent downtimes:', error)
      }
    },

    async onClientChange() {
      if (this.selectedClient) {
        try {
          const data = await this.makeRequest('get', `suapi/refunds/client-details/${this.selectedClient}/`)
          this.selectedClientDetails = data
        } catch (error) {
          console.error('Error fetching client details:', error)
          this.selectedClientDetails = null
        }
      } else {
        this.selectedClientDetails = null
      }
    },

    async testAuthentication() {
      try {
        const response = await axios.get('/suapi/auth/verify/');
        console.log('✅ Authentication working:', response.data)
        return true
      } catch (error) {
        console.error('❌ Authentication failed:', error)
        return false
      }
    },

    async processIndividualRefund() {
      if (!this.canProcessIndividualRefund) return

      // Test auth first
      const authWorking = await this.testAuthentication()
      if (!authWorking) {
        alert('❌ Authentication failed. Please log in again.')
        return
      }

      this.processingRefund = true
      try {
        console.log('🔄 Processing individual refund...', {
          account: this.selectedClient,
          downtime_minutes: this.individualDowntime
        })

        const payload = {
          account: this.selectedClient,
          downtime_minutes: this.individualDowntime,
          refund_type: 'individual'
        }

        // Log the request details for debugging
        const token = localStorage.getItem('access_token')
        console.log('🔐 Request details:', {
          url: '/suapi/refunds/process-individual/',
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          payload
        })

        const response = await this.makeRequest('post', 'suapi/refunds/process-individual/', payload)

        if (response.success) {
          // Show success message
          alert(`✅ Refund Processed: Successfully refunded KES ${response.refund_amount} to ${this.selectedClient}`)
          
          // Refresh data
          await this.fetchAllData()
        }
      } catch (error) {
        console.error('❌ Error processing individual refund:', error)
        this.lastError = error.message
        
        // Enhanced error handling
        let errorMsg = 'Failed to process refund'
        
        if (error.response) {
          // Server responded with error status
          console.error('Response error:', error.response)
          
          if (error.response.status === 403) {
            errorMsg = 'Access forbidden. You may not have permission to process refunds.'
            if (error.response.data?.detail) {
              errorMsg += ` Details: ${error.response.data.detail}`
            }
          } else if (error.response.status === 400) {
            errorMsg = error.response.data?.error || 'Invalid request data'
          } else if (error.response.status === 401) {
            errorMsg = 'Authentication failed. Please log in again.'
          } else {
            errorMsg = error.response.data?.error || `Server error: ${error.response.status}`
          }
        } else if (error.request) {
          // Request was made but no response received
          errorMsg = 'No response from server. Please check your connection.'
        } else {
          // Something else happened
          errorMsg = error.message
        }
        
        alert(`❌ Refund Failed: ${errorMsg}`)
      } finally {
        this.processingRefund = false
      }
    },

    async processBatchRefund() {
      if (!this.canProcessBatchRefund) return

      // Test auth first
      const authWorking = await this.testAuthentication()
      if (!authWorking) {
        alert('❌ Authentication failed. Please log in again.')
        return
      }

      this.processingRefund = true
      try {
        const response = await this.makeRequest('post', 'suapi/refunds/batch-refund/', {
          downtime_minutes: this.batchDowntime
        })

        if (response.success) {
          this.batchResults = response.results
          this.totalRefunded = response.total_refunded
          
          alert(`✅ Batch Refund Completed: Processed ${response.processed_count} refunds totaling KES ${response.total_refunded}`)
          
          // Refresh data
          await this.fetchAllData()
        }
      } catch (error) {
        console.error('Error processing batch refund:', error)
        this.lastError = error.message
        const errorMsg = this.getErrorMessage(error)
        alert(`❌ Batch Refund Failed: ${errorMsg}`)
      } finally {
        this.processingRefund = false
      }
    },

    enableDebugMode() {
      this.debugMode = true
      this.checkAuthStatus()
    },

    // ... other methods remain the same
    toggleManual() {
      this.manualExpanded = !this.manualExpanded
    },

    refreshData() {
      this.fetchAllData()
    },

    formatNumber(num) {
      return new Intl.NumberFormat().format(num)
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    getStatusClass(status) {
      if (status.includes('✅')) return 'text-emerald-700'
      if (status.includes('❌')) return 'text-rose-700'
      if (status.includes('⚠️')) return 'text-amber-700'
      return 'text-slate-700'
    },

    getClientStatus(client) {
      if (!client) return '❌ Not Found'
      
      const now = new Date()
      const expiry = new Date(client.dispatch_expiry)
      
      if (client.dispatch_expiry && expiry < now) {
        return '❌ Package expired'
      }
      
      if (client.usage_limit) {
        const totalUsage = (client.total_download || 0) + (client.total_upload || 0)
        if (totalUsage >= client.usage_limit) {
          return '❌ Usage limit reached'
        }
      }
      
      return '✅ Active'
    },

    calculateRefundAmount(packagePrice, durationStr, usageLimit, totalDownload, totalUpload, downtimeMinutes) {
      const MIN_DOWNTIME_FOR_REFUND = 10
      
      if (downtimeMinutes < MIN_DOWNTIME_FOR_REFUND) {
        return 0
      }

      const days = this.extractDaysFromDuration(durationStr)
      const totalMinutes = days * 24 * 60
      const refundPerMinute = packagePrice / totalMinutes
      
      return Math.max(1, Math.round(refundPerMinute * downtimeMinutes))
    },

    extractDaysFromDuration(durationStr) {
      if (!durationStr) return 30
      
      try {
        if (typeof durationStr === 'string' && durationStr.includes('day')) {
          const daysStr = durationStr.split(' day')[0]
          return parseInt(daysStr) || 1
        }
        return 30
      } catch {
        return 30
      }
    },

    downloadRefundReport() {
      const csvContent = this.convertToCSV(this.batchResults)
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `batch_refund_report_${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      window.URL.revokeObjectURL(url)
    },

    convertToCSV(data) {
      if (!data.length) return ''
      
      const headers = Object.keys(data[0])
      const csvRows = [
        headers.join(','),
        ...data.map(row => 
          headers.map(header => 
            JSON.stringify(row[header] || '')
          ).join(',')
        )
      ]
      
      return csvRows.join('\n')
    }
  }
}
</script>
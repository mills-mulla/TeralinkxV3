// stores/dashboard.js - Unified dashboard store
import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    // Account data
    account: null,
    balance: 0,
    balanceStatus: 'good',
    status: 'offline',
    userImage: null,
    clientName: null,
    phoneNumber: null,
    
    // Vouchers
    vouchers: [],
    
    // Packages
    packages: [],
    
    // Notifications
    notifications: [],
    
    // Loading states
    loading: false,
    error: null,
    lastUpdated: null,
    
    // Metadata
    metadata: null
  }),

  getters: {
    isOnline: (state) => state.status?.toLowerCase() === 'active',
    activeVouchers: (state) => state.vouchers.filter(v => v.dispatch_status === 'active' && !v.is_expired),
    hasActiveVoucher: (state) => state.vouchers.some(v => v.dispatch_status === 'active' && !v.is_expired),
    featuredPackages: (state) => state.packages.filter(p => p.is_featured),
    unreadNotifications: (state) => state.notifications.filter(n => !n.is_read),
    formattedBalance: (state) => `KES ${state.balance.toFixed(2)}`
  },

  actions: {
    async fetchDashboardData() {
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        throw new Error('Not authenticated')
      }

      this.loading = true
      this.error = null

      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/dashboard/`, {
          headers: authStore.authHeaders
        })

        if (!response.ok) {
          throw new Error(`Dashboard fetch failed: ${response.status}`)
        }

        const data = await response.json()
        
        // Update client data
        this.account = data.client?.acc_no || ''
        this.balance = data.client?.acc_bal?.parsedValue || 0
        this.balanceStatus = data.client?.balance_status || 'good'
        this.status = data.client?.acc_stat || 'inactive'
        this.userImage = data.client?.image || null
        this.clientName = data.client?.client || ''
        this.phoneNumber = data.client?.phone_number || ''
        
        // Update vouchers, packages, notifications
        this.vouchers = data.vouchers || []
        this.packages = data.packages || []
        this.notifications = data.notifications || []
        
        // Update metadata
        this.metadata = data.metadata || null
        this.lastUpdated = new Date()

        return data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // Refresh specific data if needed
    async refreshVouchers() {
      // Could call specific endpoint if needed, or refetch all
      await this.fetchDashboardData()
    },

    clearData() {
      this.$reset()
    }
  }
})
import { defineStore } from 'pinia'
import { api } from '../services/api'

export const useVoucherStore = defineStore('voucherStore', {
  state: () => ({
    vouchers: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchActiveVouchers() {
      try {
        this.loading = true
        this.error = null

        const phoneLocal = localStorage.getItem('account')
        if (!phoneLocal) throw new Error('Phone number not found in local storage')

        const phone = phoneLocal.startsWith('254') ? phoneLocal : '254' + phoneLocal.slice(1)

        const response = await api.post('/api/getactive/', { account: phone })

        if (response.status === 200) {
          this.vouchers = response.data
        } else {
          throw new Error('Unexpected response status')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message
      } finally {
        this.loading = false
      }
    }
  }
})

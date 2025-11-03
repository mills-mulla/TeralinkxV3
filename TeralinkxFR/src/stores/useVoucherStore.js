import { defineStore } from 'pinia'
import axios from 'axios'

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

        const csrfToken = await this.getCSRFToken()

        const response = await axios.post(`${import.meta.env.VITE_API_PROD_URL}/api/getactive/`, { account: phone }, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            Authorization: `Token ${localStorage.getItem('authToken')}`,
          },
        })

        if (response.status === 200) {
          this.vouchers = response.data
        } else {
          throw new Error('Unexpected response status')
        }
      } catch (error) {
        // console.error('Error fetching vouchers:', error)
        this.error = error.response?.data?.message || error.message
      } finally {
        this.loading = false
      }
    },

    async getCSRFToken() {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_PROD_URL}/api/get-csrf-token/`)
        return response.data.csrfToken
      } catch (error) {
        throw new Error('Failed to retrieve CSRF token')
      }
    }
  }
})

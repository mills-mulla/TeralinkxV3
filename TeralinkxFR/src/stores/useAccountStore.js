import { defineStore } from 'pinia'
import axios from 'axios'
import defaultAvatar from '@/assets/avatar2.png'

export const useAccountStore = defineStore('account', {
  state: () => ({
    account: '',
    balance: '',
    userImage: '',
    status: '',
    client: '',
    loading: true,
    error: null
  }),

  getters: {
    isOnline: (state) => state.status.toLowerCase() === 'online',
    formattedBalance: (state) => {
      const balance = parseFloat(state.balance) || 0
      return `KES ${balance.toFixed(2)}`
    }
  },

  actions: {
    async fetchAccountInfo() {
      this.loading = true
      this.error = null

      try {
        const phoneNumber = localStorage.getItem('account')
        if (!phoneNumber) {
          throw new Error('Phone number not found in local storage')
        }

        const authToken = localStorage.getItem('authToken')
        const csrfToken = localStorage.getItem('csrfToken')
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
        const prodAdsUrl = import.meta.env.VITE_API_PROD_ADS_URL

        const response = await axios.post(`${apiBaseUrl}/api/getclient/`, 
          { phone: phoneNumber },
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken || '',
              Authorization: `Token ${authToken}`
            }
          }
        )

        if (response.status === 200) {
          const { acc_no, acc_bal, image, acc_stat, client } = response.data
          this.account = acc_no
          this.balance = acc_bal
          this.userImage = image ? `${prodAdsUrl}${image}` : defaultAvatar
          this.status = acc_stat || 'online'
          this.client = client || acc_no
        } else {
          throw new Error('Unexpected response from server')
        }
      } catch (err) {
        this.error = err.message || 'Failed to fetch account info'
      } finally {
        this.loading = false
      }
    },

    logout() {
      localStorage.clear()
      this.account = ''
      this.balance = 0.0
      this.status = 'offline'
      this.client = ''
      alert('Logging out...')
    }
  }
})

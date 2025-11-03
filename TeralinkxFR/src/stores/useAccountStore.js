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
    formattedBalance: (state) => `KES ${state.balance.toFixed(2)}`
  },

  actions: {
    async fetchAccountInfo() {
      this.loading = true
      this.error = null

      try {
        const phone_local = localStorage.getItem('account')

        if (!phone_local) {
          throw new Error('Phone number not found in local storage')
        }

        const requestData = { phone: phone_local }

        const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/getclient/`, requestData, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': localStorage.getItem('csrfToken') || '',
            Authorization: `Token ${localStorage.getItem('authToken')}`
          }
        })

        if (response.status === 200) {
     
          const data = response.data
          this.account = data.acc_no
          this.balance = data.acc_bal
          this.userImage = data.image
            ? `${import.meta.env.VITE_API_PROD_ADS_URL}${data.image}`
            : defaultAvatar
            
          this.status = data.acc_stat || 'online'
          this.client = data.client || data.acc_no
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

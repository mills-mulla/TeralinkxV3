// NotificationHandler.vue
<template>
  <div>
    <Loader v-if="isLoading" />
  </div>
</template>

<script>
import Pusher from 'pusher-js'
import { toast } from 'vue3-toastify'
import Loader from '../views/Loader.vue'

export default {
  name: 'NotificationHandler',
  components: {
    Loader
  },
  data() {
    return {
      isLoading: false
    }
  },
  mounted() {
    const userId = localStorage.getItem('ping')
    const pusherKey = import.meta.env.VITE_PUSHER_KEY
    const cluster = import.meta.env.VITE_PUSHER_CLUSTER

    if (!userId || !pusherKey || !cluster) {
      console.warn('Pusher or user ID not configured.')
      return
    }

    const pusher = new Pusher(pusherKey, {
      cluster: cluster,
      encrypted: true
    })

    const channel = pusher.subscribe('user-' + userId)

    channel.bind('new-alert', data => {
      // console.log('🔥 Pusher event received:', data)

      let message, type

      // If backend sends a raw string
      if (typeof data === 'string') {
        message = data
        type = 'info'
      } 
      // If backend sends a structured object
      else if (typeof data === 'object' && data !== null) {
        message = data.message || '🔔 You have a new notification!'
        type = data.type || 'info'
      } 
      // Fallback
      else {
        message = '🔔 You have a new notification!'
        type = 'info'
      }

      // Loader + redirect logic
      if (message === 'Processing started...') {
        this.isLoading = true
      } else if (message === 'Processing complete') {
        this.isLoading = false
      } else if (message === 'Checkout confirmed') {
        window.location = 'https://login.teralinkxwaves.uk/status'
      }

      // Show toast
      toast(message, {
        type,
        autoClose: 5000,
        position: 'top-right',
      })
    })

  }
}
</script>

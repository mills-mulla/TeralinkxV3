import { ref, onMounted, onUnmounted } from 'vue'
import Pusher from 'pusher-js'

const pusherInstance = ref(null)
const isConnected = ref(false)

export function usePusher() {
  const initPusher = (userId) => {
    if (pusherInstance.value) return pusherInstance.value

    pusherInstance.value = new Pusher(import.meta.env.VITE_PUSHER_KEY, {
      cluster: import.meta.env.VITE_PUSHER_CLUSTER || 'mt1',
      encrypted: true
    })

    pusherInstance.value.connection.bind('connected', () => {
      isConnected.value = true
      console.log('✅ Pusher connected')
    })

    pusherInstance.value.connection.bind('disconnected', () => {
      isConnected.value = false
      console.log('❌ Pusher disconnected')
    })

    return pusherInstance.value
  }

  const subscribe = (channelName, eventName, callback) => {
    if (!pusherInstance.value) {
      console.error('Pusher not initialized')
      return null
    }

    const channel = pusherInstance.value.subscribe(channelName)
    channel.bind(eventName, callback)
    
    return channel
  }

  const unsubscribe = (channelName) => {
    if (pusherInstance.value) {
      pusherInstance.value.unsubscribe(channelName)
    }
  }

  const disconnect = () => {
    if (pusherInstance.value) {
      pusherInstance.value.disconnect()
      pusherInstance.value = null
      isConnected.value = false
    }
  }

  return {
    pusherInstance,
    isConnected,
    initPusher,
    subscribe,
    unsubscribe,
    disconnect
  }
}

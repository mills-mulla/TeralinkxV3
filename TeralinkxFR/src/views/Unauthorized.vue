<!-- src/views/Unauthorized.vue - Unauthorized Access Page -->
<template>
  <div class="unauthorized-container">
    <div class="unauthorized-content">
      <!-- Icon -->
      <div class="unauthorized-icon">
        <svg width="120" height="120" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C13.1 2 14 2.9 14 4V8C15.1 8 16 8.9 16 10V20C16 21.1 15.1 22 14 22H10C8.9 22 8 21.1 8 20V10C8 8.9 8.9 8 10 8V4C10 2.9 10.9 2 12 2ZM12 4C11.4 4 11 4.4 11 5V8H13V5C13 4.4 12.6 4 12 4Z" fill="#ef4444"/>
          <circle cx="12" cy="12" r="10" stroke="#ef4444" stroke-width="2" fill="none" opacity="0.2"/>
        </svg>
      </div>

      <!-- Title -->
      <h1 class="unauthorized-title">Access Denied</h1>
      
      <!-- Message -->
      <p class="unauthorized-message">
        {{ message || 'You do not have permission to access this page.' }}
      </p>

      <!-- Details -->
      <div class="unauthorized-details" v-if="showDetails">
        <p><strong>Attempted URL:</strong> {{ attemptedUrl }}</p>
        <p><strong>Required Permission:</strong> {{ requiredPermission }}</p>
        <p><strong>Your Role:</strong> {{ userRole }}</p>
        <p><strong>Time:</strong> {{ new Date().toLocaleString() }}</p>
      </div>

      <!-- Actions -->
      <div class="unauthorized-actions">
        <button @click="goToDashboard" class="btn btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 20V14H14V20H19V12H22L12 3L2 12H5V20H10Z" fill="currentColor"/>
          </svg>
          Go to Dashboard
        </button>
        
        <button @click="goBack" class="btn btn-secondary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 11H7.83L13.42 5.41L12 4L4 12L12 20L13.41 18.59L7.83 13H20V11Z" fill="currentColor"/>
          </svg>
          Go Back
        </button>

        <button @click="contactSupport" class="btn btn-ghost">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 8L12 13L4 8V6L12 11L20 6V8Z" fill="currentColor"/>
          </svg>
          Contact Support
        </button>
      </div>

      <!-- Help Text -->
      <div class="unauthorized-help">
        <p>If you believe this is an error, please contact your administrator or try:</p>
        <ul>
          <li>Refreshing the page</li>
          <li>Logging out and logging back in</li>
          <li>Checking your account permissions</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth_resilient'
import { navigationHelpers } from '@/router/index_enhanced'

export default {
  name: 'Unauthorized',
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()

    // Computed properties
    const message = computed(() => {
      return route.query.error || 'You do not have permission to access this page.'
    })

    const attemptedUrl = computed(() => {
      return route.query.attempted || 'Unknown'
    })

    const requiredPermission = computed(() => {
      return route.query.permission || 'Unknown'
    })

    const userRole = computed(() => {
      return authStore.user?.role || 'User'
    })

    const showDetails = computed(() => {
      return import.meta.env.DEV || route.query.debug === 'true'
    })

    // Methods
    const goToDashboard = () => {
      navigationHelpers.goToDashboard()
    }

    const goBack = () => {
      navigationHelpers.goBack()
    }

    const contactSupport = () => {
      // Open email client or support page
      const subject = encodeURIComponent('Access Denied - Need Help')
      const body = encodeURIComponent(`
I'm having trouble accessing a page on TeralinkX.

Details:
- Attempted URL: ${attemptedUrl.value}
- Required Permission: ${requiredPermission.value}
- My Role: ${userRole.value}
- Time: ${new Date().toISOString()}
- User ID: ${authStore.user?.id || 'Unknown'}

Please help me resolve this access issue.
      `)
      
      window.open(`mailto:support@teralinkxwaves.uk?subject=${subject}&body=${body}`)
    }

    // Lifecycle
    onMounted(() => {
      // Log unauthorized access attempt
      console.warn('🚫 Unauthorized access attempt:', {
        url: attemptedUrl.value,
        user: authStore.user?.id,
        role: userRole.value,
        timestamp: new Date().toISOString()
      })

      // Set page title
      document.title = 'Access Denied - TeralinkX'
    })

    return {
      message,
      attemptedUrl,
      requiredPermission,
      userRole,
      showDetails,
      goToDashboard,
      goBack,
      contactSupport
    }
  }
}
</script>

<style scoped>
.unauthorized-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.unauthorized-content {
  background: white;
  border-radius: 16px;
  padding: 3rem 2rem;
  max-width: 500px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.unauthorized-icon {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
}

.unauthorized-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.unauthorized-message {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.unauthorized-details {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
  text-align: left;
  font-size: 0.875rem;
  color: #4b5563;
}

.unauthorized-details p {
  margin: 0.5rem 0;
}

.unauthorized-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
  transform: translateY(-1px);
}

.btn-ghost {
  background: transparent;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.btn-ghost:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.unauthorized-help {
  text-align: left;
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 1rem;
  font-size: 0.875rem;
  color: #92400e;
}

.unauthorized-help p {
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.unauthorized-help ul {
  margin: 0.5rem 0 0 1rem;
  padding: 0;
}

.unauthorized-help li {
  margin: 0.25rem 0;
}

@media (max-width: 640px) {
  .unauthorized-content {
    padding: 2rem 1rem;
  }
  
  .unauthorized-title {
    font-size: 1.5rem;
  }
  
  .unauthorized-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
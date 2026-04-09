<!-- src/views/NotFound.vue - 404 Page Not Found -->
<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <!-- Animated 404 -->
      <div class="not-found-number">
        <span class="digit">4</span>
        <span class="digit">0</span>
        <span class="digit">4</span>
      </div>

      <!-- Title -->
      <h1 class="not-found-title">Page Not Found</h1>
      
      <!-- Message -->
      <p class="not-found-message">
        The page you're looking for doesn't exist or has been moved.
      </p>

      <!-- Search -->
      <div class="not-found-search">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search for pages..."
            @keyup.enter="performSearch"
            class="search-input"
          >
          <button @click="performSearch" class="search-button">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
              <path d="21 21L16.65 16.65" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Suggestions -->
      <div class="not-found-suggestions">
        <h3>Popular Pages</h3>
        <div class="suggestion-grid">
          <router-link 
            v-for="page in popularPages" 
            :key="page.path"
            :to="page.path" 
            class="suggestion-card"
          >
            <div class="suggestion-icon">
              <component :is="page.icon" />
            </div>
            <div class="suggestion-content">
              <h4>{{ page.title }}</h4>
              <p>{{ page.description }}</p>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Actions -->
      <div class="not-found-actions">
        <button @click="goHome" class="btn btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <polyline points="9,22 9,12 15,12 15,22" stroke="currentColor" stroke-width="2"/>
          </svg>
          Go Home
        </button>
        
        <button @click="goBack" class="btn btn-secondary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="15,18 9,12 15,6" stroke="currentColor" stroke-width="2"/>
          </svg>
          Go Back
        </button>

        <button @click="reportIssue" class="btn btn-ghost">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 9V5C14 3.89543 13.1046 3 12 3C10.8954 3 10 3.89543 10 5V9M12 12V16M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          Report Issue
        </button>
      </div>

      <!-- Help Text -->
      <div class="not-found-help">
        <p>If you think this is a mistake, you can:</p>
        <ul>
          <li>Check the URL for typos</li>
          <li>Use the search box above</li>
          <li>Navigate using the menu</li>
          <li>Contact support if the problem persists</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// Icon components (simplified SVG icons)
const DashboardIcon = {
  template: `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
      <rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
      <rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
      <rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
    </svg>
  `
}

const ProfileIcon = {
  template: `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2"/>
      <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" fill="none"/>
    </svg>
  `
}

const SettingsIcon = {
  template: `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
      <path d="M19.4 15C19.2669 15.3016 19.2272 15.6362 19.286 15.9606C19.3448 16.285 19.4995 16.5843 19.73 16.82L19.79 16.88C19.976 17.0657 20.1235 17.2863 20.2241 17.5291C20.3248 17.7719 20.3766 18.0322 20.3766 18.295C20.3766 18.5578 20.3248 18.8181 20.2241 19.0609C20.1235 19.3037 19.976 19.5243 19.79 19.71C19.6043 19.896 19.3837 20.0435 19.1409 20.1441C18.8981 20.2448 18.6378 20.2966 18.375 20.2966C18.1122 20.2966 17.8519 20.2448 17.6091 20.1441C17.3663 20.0435 17.1457 19.896 16.96 19.71L16.9 19.65C16.6643 19.4195 16.365 19.2648 16.0406 19.206C15.7162 19.1472 15.3816 19.1869 15.08 19.32C14.7842 19.4468 14.532 19.6572 14.3543 19.9255C14.1766 20.1938 14.0813 20.5082 14.08 20.83V21C14.08 21.5304 13.8693 22.0391 13.4942 22.4142C13.1191 22.7893 12.6104 23 12.08 23C11.5496 23 11.0409 22.7893 10.6658 22.4142C10.2907 22.0391 10.08 21.5304 10.08 21V20.91C10.0723 20.579 9.96512 20.2573 9.77251 19.9887C9.5799 19.7201 9.31074 19.5176 9 19.41C8.69838 19.2769 8.36381 19.2372 8.03941 19.296C7.71502 19.3548 7.41568 19.5095 7.18 19.74L7.12 19.8C6.93425 19.986 6.71368 20.1335 6.47088 20.2341C6.22808 20.3348 5.96783 20.3866 5.705 20.3866C5.44217 20.3866 5.18192 20.3348 4.93912 20.2341C4.69632 20.1335 4.47575 19.986 4.29 19.8C4.10405 19.6143 3.95653 19.3937 3.85588 19.1509C3.75523 18.9081 3.70343 18.6478 3.70343 18.385C3.70343 18.1222 3.75523 17.8619 3.85588 17.6191C3.95653 17.3763 4.10405 17.1557 4.29 16.97L4.35 16.91C4.58054 16.6743 4.73519 16.375 4.794 16.0506C4.85282 15.7262 4.81312 15.3916 4.68 15.09C4.55324 14.7942 4.34276 14.542 4.07447 14.3643C3.80618 14.1866 3.49179 14.0913 3.17 14.09H3C2.46957 14.09 1.96086 13.8793 1.58579 13.5042C1.21071 13.1291 1 12.6204 1 12.09C1 11.5596 1.21071 11.0509 1.58579 10.6758C1.96086 10.3007 2.46957 10.09 3 10.09H3.09C3.42099 10.0823 3.742 9.97512 4.01062 9.78251C4.27925 9.5899 4.48167 9.32074 4.59 9.01C4.72312 8.70838 4.76282 8.37381 4.704 8.04941C4.64519 7.72502 4.49054 7.42568 4.26 7.19L4.2 7.13C4.01405 6.94425 3.86653 6.72368 3.76588 6.48088C3.66523 6.23808 3.61343 5.97783 3.61343 5.715C3.61343 5.45217 3.66523 5.19192 3.76588 4.94912C3.86653 4.70632 4.01405 4.48575 4.2 4.3C4.38575 4.11405 4.60632 3.96653 4.84912 3.86588C5.09192 3.76523 5.35217 3.71343 5.615 3.71343C5.87783 3.71343 6.13808 3.76523 6.38088 3.86588C6.62368 3.96653 6.84425 4.11405 7.03 4.3L7.09 4.36C7.32568 4.59054 7.62502 4.74519 7.94941 4.804C8.27381 4.86282 8.60838 4.82312 8.91 4.69H9C9.29577 4.56324 9.54802 4.35276 9.72569 4.08447C9.90337 3.81618 9.99872 3.50179 10 3.18V3C10 2.46957 10.2107 1.96086 10.5858 1.58579C10.9609 1.21071 11.4696 1 12 1C12.5304 1 13.0391 1.21071 13.4142 1.58579C13.7893 1.96086 14 2.46957 14 3V3.09C14.0013 3.41179 14.0966 3.72618 14.2743 3.99447C14.452 4.26276 14.7042 4.47324 15 4.6C15.3016 4.73312 15.6362 4.77282 15.9606 4.714C16.285 4.65519 16.5843 4.50054 16.82 4.27L16.88 4.21C17.0657 4.02405 17.2863 3.87653 17.5291 3.77588C17.7719 3.67523 18.0322 3.62343 18.295 3.62343C18.5578 3.62343 18.8181 3.67523 19.0609 3.77588C19.3037 3.87653 19.5243 4.02405 19.71 4.21C19.896 4.39575 20.0435 4.61632 20.1441 4.85912C20.2448 5.10192 20.2966 5.36217 20.2966 5.625C20.2966 5.88783 20.2448 6.14808 20.1441 6.39088C20.0435 6.63368 19.896 6.85425 19.71 7.04L19.65 7.1C19.4195 7.33568 19.2648 7.63502 19.206 7.95941C19.1472 8.28381 19.1869 8.61838 19.32 8.92V9C19.4468 9.29577 19.6572 9.54802 19.9255 9.72569C20.1938 9.90337 20.5082 9.99872 20.83 10H21C21.5304 10 22.0391 10.2107 22.4142 10.5858C22.7893 10.9609 23 11.4696 23 12C23 12.5304 22.7893 13.0391 22.4142 13.4142C22.0391 13.7893 21.5304 14 21 14H20.91C20.5882 14.0013 20.2738 14.0966 20.0055 14.2743C19.7372 14.452 19.5268 14.7042 19.4 15Z" stroke="currentColor" stroke-width="2"/>
    </svg>
  `
}

const HelpIcon = {
  template: `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
      <path d="M9.09 9C9.3251 8.33167 9.78915 7.76811 10.4 7.40913C11.0108 7.05016 11.7289 6.91894 12.4272 7.03871C13.1255 7.15849 13.7588 7.52152 14.2151 8.06353C14.6713 8.60553 14.9211 9.29152 14.92 10C14.92 12 11.92 13 11.92 13" stroke="currentColor" stroke-width="2"/>
      <circle cx="12" cy="17" r="1" fill="currentColor"/>
    </svg>
  `
}

export default {
  name: 'NotFound',
  
  components: {
    DashboardIcon,
    ProfileIcon,
    SettingsIcon,
    HelpIcon
  },
  
  setup() {
    const router = useRouter()
    const route = useRoute()
    const searchQuery = ref('')

    // Popular pages data
    const popularPages = ref([
      {
        path: '/dashboard',
        title: 'Dashboard',
        description: 'View your account overview and statistics',
        icon: 'DashboardIcon'
      },
      {
        path: '/profile',
        title: 'Profile',
        description: 'Manage your account information',
        icon: 'ProfileIcon'
      },
      {
        path: '/settings',
        title: 'Settings',
        description: 'Configure your preferences',
        icon: 'SettingsIcon'
      },
      {
        path: '/faq',
        title: 'Help & FAQ',
        description: 'Get answers to common questions',
        icon: 'HelpIcon'
      }
    ])

    // Methods
    const goHome = () => {
      router.push('/')
    }

    const goBack = () => {
      if (window.history.length > 1) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }

    const performSearch = () => {
      if (!searchQuery.value.trim()) return

      // Simple search logic - redirect to dashboard with search query
      router.push({
        path: '/dashboard',
        query: { search: searchQuery.value }
      })
    }

    const reportIssue = () => {
      const subject = encodeURIComponent('404 Error Report')
      const body = encodeURIComponent(`
I encountered a 404 error on TeralinkX.

Details:
- URL: ${window.location.href}
- Attempted Path: ${route.path}
- Referrer: ${document.referrer || 'Direct access'}
- Time: ${new Date().toISOString()}
- User Agent: ${navigator.userAgent}

Please investigate this broken link.
      `)
      
      window.open(`mailto:support@teralinkxwaves.uk?subject=${subject}&body=${body}`)
    }

    // Lifecycle
    onMounted(() => {
      document.title = 'Page Not Found - TeralinkX'
      
      // Log 404 for analytics
      console.warn('404 Page Not Found:', {
        path: route.path,
        fullPath: route.fullPath,
        referrer: document.referrer,
        timestamp: new Date().toISOString()
      })

      // Track 404 in analytics if available
      if (typeof gtag !== 'undefined') {
        gtag('event', 'page_not_found', {
          page_path: route.path,
          page_referrer: document.referrer
        })
      }
    })

    return {
      searchQuery,
      popularPages,
      goHome,
      goBack,
      performSearch,
      reportIssue
    }
  }
}
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.not-found-content {
  background: white;
  border-radius: 16px;
  padding: 3rem 2rem;
  max-width: 700px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.not-found-number {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.digit {
  font-size: 6rem;
  font-weight: 900;
  color: #3b82f6;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  animation: bounce 2s ease-in-out infinite;
}

.digit:nth-child(2) {
  animation-delay: 0.2s;
}

.digit:nth-child(3) {
  animation-delay: 0.4s;
}

.not-found-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.not-found-message {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.not-found-search {
  margin-bottom: 3rem;
}

.search-box {
  display: flex;
  max-width: 400px;
  margin: 0 auto;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.2s ease;
}

.search-box:focus-within {
  border-color: #3b82f6;
}

.search-input {
  flex: 1;
  padding: 1rem;
  border: none;
  outline: none;
  font-size: 1rem;
}

.search-button {
  padding: 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.search-button:hover {
  background: #2563eb;
}

.not-found-suggestions {
  margin-bottom: 3rem;
  text-align: left;
}

.not-found-suggestions h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
  text-align: center;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.suggestion-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
}

.suggestion-card:hover {
  border-color: #3b82f6;
  background: #f8fafc;
  transform: translateY(-2px);
}

.suggestion-icon {
  color: #3b82f6;
  flex-shrink: 0;
}

.suggestion-content h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.suggestion-content p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.not-found-actions {
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

.not-found-help {
  text-align: left;
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 8px;
  padding: 1rem;
  font-size: 0.875rem;
  color: #0c4a6e;
}

.not-found-help p {
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.not-found-help ul {
  margin: 0.5rem 0 0 1rem;
  padding: 0;
}

.not-found-help li {
  margin: 0.25rem 0;
}

/* Animations */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

@media (max-width: 640px) {
  .not-found-content {
    padding: 2rem 1rem;
  }
  
  .not-found-number {
    gap: 0.5rem;
  }
  
  .digit {
    font-size: 4rem;
  }
  
  .not-found-title {
    font-size: 1.5rem;
  }
  
  .suggestion-grid {
    grid-template-columns: 1fr;
  }
  
  .not-found-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
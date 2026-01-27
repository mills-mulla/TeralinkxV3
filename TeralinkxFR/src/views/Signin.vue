<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white to-blue-100 dark:from-slate-900 dark:to-slate-800 px-4">
    <!-- Developer Tools Toggle (Top Right) -->
    <div class="absolute top-4 right-4">
      <button
        @click="showDevTools = !showDevTools"
        class="p-2 bg-slate-800 dark:bg-slate-700 text-white rounded-lg text-xs font-mono hover:bg-slate-900 transition"
        title="Toggle Developer Tools"
      >
        DEV
      </button>
    </div>

    <div class="w-full max-w-md bg-white dark:bg-slate-900 shadow-xl rounded-2xl overflow-hidden animate-fadeIn">
      <!-- Logo -->
      <div class="bg-white dark:bg-slate-900 p-6 flex justify-center">
        <img src="../assets/teralinkx2.png" alt="Teralinkx Waves Logo" class="h-60 object-contain" />
      </div>

      <form @submit.prevent="signin" class="p-6 space-y-6">
        <h1 class="text-2xl font-bold text-center text-slate-900 dark:text-white">Welcome to Teralinkx</h1>

        <!-- Developer Info Panel (Hidden by default) -->
        <div v-if="showDevTools" class="p-3 rounded-lg bg-slate-900 dark:bg-black border border-slate-700">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-mono text-white">DEV INFO</h3>
            <button @click="copyDevInfo" class="text-xs text-blue-400 hover:text-blue-300">
              COPY
            </button>
          </div>
          <div class="text-xs font-mono text-slate-300 space-y-1">
            <div>Env: {{ envName }}</div>
            <div>API: {{ apiBaseUrl }}</div>
            <div>Hotspot: {{ hasHotspotData ? 'YES' : 'NO' }}</div>
            <div>IP: {{ ip_addr || 'null' }}</div>
            <div>MAC: {{ mac_addr || 'null' }}</div>
            <div>Session: {{ devSessionId?.slice(0, 8) || 'null' }}</div>
          </div>
        </div>

        <!-- Status Indicators -->
        <div class="space-y-4">
          <!-- Connection Status -->
          <div v-if="!ip_addr || !mac_addr" class="p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div class="w-3 h-3 rounded-full bg-yellow-500 animate-pulse"></div>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-yellow-800 dark:text-yellow-300">
                  {{ getConnectionStatusMessage() }}
                </p>
                <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                  Ensure you're connected to Teralinkx WiFi
                </p>
              </div>
              <button 
                v-if="showDevTools"
                @click="simulateMikrotikData" 
                class="text-xs px-2 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                title="Simulate Mikrotik Data"
              >
                SIM
              </button>
            </div>
          </div>

          <!-- Connected Status -->
          <div v-if="ip_addr && mac_addr" class="p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-green-800 dark:text-green-300">
                  Connected to Teralinkx
                </p>
                <p class="text-xs text-green-600 dark:text-green-400 mt-1">
                  Ready to authenticate
                </p>
              </div>
              <button 
                v-if="showDevTools"
                @click="testBackendConnection" 
                class="text-xs px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                title="Test Backend"
              >
                TEST
              </button>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-red-800 dark:text-red-300">
                {{ error }}
              </p>
            </div>
            <button 
              v-if="showDevTools && error"
              @click="clearError" 
              class="text-xs px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700"
              title="Clear Error"
            >
              CLEAR
            </button>
          </div>
        </div>

        <!-- Phone Input -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-slate-900 dark:text-white">
            Phone Number
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span class="text-slate-500 dark:text-slate-400">+254</span>
            </div>
            <input
              v-model="phone"
              type="tel"
              placeholder="712345678"
              @input="validatePhoneNumber"
              :disabled="loading"
              class="w-full pl-14 px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:opacity-50 disabled:cursor-not-allowed"
              maxlength="9"
            />
            <!-- Test Phone Numbers (Dev Only) -->
            <div v-if="showDevTools" class="absolute right-2 top-1/2 transform -translate-y-1/2">
              <select 
                @change="setTestPhone"
                class="text-xs bg-slate-700 text-white rounded px-1 py-0.5"
              >
                <option value="">Test Phones</option>
                <option value="712345678">712345678</option>
                <option value="723456789">723456789</option>
                <option value="734567890">734567890</option>
              </select>
            </div>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            Enter your 9-digit phone number (without 0)
          </p>
        </div>

        <!-- Connection Info (Collapsible) -->
        <div v-if="ip_addr && mac_addr" class="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
          <button
            type="button"
            @click="showConnectionDetails = !showConnectionDetails"
            class="w-full px-4 py-3 flex items-center justify-between text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
          >
            <span>Connection Details</span>
            <svg
              class="w-4 h-4 transition-transform"
              :class="{ 'rotate-180': showConnectionDetails }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>
          
          <div v-if="showConnectionDetails" class="px-4 py-3 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-700">
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="text-slate-500 dark:text-slate-400">IP Address:</div>
              <div class="font-mono text-slate-900 dark:text-white truncate">{{ ip_addr }}</div>
              
              <div class="text-slate-500 dark:text-slate-400">MAC Address:</div>
              <div class="font-mono text-slate-900 dark:text-white truncate">{{ mac_addr }}</div>
              
              <div class="text-slate-500 dark:text-slate-400">Source:</div>
              <div class="font-mono text-slate-900 dark:text-white">{{ networkSource }}</div>
              
              <div class="text-slate-500 dark:text-slate-400">Hotspot Data:</div>
              <div class="font-mono text-slate-900 dark:text-white">{{ hasHotspotData ? 'Available' : 'Missing' }}</div>
            </div>
          </div>
        </div>

        <!-- Sign In Button -->
        <button
          type="submit"
          :disabled="!ip_addr || !mac_addr || loading || !phone"
          class="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl active:scale-[0.98]"
        >
          <span v-if="loading" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Signing In...
          </span>
          <span v-else class="flex items-center justify-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
            </svg>
            Sign In
          </span>
        </button>

        <!-- Test Authentication Button (Dev Only) -->
        <div v-if="showDevTools" class="flex space-x-2">
          <button
            @click="testAuthentication('success')"
            class="flex-1 py-2 px-3 bg-green-600 hover:bg-green-700 text-white text-xs font-mono rounded"
          >
            TEST SUCCESS
          </button>
          <button
            @click="testAuthentication('error')"
            class="flex-1 py-2 px-3 bg-red-600 hover:bg-red-700 text-white text-xs font-mono rounded"
          >
            TEST ERROR
          </button>
        </div>

        <!-- Help Text -->
        <p class="text-center text-xs text-slate-500 dark:text-slate-400">
          By signing in, you agree to our 
          <a href="#" class="text-blue-600 dark:text-blue-400 hover:underline">Terms of Service</a> and 
          <a href="#" class="text-blue-600 dark:text-blue-400 hover:underline">Privacy Policy</a>
        </p>
      </form>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">
        <p class="text-center text-xs text-slate-500 dark:text-slate-400">
          Need help? 
          <a href="#" class="text-blue-600 dark:text-blue-400 hover:underline">Contact Support</a>
        </p>
        <!-- Dev Version Info -->
        <p v-if="showDevTools" class="text-center text-xs text-slate-500 dark:text-slate-400 mt-2">
          Dev Mode: {{ appVersion }}
        </p>
      </div>
    </div>

    <!-- Developer Console Modal -->
    <div v-if="showDevConsole" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div class="bg-slate-900 rounded-xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
        <div class="flex items-center justify-between p-4 border-b border-slate-700">
          <h3 class="text-white font-mono">Developer Console</h3>
          <button @click="showDevConsole = false" class="text-slate-400 hover:text-white">
            ✕
          </button>
        </div>
        <div class="p-4 font-mono text-xs text-green-400 h-96 overflow-y-auto bg-black">
          <div v-for="(log, index) in devLogs" :key="index" class="mb-1">
            [{{ log.timestamp }}] {{ log.message }}
          </div>
        </div>
        <div class="p-4 border-t border-slate-700">
          <button @click="clearLogs" class="text-xs px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600">
            Clear Logs
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'signIn',
  data() {
    return {
      phone: '',
      ip_addr: '',
      mac_addr: '',
      error: '',
      loading: false,
      showConnectionDetails: false,
      showDevTools: false, // Toggle with DEV button
      showDevConsole: false,
      networkSource: 'Unknown',
      hasHotspotData: false,
      devSessionId: null,
      devLogs: [],
      appVersion: '1.0.0-dev'
    };
  },
  computed: {
    envName() {
      return import.meta.env.MODE || 'development';
    },
    apiBaseUrl() {
      return import.meta.env.VITE_API_BASE_URL || 'not-set';
    }
  },
  mounted() {
    this.log('Component mounted');
    
    // Check for existing session
    this.checkExistingSession();
    
    // Initialize network detection
    this.initializeNetwork();
    
    // Generate session ID
    this.devSessionId = this.generateSessionId();
    
    // Check for hotkey (Shift+D for dev tools)
    document.addEventListener('keydown', (e) => {
      if (e.shiftKey && e.key === 'D') {
        this.showDevTools = !this.showDevTools;
        this.log(`Dev tools ${this.showDevTools ? 'enabled' : 'disabled'}`);
      }
    });
  },
  created() {
    // Check URL for dev parameters
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('dev') === 'true') {
      this.showDevTools = true;
      this.log('Developer mode enabled via URL parameter');
    }
  },
  methods: {
    log(message) {
      const logEntry = {
        timestamp: new Date().toLocaleTimeString(),
        message: message
      };
      this.devLogs.unshift(logEntry);
      // Keep only last 50 logs
      if (this.devLogs.length > 50) {
        this.devLogs.pop();
      }
      console.log(`[Teralinkx] ${message}`);
    },

    getConnectionStatusMessage() {
      if (!this.ip_addr) return 'Detecting IP address...';
      if (!this.mac_addr) return 'Detecting MAC address...';
      return 'Connecting...';
    },

    checkExistingSession() {
      const token = localStorage.getItem('authToken');
      const account = localStorage.getItem('account');

      if (token && account) {
        this.log(`Existing session found for ${account}`);
        window.location.href = `/index.html#/dashboard`;
        return;
      }
    },

    initializeNetwork() {
      this.log('Initializing network detection...');
      
      // 1. Check for Mikrotik hotspot data
      if (window.$hotspot) {
        this.ip_addr = window.$hotspot.ip || '';
        this.mac_addr = window.$hotspot.mac || '';
        this.hasHotspotData = !!(window.$hotspot.ip && window.$hotspot.mac);
        this.networkSource = 'Mikrotik Hotspot';
        
        this.log(`Mikrotik data: IP=${this.ip_addr}, MAC=${this.mac_addr}`);
        
        if (this.hasHotspotData) {
          this.log('✅ Mikrotik hotspot data available');
          return;
        }
      }
      
      // 2. Fallback to WebRTC detection
      this.log('No Mikrotik data, trying WebRTC detection...');
      this.getLocalIPAddress()
        .then(ip => {
          this.ip_addr = ip;
          this.mac_addr = this.generatePlaceholderMac();
          this.networkSource = 'WebRTC Detection';
          this.log(`WebRTC IP: ${ip}, Generated MAC: ${this.mac_addr}`);
        })
        .catch(err => {
          this.log(`WebRTC failed: ${err}`);
          this.error = 'Unable to detect network. Please reconnect.';
        });
    },

    getLocalIPAddress() {
      return new Promise((resolve, reject) => {
        const pc = new RTCPeerConnection({ iceServers: [] });
        pc.createDataChannel('');
        pc.createOffer().then(offer => pc.setLocalDescription(offer));

        pc.onicecandidate = e => {
          if (e.candidate && e.candidate.candidate) {
            const ipMatch = e.candidate.candidate.match(/([0-9]{1,3}\.){3}[0-9]{1,3}/);
            if (ipMatch) {
              pc.close();
              resolve(ipMatch[0]);
            }
          }
        };

        setTimeout(() => {
          pc.close();
          reject('IP address timeout');
        }, 3000);
      });
    },

    generatePlaceholderMac() {
      const sessionKey = sessionStorage.getItem('session_key') || Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('session_key', sessionKey);
      
      const hash = this.hashString(sessionKey);
      return `02:00:00:${hash.slice(0,2)}:${hash.slice(2,4)}:${hash.slice(4,6)}`.toUpperCase();
    },

    hashString(str) {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash = hash & hash;
      }
      return Math.abs(hash).toString(16).padStart(6, '0');
    },

    validatePhoneNumber() {
      const cleaned = this.phone.replace(/\D/g, '');
      this.phone = cleaned;
      
      if (cleaned && cleaned.length !== 9) {
        this.error = 'Phone number must be 9 digits (without 0)';
      } else {
        this.error = '';
      }
    },

    async getCSRFToken() {
      try {
        this.log('Fetching CSRF token...');
        const res = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/cross/`);
        this.log(`CSRF token received`);
        return res.data.csrf_token;
      } catch (err) {
        this.log(`CSRF token error: ${err.message}`);
        throw new Error('Failed to fetch CSRF token');
      }
    },

    async signin() {
      this.log(`Sign in attempt with phone: ${this.phone}`);
      this.error = '';
      this.loading = true;

      if (!this.ip_addr || !this.mac_addr) {
        this.error = 'Network information missing. Please reconnect.';
        this.loading = false;
        return;
      }

      const csrfToken = await this.getCSRFToken().catch(err => {
        this.error = 'Could not get security token.';
        this.loading = false;
        return null;
      });
      if (!csrfToken) return;

      const formattedPhone = this.phone.startsWith('0') ? '254' + this.phone.slice(1) : this.phone;

      const payload = {
        phone: formattedPhone,
        current_ip: this.ip_addr,
        current_mac: this.mac_addr
      };

      this.log(`Sending auth payload: ${JSON.stringify(payload)}`);

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/api/clients/`,
          payload,
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken
            }
          }
        );

        this.log(`Auth response: ${response.status}`);
        
        if (response.status === 200 || response.status === 201) {
          const { token, account, user_id } = response.data;
          
          localStorage.setItem('authToken', token);
          localStorage.setItem('account', account);
          localStorage.setItem('ping', user_id);
          
          this.log(`Authentication successful for ${account}`);
          
          window.location.href = `/index.html#/dashboard?acc=${encodeURIComponent(account)}`;
        } else {
          this.error = 'Please connect to the Teralinkx network!';
          this.log(`Auth failed with status: ${response.status}`);
        }
      } catch (err) {
        this.log(`Auth error: ${err.message}`);
        if (err.response) {
          switch (err.response.status) {
            case 400:
              this.error = 'Invalid request. Please check your phone number.';
              break;
            case 401:
              this.error = 'Authentication failed. Please try again.';
              break;
            case 500:
              this.error = 'Server error. Please try again later.';
              break;
            default:
              this.error = 'Network error. Ensure you are connected to Teralinkx.';
          }
          this.log(`Server error ${err.response.status}: ${err.response.data}`);
        } else {
          this.error = 'Network error. Ensure you are connected to Teralinkx.';
        }
      } finally {
        this.loading = false;
      }
    },

    // ========== DEVELOPER TOOLS ==========
    
    simulateMikrotikData() {
      this.log('Simulating Mikrotik hotspot data...');
      window.$hotspot = {
        ip: '192.168.88.' + Math.floor(Math.random() * 100 + 100),
        mac: this.generateRandomMac()
      };
      this.ip_addr = window.$hotspot.ip;
      this.mac_addr = window.$hotspot.mac;
      this.hasHotspotData = true;
      this.networkSource = 'Simulated Mikrotik';
      this.log(`Simulated: IP=${this.ip_addr}, MAC=${this.mac_addr}`);
    },

    generateRandomMac() {
      const hex = '0123456789ABCDEF';
      let mac = '02:00:00:';
      for (let i = 0; i < 6; i++) {
        mac += hex[Math.floor(Math.random() * 16)];
        if (i % 2 === 1 && i < 5) mac += ':';
      }
      return mac;
    },

    testBackendConnection() {
      this.log('Testing backend connection...');
      axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/network-info/`, { timeout: 3000 })
        .then(response => {
          this.log(`✅ Backend connected: ${response.status}`);
          alert(`Backend OK!\nIP: ${response.data.ip}\nStatus: ${response.status}`);
        })
        .catch(error => {
          this.log(`❌ Backend error: ${error.message}`);
          alert(`Backend Error: ${error.message}`);
        });
    },

    setTestPhone(event) {
      if (event.target.value) {
        this.phone = event.target.value;
        this.log(`Test phone set: ${this.phone}`);
      }
    },

    testAuthentication(type) {
      if (type === 'success') {
        this.log('Testing successful authentication...');
        // Simulate success
        const mockAccount = '254' + (this.phone || '712345678');
        localStorage.setItem('authToken', 'test_token_' + Date.now());
        localStorage.setItem('account', mockAccount);
        localStorage.setItem('ping', 'test_user_123');
        alert(`Test authentication successful!\nAccount: ${mockAccount}\nCheck localStorage for test data.`);
      } else {
        this.log('Testing authentication error...');
        this.error = 'Test error: Simulated authentication failure';
      }
    },

    clearError() {
      this.error = '';
      this.log('Error cleared');
    },

    copyDevInfo() {
      const info = {
        env: this.envName,
        api: this.apiBaseUrl,
        ip: this.ip_addr,
        mac: this.mac_addr,
        source: this.networkSource,
        session: this.devSessionId,
        hotspot: this.hasHotspotData
      };
      navigator.clipboard.writeText(JSON.stringify(info, null, 2));
      this.log('Developer info copied to clipboard');
      alert('Developer info copied!');
    },

    clearLogs() {
      this.devLogs = [];
      this.log('Logs cleared');
    },

    generateSessionId() {
      const timestamp = Date.now().toString(36);
      const random = Math.random().toString(36).substr(2, 9);
      return `dev_${timestamp}_${random}`;
    }
  }
};
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.rotate-180 {
  transform: rotate(180deg);
}

/* Scrollbar for dev console */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #1e293b;
}
::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
</style>
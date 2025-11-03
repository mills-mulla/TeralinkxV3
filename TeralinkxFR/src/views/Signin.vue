<template>
 
  <div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white to-blue-100 dark:from-slate-900 dark:to-slate-800 px-4">
    <div class="w-full max-w-md bg-white dark:bg-slate-900 shadow-xl rounded-2xl overflow-hidden animate-fadeIn">
      <div class="bg-white p-6 flex justify-center">
        <img src="../assets/teralinkx2.png" alt="Teralinkx Waves Logo" class="h-60 object-contain" />
      </div>

      <form @submit.prevent="signin" class="p-6 space-y-5">
        <h1 class="text-2xl font-bold text-center text-slate-900 dark:text-white">Sign In</h1>

        <p v-if="!error" class="text-center text-sm text-gray-700 dark:text-gray-300">
          Please enter your <span class="font-semibold">Active Phone number</span> to sign in.
        </p>

        <p v-if="error" class="text-center text-sm font-semibold text-red-500">
          {{ error }}
        </p>

        <label class="block">
          <input
            v-model="phone"
            type="text"
            placeholder="0712345678"
            @input="validatePhoneNumber"
            class="w-full px-4 py-2 rounded-md border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </label>

        <p v-if="!ip_addr || !mac_addr" class="text-center text-yellow-600 dark:text-yellow-400 text-sm">
          {{ !ip_addr ? 'Reconnecting' : '' }}{{ !mac_addr ? '....' : '' }}
        </p>

        <button
          id="cbutton"
          type="submit"
          :disabled="!ip_addr || !mac_addr || loading"
          class="w-full py-2 px-4 bg-blue-700 hover:bg-blue-900 text-white font-medium rounded-md transition duration-300 disabled:opacity-50"
        >
          {{ loading ? 'Signing In...' : 'Sign In' }}
        </button>
      </form>
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
      loading: false
    };
  },
 
  mounted() {
    // console.log('MAC:', this.$hotspot.mac); 
    // console.log('IP:', this.$hotspot.ip);
  },
  created() {
    const token = localStorage.getItem('authToken');
    const account = localStorage.getItem('account');

    if (token && account) {
      window.location.href = `/index.html#/dashboard`;
      return;
    }

    const query = new URLSearchParams(window.location.search);
    this.ip_addr = this.$hotspot.ip //localStorage.getItem('hs_ip');
    this.mac_addr = this.$hotspot.mac //localStorage.getItem('hs_mac');

    if (!this.ip_addr) {
      this.getLocalIPAddress()
        .then(ip => {
          this.ip_addr = ip;
          localStorage.setItem('ip_addr', ip);
        })
        .catch(err => {
          console.error(err);
          this.error = 'Network error';
        });
    }

    // localStorage.setItem('mac_addr', this.mac_addr);
    // sessionStorage.setItem('mac_addr', this.mac_addr);
  },
  methods: {
    validatePhoneNumber() {
      const cleaned = this.phone.replace(/\D/g, '');
      this.phone = cleaned;
      if (cleaned.length !== 10) {
        this.error = 'Phone number must be 10 digits.';
      } else {
        this.error = '';
      }
    },

    getLocalIPAddress() {
      return new Promise((resolve, reject) => {
        const pc = new RTCPeerConnection({ iceServers: [] });
        pc.createDataChannel('');
        pc.createOffer().then(offer => pc.setLocalDescription(offer));

        pc.onicecandidate = e => {
          if (e.candidate && e.candidate.candidate) {
            const ipMatch = e.candidate.candidate.match(/([0-9]{1,3}\.){3}[0-9]{1,3}/);
            if (ipMatch) resolve(ipMatch[0]);
          }
        };

        setTimeout(() => reject('IP address timeout'), 3000);
      });
    },

    async getCSRFToken() {
      try {
        const res = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/get-csrf-token/`);
        return res.data.csrf_token;
      } catch (err) {
        throw new Error('Failed to fetch CSRF token');
      }
    },

    async signin() {
      this.error = ''; // Reset previous error
      this.loading = true;

      if (!this.ip_addr || !this.mac_addr) {
        this.error = 'IP or MAC address is missing.';
        this.loading = false;
        return;
      }

      const csrfToken = await this.getCSRFToken().catch(err => {
        console.error(err);
        this.error = 'Could not get CSRF token.';
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

        if (response.status === 200 || response.status === 201) {
          const { token, account, user_id } = response.data;

          localStorage.setItem('authToken', token);
          localStorage.setItem('account', account);
          localStorage.setItem('ping', user_id);

          window.location.href = `/index.html#/dashboard?acc=${encodeURIComponent(account)}`;
        } else {
          this.error = 'Please connect to the Teralinkx network!';
        }
      } catch (err) {
        this.error = 'Network error. Ensure you are connected to Teralinkx.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>




<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.7s ease-out forwards;
}
</style>
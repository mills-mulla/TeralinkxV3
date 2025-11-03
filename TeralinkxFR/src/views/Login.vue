<template>
  <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
  <div class="flex flex-col items-center mt-8 my-auto px-4">
    <div class="bg-[#98AFC7] rounded-lg shadow-lg p-6 w-full max-w-lg animate-fadeIn">
      <!-- Logo -->
      <div class="text-center p-2 rounded-t-lg">
        <img src="@/assets/teralinkx2.png" alt="Logo" class="mx-auto w-2/4" />
      </div>

      <!-- Voucher Login Form -->
      <form @submit.prevent="login" class="mt-4">
        <h1 class="text-xl font-bold text-[#023016] text-center">Enter Voucher</h1>

        <p v-if="!error" class="text-center text-black mt-2">
          If not automatically connected, <b>Enter</b> your <b>Voucher Code</b> from your
          <b>Active package</b> list to connect.
        </p>

        <p v-else class="text-center text-red-600 mt-2">{{ error }}</p>

        <input
          v-model="voucherCode"
          type="text"
          placeholder="Voucher Code"
          class="w-full border border-gray-300 rounded-md px-3 py-2 mt-4 focus:outline-none focus:ring-2 focus:ring-[#030B18]"
        />

        <button
          type="submit"
          class="w-full bg-[#28416D] hover:bg-[#030B18] text-white rounded-md py-2 mt-4 font-semibold"
        >
          Connect
        </button>
      </form>
    </div>


  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCsrfTokenStore } from '@/stores/useCsrf' 
import NavBar from '@/components/NavBar.vue'
import axios from 'axios'

const voucherCode = ref('')
const error = ref('')
const csrfStore = useCsrfTokenStore() // actual csrf store instance

async function login() {
  try {
    const payload = {
      account: localStorage.getItem('account'),
      voucher_code: voucherCode.value,
      bound_mac: localStorage.getItem('mac_addr'),
    }

    const res = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL}/api/connect/`,
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfStore.csrfToken, // from csrf store
          Authorization: `Token ${localStorage.getItem('authToken')}`,
        },
      }
    )

    if (res.status === 200) {
      window.location.href = '#/connected'
    } else {
      error.value = res.data.answer || res.data.error || 'Unknown error'
    }
  } catch (err) {
    error.value = err.response?.data?.error || err.message
  }
}
</script>


<style>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10%); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.8s ease-in-out forwards;
}
</style>

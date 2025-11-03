<template>
  <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
  <div class="max-w-lg mx-auto p-6 bg-white dark:bg-gray-800 shadow-md rounded-lg mt-20">
    <h2 class="text-xl font-bold mb-6 text-gray-900 dark:text-gray-100">My Profile</h2>

   

    <!-- Profile Image Upload -->
    <div class="flex flex-col items-center mb-6">
    <img
        :src="previewImage || accountStore.userImage"
        alt="Profile"
        class="w-24 h-24 rounded-full object-cover border-4 border-green-500 shadow mb-2"
    />
    <input type="file" @change="handleImageChange" accept="image/*" />
    </div>


    <!-- Editable Username -->
    <div class="mb-4">
      <label class="block text-gray-700 dark:text-gray-300 font-medium mb-1">Username</label>
      <input
        v-model="editedClient"
        type="text"
        class="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:text-white"
      />
    </div>

    <!-- Balance -->
    <div class="mb-4">
      <label class="block text-gray-700 dark:text-gray-300 font-medium mb-1">Balance</label>
      <p class="text-lg font-semibold text-green-600">{{ accountStore.balance }}</p>
    </div>

    <!-- Status -->
    <div class="mb-4">
      <label class="block text-gray-700 dark:text-gray-300 font-medium mb-1">Status</label>
      <span
        :class="[
          'px-3 py-1 rounded-full text-sm font-medium',
          accountStore.isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        ]"
      >
        {{ accountStore.status }}
      </span>
    </div>

    <!-- Buttons -->
    <div class="flex justify-between">
      <button
        @click="saveProfile"
        :disabled="saving"
        class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
      >
        {{ saving ? 'Saving...' : 'Save Changes' }}
      </button>
     
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAccountStore } from '@/stores/useAccountStore'
import NavBar from '@/components/NavBar.vue'

const accountStore = useAccountStore()
const editedClient = ref(accountStore.client)
const saving = ref(false)

onMounted(() => {
  accountStore.fetchAccountInfo()
})

// Save new username to server
const previewImage = ref(null)
const selectedImageFile = ref(null)

const handleImageChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedImageFile.value = file
    previewImage.value = URL.createObjectURL(file)
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('first_name', editedClient.value)
    if (selectedImageFile.value) {
      formData.append('image', selectedImageFile.value)
    }

    const response = await axios.patch(
      `${import.meta.env.VITE_API_BASE_URL}/api/update-profile/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Token ${localStorage.getItem('authToken')}`,
        },
      }
    )

    if (response.status === 200) {
      accountStore.client = editedClient.value
      if (response.data.image) {
        accountStore.userImage = response.data.image
      }
      alert('Profile updated successfully!')
    }
  } catch (error) {
    alert('Error updating profile')
  } finally {
    saving.value = false
  }
}

</script>

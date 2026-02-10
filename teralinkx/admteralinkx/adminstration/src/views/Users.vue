<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Users</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage Django user accounts</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add User
        </button>
        <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load users</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchUsers" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total Users" :value="stats.total_users" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active Users" :value="stats.active_users" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Staff Users" :value="stats.staff_users" color="purple" class="col-span-2 md:col-span-1">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20 6h-4V4c0-1.11-.89-2-2-2h-4c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-6 0h-4V4h4v2z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Superusers" :value="stats.superusers" color="amber">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      </ModernMetricCard>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search users..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Email</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Name</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Roles</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="user in filteredUsers" :key="user.id" @click="openEditModal(user)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                      {{ getInitials(user.username) }}
                    </div>
                    <p class="text-xs font-medium text-slate-900 dark:text-white">{{ user.username }}</p>
                  </div>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ user.email || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ user.first_name }} {{ user.last_name }}</td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="user.is_active ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-3 py-2">
                  <div class="flex items-center gap-1">
                    <span v-if="user.is_superuser" class="text-xs text-amber-600 dark:text-amber-400">⭐</span>
                    <span v-if="user.is_staff" class="text-xs text-purple-600 dark:text-purple-400">👔</span>
                  </div>
                </td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="openEditModal(user)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button @click.stop="openDeleteModal(user)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ selectedUser?.id ? 'Edit User' : 'Add User' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Username</label>
              <input v-model="formData.username" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" :disabled="!!selectedUser?.id" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Email</label>
              <input v-model="formData.email" type="email" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">First Name</label>
              <input v-model="formData.first_name" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Last Name</label>
              <input v-model="formData.last_name" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Password</label>
              <input v-model="formData.password" type="password" placeholder="Leave blank to keep current" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div class="col-span-2 space-y-2">
              <label class="flex items-center gap-2">
                <input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" />
                <span class="text-xs text-slate-700 dark:text-slate-300">Active</span>
              </label>
              <label class="flex items-center gap-2">
                <input v-model="formData.is_staff" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" />
                <span class="text-xs text-slate-700 dark:text-slate-300">Staff</span>
              </label>
              <label class="flex items-center gap-2">
                <input v-model="formData.is_superuser" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" />
                <span class="text-xs text-slate-700 dark:text-slate-300">Superuser</span>
              </label>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveUser" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : (selectedUser?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog :show="showDeleteModal" title="Delete User" :message="`Delete user ${userToDelete?.username}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Users',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const users = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedUser = ref(null)
    const userToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      is_active: true,
      is_staff: false,
      is_superuser: false
    })

    const filteredUsers = computed(() => {
      let result = users.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(u => u.username?.toLowerCase().includes(term) || u.email?.toLowerCase().includes(term) || u.first_name?.toLowerCase().includes(term) || u.last_name?.toLowerCase().includes(term))
      }
      if (statusFilter.value) {
        result = result.filter(u => u.is_active === (statusFilter.value === 'true'))
      }
      return result
    })

    const fetchUsers = async () => {
      try {
        const data = await makeRequest('get', 'suapi/users/')
        users.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/users/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchUsers(), fetchStats()])
    
    const openAddModal = () => {
      selectedUser.value = null
      formData.value = {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        is_active: true,
        is_staff: false,
        is_superuser: false
      }
      showFormModal.value = true
    }
    
    const openEditModal = (user) => {
      selectedUser.value = user
      formData.value = {
        username: user.username,
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        password: '',
        is_active: user.is_active,
        is_staff: user.is_staff,
        is_superuser: user.is_superuser
      }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedUser.value = null
      formData.value = {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        is_active: true,
        is_staff: false,
        is_superuser: false
      }
    }

    const saveUser = async () => {
      saveLoading.value = true
      try {
        const payload = { ...formData.value }
        if (!payload.password) delete payload.password
        
        if (selectedUser.value?.id) {
          await makeRequest('patch', `suapi/users/${selectedUser.value.id}/`, payload)
        } else {
          await makeRequest('post', 'suapi/users/', payload)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const openDeleteModal = (user) => { userToDelete.value = user; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; userToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `suapi/users/${userToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }

    onMounted(refreshData)

    return {
      loading, error, users, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedUser, userToDelete,
      saveLoading, deleteLoading, formData, filteredUsers, fetchUsers, refreshData,
      openAddModal, openEditModal, closeFormModal, saveUser, openDeleteModal, closeDeleteModal, confirmDelete, getInitials
    }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.4s ease-out;
}
</style>
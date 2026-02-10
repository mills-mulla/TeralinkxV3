<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Users</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage Django user accounts</p>
      </div>
      <button @click="refreshData" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
        <ArrowPathIcon class="w-5 h-5 text-slate-600 dark:text-slate-400" />
      </button>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <ExclamationTriangleIcon class="w-5 h-5 text-rose-600 dark:text-rose-400" />
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load users</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchUsers" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Users" :value="stats.total_users" icon="👥" color="blue" />
      <ModernMetricCard title="Active Users" :value="stats.active_users" icon="✅" color="emerald" />
      <ModernMetricCard title="Staff Users" :value="stats.staff_users" icon="👔" color="purple" class="col-span-2 md:col-span-1" />
      <ModernMetricCard title="Superusers" :value="stats.superusers" icon="⭐" color="amber" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search users..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        @add="openCreateModal"
      />

      <DataTable
        title="User Records"
        :data="filteredUsers"
        :columns="columns"
        :actions="['edit', 'delete']"
        @edit="openEditModal"
        @delete="openDeleteModal"
      >
        <template #cell-is_active="{ value }">
          <span :class="value ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'" class="px-2 py-0.5 text-xs font-medium rounded-full">
            {{ value ? 'Active' : 'Inactive' }}
          </span>
        </template>
        <template #cell-is_staff="{ value }">
          <span v-if="value" class="text-purple-600 dark:text-purple-400">✓</span>
          <span v-else class="text-slate-400 dark:text-slate-600">✗</span>
        </template>
        <template #cell-is_superuser="{ value }">
          <span v-if="value" class="text-amber-600 dark:text-amber-400">⭐</span>
          <span v-else class="text-slate-400 dark:text-slate-600">✗</span>
        </template>
      </DataTable>
    </div>

    <!-- Modals -->
    <FormModal
      :show="showFormModal"
      title="User"
      :fields="formFields"
      :initial-data="selectedUser"
      :loading="saveLoading"
      @close="closeFormModal"
      @submit="saveUser"
    />

    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete User"
      :message="`Are you sure you want to delete user <strong>${userToDelete?.username}</strong>?`"
      type="danger"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="closeDeleteModal"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import SearchBar from '../components/SearchBar.vue'
import DataTable from '../components/DataTable.vue'
import FormModal from '../components/FormModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'Users',
  components: { ModernMetricCard, SearchBar, DataTable, FormModal, ConfirmDialog, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const users = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedUser = ref(null)
    const userToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'username', label: 'Username', sortable: true },
      { key: 'email', label: 'Email', sortable: true },
      { key: 'first_name', label: 'First Name', sortable: true },
      { key: 'last_name', label: 'Last Name', sortable: true },
      { key: 'is_active', label: 'Active', sortable: true },
      { key: 'is_staff', label: 'Staff', sortable: true },
      { key: 'is_superuser', label: 'Superuser', sortable: true }
    ]

    const filters = [
      { key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] },
      { key: 'is_staff', label: 'Staff', options: [{ value: 'true', label: 'Staff' }, { value: 'false', label: 'Non-Staff' }] }
    ]

    const formFields = [
      { key: 'username', label: 'Username', type: 'text', required: true },
      { key: 'email', label: 'Email', type: 'email', required: true },
      { key: 'first_name', label: 'First Name', type: 'text' },
      { key: 'last_name', label: 'Last Name', type: 'text' },
      { key: 'password', label: 'Password', type: 'password', help: 'Leave blank to keep current password' },
      { key: 'is_active', label: 'Active', type: 'checkbox', checkboxLabel: 'User is active' },
      { key: 'is_staff', label: 'Staff', type: 'checkbox', checkboxLabel: 'Staff status' },
      { key: 'is_superuser', label: 'Superuser', type: 'checkbox', checkboxLabel: 'Superuser status' }
    ]

    const filteredUsers = computed(() => {
      let result = users.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(u => u.username?.toLowerCase().includes(term) || u.email?.toLowerCase().includes(term) || u.first_name?.toLowerCase().includes(term) || u.last_name?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(u => u[key] === (value === 'true'))
      })
      return result
    })

    const fetchUsers = async () => {
      console.log('🔍 fetchUsers() called')
      try {
        console.log('📡 Making API request to: suapi/users/')
        const data = await makeRequest('get', 'suapi/users/')
        console.log('✅ API Response received:', data)
        console.log('📊 Data type:', typeof data, 'Is array:', Array.isArray(data))
        console.log('📊 Data.results:', data.results)
        
        users.value = data.results || data
        console.log('✅ users.value set to:', users.value)
        console.log('📊 users.value length:', users.value.length)
      } catch (err) {
        console.error('❌ Error in fetchUsers:', err)
        console.error('❌ Error details:', err.response?.data)
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
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedUser.value = null; showFormModal.value = true }
    const openEditModal = (user) => { selectedUser.value = { ...user }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedUser.value = null }

    const saveUser = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `suapi/users/${data.id}/` : 'suapi/users/'
        const method = data.id ? 'put' : 'post'
        await makeRequest(method, endpoint, data)
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

    onMounted(refreshData)

    return {
      loading, error, users, stats, searchTerm, showFormModal, showDeleteModal, selectedUser, userToDelete,
      saveLoading, deleteLoading, columns, filters, formFields, filteredUsers, fetchUsers, refreshData,
      handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, saveUser,
      openDeleteModal, closeDeleteModal, confirmDelete
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
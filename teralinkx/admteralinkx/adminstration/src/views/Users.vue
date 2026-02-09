<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">
            🔐 User Management
          </h1>
          <p class="text-slate-600 font-light">Manage Django user accounts</p>
        </div>
        <button @click="refreshData" class="p-2 hover:bg-white/50 rounded-xl transition-all duration-300">
          <ArrowPathIcon class="w-6 h-6 text-slate-600" />
        </button>
      </div>
    </div>

    <div v-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <ExclamationTriangleIcon class="w-6 h-6 text-rose-600" />
          <div>
            <h3 class="text-rose-800 font-semibold">Failed to load user data</h3>
            <p class="text-rose-600 text-sm">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchUsers" class="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700">Retry</button>
      </div>
    </div>

    <div v-if="loading && !error" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
          <div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div>
        </div>
        <p class="mt-4 text-slate-500 font-light">Loading users...</p>
      </div>
    </div>

    <div v-else-if="!loading" class="space-y-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModernMetricCard title="Total Users" :value="stats.total_users" icon="👥" color="blue" :formatted="true" />
        <ModernMetricCard title="Active Users" :value="stats.active_users" icon="✅" color="emerald" :formatted="true" />
        <ModernMetricCard title="Staff Users" :value="stats.staff_users" icon="👔" color="purple" :formatted="true" />
        <ModernMetricCard title="Superusers" :value="stats.superusers" icon="⭐" color="amber" :formatted="true" />
      </div>

      <SearchBar
        v-model="searchTerm"
        placeholder="Search users by username, email, name..."
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
          <span :class="value ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-800'" class="px-2 py-1 text-xs font-medium rounded-full">
            {{ value ? 'Active' : 'Inactive' }}
          </span>
        </template>
        <template #cell-is_staff="{ value }">
          <span v-if="value" class="text-purple-600">✓</span>
          <span v-else class="text-slate-400">✗</span>
        </template>
        <template #cell-is_superuser="{ value }">
          <span v-if="value" class="text-amber-600">⭐</span>
          <span v-else class="text-slate-400">✗</span>
        </template>
      </DataTable>
    </div>

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
      try {
        const data = await makeRequest('get', 'users/')
        users.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'users/stats/')
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
        const endpoint = data.id ? `users/${data.id}/` : 'users/'
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
        await makeRequest('delete', `users/${userToDelete.value.id}/`)
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

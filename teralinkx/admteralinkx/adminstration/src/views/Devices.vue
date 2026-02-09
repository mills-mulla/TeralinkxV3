<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Devices</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Monitor and manage user devices</p>
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load devices</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchDevices" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Devices" :value="stats.total_devices" icon="📱" color="blue" />
      <ModernMetricCard title="Active Devices" :value="stats.active_devices" icon="✅" color="emerald" />
      <ModernMetricCard title="Online Now" :value="stats.online_devices" icon="🟢" color="green" />
      <ModernMetricCard title="Trusted" :value="stats.trusted_devices" icon="🔒" color="purple" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search devices..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        @add="openCreateModal"
      />

      <DataTable
        title="Device Records"
        :data="filteredDevices"
        :columns="columns"
        :actions="['edit', 'delete']"
        @edit="openEditModal"
        @delete="openDeleteModal"
      >
        <template #cell-status="{ value }">
          <span :class="value === 'active' ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : value === 'suspended' ? 'bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'" class="px-2 py-0.5 text-xs font-medium rounded-full">
            {{ value }}
          </span>
        </template>
        <template #cell-is_online="{ value }">
          <span :class="value ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-600'">{{ value ? '● Online' : '○ Offline' }}</span>
        </template>
        <template #custom-actions="{ item }">
          <button v-if="item.status === 'active'" @click="blockDevice(item)" class="text-rose-600 dark:text-rose-400 hover:text-rose-800 dark:hover:text-rose-300 p-1 rounded" title="Block">🚫</button>
          <button v-else @click="unblockDevice(item)" class="text-emerald-600 dark:text-emerald-400 hover:text-emerald-800 dark:hover:text-emerald-300 p-1 rounded" title="Unblock">✅</button>
        </template>
      </DataTable>
    </div>

    <!-- Modals -->
    <FormModal
      :show="showFormModal"
      title="Device"
      :fields="formFields"
      :initial-data="selectedDevice"
      :loading="saveLoading"
      @close="closeFormModal"
      @submit="saveDevice"
    />

    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Device"
      :message="`Are you sure you want to delete device <strong>${deviceToDelete?.device_name}</strong>?`"
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
  name: 'Devices',
  components: { ModernMetricCard, SearchBar, DataTable, FormModal, ConfirmDialog, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const devices = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedDevice = ref(null)
    const deviceToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'mac_address', label: 'MAC Address', sortable: true },
      { key: 'device_name', label: 'Device Name', sortable: true },
      { key: 'user_account', label: 'User', sortable: true },
      { key: 'device_type', label: 'Type', sortable: true },
      { key: 'status', label: 'Status', sortable: true },
      { key: 'is_online', label: 'Online', sortable: true },
      { key: 'total_connections', label: 'Connections', sortable: true }
    ]

    const filters = [
      { key: 'status', label: 'Status', options: [{ value: 'active', label: 'Active' }, { value: 'inactive', label: 'Inactive' }, { value: 'suspended', label: 'Suspended' }] },
      { key: 'device_type', label: 'Type', options: [{ value: 'phone', label: 'Phone' }, { value: 'laptop', label: 'Laptop' }, { value: 'tablet', label: 'Tablet' }, { value: 'desktop', label: 'Desktop' }] }
    ]

    const formFields = [
      { key: 'mac_address', label: 'MAC Address', type: 'text', required: true, placeholder: '00:11:22:33:44:55' },
      { key: 'device_name', label: 'Device Name', type: 'text', required: true },
      { key: 'device_type', label: 'Device Type', type: 'select', required: true, options: filters[1].options },
      { key: 'device_platform', label: 'Platform', type: 'select', options: [{ value: 'windows', label: 'Windows' }, { value: 'macos', label: 'macOS' }, { value: 'linux', label: 'Linux' }, { value: 'android', label: 'Android' }, { value: 'ios', label: 'iOS' }] },
      { key: 'status', label: 'Status', type: 'select', required: true, options: filters[0].options },
      { key: 'is_trusted', label: 'Trusted', type: 'checkbox', checkboxLabel: 'Device is trusted' }
    ]

    const filteredDevices = computed(() => {
      let result = devices.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(d => d.mac_address?.toLowerCase().includes(term) || d.device_name?.toLowerCase().includes(term) || d.user_account?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(d => d[key] === value)
      })
      return result
    })

    const fetchDevices = async () => {
      try {
        const data = await makeRequest('get', 'suapi/devices/')
        devices.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/devices/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchDevices(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedDevice.value = null; showFormModal.value = true }
    const openEditModal = (device) => { selectedDevice.value = { ...device }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedDevice.value = null }

    const saveDevice = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `suapi/devices/${data.id}/` : 'devices/'
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

    const blockDevice = async (device) => {
      try {
        await makeRequest('post', `suapi/devices/${device.id}/block/`, { reason: 'Admin action' })
        await refreshData()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const unblockDevice = async (device) => {
      try {
        await makeRequest('post', `suapi/devices/${device.id}/unblock/`, { reason: 'Admin action' })
        await refreshData()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const openDeleteModal = (device) => { deviceToDelete.value = device; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; deviceToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `suapi/devices/${deviceToDelete.value.id}/`)
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
      loading, error, devices, stats, searchTerm, showFormModal, showDeleteModal, selectedDevice, deviceToDelete,
      saveLoading, deleteLoading, columns, filters, formFields, filteredDevices, fetchDevices, refreshData,
      handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, saveDevice,
      blockDevice, unblockDevice, openDeleteModal, closeDeleteModal, confirmDelete
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

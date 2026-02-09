<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Locations</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage network locations</p>
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load locations</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchLocations" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Locations" :value="stats.total_locations" icon="📍" color="blue" />
      <ModernMetricCard title="Active" :value="stats.active_locations" icon="✅" color="emerald" />
      <ModernMetricCard title="Hotspots" :value="stats.hotspot_locations" icon="📡" color="purple" />
      <ModernMetricCard title="Branches" :value="stats.branch_locations" icon="🏢" color="cyan" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search locations..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        @add="openCreateModal"
      />

      <DataTable
        title="Location Records"
        :data="filteredLocations"
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
        <template #cell-location_type="{ value }">
          <span class="text-xs">{{ value }}</span>
        </template>
      </DataTable>
    </div>

    <!-- Modals -->
    <FormModal
      :show="showFormModal"
      title="Location"
      :fields="formFields"
      :initial-data="selectedLocation"
      :loading="saveLoading"
      @close="closeFormModal"
      @submit="saveLocation"
    />

    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Location"
      :message="`Are you sure you want to delete location <strong>${locationToDelete?.name}</strong>?`"
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
  name: 'Locations',
  components: { ModernMetricCard, SearchBar, DataTable, FormModal, ConfirmDialog, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const locations = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedLocation = ref(null)
    const locationToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'name', label: 'Name', sortable: true },
      { key: 'code', label: 'Code', sortable: true },
      { key: 'location_type', label: 'Type', sortable: true },
      { key: 'city', label: 'City', sortable: true },
      { key: 'is_active', label: 'Status', sortable: true },
      { key: 'max_concurrent_users', label: 'Max Users', sortable: true }
    ]

    const filters = [
      { key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] },
      { key: 'location_type', label: 'Type', options: [{ value: 'headquarters', label: 'Headquarters' }, { value: 'branch', label: 'Branch' }, { value: 'hotspot', label: 'Hotspot' }, { value: 'commercial', label: 'Commercial' }] }
    ]

    const formFields = [
      { key: 'name', label: 'Name', type: 'text', required: true },
      { key: 'code', label: 'Code', type: 'text', required: true, placeholder: 'LOC-001' },
      { key: 'location_type', label: 'Type', type: 'select', required: true, options: filters[1].options },
      { key: 'address', label: 'Address', type: 'textarea', rows: 2 },
      { key: 'city', label: 'City', type: 'text' },
      { key: 'coordinates', label: 'Coordinates', type: 'text', placeholder: 'lat,lng' },
      { key: 'max_concurrent_users', label: 'Max Users', type: 'number', default: 100 },
      { key: 'is_active', label: 'Active', type: 'checkbox', checkboxLabel: 'Location is active' }
    ]

    const filteredLocations = computed(() => {
      let result = locations.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(l => l.name?.toLowerCase().includes(term) || l.code?.toLowerCase().includes(term) || l.city?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) {
          if (key === 'is_active') {
            result = result.filter(l => l[key] === (value === 'true'))
          } else {
            result = result.filter(l => l[key] === value)
          }
        }
      })
      return result
    })

    const fetchLocations = async () => {
      try {
        const data = await makeRequest('get', 'suapi/locations/')
        locations.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/locations/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchLocations(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedLocation.value = null; showFormModal.value = true }
    const openEditModal = (location) => { selectedLocation.value = { ...location }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedLocation.value = null }

    const saveLocation = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `suapi/locations/${data.id}/` : 'suapi/locations/'
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

    const openDeleteModal = (location) => { locationToDelete.value = location; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; locationToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `suapi/locations/${locationToDelete.value.id}/`)
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
      loading, error, locations, stats, searchTerm, showFormModal, showDeleteModal, selectedLocation, locationToDelete,
      saveLoading, deleteLoading, columns, filters, formFields, filteredLocations, fetchLocations, refreshData,
      handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, saveLocation,
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

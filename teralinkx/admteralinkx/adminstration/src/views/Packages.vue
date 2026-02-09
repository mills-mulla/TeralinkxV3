<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Packages</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage data packages</p>
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load packages</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchPackages" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Packages" :value="stats.total_packages" icon="📦" color="blue" />
      <ModernMetricCard title="Active" :value="stats.active_packages" icon="✅" color="emerald" />
      <ModernMetricCard title="Popular" :value="stats.popular_packages" icon="🔥" color="purple" />
      <ModernMetricCard title="Avg Price" :value="`KSh ${formatNumber(stats.average_price || 0)}`" icon="💰" color="amber" :formatted="false" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search packages..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        @add="openCreateModal"
      />

      <DataTable
        title="Package Records"
        :data="filteredPackages"
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
      </DataTable>
    </div>

    <!-- Modals -->
    <FormModal
      :show="showFormModal"
      title="Package"
      :fields="formFields"
      :initial-data="selectedPackage"
      :loading="saveLoading"
      @close="closeFormModal"
      @submit="savePackage"
    />

    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Package"
      :message="`Are you sure you want to delete package <strong>${packageToDelete?.name}</strong>?`"
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
  name: 'Packages',
  components: { ModernMetricCard, SearchBar, DataTable, FormModal, ConfirmDialog, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const packages = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedPackage = ref(null)
    const packageToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'name', label: 'Name', sortable: true },
      { key: 'price', label: 'Price', sortable: true, format: (v) => `KSh ${v}` },
      { key: 'data_limit_gb', label: 'Data (GB)', sortable: true },
      { key: 'validity_days', label: 'Validity (Days)', sortable: true },
      { key: 'is_active', label: 'Status', sortable: true }
    ]

    const filters = [
      { key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] }
    ]

    const formFields = [
      { key: 'name', label: 'Package Name', type: 'text', required: true },
      { key: 'price', label: 'Price (KSh)', type: 'number', required: true },
      { key: 'data_limit_gb', label: 'Data Limit (GB)', type: 'number', required: true },
      { key: 'validity_days', label: 'Validity (Days)', type: 'number', required: true },
      { key: 'description', label: 'Description', type: 'textarea', rows: 3 },
      { key: 'is_active', label: 'Active', type: 'checkbox', checkboxLabel: 'Package is active' }
    ]

    const filteredPackages = computed(() => {
      let result = packages.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(p => p.name?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(p => p[key] === (value === 'true'))
      })
      return result
    })

    const fetchPackages = async () => {
      try {
        const data = await makeRequest('get', 'suapi/packages/')
        packages.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/packages/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchPackages(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedPackage.value = null; showFormModal.value = true }
    const openEditModal = (pkg) => { selectedPackage.value = { ...pkg }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedPackage.value = null }
    const formatNumber = (num) => new Intl.NumberFormat().format(num)

    const savePackage = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `suapi/packages/${data.id}/` : 'suapi/packages/'
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

    const openDeleteModal = (pkg) => { packageToDelete.value = pkg; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; packageToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `suapi/packages/${packageToDelete.value.id}/`)
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
      loading, error, packages, stats, searchTerm, showFormModal, showDeleteModal, selectedPackage, packageToDelete,
      saveLoading, deleteLoading, columns, filters, formFields, filteredPackages, fetchPackages, refreshData,
      handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, savePackage,
      openDeleteModal, closeDeleteModal, confirmDelete, formatNumber
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

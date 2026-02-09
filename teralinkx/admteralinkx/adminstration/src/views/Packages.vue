<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">
            📦 Package Management
          </h1>
          <p class="text-slate-600 font-light">Manage internet packages and pricing</p>
        </div>
        <button 
          @click="refreshData"
          class="p-2 hover:bg-white/50 rounded-xl transition-all duration-300"
          title="Refresh data"
        >
          <ArrowPathIcon class="w-6 h-6 text-slate-600" />
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <ExclamationTriangleIcon class="w-6 h-6 text-rose-600" />
          <div>
            <h3 class="text-rose-800 font-semibold">Failed to load package data</h3>
            <p class="text-rose-600 text-sm">{{ error }}</p>
          </div>
        </div>
        <button 
          @click="fetchPackages"
          class="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition-colors"
        >
          Retry
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !error" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
          <div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div>
        </div>
        <p class="mt-4 text-slate-500 font-light">Loading packages...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="!loading" class="space-y-8">
      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModernMetricCard
          title="Total Packages"
          :value="stats.total_packages"
          icon="📦"
          color="blue"
          :formatted="true"
        />
        <ModernMetricCard
          title="Active Packages"
          :value="stats.active_packages"
          icon="✅"
          color="emerald"
          :formatted="true"
        />
        <ModernMetricCard
          title="Public Packages"
          :value="stats.public_packages"
          icon="🌐"
          color="cyan"
          :formatted="true"
        />
        <ModernMetricCard
          title="Categories"
          :value="stats.by_category?.length || 0"
          icon="📂"
          color="purple"
          :formatted="true"
        />
      </div>

      <!-- Search Bar -->
      <SearchBar
        v-model="searchTerm"
        placeholder="Search packages by name, description, category..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        @add="openCreateModal"
      />

      <!-- Data Table -->
      <DataTable
        title="Package Records"
        :data="filteredPackages"
        :columns="columns"
        :actions="['edit', 'delete']"
        @edit="openEditModal"
        @delete="openDeleteModal"
      >
        <template #cell-is_active="{ value }">
          <span :class="value ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-800'" 
                class="px-2 py-1 text-xs font-medium rounded-full">
            {{ value ? 'Active' : 'Inactive' }}
          </span>
        </template>
        
        <template #cell-price="{ value }">
          <span class="font-medium">KSh {{ formatNumber(value) }}</span>
        </template>
      </DataTable>
    </div>

    <!-- Form Modal -->
    <FormModal
      :show="showFormModal"
      title="Package"
      :fields="formFields"
      :initial-data="selectedPackage"
      :loading="saveLoading"
      @close="closeFormModal"
      @submit="savePackage"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Package"
      :message="`Are you sure you want to delete package <strong>${packageToDelete?.name}</strong>? This action cannot be undone.`"
      type="danger"
      confirm-text="Delete"
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
  components: {
    ModernMetricCard,
    SearchBar,
    DataTable,
    FormModal,
    ConfirmDialog,
    ArrowPathIcon,
    ExclamationTriangleIcon
  },
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
      { key: 'category', label: 'Category', sortable: true },
      { key: 'tier', label: 'Tier', sortable: true },
      { key: 'price', label: 'Price', sortable: true },
      { key: 'is_active', label: 'Status', sortable: true },
      { key: 'is_public', label: 'Public', sortable: true }
    ]

    const filters = [
      {
        key: 'category',
        label: 'Category',
        options: [
          { value: 'data', label: 'Data' },
          { value: 'voice', label: 'Voice' },
          { value: 'sms', label: 'SMS' },
          { value: 'bundle', label: 'Bundle' }
        ]
      },
      {
        key: 'tier',
        label: 'Tier',
        options: [
          { value: 'basic', label: 'Basic' },
          { value: 'standard', label: 'Standard' },
          { value: 'premium', label: 'Premium' },
          { value: 'enterprise', label: 'Enterprise' }
        ]
      },
      {
        key: 'is_active',
        label: 'Status',
        options: [
          { value: 'true', label: 'Active' },
          { value: 'false', label: 'Inactive' }
        ]
      }
    ]

    const formFields = [
      { key: 'name', label: 'Package Name', type: 'text', required: true, placeholder: 'e.g., Premium 100GB' },
      { key: 'description', label: 'Description', type: 'textarea', rows: 3, placeholder: 'Package description...' },
      { key: 'category', label: 'Category', type: 'select', required: true, options: filters[0].options },
      { key: 'tier', label: 'Tier', type: 'select', required: true, options: filters[1].options },
      { key: 'price', label: 'Price (KSh)', type: 'number', required: true, min: 0, step: '0.01' },
      { key: 'data_limit', label: 'Data Limit (MB)', type: 'number', min: 0 },
      { key: 'validity_days', label: 'Validity (Days)', type: 'number', min: 1 },
      { key: 'is_active', label: 'Active', type: 'checkbox', checkboxLabel: 'Package is active' },
      { key: 'is_public', label: 'Public', type: 'checkbox', checkboxLabel: 'Visible to customers' }
    ]

    const filteredPackages = computed(() => {
      let result = packages.value

      // Apply search
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(pkg =>
          pkg.name?.toLowerCase().includes(term) ||
          pkg.description?.toLowerCase().includes(term) ||
          pkg.category?.toLowerCase().includes(term)
        )
      }

      // Apply filters
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) {
          if (key === 'is_active') {
            result = result.filter(pkg => pkg.is_active === (value === 'true'))
          } else {
            result = result.filter(pkg => pkg[key] === value)
          }
        }
      })

      return result
    })

    const fetchPackages = async () => {
      try {
        const data = await makeRequest('get', 'packages/')
        packages.value = data.results || data
      } catch (err) {
        console.error('Error fetching packages:', err)
      }
    }

    const fetchStats = async () => {
      try {
        const data = await makeRequest('get', 'packages/stats/')
        stats.value = data
      } catch (err) {
        console.error('Error fetching stats:', err)
      }
    }

    const refreshData = async () => {
      await Promise.all([fetchPackages(), fetchStats()])
    }

    const handleFilterChange = ({ all }) => {
      activeFilters.value = all
    }

    const clearFilters = () => {
      searchTerm.value = ''
      activeFilters.value = {}
    }

    const openCreateModal = () => {
      selectedPackage.value = null
      showFormModal.value = true
    }

    const openEditModal = (pkg) => {
      selectedPackage.value = { ...pkg }
      showFormModal.value = true
    }

    const closeFormModal = () => {
      showFormModal.value = false
      selectedPackage.value = null
    }

    const savePackage = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `packages/${data.id}/` : 'packages/'
        const method = data.id ? 'put' : 'post'
        
        await makeRequest(method, endpoint, data)
        await refreshData()
        closeFormModal()
      } catch (err) {
        console.error('Error saving package:', err)
        alert('Error saving package: ' + (err.response?.data?.error || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const openDeleteModal = (pkg) => {
      packageToDelete.value = pkg
      showDeleteModal.value = true
    }

    const closeDeleteModal = () => {
      showDeleteModal.value = false
      packageToDelete.value = null
    }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `packages/${packageToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        console.error('Error deleting package:', err)
        alert('Error deleting package: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num)
    }

    onMounted(() => {
      refreshData()
    })

    return {
      loading,
      error,
      packages,
      stats,
      searchTerm,
      showFormModal,
      showDeleteModal,
      selectedPackage,
      packageToDelete,
      saveLoading,
      deleteLoading,
      columns,
      filters,
      formFields,
      filteredPackages,
      fetchPackages,
      refreshData,
      handleFilterChange,
      clearFilters,
      openCreateModal,
      openEditModal,
      closeFormModal,
      savePackage,
      openDeleteModal,
      closeDeleteModal,
      confirmDelete,
      formatNumber
    }
  }
}
</script>

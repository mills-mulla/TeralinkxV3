<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Vouchers</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage dispatch vouchers</p>
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load vouchers</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchVouchers" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Vouchers" :value="stats.total_vouchers" icon="🎫" color="blue" />
      <ModernMetricCard title="Active" :value="stats.active_vouchers" icon="✅" color="emerald" />
      <ModernMetricCard title="Expired" :value="stats.expired_vouchers" icon="⏰" color="amber" />
      <ModernMetricCard title="Used" :value="stats.used_vouchers" icon="📊" color="purple" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search vouchers..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        @add="openCreateModal"
      />

      <DataTable
        title="Voucher Records"
        :data="filteredVouchers"
        :columns="columns"
        :actions="['edit', 'delete']"
        @edit="openEditModal"
        @delete="openDeleteModal"
      >
        <template #cell-status="{ value }">
          <span :class="value === 'active' ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : value === 'expired' ? 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'" class="px-2 py-0.5 text-xs font-medium rounded-full">
            {{ value }}
          </span>
        </template>
      </DataTable>
    </div>

    <!-- Modals -->
    <FormModal
      :show="showFormModal"
      title="Voucher"
      :fields="formFields"
      :initial-data="selectedVoucher"
      :loading="saveLoading"
      @close="closeFormModal"
      @submit="saveVoucher"
    />

    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Voucher"
      :message="`Are you sure you want to delete this voucher?`"
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
  name: 'Vouchers',
  components: { ModernMetricCard, SearchBar, DataTable, FormModal, ConfirmDialog, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const vouchers = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedVoucher = ref(null)
    const voucherToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'user_username', label: 'User', sortable: true },
      { key: 'package_name', label: 'Package', sortable: true },
      { key: 'price_paid', label: 'Price', sortable: true, format: (v) => `KSh ${v}` },
      { key: 'status', label: 'Status', sortable: true },
      { key: 'activated_at', label: 'Activated', sortable: true, format: (v) => v ? new Date(v).toLocaleDateString() : 'N/A' },
      { key: 'expires_at', label: 'Expires', sortable: true, format: (v) => v ? new Date(v).toLocaleDateString() : 'N/A' }
    ]

    const filters = [
      { key: 'status', label: 'Status', options: [{ value: 'active', label: 'Active' }, { value: 'expired', label: 'Expired' }, { value: 'used', label: 'Used' }] }
    ]

    const formFields = [
      { key: 'user', label: 'User ID', type: 'number', required: true },
      { key: 'package', label: 'Package ID', type: 'number', required: true },
      { key: 'price_paid', label: 'Price Paid', type: 'number', required: true },
      { key: 'expires_at', label: 'Expires At', type: 'datetime-local' }
    ]

    const filteredVouchers = computed(() => {
      let result = vouchers.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(v => v.user_username?.toLowerCase().includes(term) || v.package_name?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(v => v[key] === value)
      })
      return result
    })

    const fetchVouchers = async () => {
      try {
        const data = await makeRequest('get', 'suapi/vouchers/')
        vouchers.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/vouchers/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchVouchers(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedVoucher.value = null; showFormModal.value = true }
    const openEditModal = (voucher) => { selectedVoucher.value = { ...voucher }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedVoucher.value = null }

    const saveVoucher = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `suapi/vouchers/${data.id}/` : 'suapi/vouchers/'
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

    const openDeleteModal = (voucher) => { voucherToDelete.value = voucher; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; voucherToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `suapi/vouchers/${voucherToDelete.value.id}/`)
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
      loading, error, vouchers, stats, searchTerm, showFormModal, showDeleteModal, selectedVoucher, voucherToDelete,
      saveLoading, deleteLoading, columns, filters, formFields, filteredVouchers, fetchVouchers, refreshData,
      handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, saveVoucher,
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

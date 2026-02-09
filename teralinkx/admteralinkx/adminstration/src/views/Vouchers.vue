// Vouchers.vue
<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <div class="mb-8"><div class="flex items-center justify-between"><div><h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">🎫 Voucher Management</h1><p class="text-slate-600 font-light">Manage dispatch vouchers</p></div><button @click="refreshData" class="p-2 hover:bg-white/50 rounded-xl transition-all duration-300"><ArrowPathIcon class="w-6 h-6 text-slate-600" /></button></div></div>
    <div v-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6 mb-6"><div class="flex items-center justify-between"><div class="flex items-center space-x-3"><ExclamationTriangleIcon class="w-6 h-6 text-rose-600" /><div><h3 class="text-rose-800 font-semibold">Failed to load voucher data</h3><p class="text-rose-600 text-sm">{{ error }}</p></div></div><button @click="fetchVouchers" class="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700">Retry</button></div></div>
    <div v-if="loading && !error" class="flex items-center justify-center py-20"><div class="text-center"><div class="relative"><div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div><div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div></div><p class="mt-4 text-slate-500 font-light">Loading vouchers...</p></div></div>
    <div v-else-if="!loading" class="space-y-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"><ModernMetricCard title="Total Vouchers" :value="stats.total_vouchers" icon="🎫" color="blue" :formatted="true" /><ModernMetricCard title="Active" :value="stats.active_vouchers" icon="✅" color="emerald" :formatted="true" /><ModernMetricCard title="Expired" :value="stats.expired_vouchers" icon="⏰" color="rose" :formatted="true" /><ModernMetricCard title="Revenue" :value="`KSh ${formatNumber(stats.total_revenue)}`" icon="💰" color="amber" :formatted="false" /></div>
      <SearchBar v-model="searchTerm" placeholder="Search vouchers..." :filters="filters" @filter-change="handleFilterChange" @clear="clearFilters" @add="openCreateModal" />
      <DataTable title="Voucher Records" :data="filteredVouchers" :columns="columns" :actions="['edit', 'delete']" @edit="openEditModal" @delete="openDeleteModal"><template #cell-status="{ value }"><span :class="value === 'active' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-800'" class="px-2 py-1 text-xs font-medium rounded-full">{{ value }}</span></template><template #cell-dispatch_price="{ value }"><span class="font-medium">KSh {{ formatNumber(value) }}</span></template></DataTable>
    </div>
    <FormModal :show="showFormModal" title="Voucher" :fields="formFields" :initial-data="selectedVoucher" :loading="saveLoading" @close="closeFormModal" @submit="saveVoucher" />
    <ConfirmDialog :show="showDeleteModal" title="Delete Voucher" :message="`Delete voucher <strong>${voucherToDelete?.voucher_code}</strong>?`" type="danger" :loading="deleteLoading" @confirm="confirmDelete" @cancel="closeDeleteModal" />
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
      { key: 'voucher_code', label: 'Code', sortable: true },
      { key: 'client_account', label: 'Client', sortable: true },
      { key: 'dispatch_price', label: 'Price', sortable: true },
      { key: 'status', label: 'Status', sortable: true },
      { key: 'dispatch_expiry', label: 'Expiry', sortable: true, format: (v) => v ? new Date(v).toLocaleDateString() : 'N/A' }
    ]

    const filters = [{ key: 'status', label: 'Status', options: [{ value: 'active', label: 'Active' }, { value: 'expired', label: 'Expired' }, { value: 'used', label: 'Used' }] }]

    const formFields = [
      { key: 'voucher_code', label: 'Voucher Code', type: 'text', required: true },
      { key: 'dispatch_price', label: 'Price (KSh)', type: 'number', required: true, min: 0, step: '0.01' },
      { key: 'dispatch_package_duration', label: 'Duration (days)', type: 'number', min: 1 },
      { key: 'usage_limit', label: 'Usage Limit (MB)', type: 'number', min: 0 },
      { key: 'status', label: 'Status', type: 'select', required: true, options: filters[0].options }
    ]

    const filteredVouchers = computed(() => {
      let result = vouchers.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(v => v.voucher_code?.toLowerCase().includes(term) || v.client_account?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(v => v[key] === value)
      })
      return result
    })

    const fetchVouchers = async () => { try { const data = await makeRequest('get', 'vouchers/'); vouchers.value = data.results || data } catch (err) { console.error('Error:', err) } }
    const fetchStats = async () => { try { stats.value = await makeRequest('get', 'vouchers/stats/') } catch (err) { console.error('Error:', err) } }
    const refreshData = () => Promise.all([fetchVouchers(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedVoucher.value = null; showFormModal.value = true }
    const openEditModal = (voucher) => { selectedVoucher.value = { ...voucher }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedVoucher.value = null }

    const saveVoucher = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `vouchers/${data.id}/` : 'vouchers/'
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
        await makeRequest('delete', `vouchers/${voucherToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const formatNumber = (num) => new Intl.NumberFormat().format(num)

    onMounted(refreshData)

    return { loading, error, vouchers, stats, searchTerm, showFormModal, showDeleteModal, selectedVoucher, voucherToDelete, saveLoading, deleteLoading, columns, filters, formFields, filteredVouchers, fetchVouchers, refreshData, handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, saveVoucher, openDeleteModal, closeDeleteModal, confirmDelete, formatNumber }
  }
}
</script>

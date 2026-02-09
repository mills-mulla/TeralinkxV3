<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <div class="mb-8"><div class="flex items-center justify-between"><div><h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">🎟️ Coupon Management</h1><p class="text-slate-600 font-light">Manage discount coupons</p></div><button @click="refreshData" class="p-2 hover:bg-white/50 rounded-xl transition-all duration-300"><ArrowPathIcon class="w-6 h-6 text-slate-600" /></button></div></div>
    <div v-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6 mb-6"><div class="flex items-center justify-between"><div class="flex items-center space-x-3"><ExclamationTriangleIcon class="w-6 h-6 text-rose-600" /><div><h3 class="text-rose-800 font-semibold">Failed to load coupon data</h3><p class="text-rose-600 text-sm">{{ error }}</p></div></div><button @click="fetchCoupons" class="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700">Retry</button></div></div>
    <div v-if="loading && !error" class="flex items-center justify-center py-20"><div class="text-center"><div class="relative"><div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div><div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div></div><p class="mt-4 text-slate-500 font-light">Loading coupons...</p></div></div>
    <div v-else-if="!loading" class="space-y-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"><ModernMetricCard title="Total Coupons" :value="stats.total_coupons" icon="🎟️" color="blue" :formatted="true" /><ModernMetricCard title="Active" :value="stats.active_coupons" icon="✅" color="emerald" :formatted="true" /><ModernMetricCard title="Reward Coupons" :value="stats.reward_coupons" icon="🏆" color="purple" :formatted="true" /><ModernMetricCard title="Valid Now" :value="stats.valid_coupons" icon="✓" color="green" :formatted="true" /></div>
      <SearchBar v-model="searchTerm" placeholder="Search coupons..." :filters="filters" @filter-change="handleFilterChange" @clear="clearFilters" @add="openCreateModal" />
      <DataTable title="Coupon Records" :data="filteredCoupons" :columns="columns" :actions="['edit', 'delete']" @edit="openEditModal" @delete="openDeleteModal"><template #cell-is_active="{ value }"><span :class="value ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-800'" class="px-2 py-1 text-xs font-medium rounded-full">{{ value ? 'Active' : 'Inactive' }}</span></template></DataTable>
    </div>
    <FormModal :show="showFormModal" title="Coupon" :fields="formFields" :initial-data="selectedCoupon" :loading="saveLoading" @close="closeFormModal" @submit="saveCoupon" />
    <ConfirmDialog :show="showDeleteModal" title="Delete Coupon" :message="`Delete coupon <strong>${couponToDelete?.code}</strong>?`" type="danger" :loading="deleteLoading" @confirm="confirmDelete" @cancel="closeDeleteModal" />
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
  name: 'Coupons',
  components: { ModernMetricCard, SearchBar, DataTable, FormModal, ConfirmDialog, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const coupons = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedCoupon = ref(null)
    const couponToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)

    const columns = [{ key: 'id', label: 'ID', sortable: true }, { key: 'code', label: 'Code', sortable: true }, { key: 'name', label: 'Name', sortable: true }, { key: 'discount_value', label: 'Discount', sortable: true }, { key: 'coupon_type', label: 'Type', sortable: true }, { key: 'is_active', label: 'Status', sortable: true }, { key: 'total_uses', label: 'Uses', sortable: true }]
    const filters = [{ key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] }, { key: 'is_reward', label: 'Type', options: [{ value: 'true', label: 'Reward' }, { value: 'false', label: 'Regular' }] }]
    const formFields = [{ key: 'code', label: 'Coupon Code', type: 'text', required: true }, { key: 'name', label: 'Name', type: 'text', required: true }, { key: 'description', label: 'Description', type: 'textarea', rows: 3 }, { key: 'coupon_type', label: 'Type', type: 'select', required: true, options: [{ value: 'percentage', label: 'Percentage' }, { value: 'fixed', label: 'Fixed Amount' }] }, { key: 'discount_value', label: 'Discount Value', type: 'number', required: true, min: 0, step: '0.01' }, { key: 'max_uses', label: 'Max Uses', type: 'number', min: 1 }, { key: 'is_active', label: 'Active', type: 'checkbox', checkboxLabel: 'Coupon is active' }, { key: 'is_reward', label: 'Reward', type: 'checkbox', checkboxLabel: 'Reward coupon' }]

    const filteredCoupons = computed(() => {
      let result = coupons.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(c => c.code?.toLowerCase().includes(term) || c.name?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(c => c[key] === (value === 'true'))
      })
      return result
    })

    const fetchCoupons = async () => { try { const data = await makeRequest('get', 'coupons/'); coupons.value = data.results || data } catch (err) { console.error('Error:', err) } }
    const fetchStats = async () => { try { stats.value = await makeRequest('get', 'coupons/stats/') } catch (err) { console.error('Error:', err) } }
    const refreshData = () => Promise.all([fetchCoupons(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedCoupon.value = null; showFormModal.value = true }
    const openEditModal = (coupon) => { selectedCoupon.value = { ...coupon }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedCoupon.value = null }

    const saveCoupon = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `coupons/${data.id}/` : 'coupons/'
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

    const openDeleteModal = (coupon) => { couponToDelete.value = coupon; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; couponToDelete.value = null }
    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `coupons/${couponToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    onMounted(refreshData)

    return { loading, error, coupons, stats, searchTerm, showFormModal, showDeleteModal, selectedCoupon, couponToDelete, saveLoading, deleteLoading, columns, filters, formFields, filteredCoupons, fetchCoupons, refreshData, handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, saveCoupon, openDeleteModal, closeDeleteModal, confirmDelete }
  }
}
</script>

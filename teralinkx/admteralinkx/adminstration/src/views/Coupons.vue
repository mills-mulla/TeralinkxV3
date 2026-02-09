<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Coupons</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage discount coupons</p>
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load coupons</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchCoupons" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Coupons" :value="stats.total_coupons" icon="🎟️" color="blue" />
      <ModernMetricCard title="Active" :value="stats.active_coupons" icon="✅" color="emerald" />
      <ModernMetricCard title="Used" :value="stats.used_coupons" icon="📊" color="purple" />
      <ModernMetricCard title="Expired" :value="stats.expired_coupons" icon="⏰" color="amber" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search coupons..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        @add="openCreateModal"
      />

      <DataTable
        title="Coupon Records"
        :data="filteredCoupons"
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
      title="Coupon"
      :fields="formFields"
      :initial-data="selectedCoupon"
      :loading="saveLoading"
      @close="closeFormModal"
      @submit="saveCoupon"
    />

    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Coupon"
      :message="`Are you sure you want to delete coupon <strong>${couponToDelete?.code}</strong>?`"
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

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'code', label: 'Code', sortable: true },
      { key: 'discount_percentage', label: 'Discount %', sortable: true },
      { key: 'max_uses', label: 'Max Uses', sortable: true },
      { key: 'times_used', label: 'Used', sortable: true },
      { key: 'is_active', label: 'Status', sortable: true },
      { key: 'valid_until', label: 'Valid Until', sortable: true, format: (v) => v ? new Date(v).toLocaleDateString() : 'N/A' }
    ]

    const filters = [
      { key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] }
    ]

    const formFields = [
      { key: 'code', label: 'Coupon Code', type: 'text', required: true, placeholder: 'SAVE20' },
      { key: 'discount_percentage', label: 'Discount %', type: 'number', min: 0, max: 100, required: true },
      { key: 'max_uses', label: 'Max Uses', type: 'number', min: 1, default: 100 },
      { key: 'valid_until', label: 'Valid Until', type: 'date' },
      { key: 'is_active', label: 'Active', type: 'checkbox', checkboxLabel: 'Coupon is active' }
    ]

    const filteredCoupons = computed(() => {
      let result = coupons.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(c => c.code?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(c => c[key] === (value === 'true'))
      })
      return result
    })

    const fetchCoupons = async () => {
      try {
        const data = await makeRequest('get', 'suapi/coupons/')
        coupons.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/coupons/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchCoupons(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedCoupon.value = null; showFormModal.value = true }
    const openEditModal = (coupon) => { selectedCoupon.value = { ...coupon }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedCoupon.value = null }

    const saveCoupon = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `suapi/coupons/${data.id}/` : 'suapi/coupons/'
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
        await makeRequest('delete', `suapi/coupons/${couponToDelete.value.id}/`)
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
      loading, error, coupons, stats, searchTerm, showFormModal, showDeleteModal, selectedCoupon, couponToDelete,
      saveLoading, deleteLoading, columns, filters, formFields, filteredCoupons, fetchCoupons, refreshData,
      handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, saveCoupon,
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

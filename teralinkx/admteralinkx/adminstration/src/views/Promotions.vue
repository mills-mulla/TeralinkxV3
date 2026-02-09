<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Promotions</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage featured promotions</p>
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load promotions</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchPromotions" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Promotions" :value="stats.total_promotions" icon="🎁" color="blue" />
      <ModernMetricCard title="Active" :value="stats.active_promotions" icon="✅" color="emerald" />
      <ModernMetricCard title="Featured" :value="stats.featured_promotions" icon="⭐" color="purple" />
      <ModernMetricCard title="Expired" :value="stats.expired_promotions" icon="⏰" color="amber" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search promotions..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        @add="openCreateModal"
      />

      <DataTable
        title="Promotion Records"
        :data="filteredPromotions"
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
        <template #cell-is_featured="{ value }">
          <span v-if="value" class="text-amber-600 dark:text-amber-400">⭐</span>
          <span v-else class="text-slate-400 dark:text-slate-600">○</span>
        </template>
      </DataTable>
    </div>

    <!-- Modals -->
    <FormModal
      :show="showFormModal"
      title="Promotion"
      :fields="formFields"
      :initial-data="selectedPromotion"
      :loading="saveLoading"
      @close="closeFormModal"
      @submit="savePromotion"
    />

    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Promotion"
      :message="`Are you sure you want to delete promotion <strong>${promotionToDelete?.title}</strong>?`"
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
  name: 'Promotions',
  components: { ModernMetricCard, SearchBar, DataTable, FormModal, ConfirmDialog, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const promotions = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedPromotion = ref(null)
    const promotionToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'title', label: 'Title', sortable: true },
      { key: 'description', label: 'Description', sortable: true },
      { key: 'discount_percentage', label: 'Discount %', sortable: true },
      { key: 'is_active', label: 'Status', sortable: true },
      { key: 'is_featured', label: 'Featured', sortable: true },
      { key: 'valid_until', label: 'Valid Until', sortable: true, format: (v) => v ? new Date(v).toLocaleDateString() : 'N/A' }
    ]

    const filters = [
      { key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] },
      { key: 'is_featured', label: 'Featured', options: [{ value: 'true', label: 'Featured' }, { value: 'false', label: 'Not Featured' }] }
    ]

    const formFields = [
      { key: 'title', label: 'Title', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'textarea', rows: 3, required: true },
      { key: 'discount_percentage', label: 'Discount %', type: 'number', min: 0, max: 100, required: true },
      { key: 'valid_until', label: 'Valid Until', type: 'date' },
      { key: 'is_active', label: 'Active', type: 'checkbox', checkboxLabel: 'Promotion is active' },
      { key: 'is_featured', label: 'Featured', type: 'checkbox', checkboxLabel: 'Show as featured' }
    ]

    const filteredPromotions = computed(() => {
      let result = promotions.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(p => p.title?.toLowerCase().includes(term) || p.description?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(p => p[key] === (value === 'true'))
      })
      return result
    })

    const fetchPromotions = async () => {
      try {
        const data = await makeRequest('get', 'suapi/promotions/')
        promotions.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/promotions/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchPromotions(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const openCreateModal = () => { selectedPromotion.value = null; showFormModal.value = true }
    const openEditModal = (promotion) => { selectedPromotion.value = { ...promotion }; showFormModal.value = true }
    const closeFormModal = () => { showFormModal.value = false; selectedPromotion.value = null }

    const savePromotion = async (data) => {
      saveLoading.value = true
      try {
        const endpoint = data.id ? `suapi/promotions/${data.id}/` : 'suapi/promotions/'
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

    const openDeleteModal = (promotion) => { promotionToDelete.value = promotion; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; promotionToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `suapi/promotions/${promotionToDelete.value.id}/`)
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
      loading, error, promotions, stats, searchTerm, showFormModal, showDeleteModal, selectedPromotion, promotionToDelete,
      saveLoading, deleteLoading, columns, filters, formFields, filteredPromotions, fetchPromotions, refreshData,
      handleFilterChange, clearFilters, openCreateModal, openEditModal, closeFormModal, savePromotion,
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

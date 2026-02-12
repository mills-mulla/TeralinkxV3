<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Vouchers</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage dispatch vouchers</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Voucher
        </button>
        <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load vouchers</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchVouchers" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total" :value="stats.total_vouchers" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active" :value="stats.active_vouchers" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Expired" :value="stats.expired_vouchers" color="amber">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Revenue" :value="`KSh ${formatNumber(stats.total_revenue || 0)}`" color="purple">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
        </svg>
      </ModernMetricCard>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search vouchers..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="used">Used</option>
        </select>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Voucher</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Package</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Price</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Usage</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Activated</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Expires</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="voucher in filteredVouchers" :key="voucher.id" @click="openEditModal(voucher)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42z"/>
                      </svg>
                    </div>
                    <div>
                      <p class="text-xs font-medium text-slate-900 dark:text-white font-mono">{{ voucher.voucher_code }}</p>
                      <p class="text-[10px] text-slate-500 dark:text-slate-400">Sessions: {{ voucher.session_count || 0 }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ voucher.user_username || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ voucher.package_name || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs font-semibold text-slate-900 dark:text-white">KSh {{ formatNumber(voucher.price_paid) }}</td>
                <td class="px-3 py-2">
                  <div class="text-xs text-slate-900 dark:text-white">
                    <div class="flex items-center gap-1">
                      <svg class="w-3 h-3 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
                      <span class="text-[10px]">{{ formatBytes(voucher.download_bytes) }}</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <svg class="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 24 24"><path d="M7 14l5-5 5 5z"/></svg>
                      <span class="text-[10px]">{{ formatBytes(voucher.upload_bytes) }}</span>
                    </div>
                    <div class="text-[10px] font-semibold text-slate-600 dark:text-slate-400 mt-0.5">
                      Total: {{ formatBytes((voucher.download_bytes || 0) + (voucher.upload_bytes || 0)) }}
                    </div>
                  </div>
                </td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getStatusBadge(voucher.status)">
                    {{ voucher.status }}
                  </span>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatDate(voucher.activated_at) }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatDate(voucher.expires_at) }}</td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="openEditModal(voucher)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button @click.stop="openDeleteModal(voucher)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ selectedVoucher?.id ? 'Edit Voucher' : 'Add Voucher' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">User ID</label>
              <input v-model="formData.user" type="number" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Package ID</label>
              <input v-model="formData.package" type="number" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Price Paid (KSh)</label>
              <input v-model="formData.price_paid" type="number" step="0.01" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Expires At</label>
              <input v-model="formData.expires_at" type="datetime-local" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveVoucher" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : (selectedVoucher?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog :show="showDeleteModal" title="Delete Voucher" :message="`Delete voucher ${voucherToDelete?.voucher_code}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Vouchers',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const vouchers = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedVoucher = ref(null)
    const voucherToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({ user: '', package: '', price_paid: 0, expires_at: '' })

    const filteredVouchers = computed(() => {
      let result = vouchers.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(v => v.user_username?.toLowerCase().includes(term) || v.package_name?.toLowerCase().includes(term) || v.voucher_code?.toLowerCase().includes(term))
      }
      if (statusFilter.value) result = result.filter(v => v.status === statusFilter.value)
      return result
    })

    const fetchVouchers = async () => {
      try {
        const data = await makeRequest('get', 'suapi/vouchers/')
        vouchers.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/vouchers/stats/')
      } catch (err) { console.error('Error:', err) }
    }

    const refreshData = () => Promise.all([fetchVouchers(), fetchStats()])
    const formatNumber = (num) => new Intl.NumberFormat().format(num || 0)
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
    const formatBytes = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }
    
    const openAddModal = () => {
      selectedVoucher.value = null
      formData.value = { user: '', package: '', price_paid: 0, expires_at: '' }
      showFormModal.value = true
    }
    
    const openEditModal = (voucher) => {
      selectedVoucher.value = voucher
      formData.value = { user: voucher.user || '', package: voucher.package || '', price_paid: voucher.price_paid || 0, expires_at: voucher.expires_at || '' }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedVoucher.value = null
      formData.value = { user: '', package: '', price_paid: 0, expires_at: '' }
    }

    const saveVoucher = async () => {
      saveLoading.value = true
      try {
        if (selectedVoucher.value?.id) {
          await makeRequest('patch', `suapi/vouchers/${selectedVoucher.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/vouchers/', formData.value)
        }
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

    const getStatusBadge = (status) => {
      const badges = {
        'active': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'expired': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'exhausted': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400',
        'suspended': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400',
        'cancelled': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'
      }
      return badges[status] || badges.suspended
    }

    onMounted(refreshData)

    return {
      loading, error, vouchers, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedVoucher, voucherToDelete,
      saveLoading, deleteLoading, formData, filteredVouchers, fetchVouchers, refreshData, formatNumber, formatDate, formatBytes,
      openAddModal, openEditModal, closeFormModal, saveVoucher, openDeleteModal, closeDeleteModal, confirmDelete, getStatusBadge
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

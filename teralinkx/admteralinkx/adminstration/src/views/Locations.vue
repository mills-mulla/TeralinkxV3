<template>
  <div class="space-y-4 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Locations</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage network locations</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
          Add Location
        </button>
        <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
        </button>
      </div>
    </div>

    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load locations</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchLocations" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total" :value="stats.total_locations" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active" :value="stats.active_locations" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Hotspots" :value="stats.hotspot_locations" color="purple">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Branches" :value="stats.branch_locations" color="amber">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
      </ModernMetricCard>
    </div>

    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search locations..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Location</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Code</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">City</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Capacity</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="location in filteredLocations" :key="location.id" @click="openEditModal(location)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-green-500 to-teal-600 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                    </div>
                    <p class="text-xs font-medium text-slate-900 dark:text-white">{{ location.name }}</p>
                  </div>
                </td>
                <td class="px-3 py-2 text-xs font-mono text-slate-900 dark:text-white">{{ location.code }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ location.location_type }}</span></td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ location.city || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ location.max_concurrent_users }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="location.is_active ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'">{{ location.is_active ? 'Active' : 'Inactive' }}</span></td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="openEditModal(location)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button @click.stop="openDeleteModal(location)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ selectedLocation?.id ? 'Edit Location' : 'Add Location' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label><input v-model="formData.name" type="text" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Code *</label><input v-model="formData.code" type="text" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Type *</label><select v-model="formData.location_type" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"><option value="headquarters">Headquarters</option><option value="branch">Branch</option><option value="hotspot">Hotspot</option><option value="commercial">Commercial</option><option value="fallback">Fallback</option></select></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">City</label><input v-model="formData.city" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Max Users</label><input v-model="formData.max_concurrent_users" type="number" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Router IP</label><input v-model="formData.router_ip" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div class="flex items-center"><label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Active</span></label></div>
            <div class="flex items-center"><label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.allow_roaming_in" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Allow Roaming In</span></label></div>
            <div class="col-span-2"><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Address</label><textarea v-model="formData.address" rows="2" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"></textarea></div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveLocation" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : (selectedLocation?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <ConfirmDialog :show="showDeleteModal" title="Delete Location" :message="`Delete location ${locationToDelete?.name}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Locations',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const locations = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedLocation = ref(null)
    const locationToDelete = ref(null)
    const saveLoading = ref(false)
    const formData = ref({ name: '', code: '', location_type: 'hotspot', city: '', max_concurrent_users: 100, router_ip: '', is_active: true, allow_roaming_in: true, address: '' })

    const filteredLocations = computed(() => {
      let result = locations.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(l => l.name?.toLowerCase().includes(term) || l.code?.toLowerCase().includes(term) || l.city?.toLowerCase().includes(term))
      }
      if (statusFilter.value) result = result.filter(l => l.is_active === (statusFilter.value === 'true'))
      return result
    })

    const fetchLocations = async () => {
      try {
        const data = await makeRequest('get', 'suapi/locations/')
        locations.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/locations/stats/')
      } catch (err) { console.error('Error:', err) }
    }

    const refreshData = () => Promise.all([fetchLocations(), fetchStats()])
    
    const openAddModal = () => {
      selectedLocation.value = null
      formData.value = { name: '', code: '', location_type: 'hotspot', city: '', max_concurrent_users: 100, router_ip: '', is_active: true, allow_roaming_in: true, address: '' }
      showFormModal.value = true
    }
    
    const openEditModal = (location) => {
      selectedLocation.value = location
      formData.value = { name: location.name || '', code: location.code || '', location_type: location.location_type || 'hotspot', city: location.city || '', max_concurrent_users: location.max_concurrent_users || 100, router_ip: location.router_ip || '', is_active: location.is_active || false, allow_roaming_in: location.allow_roaming_in || false, address: location.address || '' }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedLocation.value = null
      formData.value = { name: '', code: '', location_type: 'hotspot', city: '', max_concurrent_users: 100, router_ip: '', is_active: true, allow_roaming_in: true, address: '' }
    }

    const saveLocation = async () => {
      saveLoading.value = true
      try {
        if (selectedLocation.value?.id) {
          await makeRequest('patch', `suapi/locations/${selectedLocation.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/locations/', formData.value)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || JSON.stringify(err.response?.data) || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const openDeleteModal = (location) => { locationToDelete.value = location; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; locationToDelete.value = null }

    const confirmDelete = async () => {
      try {
        await makeRequest('delete', `suapi/locations/${locationToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    onMounted(refreshData)

    return {
      loading, error, locations, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedLocation, locationToDelete,
      saveLoading, formData, filteredLocations, fetchLocations, refreshData,
      openAddModal, openEditModal, closeFormModal, saveLocation, openDeleteModal, closeDeleteModal, confirmDelete
    }
  }
}
</script>

<style scoped>
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes slide-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 0.3s ease-out; }
.animate-slide-up { animation: slide-up 0.4s ease-out; }
</style>

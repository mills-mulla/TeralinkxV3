<template>
  <div class="space-y-6">
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-100 text-sm font-medium">Total Budget</p>
            <p class="text-3xl font-bold mt-2">KES {{ formatNumber(totalBudget) }}</p>
          </div>
          <svg class="w-12 h-12 text-blue-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-purple-100 text-sm font-medium">Total Spent</p>
            <p class="text-3xl font-bold mt-2">KES {{ formatNumber(totalSpent) }}</p>
          </div>
          <svg class="w-12 h-12 text-purple-200" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-emerald-100 text-sm font-medium">Avg Utilization</p>
            <p class="text-3xl font-bold mt-2">{{ avgUtilization.toFixed(0) }}%</p>
          </div>
          <svg class="w-12 h-12 text-emerald-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-amber-100 text-sm font-medium">Active Departments</p>
            <p class="text-3xl font-bold mt-2">{{ activeCount }}</p>
          </div>
          <svg class="w-12 h-12 text-amber-200" fill="currentColor" viewBox="0 0 20 20">
            <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Departments Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
      <div class="p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
        <h2 class="text-xl font-bold text-slate-900 dark:text-white">Department Budgets</h2>
        <button @click="openAddModal" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Department
        </button>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Department</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Manager</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Budget</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Spent</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Remaining</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Utilization</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="dept in data" :key="dept.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-slate-900 dark:text-white">{{ dept.name }}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400">{{ dept.code }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600 dark:text-slate-400">{{ dept.manager_name || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-slate-900 dark:text-white">KES {{ formatNumber(dept.budget) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-slate-900 dark:text-white">KES {{ formatNumber(dept.spent) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm" :class="dept.remaining >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
                  KES {{ formatNumber(dept.remaining) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="flex-1 bg-slate-200 dark:bg-slate-700 rounded-full h-2 w-24">
                    <div 
                      class="h-2 rounded-full transition-all" 
                      :class="getUtilizationColor(dept.utilization)"
                      :style="{ width: Math.min(dept.utilization, 100) + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium text-slate-900 dark:text-white">{{ dept.utilization.toFixed(0) }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="dept.is_active" class="px-2 py-1 text-xs font-medium rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                  Active
                </span>
                <span v-else class="px-2 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400">
                  Inactive
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="openEditModal(dept)" class="p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="openDeleteModal(dept)" class="p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                    <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

    <!-- Form Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">{{ selectedDepartment ? 'Edit Department' : 'Add Department' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Name *</label>
              <input v-model="formData.name" type="text" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Code *</label>
              <input v-model="formData.code" type="text" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Budget (KES) *</label>
            <input v-model="formData.budget" type="number" step="0.01" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
          </div>
          <div>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" />
              <span class="text-sm text-slate-700 dark:text-slate-300">Active Department</span>
            </label>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveDepartment" :disabled="saveLoading" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : 'Save' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeDeleteModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-md w-full">
        <div class="p-6">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Delete Department</h3>
              <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">Are you sure you want to delete "{{ departmentToDelete?.name }}"?</p>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeDeleteModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="confirmDelete" :disabled="deleteLoading" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg" :class="{ 'opacity-50': deleteLoading }">{{ deleteLoading ? 'Deleting...' : 'Delete' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Departments',
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  emits: ['refresh'],
  data() {
    return {
      showFormModal: false,
      showDeleteModal: false,
      selectedDepartment: null,
      departmentToDelete: null,
      saveLoading: false,
      deleteLoading: false,
      formData: {
        name: '',
        code: '',
        budget: 0,
        is_active: true
      }
    }
  },
  computed: {
    totalBudget() {
      return this.data.reduce((sum, dept) => sum + (dept.budget || 0), 0)
    },
    totalSpent() {
      return this.data.reduce((sum, dept) => sum + (dept.spent || 0), 0)
    },
    avgUtilization() {
      if (this.data.length === 0) return 0
      return this.data.reduce((sum, dept) => sum + (dept.utilization || 0), 0) / this.data.length
    },
    activeCount() {
      return this.data.filter(d => d.is_active).length
    }
  },
  methods: {
    formatNumber(num) {
      return new Intl.NumberFormat('en-KE').format(num || 0)
    },
    getUtilizationColor(utilization) {
      if (utilization >= 90) return 'bg-red-500'
      if (utilization >= 75) return 'bg-amber-500'
      if (utilization >= 50) return 'bg-blue-500'
      return 'bg-emerald-500'
    },
    openAddModal() {
      this.selectedDepartment = null
      this.formData = {
        name: '',
        code: '',
        budget: 0,
        is_active: true
      }
      this.showFormModal = true
    },
    openEditModal(dept) {
      this.selectedDepartment = dept
      this.formData = {
        name: dept.name,
        code: dept.code,
        budget: dept.budget,
        is_active: dept.is_active
      }
      this.showFormModal = true
    },
    closeFormModal() {
      this.showFormModal = false
      this.selectedDepartment = null
    },
    async saveDepartment() {
      this.saveLoading = true
      try {
        const url = this.selectedDepartment 
          ? `https://service.teralinkxwaves.uk/api/finance/api/departments/${this.selectedDepartment.id}/`
          : 'https://service.teralinkxwaves.uk/api/finance/api/departments/'
        const method = this.selectedDepartment ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify(this.formData)
        })
        
        if (!response.ok) throw new Error('Failed to save')
        this.$emit('refresh')
        this.closeFormModal()
      } catch (error) {
        console.error('Error saving department:', error)
        alert('Failed to save department')
      } finally {
        this.saveLoading = false
      }
    },
    openDeleteModal(dept) {
      this.departmentToDelete = dept
      this.showDeleteModal = true
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.departmentToDelete = null
    },
    async confirmDelete() {
      this.deleteLoading = true
      try {
        const response = await fetch(`https://service.teralinkxwaves.uk/api/finance/api/departments/${this.departmentToDelete.id}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        
        if (!response.ok) throw new Error('Failed to delete')
        this.$emit('refresh')
        this.closeDeleteModal()
      } catch (error) {
        console.error('Error deleting department:', error)
        alert('Failed to delete department')
      } finally {
        this.deleteLoading = false
      }
    }
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-indigo-100 text-sm font-medium">Total Invested</p>
            <p class="text-3xl font-bold mt-2">KES {{ formatNumber(totalInvested) }}</p>
          </div>
          <svg class="w-12 h-12 text-indigo-200" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-teal-100 text-sm font-medium">Current Value</p>
            <p class="text-3xl font-bold mt-2">KES {{ formatNumber(currentValue) }}</p>
          </div>
          <svg class="w-12 h-12 text-teal-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-cyan-100 text-sm font-medium">Total ROI</p>
            <p class="text-3xl font-bold mt-2">{{ avgROI.toFixed(1) }}%</p>
          </div>
          <svg class="w-12 h-12 text-cyan-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-violet-500 to-violet-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-violet-100 text-sm font-medium">Active Investments</p>
            <p class="text-3xl font-bold mt-2">{{ activeCount }}</p>
          </div>
          <svg class="w-12 h-12 text-violet-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Investments Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
      <div class="p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
        <h2 class="text-xl font-bold text-slate-900 dark:text-white">Investment Portfolio</h2>
        <button @click="openAddModal" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Investment
        </button>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Current Value</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">ROI</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="investment in data" :key="investment.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-slate-900 dark:text-white">{{ investment.name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getTypeColor(investment.investment_type)">
                  {{ investment.type_display }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-slate-900 dark:text-white">KES {{ formatNumber(investment.amount) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-slate-900 dark:text-white">KES {{ formatNumber(investment.current_value) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-1">
                  <svg v-if="investment.roi > 0" class="w-4 h-4 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                  </svg>
                  <svg v-else-if="investment.roi < 0" class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                  <span class="text-sm font-medium" :class="investment.roi > 0 ? 'text-emerald-600 dark:text-emerald-400' : investment.roi < 0 ? 'text-red-600 dark:text-red-400' : 'text-slate-600 dark:text-slate-400'">
                    {{ investment.roi.toFixed(1) }}%
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600 dark:text-slate-400">{{ formatDate(investment.investment_date) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getStatusColor(investment.status)">
                  {{ investment.status_display }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="openEditModal(investment)" class="p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="openDeleteModal(investment)" class="p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
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
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">{{ selectedInvestment ? 'Edit Investment' : 'Add Investment' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Name *</label>
            <input v-model="formData.name" type="text" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Type *</label>
              <select v-model="formData.investment_type" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="equity">Equity</option>
                <option value="debt">Debt</option>
                <option value="infrastructure">Infrastructure</option>
                <option value="technology">Technology</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Amount (KES) *</label>
              <input v-model="formData.amount" type="number" step="0.01" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Current Value (KES) *</label>
              <input v-model="formData.current_value" type="number" step="0.01" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Investment Date *</label>
              <input v-model="formData.investment_date" type="date" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Status *</label>
            <select v-model="formData.status" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
              <option value="active">Active</option>
              <option value="matured">Matured</option>
              <option value="liquidated">Liquidated</option>
            </select>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveInvestment" :disabled="saveLoading" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : 'Save' }}</button>
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
              <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Delete Investment</h3>
              <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">Are you sure you want to delete "{{ investmentToDelete?.name }}"?</p>
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
  name: 'Investments',
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
      selectedInvestment: null,
      investmentToDelete: null,
      saveLoading: false,
      deleteLoading: false,
      formData: {
        name: '',
        investment_type: 'equity',
        amount: 0,
        current_value: 0,
        investment_date: new Date().toISOString().split('T')[0],
        status: 'active'
      }
    }
  },
  computed: {
    totalInvested() {
      return this.data.reduce((sum, inv) => sum + (inv.amount || 0), 0)
    },
    currentValue() {
      return this.data.reduce((sum, inv) => sum + (inv.current_value || 0), 0)
    },
    avgROI() {
      if (this.data.length === 0) return 0
      return this.data.reduce((sum, inv) => sum + (inv.roi || 0), 0) / this.data.length
    },
    activeCount() {
      return this.data.filter(i => i.status === 'active').length
    }
  },
  methods: {
    formatNumber(num) {
      return new Intl.NumberFormat('en-KE').format(num || 0)
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('en-KE', { year: 'numeric', month: 'short', day: 'numeric' })
    },
    getTypeColor(type) {
      const colors = {
        'equity': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
        'debt': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
        'infrastructure': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
        'technology': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        'other': 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400'
      }
      return colors[type] || colors.other
    },
    getStatusColor(status) {
      const colors = {
        'active': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
        'matured': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        'liquidated': 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400'
      }
      return colors[status] || colors.active
    },
    openAddModal() {
      this.selectedInvestment = null
      this.formData = {
        name: '',
        investment_type: 'equity',
        amount: 0,
        current_value: 0,
        investment_date: new Date().toISOString().split('T')[0],
        status: 'active'
      }
      this.showFormModal = true
    },
    openEditModal(investment) {
      this.selectedInvestment = investment
      this.formData = {
        name: investment.name,
        investment_type: investment.investment_type,
        amount: investment.amount,
        current_value: investment.current_value,
        investment_date: investment.investment_date,
        status: investment.status
      }
      this.showFormModal = true
    },
    closeFormModal() {
      this.showFormModal = false
      this.selectedInvestment = null
    },
    async saveInvestment() {
      this.saveLoading = true
      try {
        const url = this.selectedInvestment 
          ? `https://srv.teralinkxwaves.uk/api/finance/api/investments/${this.selectedInvestment.id}/`
          : 'https://srv.teralinkxwaves.uk/api/finance/api/investments/'
        const method = this.selectedInvestment ? 'PUT' : 'POST'
        
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
        console.error('Error saving investment:', error)
        alert('Failed to save investment')
      } finally {
        this.saveLoading = false
      }
    },
    openDeleteModal(investment) {
      this.investmentToDelete = investment
      this.showDeleteModal = true
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.investmentToDelete = null
    },
    async confirmDelete() {
      this.deleteLoading = true
      try {
        const response = await fetch(`https://srv.teralinkxwaves.uk/api/finance/api/investments/${this.investmentToDelete.id}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        
        if (!response.ok) throw new Error('Failed to delete')
        this.$emit('refresh')
        this.closeDeleteModal()
      } catch (error) {
        console.error('Error deleting investment:', error)
        alert('Failed to delete investment')
      } finally {
        this.deleteLoading = false
      }
    }
  }
}
</script>

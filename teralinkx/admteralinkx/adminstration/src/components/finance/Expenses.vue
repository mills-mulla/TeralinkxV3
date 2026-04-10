<template>
  <div class="space-y-6">
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-red-100 text-sm font-medium">Total Expenses</p>
            <p class="text-3xl font-bold mt-2">KES {{ formatNumber(totalExpenses) }}</p>
          </div>
          <svg class="w-12 h-12 text-red-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-orange-100 text-sm font-medium">Pending Approval</p>
            <p class="text-3xl font-bold mt-2">{{ pendingCount }}</p>
          </div>
          <svg class="w-12 h-12 text-orange-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-emerald-100 text-sm font-medium">Paid This Month</p>
            <p class="text-3xl font-bold mt-2">KES {{ formatNumber(paidThisMonth) }}</p>
          </div>
          <svg class="w-12 h-12 text-emerald-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-slate-500 to-slate-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-slate-100 text-sm font-medium">Total Items</p>
            <p class="text-3xl font-bold mt-2">{{ data.length }}</p>
          </div>
          <svg class="w-12 h-12 text-slate-200" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Expenses Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
      <div class="p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
        <h2 class="text-xl font-bold text-slate-900 dark:text-white">Expense Records</h2>
        <button @click="openAddModal" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Expense
        </button>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Description</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Category</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Department</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="expense in data" :key="expense.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-slate-900 dark:text-white">{{ expense.description }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getCategoryColor(expense.category)">
                  {{ expense.category_display }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-slate-900 dark:text-white">KES {{ formatNumber(expense.amount) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600 dark:text-slate-400">{{ expense.department_name || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600 dark:text-slate-400">{{ formatDate(expense.expense_date) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getStatusColor(expense.status)">
                  {{ expense.status_display }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="openEditModal(expense)" class="p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="openDeleteModal(expense)" class="p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
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
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">{{ selectedExpense ? 'Edit Expense' : 'Add Expense' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Description *</label>
            <input v-model="formData.description" type="text" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Category *</label>
              <select v-model="formData.category" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="operational">Operational</option>
                <option value="marketing">Marketing</option>
                <option value="infrastructure">Infrastructure</option>
                <option value="salaries">Salaries</option>
                <option value="maintenance">Maintenance</option>
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
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Expense Date *</label>
              <input v-model="formData.expense_date" type="date" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Status *</label>
              <select v-model="formData.status" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="paid">Paid</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveExpense" :disabled="saveLoading" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : 'Save' }}</button>
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
              <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Delete Expense</h3>
              <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">Are you sure you want to delete this expense?</p>
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
import { useApi } from '../../composables/useApi'

export default {
  name: 'Expenses',
  setup() {
    const { makeRequest } = useApi()
    return { makeRequest }
  },
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
      selectedExpense: null,
      expenseToDelete: null,
      saveLoading: false,
      deleteLoading: false,
      formData: {
        description: '',
        category: 'operational',
        amount: 0,
        expense_date: new Date().toISOString().split('T')[0],
        status: 'pending'
      }
    }
  },
  computed: {
    totalExpenses() {
      return this.data.reduce((sum, exp) => sum + (exp.amount || 0), 0)
    },
    pendingCount() {
      return this.data.filter(e => e.status === 'pending').length
    },
    paidThisMonth() {
      const now = new Date()
      const thisMonth = now.getMonth()
      const thisYear = now.getFullYear()
      return this.data
        .filter(e => {
          const expDate = new Date(e.expense_date)
          return e.status === 'paid' && expDate.getMonth() === thisMonth && expDate.getFullYear() === thisYear
        })
        .reduce((sum, e) => sum + (e.amount || 0), 0)
    }
  },
  methods: {
    formatNumber(num) {
      return new Intl.NumberFormat('en-KE').format(num || 0)
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('en-KE', { year: 'numeric', month: 'short', day: 'numeric' })
    },
    getCategoryColor(category) {
      const colors = {
        'operational': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        'marketing': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
        'infrastructure': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
        'salaries': 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
        'maintenance': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
        'other': 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400'
      }
      return colors[category] || colors.other
    },
    getStatusColor(status) {
      const colors = {
        'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
        'approved': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        'paid': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
        'rejected': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
      }
      return colors[status] || colors.pending
    },
    openAddModal() {
      this.selectedExpense = null
      this.formData = {
        description: '',
        category: 'operational',
        amount: 0,
        expense_date: new Date().toISOString().split('T')[0],
        status: 'pending'
      }
      this.showFormModal = true
    },
    openEditModal(expense) {
      this.selectedExpense = expense
      this.formData = {
        description: expense.description,
        category: expense.category,
        amount: expense.amount,
        expense_date: expense.expense_date,
        status: expense.status
      }
      this.showFormModal = true
    },
    closeFormModal() {
      this.showFormModal = false
      this.selectedExpense = null
    },
    async saveExpense() {
      this.saveLoading = true
      try {
        const url = this.selectedExpense
          ? `api/finance/api/expenses/${this.selectedExpense.id}/`
          : 'api/finance/api/expenses/'
        const method = this.selectedExpense ? 'put' : 'post'
        await this.makeRequest(method, url, this.formData)
        this.$emit('refresh')
        this.closeFormModal()
      } catch (error) {
        console.error('Error saving expense:', error)
        alert('Failed to save expense')
      } finally {
        this.saveLoading = false
      }
    },
    openDeleteModal(expense) {
      this.expenseToDelete = expense
      this.showDeleteModal = true
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.expenseToDelete = null
    },
    async confirmDelete() {
      this.deleteLoading = true
      try {
        await this.makeRequest('delete', `api/finance/api/expenses/${this.expenseToDelete.id}/`)
        this.$emit('refresh')
        this.closeDeleteModal()
      } catch (error) {
        console.error('Error deleting expense:', error)
        alert('Failed to delete expense')
      } finally {
        this.deleteLoading = false
      }
    }
  }
}
</script>

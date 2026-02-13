<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white">Finance Management</h1>
        <p class="text-slate-600 dark:text-slate-400 mt-1">Manage revenue streams, expenses, investments, and financial reports</p>
      </div>
      <button @click="refreshData" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Tabs -->
    <div class="border-b border-slate-200 dark:border-slate-700">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400 dark:hover:text-slate-300'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div>
      <!-- Revenue Streams Tab -->
      <div v-if="activeTab === 'revenue-streams'">
        <RevenueStreams :data="revenueStreams" @refresh="fetchRevenueStreams" />
      </div>

      <!-- Expenses Tab -->
      <div v-if="activeTab === 'expenses'">
        <Expenses :data="expenses" @refresh="fetchExpenses" />
      </div>

      <!-- Investments Tab -->
      <div v-if="activeTab === 'investments'">
        <Investments :data="investments" @refresh="fetchInvestments" />
      </div>

      <!-- Departments Tab -->
      <div v-if="activeTab === 'departments'">
        <Departments :data="departments" @refresh="fetchDepartments" />
      </div>
    </div>
  </div>
</template>

<script>
import RevenueStreams from '../components/finance/RevenueStreams.vue'
import Expenses from '../components/finance/Expenses.vue'
import Investments from '../components/finance/Investments.vue'
import Departments from '../components/finance/Departments.vue'

export default {
  name: 'Finance',
  components: {
    RevenueStreams,
    Expenses,
    Investments,
    Departments
  },
  data() {
    return {
      activeTab: 'revenue-streams',
      tabs: [
        { id: 'revenue-streams', name: 'Revenue Streams' },
        { id: 'expenses', name: 'Expenses' },
        { id: 'investments', name: 'Investments' },
        { id: 'departments', name: 'Departments' }
      ],
      revenueStreams: [],
      expenses: [],
      investments: [],
      departments: []
    }
  },
  methods: {
    async fetchRevenueStreams() {
      try {
        const response = await fetch('https://service.teralinkxwaves.uk/api/finance/api/revenue-streams/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        if (!response.ok) throw new Error('Failed to fetch')
        this.revenueStreams = await response.json()
      } catch (error) {
        console.error('Error fetching revenue streams:', error)
        this.revenueStreams = []
      }
    },
    async fetchExpenses() {
      try {
        const response = await fetch('https://service.teralinkxwaves.uk/api/finance/api/expenses/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        if (!response.ok) throw new Error('Failed to fetch')
        this.expenses = await response.json()
      } catch (error) {
        console.error('Error fetching expenses:', error)
        this.expenses = []
      }
    },
    async fetchInvestments() {
      try {
        const response = await fetch('https://service.teralinkxwaves.uk/api/finance/api/investments/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        if (!response.ok) throw new Error('Failed to fetch')
        this.investments = await response.json()
      } catch (error) {
        console.error('Error fetching investments:', error)
        this.investments = []
      }
    },
    async fetchDepartments() {
      try {
        const response = await fetch('https://service.teralinkxwaves.uk/api/finance/api/departments/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        if (!response.ok) throw new Error('Failed to fetch')
        this.departments = await response.json()
      } catch (error) {
        console.error('Error fetching departments:', error)
        this.departments = []
      }
    },
    refreshData() {
      this.fetchRevenueStreams()
      this.fetchExpenses()
      this.fetchInvestments()
      this.fetchDepartments()
    }
  },
  mounted() {
    this.refreshData()
  }
}
</script>

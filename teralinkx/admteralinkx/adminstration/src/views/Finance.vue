<template>
  <div class="p-6 space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white">Finance Management</h1>
        <p class="text-slate-600 dark:text-slate-400 mt-1">Complete enterprise finance — revenue, expenses, payroll, tax, and more</p>
      </div>
      <button @click="refreshData" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Tab Groups -->
    <div class="border-b border-slate-200 dark:border-slate-700 overflow-x-auto">
      <nav class="-mb-px flex space-x-1 min-w-max">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          :class="['py-3 px-3 border-b-2 font-medium text-xs transition-colors whitespace-nowrap',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400']">
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <div>
      <!-- Existing tabs -->
      <div v-if="activeTab === 'analytics'" class="space-y-6">
        <FinancialAnalytics :metrics="metrics" :packages="packagePerformance" :loading="loading" />
        <RevenueForecast :data="forecastData" :loading="loading" />
      </div>
      <div v-if="activeTab === 'kpi'"><KpiDashboard ref="kpiRef" /></div>
      <div v-if="activeTab === 'revenue-streams'"><RevenueStreams :data="revenueStreams" @refresh="fetchRevenueStreams" /></div>
      <div v-if="activeTab === 'expenses'"><Expenses :data="expenses" @refresh="fetchExpenses" /></div>
      <div v-if="activeTab === 'budget'"><BudgetDashboard ref="budgetRef" /></div>
      <div v-if="activeTab === 'revenue-at-risk'"><RevenueAtRisk ref="rarRef" /></div>
      <div v-if="activeTab === 'pricing'"><PricingIntelligence /></div>
      <div v-if="activeTab === 'vendors'"><VendorIntelligence /></div>
      <div v-if="activeTab === 'board-reports'"><BoardReports ref="boardRef" /></div>
      <div v-if="activeTab === 'reconciliation'"><Reconciliation ref="reconRef" /></div>
      <div v-if="activeTab === 'investments'"><Investments ref="invRef" /></div>
      <div v-if="activeTab === 'departments'"><Departments :data="departments" @refresh="fetchDepartments" /></div>
      <!-- Phase 7 new tabs -->
      <div v-if="activeTab === 'invoices'"><Invoices ref="invoicesRef" /></div>
      <div v-if="activeTab === 'vat'"><VATDashboard ref="vatRef" /></div>
      <div v-if="activeTab === 'tax'"><TaxCalendar ref="taxRef" /></div>
      <div v-if="activeTab === 'credit-notes'"><CreditNotes ref="cnRef" /></div>
      <div v-if="activeTab === 'payroll'"><Payroll ref="payrollRef" /></div>
      <div v-if="activeTab === 'assets'"><AssetRegister ref="assetRef" /></div>
      <div v-if="activeTab === 'ap'"><AccountsPayable ref="apRef" /></div>
      <div v-if="activeTab === 'reminders'"><PaymentReminders ref="remRef" /></div>
      <div v-if="activeTab === 'ar-collection'"><ARCollection ref="arRef" /></div>
      <div v-if="activeTab === 'pl'"><ProfitLoss ref="plRef" /></div>
      <div v-if="activeTab === 'bank-import'"><BankImport ref="bankRef" /></div>
      <div v-if="activeTab === 'recurring-billing'"><RecurringBilling ref="billingRef" /></div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../composables/useApi'
import FinancialAnalytics from '../components/FinancialAnalytics.vue'
import RevenueForecast from '../components/RevenueForecast.vue'
import RevenueStreams from '../components/finance/RevenueStreams.vue'
import Expenses from '../components/finance/Expenses.vue'
import Investments from '../components/finance/Investments.vue'
import Departments from '../components/finance/Departments.vue'
import KpiDashboard from '../components/finance/KpiDashboard.vue'
import BudgetDashboard from '../components/finance/BudgetDashboard.vue'
import RevenueAtRisk from '../components/finance/RevenueAtRisk.vue'
import PricingIntelligence from '../components/finance/PricingIntelligence.vue'
import VendorIntelligence from '../components/finance/VendorIntelligence.vue'
import BoardReports from '../components/finance/BoardReports.vue'
import Reconciliation from '../components/finance/Reconciliation.vue'
import Invoices from '../components/finance/Invoices.vue'
import VATDashboard from '../components/finance/VATDashboard.vue'
import TaxCalendar from '../components/finance/TaxCalendar.vue'
import CreditNotes from '../components/finance/CreditNotes.vue'
import Payroll from '../components/finance/Payroll.vue'
import AssetRegister from '../components/finance/AssetRegister.vue'
import AccountsPayable from '../components/finance/AccountsPayable.vue'
import PaymentReminders from '../components/finance/PaymentReminders.vue'
import ARCollection from '../components/finance/ARCollection.vue'
import ProfitLoss from '../components/finance/ProfitLoss.vue'
import BankImport from '../components/finance/BankImport.vue'
import RecurringBilling from '../components/finance/RecurringBilling.vue'
import ExpenseNotifications from '../components/finance/ExpenseNotifications.vue'
import FinancialYear from '../components/finance/FinancialYear.vue'
import PettyCash from '../components/finance/PettyCash.vue'
import PurchaseOrders from '../components/finance/PurchaseOrders.vue'
import AuditTrail from '../components/finance/AuditTrail.vue'

export default {
  name: 'Finance',
  components: {
    FinancialAnalytics, RevenueForecast, RevenueStreams, Expenses,
    Investments, Departments, KpiDashboard, BudgetDashboard,
    RevenueAtRisk, PricingIntelligence, VendorIntelligence,
    BoardReports, Reconciliation,
    Invoices, VATDashboard, TaxCalendar, CreditNotes,
    Payroll, AssetRegister, AccountsPayable, PaymentReminders,
    ARCollection, ProfitLoss, BankImport, RecurringBilling,
  },
  setup() {
    const { makeRequest } = useApi()
    return { makeRequest }
  },
  data() {
    return {
      activeTab: 'analytics',
      tabs: [
        // Core
        { id: 'analytics',       name: '📊 Analytics' },
        { id: 'kpi',             name: '🎯 KPI' },
        // Revenue
        { id: 'revenue-streams', name: '💰 Revenue' },
        { id: 'invoices',        name: '🧾 Invoices' },
        { id: 'revenue-at-risk', name: '⚠️ At Risk' },
        // Expenses & Payroll
        { id: 'expenses',        name: '💸 Expenses' },
        { id: 'payroll',         name: '👥 Payroll' },
        { id: 'ap',              name: '🏦 Payables' },
        { id: 'assets',          name: '🏗️ Assets' },
        // Tax & Compliance
        { id: 'vat',             name: '📋 VAT' },
        { id: 'tax',             name: '🗓️ Tax Calendar' },
        { id: 'credit-notes',    name: '📝 Credit Notes' },
        { id: 'reminders',       name: '🔔 Reminders' },
        { id: 'ar-collection',   name: '📥 AR Collection' },
        { id: 'pl',              name: '📉 P&L' },
        { id: 'bank-import',     name: '🏦 Bank Import' },
        { id: 'recurring-billing', name: '🔁 Recurring' },
        // Planning & Reporting
        { id: 'budget',          name: '📊 Budget' },
        { id: 'board-reports',   name: '📑 Board Reports' },
        { id: 'reconciliation',  name: '🔄 Reconciliation' },
        // Other
        { id: 'pricing',         name: '💡 Pricing' },
        { id: 'vendors',         name: '🏭 Vendors' },
        { id: 'investments',     name: '📈 Investments' },
        { id: 'departments',     name: '🏢 Departments' },
      ],
      loading: false,
      metrics: { mrr: 0, arr: 0, arpu: 0, ltv: 0, growth_rate: 0 },
      forecastData: { historical: [], forecast: [], avg_monthly_growth: 0, trend: 'upward' },
      packagePerformance: [],
      revenueStreams: [],
      expenses: [],
      departments: []
    }
  },
  methods: {
    async fetchMetrics() {
      try {
        this.loading = true
        const data = await this.makeRequest('get', 'api/finance/api/metrics/')
        this.metrics = { mrr: data.mrr || 0, arr: data.arr || 0, arpu: data.arpu || 0, ltv: data.ltv || 0, growth_rate: data.growth_rate || 0 }
      } catch (e) { console.error('fetchMetrics:', e) }
      finally { this.loading = false }
    },
    async fetchPackagePerformance() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/package-performance/')
        const list = Array.isArray(data) ? data : (data.results || [])
        this.packagePerformance = list.map(pkg => ({ name: pkg.package_name, sales: pkg.sales, revenue: pkg.revenue, profit: pkg.revenue * 0.7, margin: 70 }))
      } catch (e) { console.error('fetchPackagePerformance:', e) }
    },
    async fetchForecast() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/kpi/summary/')
        if (data) {
          this.forecastData = { historical: data.revenue_history || [], forecast: data.revenue_forecast || [], avg_monthly_growth: data.mrr_growth_pct || 0, trend: (data.mrr_growth_pct || 0) >= 0 ? 'upward' : 'downward' }
        }
      } catch (e) { console.error('fetchForecast:', e) }
    },
    async fetchRevenueStreams() {
      try { const data = await this.makeRequest('get', 'api/finance/api/revenue-streams/'); this.revenueStreams = Array.isArray(data) ? data : (data.results || []) }
      catch (e) { this.revenueStreams = [] }
    },
    async fetchExpenses() {
      try { const data = await this.makeRequest('get', 'api/finance/api/expenses/'); this.expenses = Array.isArray(data) ? data : (data.results || []) }
      catch (e) { this.expenses = [] }
    },
    async fetchDepartments() {
      try { const data = await this.makeRequest('get', 'api/finance/api/departments/'); this.departments = Array.isArray(data) ? data : (data.results || []) }
      catch (e) { this.departments = [] }
    },
    refreshData() {
      this.fetchMetrics()
      this.fetchPackagePerformance()
      this.fetchForecast()
      this.fetchRevenueStreams()
      this.fetchExpenses()
      this.fetchDepartments()
      this.$refs.kpiRef?.refresh?.()
      this.$refs.budgetRef?.refresh?.()
      this.$refs.rarRef?.refresh?.()
      this.$refs.boardRef?.refresh?.()
      this.$refs.reconRef?.refresh?.()
      this.$refs.invRef?.load?.()
      this.$refs.invoicesRef?.load?.()
      this.$refs.vatRef?.load?.()
      this.$refs.taxRef?.load?.()
      this.$refs.cnRef?.load?.()
      this.$refs.assetRef?.load?.()
      this.$refs.apRef?.load?.()
    }
  },
  mounted() { this.refreshData() }
}
</script>

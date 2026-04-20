<template>
  <div class="p-6">
    <!-- Breadcrumb -->
    <div class="mb-4 flex items-center gap-2 text-xs text-slate-500">
      <span>Finance</span>
      <span>›</span>
      <span class="text-slate-900 dark:text-white font-medium">{{ activeTabLabel }}</span>
    </div>

    <div v-if="activeTab === 'analytics'" class="space-y-6">
      <FinancialAnalytics :metrics="metrics" :packages="packagePerformance" :loading="loading" />
      <RevenueForecast />
    </div>
    <div v-if="activeTab === 'kpi'"><KpiDashboard ref="kpiRef" /></div>
    <div v-if="activeTab === 'pl'"><ProfitLoss ref="plRef" /></div>
    <div v-if="activeTab === 'budget'"><BudgetDashboard ref="budgetRef" /></div>
    <div v-if="activeTab === 'invoices'"><Invoices ref="invoicesRef" /></div>
    <div v-if="activeTab === 'revenue-streams'"><RevenueStreams :data="revenueStreams" @refresh="fetchRevenueStreams" /></div>
    <div v-if="activeTab === 'recurring-billing'"><RecurringBilling ref="billingRef" /></div>
    <div v-if="activeTab === 'ar-collection'"><ARCollection ref="arRef" /></div>
    <div v-if="activeTab === 'revenue-at-risk'"><RevenueAtRisk ref="rarRef" /></div>
    <div v-if="activeTab === 'reminders'"><PaymentReminders ref="remRef" /></div>
    <div v-if="activeTab === 'payment-allocation'"><PaymentAllocation ref="paRef" /></div>
    <div v-if="activeTab === 'clv-cohorts'"><CLVCohorts ref="clvRef" /></div>
    <div v-if="activeTab === 'expenses'"><Expenses :data="expenses" @refresh="fetchExpenses" /></div>
    <div v-if="activeTab === 'payroll'"><Payroll ref="payrollRef" /></div>
    <div v-if="activeTab === 'ap'"><AccountsPayable ref="apRef" /></div>
    <div v-if="activeTab === 'assets'"><AssetRegister ref="assetRef" /></div>
    <div v-if="activeTab === 'petty-cash'"><PettyCash ref="pcRef" /></div>
    <div v-if="activeTab === 'purchase-orders'"><PurchaseOrders ref="poRef" /></div>
    <div v-if="activeTab === 'loan-repayment'"><LoanRepayment ref="loanRef" /></div>
    <div v-if="activeTab === 'vat'"><VATDashboard ref="vatRef" /></div>
    <div v-if="activeTab === 'tax'"><TaxCalendar ref="taxRef" /></div>
    <div v-if="activeTab === 'credit-notes'"><CreditNotes ref="cnRef" /></div>
    <div v-if="activeTab === 'financial-year'"><FinancialYear ref="fyRef" /></div>
    <div v-if="activeTab === 'audit-trail'"><AuditTrail ref="auditRef" /></div>
    <div v-if="activeTab === 'dividends'"><DividendDistribution ref="dividendRef" /></div>
    <div v-if="activeTab === 'bank-import'"><BankImport ref="bankRef" /></div>
    <div v-if="activeTab === 'reconciliation'"><Reconciliation ref="reconRef" /></div>
    <div v-if="activeTab === 'branches'"><MultiBranch ref="branchRef" /></div>
    <div v-if="activeTab === 'insurance'"><InsuranceManagement ref="insuranceRef" /></div>
    <div v-if="activeTab === 'sla-credits'"><SLACredits ref="slaRef" /></div>
    <div v-if="activeTab === 'notifications'"><ExpenseNotifications ref="notifRef" /></div>
    <div v-if="activeTab === 'transactions'"><Transactions /></div>
    <div v-if="activeTab === 'refunds'"><Refunds /></div>
    <div v-if="activeTab === 'customer-intelligence'"><CustomerIntelligence /></div>

    <div v-if="activeTab === 'board-reports'"><BoardReports ref="boardRef" /></div>
    <div v-if="activeTab === 'pricing'"><PricingIntelligence /></div>
    <div v-if="activeTab === 'vendors'"><VendorIntelligence /></div>
    <div v-if="activeTab === 'investments'"><Investments ref="invRef" /></div>
    <div v-if="activeTab === 'departments'"><Departments :data="departments" @refresh="fetchDepartments" /></div>
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
import Transactions from '../views/Transactions.vue'
import Refunds from '../views/Refunds.vue'
import CustomerIntelligence from '../views/CustomerIntelligence.vue'
import PaymentAllocation from '../components/finance/PaymentAllocation.vue'
import SLACredits from '../components/finance/SLACredits.vue'
import LoanRepayment from '../components/finance/LoanRepayment.vue'
import MultiBranch from '../components/finance/MultiBranch.vue'
import InsuranceManagement from '../components/finance/InsuranceManagement.vue'
import DividendDistribution from '../components/finance/DividendDistribution.vue'
import CLVCohorts from '../components/finance/CLVCohorts.vue'

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
    ExpenseNotifications, FinancialYear, PettyCash, PurchaseOrders, AuditTrail,
    PaymentAllocation, SLACredits, LoanRepayment, MultiBranch, InsuranceManagement, DividendDistribution, CLVCohorts,
    Transactions, Refunds, CustomerIntelligence,
  },
  props: {
    activeTab: { type: String, default: 'analytics' }
  },
  setup() {
    const { makeRequest } = useApi()
    return { makeRequest }
  },
  computed: {
    activeTabLabel() {
      const allItems = [
        { id: 'analytics', name: 'Analytics' }, { id: 'kpi', name: 'KPI' }, { id: 'pl', name: 'P&L' }, { id: 'budget', name: 'Budget' },
        { id: 'invoices', name: 'Invoices' }, { id: 'revenue-streams', name: 'Revenue Streams' }, { id: 'recurring-billing', name: 'Recurring Billing' },
        { id: 'ar-collection', name: 'AR Collection' }, { id: 'revenue-at-risk', name: 'At Risk' }, { id: 'reminders', name: 'Reminders' },
        { id: 'payment-allocation', name: 'Allocations' }, { id: 'clv-cohorts', name: 'CLV Cohorts' },
        { id: 'expenses', name: 'Expenses' }, { id: 'payroll', name: 'Payroll' }, { id: 'ap', name: 'Payables' },
        { id: 'assets', name: 'Assets' }, { id: 'petty-cash', name: 'Petty Cash' }, { id: 'purchase-orders', name: 'Purchase Orders' }, { id: 'loan-repayment', name: 'Loan Schedule' },
        { id: 'vat', name: 'VAT' }, { id: 'tax', name: 'Tax Calendar' }, { id: 'credit-notes', name: 'Credit Notes' },
        { id: 'financial-year', name: 'Financial Year' }, { id: 'audit-trail', name: 'Audit Trail' }, { id: 'dividends', name: 'Dividends' },
        { id: 'bank-import', name: 'Bank Import' }, { id: 'reconciliation', name: 'Reconciliation' }, { id: 'branches', name: 'Branches' },
        { id: 'insurance', name: 'Insurance' }, { id: 'sla-credits', name: 'SLA Credits' }, { id: 'notifications', name: 'Notifications' },
        { id: 'transactions', name: 'Transactions' }, { id: 'refunds', name: 'Refunds' }, { id: 'customer-intelligence', name: 'Intelligence' },
        { id: 'board-reports', name: 'Board Reports' }, { id: 'pricing', name: 'Pricing' }, { id: 'vendors', name: 'Vendors' },
        { id: 'investments', name: 'Investments' }, { id: 'departments', name: 'Departments' },
      ]
      return allItems.find(i => i.id === this.activeTab)?.name || ''
    }
  },
  data() {
    return {
      loading: false,
      metrics: { mrr: 0, arr: 0, arpu: 0, ltv: 0, growth_rate: 0 },
      forecastData: { historical: [], forecast: [], avg_monthly_growth: 0, trend: 'upward' },
      packagePerformance: [],
      revenueStreams: [],
      expenses: [],
      departments: []
    }
  },
  computed: {
    activeTabLabel() {
      const allItems = [
        { id: 'analytics', name: 'Analytics' }, { id: 'kpi', name: 'KPI' }, { id: 'pl', name: 'P&L' }, { id: 'budget', name: 'Budget' },
        { id: 'invoices', name: 'Invoices' }, { id: 'revenue-streams', name: 'Revenue Streams' }, { id: 'recurring-billing', name: 'Recurring Billing' },
        { id: 'ar-collection', name: 'AR Collection' }, { id: 'revenue-at-risk', name: 'At Risk' }, { id: 'reminders', name: 'Reminders' },
        { id: 'payment-allocation', name: 'Allocations' }, { id: 'clv-cohorts', name: 'CLV Cohorts' },
        { id: 'expenses', name: 'Expenses' }, { id: 'payroll', name: 'Payroll' }, { id: 'ap', name: 'Payables' },
        { id: 'assets', name: 'Assets' }, { id: 'petty-cash', name: 'Petty Cash' }, { id: 'purchase-orders', name: 'Purchase Orders' }, { id: 'loan-repayment', name: 'Loan Schedule' },
        { id: 'vat', name: 'VAT' }, { id: 'tax', name: 'Tax Calendar' }, { id: 'credit-notes', name: 'Credit Notes' },
        { id: 'financial-year', name: 'Financial Year' }, { id: 'audit-trail', name: 'Audit Trail' }, { id: 'dividends', name: 'Dividends' },
        { id: 'bank-import', name: 'Bank Import' }, { id: 'reconciliation', name: 'Reconciliation' }, { id: 'branches', name: 'Branches' },
        { id: 'insurance', name: 'Insurance' }, { id: 'sla-credits', name: 'SLA Credits' }, { id: 'notifications', name: 'Notifications' },
        { id: 'transactions', name: 'Transactions' }, { id: 'refunds', name: 'Refunds' }, { id: 'customer-intelligence', name: 'Intelligence' },
        { id: 'board-reports', name: 'Board Reports' }, { id: 'pricing', name: 'Pricing' }, { id: 'vendors', name: 'Vendors' },
        { id: 'investments', name: 'Investments' }, { id: 'departments', name: 'Departments' },
      ]
      return allItems.find(i => i.id === this.activeTab)?.name || ''
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

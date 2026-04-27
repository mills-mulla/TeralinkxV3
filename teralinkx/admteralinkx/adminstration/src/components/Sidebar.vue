<template>
  <div>
    <!-- Mobile overlay -->
    <div v-if="isMobileOpen && isMobile" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden" @click="$emit('close-mobile')"></div>

    <!-- Floating sidebar -->
    <aside
      class="fixed top-3 bottom-3 left-3 flex flex-col rounded-2xl shadow-2xl border border-slate-200/80 dark:border-slate-700/50 overflow-hidden transition-all duration-300 ease-in-out"
      :class="[
        isCollapsed ? 'w-[60px]' : 'w-[220px]',
        isMobileOpen || !isMobile ? 'translate-x-0' : '-translate-x-[calc(100%+12px)]',
        'lg:translate-x-0'
      ]"
      style="z-index:50;"
      :style="{ background: isDark ? 'rgba(15,23,42,0.95)' : 'rgba(255,255,255,0.95)', backdropFilter: 'blur(20px)', borderColor: isDark ? 'rgba(51,65,85,0.5)' : 'rgba(226,232,240,0.8)' }"
    >
      <!-- Logo -->
      <div class="flex items-center gap-2.5 px-3 py-3.5 border-b border-slate-200/80 dark:border-slate-700/50 shrink-0">
        <img src="/src/assets/logo/teralinkx2.png" class="w-8 h-8 rounded-lg shrink-0 object-contain" />
        <transition name="label">
          <div v-if="!isCollapsed" class="overflow-hidden">
            <p class="text-white font-bold text-sm leading-none">TeralinkX</p>
            <p class="text-slate-400 text-[10px] mt-0.5">Admin Console</p>
          </div>
        </transition>
      </div>

      <!-- Live stats pills -->
      <transition name="label">
        <div v-if="!isCollapsed" class="px-3 py-2 border-b border-slate-200/80 dark:border-slate-700/50 grid grid-cols-2 gap-1.5 shrink-0">
          <div class="bg-blue-500/10 border border-blue-500/20 rounded-lg px-2 py-1.5 text-center">
            <p class="text-[10px] text-blue-400">Users</p>
            <p class="text-sm font-bold text-blue-300">{{ stats.activeUsers }}</p>
          </div>
          <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-2 py-1.5 text-center">
            <p class="text-[10px] text-emerald-400">Sessions</p>
            <p class="text-sm font-bold text-emerald-300">{{ stats.activeSessions }}</p>
          </div>
        </div>
      </transition>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto py-2 px-2 space-y-0.5 sidebar-scroll">

        <template v-for="section in navSections" :key="section.label">
          <template v-if="section.items.length">
          <!-- Section label -->
          <transition name="label">
            <p v-if="!isCollapsed" class="text-[9px] font-semibold text-slate-500 uppercase tracking-widest px-2 pt-3 pb-1">{{ section.label }}</p>
          </transition>
          <div v-if="isCollapsed" class="border-t border-slate-700/40 my-1.5"></div>

          <!-- Nav items -->
          <button
            v-for="item in section.items"
            :key="item.id"
            @click="handleNav(item)"
            class="nav-btn w-full flex items-center gap-2.5 rounded-xl text-left transition-all duration-200 relative"
            :class="[
              isCollapsed ? 'px-0 py-2 justify-center' : 'px-2 py-2',
              activeComponent === item.component
                ? 'nav-active'
                : 'nav-inactive'
            ]"
            :style="activeComponent === item.component ? `background: ${item.color}18` : ''"
            :title="isCollapsed ? item.name : ''"
          >
            <!-- No absolute glow span needed -->

            <!-- Icon pill - always same bg, never changes -->
            <span
              class="relative shrink-0 w-7 h-7 rounded-lg flex items-center justify-center"
              :style="`background: ${item.color}20`"
            >
              <span v-html="item.icon" :style="`color: ${item.color}`" class="w-4 h-4 block [&>svg]:w-4 [&>svg]:h-4"></span>
            </span>

            <!-- Label + badge -->
            <transition name="label">
              <span v-if="!isCollapsed" class="flex-1 flex items-center justify-between overflow-hidden">
                <span
                  class="text-xs font-medium truncate transition-colors duration-200"
                  :class="activeComponent === item.component ? 'text-white' : 'text-slate-600 dark:text-slate-400'"
                >{{ item.name }}</span>
                <span
                  v-if="getBadgeCount(item.component)"
                  class="text-[9px] font-bold px-1.5 py-0.5 rounded-full ml-1 shrink-0"
                  :style="`background: ${item.color}30; color: ${item.color}`"
                >{{ getBadgeCount(item.component) }}</span>
              </span>
            </transition>

            <!-- Active left bar -->
            <span
              v-if="activeComponent === item.component"
              class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full transition-all duration-300"
              :style="`background: ${item.color}`"
            ></span>
          </button>

          <!-- Finance sub-accordion -->
          <transition name="accordion">
            <div v-if="item.hasAccordion && activeComponent === item.component && !isCollapsed" class="mt-0.5 space-y-0.5">
              <template v-for="group in financeGroups" :key="group.id">
                <button @click="toggleFinanceGroup(group.id)"
                  class="w-full flex items-center gap-1.5 pl-4 pr-2 py-1.5 text-[10px] font-semibold rounded-lg transition-colors"
                  :class="activeFinanceGroup === group.id ? 'text-violet-300 bg-violet-500/10' : 'text-slate-500 hover:text-slate-300 hover:bg-slate-700/30'">
                  <span>{{ group.icon }}</span>
                  <span class="flex-1 text-left">{{ group.label }}</span>
                  <svg class="w-2.5 h-2.5 transition-transform" :class="activeFinanceGroup === group.id ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                </button>
                <transition name="accordion">
                  <div v-if="activeFinanceGroup === group.id" class="space-y-0.5 pl-2">
                    <button v-for="fi in group.items" :key="fi.id" @click="selectFinanceTab(fi.id)"
                      class="w-full text-left pl-6 pr-2 py-1 text-[10px] rounded-lg transition-all duration-150"
                      :class="activeFinanceTab === fi.id ? 'bg-violet-500/20 text-violet-300 font-medium' : 'text-slate-500 hover:text-slate-300 hover:bg-slate-700/20'">
                      {{ fi.name }}
                    </button>
                  </div>
                </transition>
              </template>
            </div>
          </transition>
          </template>
        </template>

        <!-- Finance standalone section -->
        <div class="border-t border-slate-700/40 my-1.5"></div>
        <transition name="label">
          <p v-if="!isCollapsed" class="text-[9px] font-semibold text-slate-500 uppercase tracking-widest px-2 pt-2 pb-1">Finance</p>
        </transition>

        <!-- Finance top-level button -->
        <button @click="handleNav({component:'Finance'})" :title="isCollapsed ? 'Finance' : ''"
          class="nav-btn w-full flex items-center gap-2.5 rounded-xl text-left transition-all duration-200 relative"
          :class="[isCollapsed ? 'px-0 py-2 justify-center' : 'px-2 py-2', activeComponent === 'Finance' ? 'nav-active' : 'nav-inactive']"
          :style="activeComponent === 'Finance' ? 'background: #8b5cf620' : ''">
          <span class="relative shrink-0 w-7 h-7 rounded-lg flex items-center justify-center" style="background:#8b5cf620">
            <svg class="w-4 h-4" fill="currentColor" style="color:#8b5cf6" viewBox="0 0 24 24"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>
          </span>
          <transition name="label">
            <span v-if="!isCollapsed" class="text-xs font-medium truncate" :class="activeComponent === 'Finance' ? 'text-white' : 'text-slate-600 dark:text-slate-400'">Finance</span>
          </transition>
          <span v-if="activeComponent === 'Finance'" class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full" style="background:#8b5cf6"></span>
        </button>

        <!-- Finance accordion — exact original style -->
        <template v-if="activeComponent === 'Finance' && !isCollapsed">
          <div v-for="group in financeGroups" :key="group.id">
            <button @click="toggleFinanceGroup(group.id)"
              class="w-full flex items-center gap-2 pl-5 pr-3 py-1.5 text-xs font-semibold transition-colors"
              :class="activeFinanceGroup === group.id ? 'text-violet-400' : 'text-slate-500 hover:text-slate-300'">
              <span>{{ group.icon }}</span>
              <span class="flex-1 text-left">{{ group.label }}</span>
              <svg class="w-3 h-3 transition-transform" :class="activeFinanceGroup === group.id ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-if="activeFinanceGroup === group.id">
              <button v-for="fi in group.items" :key="fi.id" @click="selectFinanceTab(fi.id)"
                class="w-full text-left pl-9 pr-3 py-1.5 text-xs transition-colors border-l-2"
                :class="activeFinanceTab === fi.id
                  ? 'border-violet-500 text-violet-400 bg-violet-500/10 font-medium'
                  : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-700/30'">
                {{ fi.name }}
              </button>
            </div>
          </div>
        </template>

      </nav>

      <!-- Footer -->
      <div class="shrink-0 border-t border-slate-200/80 dark:border-slate-700/50 px-2 py-2 space-y-1">
        <!-- Theme + collapse row -->
        <div class="flex items-center" :class="isCollapsed ? 'justify-center gap-0 flex-col gap-1' : 'justify-between px-1'">
          <button @click="toggleTheme" class="w-7 h-7 rounded-lg bg-slate-200 dark:bg-slate-700/50 hover:bg-slate-300 dark:hover:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <svg v-if="isDark" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m8.66-12.66l-.71.71M4.05 19.95l-.7-.71M21 12h-1M4 12H3m16.95 7.05l-.7-.71M4.05 4.05l.7.71M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
            <svg v-else class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a8 8 0 106.32 12.906 7.5 7.5 0 01-6.32-12.905z"/></svg>
          </button>
          <button @click="toggleSidebar" class="hidden lg:flex w-7 h-7 rounded-lg bg-slate-200 dark:bg-slate-700/50 hover:bg-slate-300 dark:hover:bg-slate-700 items-center justify-center text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <svg class="w-3.5 h-3.5 transition-transform duration-300" :class="isCollapsed ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7M19 19l-7-7 7-7"/></svg>
          </button>
        </div>
        <!-- Online status -->
        <transition name="label">
          <div v-if="!isCollapsed" class="flex items-center justify-between px-1">
            <div class="flex items-center gap-1.5">
              <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
              <span class="text-[10px] text-slate-500">Online</span>
            </div>
            <span class="text-[10px] text-slate-600 font-mono">v3.1</span>
          </div>
        </transition>
      </div>
    </aside>
  </div>
</template>

<script>
import { useTheme } from '../composables/useTheme'

export default {
  name: 'Sidebar',
  props: {
    stats: { type: Object, default: () => ({ activeUsers: 0, activeSessions: 0, activeDevices: 0, pendingRefunds: 0 }) },
    isMobileOpen: { type: Boolean, default: false },
    activeComponent: { type: String, default: 'Dashboard' }
  },
  emits: ['component-selected', 'finance-tab-selected', 'refresh-data', 'close-mobile', 'sidebar-toggle'],
  setup() {
    const { isDark, isAuto, toggleTheme, setAutoTheme } = useTheme()
    return { isDark, isAuto, toggleTheme, setAutoTheme }
  },
  data() {
    return {
      isMobile: false,
      isCollapsed: false,
      activeFinanceGroup: 'overview',
      activeFinanceTab: 'analytics',
      financeGroups: [
        { id: 'overview',    icon: '📊', label: 'Overview',    items: [{ id: 'analytics', name: 'Analytics' }, { id: 'kpi', name: 'KPI' }, { id: 'pl', name: 'P&L' }, { id: 'budget', name: 'Budget' }] },
        { id: 'revenue',     icon: '💰', label: 'Revenue',     items: [{ id: 'invoices', name: 'Invoices' }, { id: 'revenue-streams', name: 'Revenue Streams' }, { id: 'recurring-billing', name: 'Recurring Billing' }, { id: 'ar-collection', name: 'AR Collection' }, { id: 'revenue-at-risk', name: 'At Risk' }, { id: 'reminders', name: 'Reminders' }, { id: 'payment-allocation', name: 'Allocations' }, { id: 'clv-cohorts', name: 'CLV Cohorts' }] },
        { id: 'costs',       icon: '💸', label: 'Costs',       items: [{ id: 'expenses', name: 'Expenses' }, { id: 'payroll', name: 'Payroll' }, { id: 'ap', name: 'Payables' }, { id: 'assets', name: 'Assets' }, { id: 'petty-cash', name: 'Petty Cash' }, { id: 'purchase-orders', name: 'Purchase Orders' }, { id: 'loan-repayment', name: 'Loan Schedule' }] },
        { id: 'compliance',  icon: '📋', label: 'Compliance',  items: [{ id: 'vat', name: 'VAT' }, { id: 'tax', name: 'Tax Calendar' }, { id: 'credit-notes', name: 'Credit Notes' }, { id: 'financial-year', name: 'Financial Year' }, { id: 'audit-trail', name: 'Audit Trail' }, { id: 'dividends', name: 'Dividends' }] },
        { id: 'operations',  icon: '🏗️', label: 'Operations',  items: [{ id: 'bank-import', name: 'Bank Import' }, { id: 'reconciliation', name: 'Reconciliation' }, { id: 'branches', name: 'Branches' }, { id: 'insurance', name: 'Insurance' }, { id: 'sla-credits', name: 'SLA Credits' }, { id: 'notifications', name: 'Notifications' }] },
        { id: 'customer',    icon: '👥', label: 'Customer',    items: [{ id: 'transactions', name: 'Transactions' }, { id: 'refunds', name: 'Refunds' }, { id: 'customer-intelligence', name: 'Intelligence' }, { id: 'churn', name: 'Churn' }] },
        { id: 'reports',     icon: '📑', label: 'Reports',     items: [{ id: 'board-reports', name: 'Board Reports' }, { id: 'pricing', name: 'Pricing' }, { id: 'vendors', name: 'Vendors' }, { id: 'investments', name: 'Investments' }, { id: 'departments', name: 'Departments' }] },
      ],
      navSections: [
        {
          label: 'Overview',
          items: [
            { id: 1, name: 'Dashboard', component: 'Dashboard', color: '#3b82f6', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>' },
          ]
        },
        {
          label: 'Management',
          items: [
            { id: 2, name: 'Clients',   component: 'Clients',   color: '#10b981', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>' },
            { id: 3, name: 'Users',     component: 'Users',     color: '#a855f7', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>' },
            { id: 4, name: 'Devices',   component: 'Devices',   color: '#06b6d4', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>' },
            { id: 5, name: 'Sessions',  component: 'Sessions',  color: '#f97316', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>' },
          ]
        },
        {
          label: 'Products',
          items: [
            { id: 6,  name: 'Packages',    component: 'Packages',    color: '#6366f1', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4z"/></svg>' },
            { id: 7,  name: 'Vouchers',    component: 'Vouchers',    color: '#ec4899', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42z"/></svg>' },
            { id: 8,  name: 'Coupons',     component: 'Coupons',     color: '#f43f5e', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>' },
            { id: 9,  name: 'Promotions',  component: 'Promotions',  color: '#f59e0b', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>' },
            { id: 14, name: 'Points',       component: 'PointTransactions', color: '#eab308', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>' },
          ]
        },
        {
          label: 'Finance',
          items: []
        },
        {
          label: 'Network',
          items: [
            { id: 13, name: 'Locations', component: 'Locations', color: '#22c55e', icon: '<svg fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>' },
          ]
        },
      ]
    }
  },
  methods: {
    handleNav(item) {
      this.$emit('component-selected', item.component)
      if (this.isMobile) this.$emit('close-mobile')
    },
    toggleFinanceGroup(id) {
      this.activeFinanceGroup = this.activeFinanceGroup === id ? null : id
    },
    selectFinanceTab(tabId) {
      this.activeFinanceTab = tabId
      const group = this.financeGroups.find(g => g.items.some(i => i.id === tabId))
      if (group) this.activeFinanceGroup = group.id
      this.$emit('finance-tab-selected', tabId)
      if (this.isMobile) this.$emit('close-mobile')
    },
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed
      this.$emit('sidebar-toggle', this.isCollapsed)
    },
    getBadgeCount(component) {
      return { Users: this.stats.activeUsers, Sessions: this.stats.activeSessions, Devices: this.stats.activeDevices, Refunds: this.stats.pendingRefunds }[component] || 0
    },
    checkMobile() { this.isMobile = window.innerWidth < 1024 }
  },
  mounted() {
    this.checkMobile()
    window.addEventListener('resize', this.checkMobile)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkMobile)
  }
}
</script>

<style scoped>
.sidebar-scroll::-webkit-scrollbar { width: 2px; }
.sidebar-scroll::-webkit-scrollbar-track { background: transparent; }
.sidebar-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }

/* Label slide transition */
.label-enter-active { transition: all 0.2s ease; }
.label-leave-active { transition: all 0.15s ease; }
.label-enter-from, .label-leave-to { opacity: 0; transform: translateX(-6px); }

/* Accordion transition */
.accordion-enter-active { transition: all 0.25s ease; max-height: 500px; }
.accordion-leave-active { transition: all 0.2s ease; }
.accordion-enter-from, .accordion-leave-to { opacity: 0; max-height: 0; transform: translateY(-4px); }

/* Nav button states */
.nav-btn { min-height: 36px; }
.nav-inactive { color: #64748b; }
.nav-inactive:hover { background: rgba(0,0,0,0.05); color: #1e293b; }
:global(.dark) .nav-inactive { color: #94a3b8; }
:global(.dark) .nav-inactive:hover { background: rgba(255,255,255,0.05); color: #e2e8f0; }
.nav-active { color: #1e293b; }
:global(.dark) .nav-active { color: white; }

/* Icon pill glow pulse on active */
.nav-active .icon-pill { animation: iconPulse 2s ease-in-out infinite; }
@keyframes iconPulse {
  0%, 100% { box-shadow: 0 0 8px currentColor; }
  50% { box-shadow: 0 0 16px currentColor; }
}
</style>

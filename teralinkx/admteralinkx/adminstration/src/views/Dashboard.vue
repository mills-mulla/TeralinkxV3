<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Dashboard</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Welcome back, here's your overview</p>
      </div>
      <div class="flex items-center gap-2">
        <!-- Quick Links -->
        <div class="relative">
          <button @click="showQuickLinks = !showQuickLinks" class="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg transition-colors">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            Quick Links
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div v-if="showQuickLinks" class="absolute right-0 top-full mt-1 w-52 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 z-50 py-1">
            <router-link to="/transactions" @click="showQuickLinks=false" class="flex items-center gap-2.5 px-3 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <span class="w-5 h-5 rounded-md bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center text-amber-600 dark:text-amber-400 text-[10px]">⏳</span>
              Pending Transactions
              <span class="ml-auto text-[10px] font-bold text-amber-600 dark:text-amber-400">{{ kpi.pending_transactions || 0 }}</span>
            </router-link>
            <router-link to="/transactions" @click="showQuickLinks=false" class="flex items-center gap-2.5 px-3 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <span class="w-5 h-5 rounded-md bg-rose-100 dark:bg-rose-500/20 flex items-center justify-center text-rose-600 dark:text-rose-400 text-[10px]">❌</span>
              Failed (24h)
              <span class="ml-auto text-[10px] font-bold text-rose-600 dark:text-rose-400">{{ kpi.failed_transactions_24h || 0 }}</span>
            </router-link>
            <router-link to="/vouchers" @click="showQuickLinks=false" class="flex items-center gap-2.5 px-3 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <span class="w-5 h-5 rounded-md bg-orange-100 dark:bg-orange-500/20 flex items-center justify-center text-orange-600 dark:text-orange-400 text-[10px]">⚠️</span>
              Expiring Vouchers
            </router-link>
            <router-link to="/clients" @click="showQuickLinks=false" class="flex items-center gap-2.5 px-3 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <span class="w-5 h-5 rounded-md bg-red-100 dark:bg-red-500/20 flex items-center justify-center text-red-600 dark:text-red-400 text-[10px]">🔴</span>
              At-Risk Clients
            </router-link>
          </div>
        </div>
        <button 
          @click="refreshData" 
          class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
          :class="{ 'animate-spin': loading }"
        >
          <svg class="w-5 h-5 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- System Health - Always visible at top -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div :class="systemOverallStatus === 'healthy' ? 'bg-emerald-500' : systemOverallStatus === 'warning' ? 'bg-amber-500' : 'bg-rose-500'" class="w-2 h-2 rounded-full"></div>
          <span class="text-xs font-semibold text-slate-900 dark:text-white">System Health</span>
        </div>
        <div class="flex items-center gap-4">
          <div v-for="stat in systemStats" :key="stat.name" class="flex items-center gap-1.5">
            <div :class="stat.statusColor" class="w-1.5 h-1.5 rounded-full"></div>
            <span class="text-[10px] text-slate-500 dark:text-slate-400">{{ stat.name }}</span>
            <span class="text-[10px] font-medium text-slate-900 dark:text-white">{{ stat.value }}</span>
          </div>
          <select v-model="systemStatusInterval" @change="updateSystemStatusInterval" class="text-[10px] bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded px-1.5 py-0.5 text-slate-900 dark:text-white">
            <option value="5000">5s</option>
            <option value="10000">10s</option>
            <option value="20000">20s</option>
            <option value="30000">30s</option>
            <option value="40000">40s</option>
            <option value="50000">50s</option>
            <option value="60000">1m</option>
            <option value="300000">5m</option>
            <option value="600000">10m</option>
            <option value="1800000">30m</option>
            <option value="3600000">1h</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Real-Time Monitor -->
    <RealTimeMonitor />

    <!-- KPI Banner -->
    <div class="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-xs">
      <router-link to="/finance" class="flex items-center gap-1 text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
        <span class="text-slate-400">MRR</span>
        <span class="font-semibold text-slate-900 dark:text-white" :class="hideKpi ? 'blur-sm select-none' : ''">KSh {{ formatNumber(kpi.mrr || 0) }}</span>
        <button @click.prevent="hideKpi = !hideKpi" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
          <svg v-if="hideKpi" class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
          <svg v-else class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/></svg>
        </button>
      </router-link>
      <span class="text-slate-300 dark:text-slate-600">|</span>
      <router-link to="/finance" class="flex items-center gap-1 hover:text-blue-600 dark:hover:text-blue-400">
        <span class="text-slate-400">Churn</span>
        <span class="font-semibold" :class="[hideKpi ? 'blur-sm select-none' : '', (kpi.churn_rate || 0) > 5 ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400']">{{ kpi.churn_rate || 0 }}%</span>
      </router-link>
      <span class="text-slate-300 dark:text-slate-600">|</span>
      <router-link to="/finance" class="flex items-center gap-1 hover:text-blue-600 dark:hover:text-blue-400">
        <span class="text-slate-400">Cash</span>
        <span class="font-semibold text-slate-900 dark:text-white" :class="hideKpi ? 'blur-sm select-none' : ''">KSh {{ formatNumber(kpi.cash_position || 0) }}</span>
      </router-link>
      <span class="text-slate-300 dark:text-slate-600">|</span>
      <router-link to="/transactions" class="flex items-center gap-1 hover:text-amber-600 dark:hover:text-amber-400">
        <span class="text-slate-400">Pending</span>
        <span class="font-semibold" :class="(kpi.pending_transactions || 0) > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-900 dark:text-white'">{{ kpi.pending_transactions || 0 }}</span>
      </router-link>
      <span class="text-slate-300 dark:text-slate-600">|</span>
      <router-link to="/transactions" class="flex items-center gap-1 hover:text-rose-600 dark:hover:text-rose-400">
        <span class="text-slate-400">Failed (24h)</span>
        <span class="font-semibold" :class="(kpi.failed_transactions_24h || 0) > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-white'">{{ kpi.failed_transactions_24h || 0 }}</span>
      </router-link>
    </div>

    <!-- Section: Performance Metrics -->
    <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
      <button @click="showMetrics = !showMetrics" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
        <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Performance Metrics</span>
        <svg class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200" :class="showMetrics ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
      </button>
      <div v-show="showMetrics" class="p-4 space-y-4 bg-white dark:bg-slate-900">
    <!-- Metric Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 animate-slide-up">

      <!-- Total Clients -->
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-4 text-white shadow-lg shadow-blue-500/20">
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
          </div>
          <span v-if="metrics.clientsTrend" class="flex items-center gap-0.5 text-[10px] font-medium px-1.5 py-0.5 rounded-full" :class="metrics.clientsTrend==='up' ? 'bg-white/20' : 'bg-white/10'">
            <span>{{ metrics.clientsTrend==='up' ? '▲' : metrics.clientsTrend==='down' ? '▼' : '—' }}</span>
            <span>{{ metrics.clientsTrendValue || '' }}</span>
          </span>
        </div>
        <p class="text-2xl font-bold">{{ metrics.totalClients || 0 }}</p>
        <p class="text-blue-100 text-xs mt-0.5">Total Clients</p>
      </div>

      <!-- New (7d) -->
      <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-4 text-white shadow-lg shadow-emerald-500/20">
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          </div>
          <span v-if="metrics.newClientsTrend" class="flex items-center gap-0.5 text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-white/20">
            <span>{{ metrics.newClientsTrend==='up' ? '▲' : metrics.newClientsTrend==='down' ? '▼' : '—' }}</span>
            <span>{{ metrics.newClientsTrendValue || '' }}</span>
          </span>
        </div>
        <p class="text-2xl font-bold">{{ metrics.newClients7d || 0 }}</p>
        <p class="text-emerald-100 text-xs mt-0.5">New This Week</p>
      </div>

      <!-- Active Vouchers -->
      <div class="bg-gradient-to-br from-violet-500 to-violet-600 rounded-xl p-4 text-white shadow-lg shadow-violet-500/20">
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42z"/></svg>
          </div>
          <div class="w-2 h-2 bg-white/60 rounded-full animate-pulse"></div>
        </div>
        <p class="text-2xl font-bold">{{ metrics.activeVouchers || 0 }}</p>
        <p class="text-violet-100 text-xs mt-0.5">Active Vouchers</p>
      </div>

      <!-- Active Sessions -->
      <div class="bg-gradient-to-br from-amber-500 to-orange-500 rounded-xl p-4 text-white shadow-lg shadow-amber-500/20">
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <div class="w-2 h-2 bg-white/60 rounded-full animate-pulse"></div>
        </div>
        <p class="text-2xl font-bold">{{ metrics.activeSessions || 0 }}</p>
        <p class="text-amber-100 text-xs mt-0.5">Active Sessions</p>
      </div>

    </div>

    <!-- Charts Row 1 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.1s">
      <!-- Revenue Chart -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center justify-between">
          <div>
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-lg bg-emerald-100 dark:bg-emerald-500/20 flex items-center justify-center">
                <svg class="w-4 h-4 text-emerald-600 dark:text-emerald-400" fill="currentColor" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>
              </div>
              <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Revenue Analytics</h3>
            </div>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 ml-9">KSh earned over time</p>
          </div>
          <select v-model="revenuePeriod" @change="fetchRevenueAnalytics" class="text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1.5 text-slate-700 dark:text-slate-300">
            <option value="7d">7 days</option><option value="14d">14 days</option><option value="30d">30 days</option><option value="90d">90 days</option><option value="6m">6 months</option><option value="1y">1 year</option>
          </select>
        </div>
        <div v-if="revenueData.length > 0" class="h-64 px-2 pb-2">
          <apexchart type="area" height="100%" :options="revenueChartOptions" :series="revenueChartSeries" />
        </div>
        <div v-else class="h-64 flex items-center justify-center">
          <div class="text-center"><div class="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div><p class="text-xs text-slate-400">Loading...</p></div>
        </div>
      </div>

      <!-- Growth Chart -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center justify-between">
          <div>
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-lg bg-purple-100 dark:bg-purple-500/20 flex items-center justify-center">
                <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>
              </div>
              <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Client Growth</h3>
            </div>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 ml-9">New clients over time</p>
          </div>
          <select v-model="growthPeriod" @change="fetchClientGrowth" class="text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1.5 text-slate-700 dark:text-slate-300">
            <option value="7d">7 days</option><option value="14d">14 days</option><option value="30d">30 days</option><option value="90d">90 days</option><option value="6m">6 months</option><option value="1y">1 year</option>
          </select>
        </div>
        <div v-if="clientGrowthData.length > 0" class="h-64 px-2 pb-2">
          <apexchart type="bar" height="100%" :options="growthChartOptions" :series="growthChartSeries" />
        </div>
        <div v-else class="h-64 flex items-center justify-center">
          <div class="text-center"><div class="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div><p class="text-xs text-slate-400">Loading...</p></div>
        </div>
      </div>
    </div>

    <!-- Charts Row 2: Package Sales -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.15s">
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24"><path d="M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Package Sales</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">Distribution by package type</p>
          </div>
        </div>
        <div v-if="packageSales.length > 0" class="h-80 px-2 pb-3">
          <apexchart type="pie" height="100%" :options="packageChartOptions" :series="packageChartSeries" />
        </div>
        <div v-else class="h-64 flex items-center justify-center">
          <div class="text-center"><div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div><p class="text-xs text-slate-400">Loading...</p></div>
        </div>
      </div>

      <!-- Voucher Status -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-orange-100 dark:bg-orange-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-orange-600 dark:text-orange-400" fill="currentColor" viewBox="0 0 24 24"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Voucher Status</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">Current voucher breakdown</p>
          </div>
        </div>
        <div class="px-5 pb-5 space-y-3">
          <div class="grid grid-cols-3 gap-3">
            <div class="bg-emerald-50 dark:bg-emerald-500/10 rounded-xl p-4 text-center border border-emerald-100 dark:border-emerald-500/20">
              <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{{ voucherStatus.active || 0 }}</p>
              <p class="text-[10px] text-emerald-600 dark:text-emerald-400 mt-1 font-medium">Active</p>
            </div>
            <div class="bg-amber-50 dark:bg-amber-500/10 rounded-xl p-4 text-center border border-amber-100 dark:border-amber-500/20">
              <p class="text-2xl font-bold text-amber-600 dark:text-amber-400">{{ voucherStatus.pending || 0 }}</p>
              <p class="text-[10px] text-amber-600 dark:text-amber-400 mt-1 font-medium">Pending</p>
            </div>
            <div class="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-4 text-center border border-slate-200 dark:border-slate-600">
              <p class="text-2xl font-bold text-slate-600 dark:text-slate-400">{{ voucherStatus.expired || 0 }}</p>
              <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-1 font-medium">Expired</p>
            </div>
          </div>
          <!-- Usage bar -->
          <div class="pt-2">
            <div class="flex justify-between text-xs mb-1.5">
              <span class="text-slate-500 dark:text-slate-400">Total Vouchers</span>
              <span class="font-bold text-slate-900 dark:text-white">{{ voucherStatus.total || 0 }}</span>
            </div>
            <div class="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden flex">
              <div class="h-full bg-emerald-500 transition-all" :style="`width:${voucherStatus.total ? (voucherStatus.active/voucherStatus.total*100) : 0}%`"></div>
              <div class="h-full bg-amber-400 transition-all" :style="`width:${voucherStatus.total ? (voucherStatus.pending/voucherStatus.total*100) : 0}%`"></div>
              <div class="h-full bg-slate-300 dark:bg-slate-600 transition-all" :style="`width:${voucherStatus.total ? (voucherStatus.expired/voucherStatus.total*100) : 0}%`"></div>
            </div>
            <div class="flex gap-3 mt-2">
              <span class="flex items-center gap-1 text-[10px] text-slate-500"><span class="w-2 h-2 rounded-full bg-emerald-500"></span>Active</span>
              <span class="flex items-center gap-1 text-[10px] text-slate-500"><span class="w-2 h-2 rounded-full bg-amber-400"></span>Pending</span>
              <span class="flex items-center gap-1 text-[10px] text-slate-500"><span class="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600"></span>Expired</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Conversion Funnel -->
    <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-indigo-100 dark:bg-indigo-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 24 24"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Conversion Funnel</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">Signup to active client journey</p>
          </div>
        </div>
        <div class="px-5 pb-5 space-y-3">
          <div v-for="(step, i) in [
            { label: 'Signups', value: conversionFunnel.signups, color: 'bg-blue-500', pct: 100 },
            { label: 'Purchased', value: conversionFunnel.purchased, color: 'bg-purple-500', pct: conversionFunnel.signups ? Math.round(conversionFunnel.purchased/conversionFunnel.signups*100) : 0 },
            { label: 'Active', value: conversionFunnel.active, color: 'bg-emerald-500', pct: conversionFunnel.signups ? Math.round(conversionFunnel.active/conversionFunnel.signups*100) : 0 },
          ]" :key="step.label" class="space-y-1">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :class="step.color"></span>
                <span class="text-xs text-slate-600 dark:text-slate-400">{{ step.label }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-slate-900 dark:text-white">{{ step.value || 0 }}</span>
                <span class="text-[10px] text-slate-400 w-8 text-right">{{ step.pct }}%</span>
              </div>
            </div>
            <div class="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500" :class="step.color" :style="`width:${step.pct}%`"></div>
            </div>
          </div>
          <div class="pt-3 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between">
            <span class="text-xs text-slate-500 dark:text-slate-400">Conversion Rate</span>
            <span class="text-sm font-bold text-emerald-600 dark:text-emerald-400">{{ conversionFunnel.conversion_rate || 0 }}%</span>
          </div>
        </div>
    </div>

    <!-- Location Performance & Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.25s">
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-rose-100 dark:bg-rose-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Top Locations</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">By revenue this period</p>
          </div>
        </div>
        <div class="px-4 pb-4 space-y-2">
          <div v-for="(loc, idx) in locationPerformance" :key="idx" class="flex items-center gap-3 p-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
            <span class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0"
              :class="idx===0?'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400':idx===1?'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300':idx===2?'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400':'bg-slate-50 text-slate-400 dark:bg-slate-800 dark:text-slate-500'">
              {{ idx+1 }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-slate-900 dark:text-white">{{ loc.location__name || 'Unknown' }}</p>
              <div class="flex items-center gap-2 mt-0.5">
                <div class="flex-1 bg-slate-100 dark:bg-slate-700 rounded-full h-1">
                  <div class="h-1 rounded-full bg-rose-400" :style="{width: locationPerformance[0]?.revenue ? (loc.revenue/locationPerformance[0].revenue*100)+'%' : '0%'}"></div>
                </div>
                <span class="text-[10px] text-slate-500 shrink-0">{{ loc.sales }} sales</span>
              </div>
            </div>
            <p class="text-xs font-bold text-slate-900 dark:text-white shrink-0">KSh {{ formatNumber(loc.revenue||0) }}</p>
          </div>
          <div v-if="!locationPerformance.length" class="text-center py-4 text-xs text-slate-400">No data</div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-amber-600 dark:text-amber-400" fill="currentColor" viewBox="0 0 24 24"><path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Recent Activity</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">Latest events across the platform</p>
          </div>
        </div>
        <div class="px-4 pb-4 space-y-1 max-h-72 overflow-y-auto">
          <div v-for="activity in recentActivity" :key="activity.time"
            class="flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
            <div class="w-7 h-7 rounded-lg shrink-0 flex items-center justify-center"
              :class="activity.type==='payment' ? 'bg-emerald-100 dark:bg-emerald-500/20' : activity.type==='session' ? 'bg-blue-100 dark:bg-blue-500/20' : 'bg-purple-100 dark:bg-purple-500/20'">
              <svg v-if="activity.type==='payment'" class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" fill="currentColor" viewBox="0 0 24 24"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>
              <svg v-else class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium text-slate-900 dark:text-white truncate">{{ activity.description }}</p>
              <p class="text-[10px] text-slate-400 mt-0.5 truncate">{{ activity.user }} · {{ formatTime(activity.time) }}</p>
            </div>
            <span class="text-[10px] px-1.5 py-0.5 rounded-full shrink-0"
              :class="activity.type==='payment' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400'">
              {{ activity.type }}
            </span>
          </div>
          <div v-if="!recentActivity.length" class="text-center py-4 text-xs text-slate-400">No recent activity</div>
        </div>
      </div>
    </div>

    <!-- Additional Metrics Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.3s">
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-teal-100 dark:bg-teal-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-teal-600 dark:text-teal-400" fill="currentColor" viewBox="0 0 24 24"><path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Device Breakdown</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">Connected device types</p>
          </div>
        </div>
        <div v-if="deviceBreakdown.length > 0" class="px-4 pb-4 space-y-2">
          <div v-for="device in deviceBreakdown" :key="device.device_type" class="flex items-center gap-3">
            <span class="text-xs text-slate-600 dark:text-slate-400 w-20 shrink-0 capitalize">{{ device.device_type || 'Unknown' }}</span>
            <div class="flex-1 bg-slate-100 dark:bg-slate-700 rounded-full h-2">
              <div class="h-2 rounded-full bg-teal-500 transition-all"
                :style="{width: deviceBreakdown[0]?.count ? (device.count/deviceBreakdown[0].count*100)+'%' : '0%'}"></div>
            </div>
            <span class="text-xs font-bold text-slate-900 dark:text-white w-8 text-right">{{ device.count }}</span>
          </div>
        </div>
        <div v-else class="px-4 pb-4 text-center py-6 text-xs text-slate-400">No device data</div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="px-5 pt-5 pb-3 flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-yellow-100 dark:bg-yellow-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-yellow-600 dark:text-yellow-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Reward Tiers</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">Client distribution by tier</p>
          </div>
        </div>
        <div v-if="rewardTiers.length > 0" class="px-4 pb-4 space-y-2">
          <div v-for="tier in rewardTiers" :key="tier.reward_tier" class="flex items-center gap-3">
            <span class="text-[10px] font-medium px-2 py-0.5 rounded-full shrink-0 capitalize"
              :class="tier.reward_tier==='gold'?'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400':tier.reward_tier==='silver'?'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300':tier.reward_tier==='platinum'?'bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400':'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400'">
              {{ tier.reward_tier || 'None' }}
            </span>
            <div class="flex-1 bg-slate-100 dark:bg-slate-700 rounded-full h-2">
              <div class="h-2 rounded-full transition-all"
                :class="tier.reward_tier==='gold'?'bg-amber-400':tier.reward_tier==='silver'?'bg-slate-400':tier.reward_tier==='platinum'?'bg-purple-500':'bg-orange-400'"
                :style="{width: rewardTiers[0]?.count ? (tier.count/rewardTiers[0].count*100)+'%' : '0%'}"></div>
            </div>
            <span class="text-xs font-bold text-slate-900 dark:text-white w-8 text-right">{{ tier.count }}</span>
          </div>
        </div>
        <div v-else class="px-4 pb-4 text-center py-6 text-xs text-slate-400">No tier data</div>
      </div>
    </div>

      </div>
    </div>
  </div>
</template>

<script>
import ModernMetricCard from '../components/MetricCard.vue'
import VueApexCharts from 'vue3-apexcharts'
import { useApi } from '../composables/useApi'
import DateRangePicker from '../components/DateRangePicker.vue'
import MultiSelectFilter from '../components/MultiSelectFilter.vue'
import ExportButton from '../components/ExportButton.vue'
import RealTimeMonitor from '../components/RealTimeMonitor.vue'

export default {
  name: 'Dashboard',
  components: {
    ModernMetricCard,
    apexchart: VueApexCharts,
    DateRangePicker,
    MultiSelectFilter,
    ExportButton,
    RealTimeMonitor
  },
  setup() {
    const { loading, makeRequest } = useApi()
    return { loading, makeRequest }
  },
  data() {
    return {
      showMetrics: true,
      showActivity: true,
      showExtras: false,
      revenuePeriod: '7d',
      growthPeriod: '30d',
      metrics: {},
      revenueData: [],
      clientGrowthData: [],
      systemStats: [],
      systemStatusInterval: 30000,
      systemStatusTimer: null,
      packageSales: [],
      paymentMethods: [],
      packageColors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#F97316'],
      paymentColors: ['#06B6D4', '#10B981', '#F59E0B', '#8B5CF6'],
      locationPerformance: [],
      recentActivity: [],
      voucherStatus: {},
      conversionFunnel: {},
      deviceBreakdown: [],
      rewardTiers: [],
      kpi: {},
      hideKpi: true,
      refundMetrics: {},
      
      // Filters
      dateRange: { start: '', end: '', compare: false },
      selectedLocations: [],
      selectedPackages: [],
      locationOptions: [],
      packageOptions: [],
      
      revenueChartOptions: {
        chart: { type: 'area', toolbar: { show: false }, zoom: { enabled: false }, background: 'transparent', fontFamily: 'inherit' },
        colors: ['#10B981'],
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 2.5 },
        fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.02, stops: [0, 100] } },
        xaxis: { type: 'datetime', labels: { style: { colors: '#94a3b8', fontSize: '10px' } }, axisBorder: { show: false }, axisTicks: { show: false } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '10px' }, formatter: (v) => `${this.formatNumber(v)}` } },
        grid: { borderColor: '#1e293b', strokeDashArray: 4, xaxis: { lines: { show: false } } },
        tooltip: { theme: 'dark', x: { format: 'dd MMM' } },
        markers: { size: 0, hover: { size: 4 } }
      },
      revenueChartSeries: [{ name: 'Revenue (KSh)', data: [] }],

      growthChartOptions: {
        chart: { type: 'bar', toolbar: { show: false }, background: 'transparent', fontFamily: 'inherit' },
        colors: ['#8B5CF6'],
        plotOptions: { bar: { borderRadius: 6, columnWidth: '55%', distributed: false } },
        dataLabels: { enabled: false },
        xaxis: { type: 'datetime', labels: { style: { colors: '#94a3b8', fontSize: '10px' } }, axisBorder: { show: false }, axisTicks: { show: false } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '10px' } } },
        grid: { borderColor: '#1e293b', strokeDashArray: 4, xaxis: { lines: { show: false } } },
        tooltip: { theme: 'dark', x: { format: 'dd MMM' } },
        states: { hover: { filter: { type: 'lighten', value: 0.1 } } }
      },
      growthChartSeries: [{ name: 'New Clients', data: [] }],

      packageChartOptions: {
        chart: { type: 'donut', background: 'transparent', fontFamily: 'inherit' },
        colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#F97316'],
        labels: [],
        legend: { position: 'right', fontSize: '11px', labels: { colors: '#94a3b8' }, markers: { width: 10, height: 10, radius: 2 }, itemMargin: { horizontal: 4, vertical: 4 } },
        dataLabels: { enabled: true, style: { fontSize: '11px', fontWeight: 'bold', colors: ['#fff'] }, dropShadow: { enabled: false } },
        stroke: { width: 2, colors: ['transparent'] },
        plotOptions: { pie: { donut: { size: '55%', labels: { show: true, total: { show: true, label: 'Total', color: '#94a3b8', fontSize: '11px', fontWeight: 600 } } } } },
        tooltip: { theme: 'dark', y: { formatter: (val) => `${val} sales` } },
        responsive: [{ breakpoint: 480, options: { legend: { position: 'bottom' } } }]
      },
      packageChartSeries: [],

      paymentChartOptions: {
        chart: { type: 'pie' },
        colors: ['#06B6D4', '#10B981', '#F59E0B', '#8B5CF6'],
        labels: [],
        legend: { position: 'bottom', fontSize: '11px' },
        dataLabels: { 
          enabled: true, 
          style: { fontSize: '12px', fontWeight: 'bold' },
          dropShadow: { enabled: true, blur: 2, opacity: 0.5 }
        },
        plotOptions: {
          pie: {
            expandOnClick: true
          }
        },
        stroke: { width: 2, colors: ['#fff'] },
        tooltip: {
          y: {
            formatter: (val) => `${val} transactions`
          }
        }
      },
      paymentChartSeries: []
    }
  },
  computed: {
    systemOverallStatus() {
      if (!this.systemStats.length) return 'unknown'
      if (this.systemStats.some(s => s.statusColor === 'bg-rose-500')) return 'critical'
      if (this.systemStats.some(s => s.statusColor === 'bg-amber-500')) return 'warning'
      return 'healthy'
    },
    exportData() {
      return {
        metrics: this.metrics,
        revenueData: this.revenueData,
        clientGrowthData: this.clientGrowthData,
        packageSales: this.packageSales,
        locationPerformance: this.locationPerformance
      }
    },
    exportFilename() {
      const date = new Date().toISOString().split('T')[0]
      return `dashboard-report-${date}`
    }
  },
  async mounted() {
    await this.fetchFilterOptions()
    await this.fetchAllData()
    this.updateSystemStatusInterval()
  },
  beforeUnmount() {
    if (this.systemStatusTimer) {
      clearInterval(this.systemStatusTimer)
    }
  },
  methods: {
    async fetchFilterOptions() {
      try {
        // Fetch locations
        const locations = await this.makeRequest('get', 'suapi/locations/')
        this.locationOptions = locations.results?.map(l => ({ 
          value: l.id, 
          label: l.name 
        })) || []

        // Fetch packages
        const packages = await this.makeRequest('get', 'suapi/packages/')
        this.packageOptions = packages.results?.map(p => ({ 
          value: p.id, 
          label: p.name 
        })) || []
      } catch (error) {
        console.error('Error fetching filter options:', error)
      }
    },

    handleDateChange(range) {
      this.dateRange = range
      this.fetchAllData()
    },

    handleLocationFilter(locations) {
      this.selectedLocations = locations
      this.fetchAllData()
    },

    handlePackageFilter(packages) {
      this.selectedPackages = packages
      this.fetchAllData()
    },

    async fetchAllData() {
      await Promise.all([
        this.fetchDashboardMetrics(),
        this.fetchRevenueAnalytics(),
        this.fetchClientGrowth(),
        this.fetchSystemStatus(),
        this.fetchPackageSales(),
        this.fetchPaymentMethods(),
        this.fetchLocationPerformance(),
        this.fetchRecentActivity(),
        this.fetchVoucherStatus(),
        this.fetchConversionFunnel(),
        this.fetchDeviceBreakdown(),
        this.fetchRewardTiers(),
        this.fetchKpi()
      ])
    },

    async fetchDashboardMetrics() {
      try {
        let url = 'suapi/dashboard-metrics/'
        const params = new URLSearchParams()
        
        if (this.dateRange.start) params.append('start_date', this.dateRange.start)
        if (this.dateRange.end) params.append('end_date', this.dateRange.end)
        if (this.selectedLocations.length) params.append('locations', this.selectedLocations.join(','))
        if (this.selectedPackages.length) params.append('packages', this.selectedPackages.join(','))
        
        if (params.toString()) url += `?${params.toString()}`
        
        this.metrics = await this.makeRequest('get', url)
      } catch (error) {
        console.error('Error fetching metrics:', error)
      }
    },

    async fetchRevenueAnalytics() {
      try {
        let url = `suapi/dashboard-metrics/revenue-analytics/?period=${this.revenuePeriod}`
        const params = new URLSearchParams({ period: this.revenuePeriod })
        
        if (this.dateRange.start) params.append('start_date', this.dateRange.start)
        if (this.dateRange.end) params.append('end_date', this.dateRange.end)
        if (this.selectedLocations.length) params.append('locations', this.selectedLocations.join(','))
        if (this.selectedPackages.length) params.append('packages', this.selectedPackages.join(','))
        
        url = `suapi/dashboard-metrics/revenue-analytics/?${params.toString()}`
        
        const data = await this.makeRequest('get', url)
        this.revenueData = data.data
        this.revenueChartSeries = [{
          name: 'Revenue',
          data: this.revenueData.map(item => ({ x: new Date(item.date).getTime(), y: item.revenue }))
        }]
      } catch (error) {
        console.error('Error fetching revenue:', error)
      }
    },

    async fetchClientGrowth() {
      try {
        let url = `suapi/dashboard-metrics/client-growth/?period=${this.growthPeriod}`
        const params = new URLSearchParams({ period: this.growthPeriod })
        
        if (this.dateRange.start) params.append('start_date', this.dateRange.start)
        if (this.dateRange.end) params.append('end_date', this.dateRange.end)
        if (this.selectedLocations.length) params.append('locations', this.selectedLocations.join(','))
        
        url = `suapi/dashboard-metrics/client-growth/?${params.toString()}`
        
        const data = await this.makeRequest('get', url)
        this.clientGrowthData = data.data
        this.growthChartSeries = [{
          name: 'Signups',
          data: this.clientGrowthData.map(item => ({ x: new Date(item.date).getTime(), y: item.signups }))
        }]
      } catch (error) {
        console.error('Error fetching growth:', error)
      }
    },

    async fetchSystemStatus() {
      try {
        const data = await this.makeRequest('get', 'suapi/system-status/')
        this.systemStats = [
          { name: 'Database', value: data.database_response, statusColor: data.database_status === 'healthy' ? 'bg-emerald-500' : data.database_status === 'warning' ? 'bg-amber-500' : 'bg-rose-500' },
          { name: 'Internet', value: data.internet_response, statusColor: data.internet_status === 'healthy' ? 'bg-emerald-500' : data.internet_status === 'warning' ? 'bg-amber-500' : 'bg-rose-500' },
          { name: 'Cache', value: data.cache_response, statusColor: data.cache_status === 'healthy' ? 'bg-emerald-500' : data.cache_status === 'warning' ? 'bg-amber-500' : 'bg-rose-500' },
          { name: 'Disk', value: data.disk_usage, statusColor: data.disk_status === 'healthy' ? 'bg-emerald-500' : data.disk_status === 'warning' ? 'bg-amber-500' : 'bg-rose-500' }
        ]
      } catch (error) {
        console.error('Error fetching system status:', error)
      }
    },

    updateSystemStatusInterval() {
      if (this.systemStatusTimer) {
        clearInterval(this.systemStatusTimer)
      }
      this.systemStatusTimer = setInterval(() => {
        this.fetchSystemStatus()
      }, parseInt(this.systemStatusInterval))
    },

    async fetchPackageSales() {
      try {
        let url = 'suapi/dashboard-metrics/package-sales/'
        const params = new URLSearchParams()
        
        if (this.dateRange.start) params.append('start_date', this.dateRange.start)
        if (this.dateRange.end) params.append('end_date', this.dateRange.end)
        if (this.selectedLocations.length) params.append('locations', this.selectedLocations.join(','))
        if (this.selectedPackages.length) params.append('packages', this.selectedPackages.join(','))
        
        if (params.toString()) url += `?${params.toString()}`
        
        const data = await this.makeRequest('get', url)
        this.packageSales = data.data
        this.packageChartOptions.labels = this.packageSales.map(p => p.package__name || 'Unknown')
        this.packageChartSeries = this.packageSales.map(p => p.count)
      } catch (error) {
        console.error('Error fetching package sales:', error)
      }
    },

    async fetchPaymentMethods() {
      try {
        const data = await this.makeRequest('get', 'suapi/dashboard-metrics/payment-methods/')
        this.paymentMethods = data.data
        this.paymentChartOptions.labels = this.paymentMethods.map(p => p.payment_method || 'Unknown')
        this.paymentChartSeries = this.paymentMethods.map(p => p.count)
      } catch (error) {
        console.error('Error fetching payment methods:', error)
      }
    },

    async fetchLocationPerformance() {
      try {
        let url = 'suapi/dashboard-metrics/location-performance/'
        const params = new URLSearchParams()
        
        if (this.dateRange.start) params.append('start_date', this.dateRange.start)
        if (this.dateRange.end) params.append('end_date', this.dateRange.end)
        if (this.selectedLocations.length) params.append('locations', this.selectedLocations.join(','))
        if (this.selectedPackages.length) params.append('packages', this.selectedPackages.join(','))
        
        if (params.toString()) url += `?${params.toString()}`
        
        const data = await this.makeRequest('get', url)
        this.locationPerformance = data.data
      } catch (error) {
        console.error('Error fetching location performance:', error)
      }
    },

    async fetchRecentActivity() {
      try {
        const data = await this.makeRequest('get', 'suapi/dashboard-metrics/recent-activity/')
        this.recentActivity = data.data
      } catch (error) {
        console.error('Error fetching recent activity:', error)
      }
    },

    async fetchVoucherStatus() {
      try {
        this.voucherStatus = await this.makeRequest('get', 'suapi/dashboard-metrics/voucher-status/')
      } catch (error) {
        console.error('Error fetching voucher status:', error)
      }
    },

    async fetchConversionFunnel() {
      try {
        this.conversionFunnel = await this.makeRequest('get', 'suapi/dashboard-metrics/conversion-funnel/')
      } catch (error) {
        console.error('Error fetching conversion funnel:', error)
      }
    },

    async fetchDeviceBreakdown() {
      try {
        const data = await this.makeRequest('get', 'suapi/dashboard-metrics/device-breakdown/')
        this.deviceBreakdown = data.data
      } catch (error) {
        console.error('Error fetching device breakdown:', error)
      }
    },

    async fetchRewardTiers() {
      try {
        const data = await this.makeRequest('get', 'suapi/dashboard-metrics/reward-tiers/')
        this.rewardTiers = data.data
      } catch (error) {
        console.error('Error fetching reward tiers:', error)
      }
    },

    async fetchKpi() {
      try {
        this.kpi = await this.makeRequest('get', 'api/finance/api/kpi/summary/')
      } catch (e) { console.error('KPI fetch failed', e) }
    },

    async fetchRefundMetrics() {
      try {
        this.refundMetrics = await this.makeRequest('get', 'suapi/dashboard-metrics/refund-metrics/')
      } catch (error) {
        console.error('Error fetching refund metrics:', error)
      }
    },

    refreshData() {
      this.fetchAllData()
    },

    formatNumber(num) {
      return new Intl.NumberFormat().format(num)
    },

    formatTime(isoString) {
      const date = new Date(isoString)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000)
      
      if (diff < 60) return 'Just now'
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
      return `${Math.floor(diff / 86400)}d ago`
    },

    toggleMetrics() {
      this.showMetrics = !this.showMetrics
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

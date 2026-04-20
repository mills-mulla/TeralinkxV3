<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Dashboard</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Welcome back, here's your overview</p>
      </div>
      <div class="flex items-center gap-3">
        <DateRangePicker @change="handleDateChange" />
        <MultiSelectFilter 
          label="Locations" 
          :options="locationOptions" 
          @change="handleLocationFilter"
        />
        <MultiSelectFilter 
          label="Packages" 
          :options="packageOptions" 
          @change="handlePackageFilter"
        />
        <ExportButton :data="exportData" :filename="exportFilename" />
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
            <option value="30000">30s</option>
            <option value="60000">1m</option>
            <option value="300000">5m</option>
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
    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard
        title="Total Clients"
        :value="metrics.totalClients || 0"
        :trend="metrics.clientsTrend || 'stable'"
        :trendValue="metrics.clientsTrendValue || '0%'"
        color="blue"
      >
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard
        title="New (7d)"
        :value="metrics.newClients7d || 0"
        :trend="metrics.newClientsTrend || 'stable'"
        :trendValue="metrics.newClientsTrendValue || '0%'"
        color="emerald"
      >
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard
        title="Active Vouchers"
        :value="metrics.activeUsers || 0"
        :trend="metrics.activeUsersTrend || 'stable'"
        :trendValue="metrics.activeUsersTrendValue || '0%'"
        color="green"
      >
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard
        title="Active Sessions"
        :value="metrics.activeUsers || 0"
        :trend="metrics.activeUsersTrend || 'stable'"
        :trendValue="metrics.activeUsersTrendValue || '0%'"
        color="amber"
      >
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/></svg>
      </ModernMetricCard>
    </div>

    <!-- Charts Row 1 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.1s">
      <!-- Revenue Chart -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 transition-colors duration-300">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
            </svg>
            <h3 class="text-sm font-medium text-slate-900 dark:text-white">Revenue Analytics</h3>
          </div>
          <select 
            v-model="revenuePeriod" 
            @change="fetchRevenueAnalytics"
            class="text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 text-slate-900 dark:text-white"
          >
            <option value="7d">7 days</option>
            <option value="14d">14 days</option>
            <option value="30d">30 days</option>
            <option value="90d">90 days</option>
            <option value="6m">6 months</option>
            <option value="1y">1 year</option>
          </select>
        </div>
        <div v-if="revenueData.length > 0" class="h-64">
          <apexchart
            type="area"
            height="100%"
            :options="revenueChartOptions"
            :series="revenueChartSeries"
          />
        </div>
        <div v-else class="h-64 flex items-center justify-center text-slate-400 dark:text-slate-500 text-sm">
          Loading...
        </div>
      </div>

      <!-- Growth Chart -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 transition-colors duration-300">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
            </svg>
            <h3 class="text-sm font-medium text-slate-900 dark:text-white">Client Growth</h3>
          </div>
          <select 
            v-model="growthPeriod" 
            @change="fetchClientGrowth"
            class="text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 text-slate-900 dark:text-white"
          >
            <option value="7d">7 days</option>
            <option value="14d">14 days</option>
            <option value="30d">30 days</option>
            <option value="90d">90 days</option>
            <option value="6m">6 months</option>
            <option value="1y">1 year</option>
          </select>
        </div>
        <div v-if="clientGrowthData.length > 0" class="h-64">
          <apexchart
            type="bar"
            height="100%"
            :options="growthChartOptions"
            :series="growthChartSeries"
          />
        </div>
        <div v-else class="h-64 flex items-center justify-center text-slate-400 dark:text-slate-500 text-sm">
          Loading...
        </div>
      </div>
    </div>

    <!-- Charts Row 2: Package Sales -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.15s">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div class="flex items-center gap-2 mb-4">
          <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83 8.62 12 11 8.76l1-1.36 1 1.36L15.38 12 17 10.83 14.92 8H20v6z"/>
          </svg>
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Package Sales</h3>
        </div>
        <div v-if="packageSales.length > 0" class="h-96">
          <apexchart type="pie" height="100%" :options="packageChartOptions" :series="packageChartSeries" />
        </div>
        <div v-else class="h-64 flex items-center justify-center text-slate-400 text-sm">Loading...</div>
      </div>
    </div>

    <!-- Voucher Status & Conversion Funnel -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.2s">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div class="flex items-center gap-2 mb-4">
          <svg class="w-5 h-5 text-orange-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/>
          </svg>
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Voucher Status</h3>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div class="bg-emerald-50 dark:bg-emerald-500/10 rounded-lg p-4 text-center">
            <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{{ voucherStatus.active || 0 }}</p>
            <p class="text-xs text-slate-600 dark:text-slate-400 mt-1">Active</p>
          </div>
          <div class="bg-amber-50 dark:bg-amber-500/10 rounded-lg p-4 text-center">
            <p class="text-2xl font-bold text-amber-600 dark:text-amber-400">{{ voucherStatus.pending || 0 }}</p>
            <p class="text-xs text-slate-600 dark:text-slate-400 mt-1">Pending</p>
          </div>
          <div class="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 text-center">
            <p class="text-2xl font-bold text-slate-600 dark:text-slate-400">{{ voucherStatus.expired || 0 }}</p>
            <p class="text-xs text-slate-600 dark:text-slate-400 mt-1">Expired</p>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
          <div class="flex justify-between text-sm">
            <span class="text-slate-600 dark:text-slate-400">Total Vouchers</span>
            <span class="font-semibold text-slate-900 dark:text-white">{{ voucherStatus.total || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div class="flex items-center gap-2 mb-4">
          <svg class="w-5 h-5 text-indigo-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
          </svg>
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Conversion Funnel</h3>
        </div>
        <div class="space-y-3">
          <div class="relative">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-slate-600 dark:text-slate-400">Signups</span>
              <span class="font-semibold text-slate-900 dark:text-white">{{ conversionFunnel.signups || 0 }}</span>
            </div>
            <div class="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div class="h-full bg-blue-500" style="width: 100%"></div>
            </div>
          </div>
          <div class="relative">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-slate-600 dark:text-slate-400">Purchased</span>
              <span class="font-semibold text-slate-900 dark:text-white">{{ conversionFunnel.purchased || 0 }}</span>
            </div>
            <div class="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div class="h-full bg-purple-500" :style="`width: ${(conversionFunnel.purchased / conversionFunnel.signups * 100) || 0}%`"></div>
            </div>
          </div>
          <div class="relative">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-slate-600 dark:text-slate-400">Active</span>
              <span class="font-semibold text-slate-900 dark:text-white">{{ conversionFunnel.active || 0 }}</span>
            </div>
            <div class="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div class="h-full bg-emerald-500" :style="`width: ${(conversionFunnel.active / conversionFunnel.signups * 100) || 0}%`"></div>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
            <div class="flex justify-between text-sm">
              <span class="text-slate-600 dark:text-slate-400">Conversion Rate</span>
              <span class="font-semibold text-emerald-600 dark:text-emerald-400">{{ conversionFunnel.conversion_rate || 0 }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Location Performance & Recent Activity -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.25s">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div class="flex items-center gap-2 mb-4">
          <svg class="w-5 h-5 text-rose-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Top Locations</h3>
        </div>
        <div class="space-y-2 max-h-64 overflow-y-auto">
          <div v-for="(loc, idx) in locationPerformance" :key="idx" class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-rose-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold">
                {{ idx + 1 }}
              </div>
              <div>
                <p class="text-sm font-medium text-slate-900 dark:text-white">{{ loc.location__name || 'Unknown' }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400">{{ loc.sales }} sales</p>
              </div>
            </div>
            <p class="text-sm font-semibold text-slate-900 dark:text-white">KSh {{ formatNumber(loc.revenue || 0) }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div class="flex items-center gap-2 mb-4">
          <svg class="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>
          </svg>
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Recent Activity</h3>
        </div>
        <div class="space-y-2 max-h-64 overflow-y-auto">
          <div v-for="activity in recentActivity" :key="activity.time" class="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="activity.type === 'payment' ? 'bg-emerald-100 dark:bg-emerald-500/20' : 'bg-blue-100 dark:bg-blue-500/20'">
              <svg v-if="activity.type === 'payment'" class="w-4 h-4 text-emerald-600 dark:text-emerald-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
              </svg>
              <svg v-else class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-slate-900 dark:text-white">{{ activity.description }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ activity.user }} • {{ formatTime(activity.time) }}</p>
            </div>
          </div>
        </div>
      </div>
      </div>

      <!-- Additional Metrics Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.3s">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div class="flex items-center gap-2 mb-3">
          <svg class="w-5 h-5 text-teal-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
          </svg>
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Device Breakdown</h3>
        </div>
        <div v-if="deviceBreakdown.length > 0" class="space-y-2">
          <div v-for="device in deviceBreakdown" :key="device.device_type" class="flex justify-between items-center">
            <span class="text-sm text-slate-600 dark:text-slate-400">{{ device.device_type || 'Unknown' }}</span>
            <span class="text-sm font-semibold text-slate-900 dark:text-white">{{ device.count }}</span>
          </div>
        </div>
        <div v-else class="text-center text-slate-400 text-sm py-4">No data</div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div class="flex items-center gap-2 mb-3">
          <svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg>
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Reward Tiers</h3>
        </div>
        <div v-if="rewardTiers.length > 0" class="space-y-2">
          <div v-for="tier in rewardTiers" :key="tier.reward_tier" class="flex justify-between items-center">
            <span class="text-sm text-slate-600 dark:text-slate-400">{{ tier.reward_tier || 'None' }}</span>
            <span class="text-sm font-semibold text-slate-900 dark:text-white">{{ tier.count }}</span>
          </div>
        </div>
        <div v-else class="text-center text-slate-400 text-sm py-4">No data</div>
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
      hideKpi: false,
      refundMetrics: {},
      
      // Filters
      dateRange: { start: '', end: '', compare: false },
      selectedLocations: [],
      selectedPackages: [],
      locationOptions: [],
      packageOptions: [],
      
      revenueChartOptions: {
        chart: { type: 'area', toolbar: { show: false }, zoom: { enabled: false } },
        colors: ['#10B981'],
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 2 },
        fill: { type: 'gradient', gradient: { opacityFrom: 0.4, opacityTo: 0.1 } },
        xaxis: { type: 'datetime', labels: { style: { colors: '#94a3b8', fontSize: '11px' } } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '11px' }, formatter: (v) => `${this.formatNumber(v)}` } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        tooltip: { theme: 'dark' }
      },
      revenueChartSeries: [{ name: 'Revenue', data: [] }],

      growthChartOptions: {
        chart: { type: 'bar', toolbar: { show: false } },
        colors: ['#8B5CF6'],
        plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
        dataLabels: { enabled: false },
        xaxis: { type: 'datetime', labels: { style: { colors: '#94a3b8', fontSize: '11px' } } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '11px' } } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        tooltip: { theme: 'dark' }
      },
      growthChartSeries: [{ name: 'Signups', data: [] }],

      packageChartOptions: {
        chart: { type: 'pie' },
        colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#F97316'],
        labels: [],
        legend: { 
          position: 'right',
          fontSize: '12px',
          offsetY: 0,
          height: 320,
          markers: {
            width: 12,
            height: 12,
            radius: 2
          },
          itemMargin: {
            horizontal: 5,
            vertical: 5
          }
        },
        dataLabels: { 
          enabled: true,
          style: { fontSize: '14px', fontWeight: 'bold' },
          dropShadow: { enabled: false }
        },
        stroke: { width: 2, colors: ['#fff'] },
        tooltip: {
          y: {
            formatter: (val) => `${val} sales`
          }
        },
        responsive: [{
          breakpoint: 480,
          options: {
            legend: {
              position: 'bottom'
            }
          }
        }]
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

<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Packages</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage data packages</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Package
        </button>
        <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load packages</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchPackages" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <!-- Metric Pills -->
    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Total Packages</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_packages || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Active</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.active_packages || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 rounded-xl">
        <span class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">Public</span>
        <span class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ stats.public_packages || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl">
        <span class="text-[10px] text-amber-600 dark:text-amber-400 font-medium">Avg Price</span>
        <span class="text-sm font-bold text-amber-700 dark:text-amber-300">KSh {{ formatNumber(stats.average_price || 0) }}</span>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-2 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2 flex-wrap">
        <div class="flex-1 min-w-48">
          <input v-model="searchTerm" type="text" placeholder="Search name, code, description..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
        <select v-model="categoryFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Categories</option>
          <option value="home">Home</option>
          <option value="business">Business</option>
          <option value="hotspot">Hotspot</option>
          <option value="mobile">Mobile</option>
        </select>
        <select v-model="tierFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Tiers</option>
          <option value="basic">Basic</option>
          <option value="standard">Standard</option>
          <option value="premium">Premium</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <select v-model="featuredFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All</option>
          <option value="true">Featured</option>
          <option value="false">Not Featured</option>
        </select>
      </div>

      <!-- Bulk Actions -->
      <div v-if="selectedIds.length" class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
        <span class="text-xs text-blue-700 dark:text-blue-400 font-medium">{{ selectedIds.length }} selected</span>
        <button @click="bulkAction('activate')" class="px-2 py-1 text-[10px] font-medium rounded bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200">✅ Activate</button>
        <button @click="bulkAction('deactivate')" class="px-2 py-1 text-[10px] font-medium rounded bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200">❌ Deactivate</button>
        <button @click="bulkAction('feature')" class="px-2 py-1 text-[10px] font-medium rounded bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 hover:bg-amber-200">⭐ Feature</button>
        <button @click="bulkAction('unfeature')" class="px-2 py-1 text-[10px] font-medium rounded bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200">☆ Unfeature</button>
        <button @click="selectedIds = []" class="ml-auto text-[10px] text-slate-500 hover:text-slate-700">Clear</button>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 w-6"><input type="checkbox" @change="toggleSelectAll" :checked="selectedIds.length === filteredPackages.length && filteredPackages.length > 0" class="rounded" /></th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Package</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Code</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Category</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Tier</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Price</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Speed</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Data</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">QoS</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Active</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Public</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Featured</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Sales</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="pkg in filteredPackages" :key="pkg.id" @click="openEditModal(pkg)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2" @click.stop><input type="checkbox" :value="pkg.id" v-model="selectedIds" class="rounded" /></td>
                <td class="px-3 py-2">
                  <p class="text-xs font-medium text-slate-900 dark:text-white">{{ pkg.name }}</p>
                  <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ pkg.description?.slice(0,40) }}</p>
                </td>
                <td class="px-3 py-2 text-xs font-mono text-slate-900 dark:text-white">{{ pkg.code }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ pkg.category }}</span></td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400">{{ pkg.tier }}</span></td>
                <td class="px-3 py-2 text-xs font-semibold text-slate-900 dark:text-white">KSh {{ formatNumber(pkg.price) }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ pkg.speed_limit_mbps }} Mbps</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatData(pkg.data_limit_mb) }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">{{ pkg.qos_priority }}</span></td>
                <td class="px-3 py-2"><span class="w-2 h-2 rounded-full inline-block" :class="pkg.is_active ? 'bg-emerald-500' : 'bg-slate-300'"></span></td>
                <td class="px-3 py-2"><span class="w-2 h-2 rounded-full inline-block" :class="pkg.is_public ? 'bg-blue-500' : 'bg-slate-300'"></span></td>
                <td class="px-3 py-2"><span class="w-2 h-2 rounded-full inline-block" :class="pkg.is_featured ? 'bg-amber-500' : 'bg-slate-300'"></span></td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ pkg.sold_quantity || 0 }}</td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="duplicatePackage(pkg)" class="p-1 hover:bg-purple-100 dark:hover:bg-purple-600 rounded" title="Duplicate">
                      <svg class="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                    </button>
                    <button @click.stop="openDeleteModal(pkg)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Package Analytics -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">

      <!-- Header -->
      <div class="bg-slate-50 dark:bg-slate-700/40 border-b border-slate-200 dark:border-slate-700 px-4 py-3">
        <div class="flex items-center justify-between">
          <button @click="showAnalytics=!showAnalytics" class="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">📊 Sales Intelligence</span>
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="showAnalytics?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div class="flex items-center gap-2">
            <select v-model="analyticsPackage" @change="fetchAnalytics" class="px-2 py-1 text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-700 dark:text-slate-300">
              <option value="">All Packages</option>
              <option v-for="p in packages" :key="p.id" :value="p.id">{{ p.name }} ({{ p.code }})</option>
            </select>
            <button @click="fetchAnalytics" class="px-2.5 py-1 text-xs bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-lg border border-slate-200 dark:border-slate-600 transition-colors">🔄 Refresh</button>
            <button @click="hideRevenue=!hideRevenue" class="p-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 rounded-lg border border-slate-200 dark:border-slate-600 transition-colors" :title="hideRevenue?'Show revenue':'Hide revenue'">
              <svg v-if="hideRevenue" class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
              <svg v-else class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-5 0-9.27-3.11-11-7.5a10.05 10.05 0 012.38-3.88M9.9 4.24A9.12 9.12 0 0112 4c5 0 9.27 3.11 11 7.5a10.1 10.1 0 01-1.67 2.94M1 1l22 22"/></svg>
            </button>
          </div>
        </div>

        <!-- Period selectors -->
        <div v-show="showAnalytics" class="flex items-center gap-2 mt-3 flex-wrap">
          <div class="flex items-center gap-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-lg p-1">
            <span class="text-[10px] text-slate-400 px-1">Show:</span>
            <button v-for="p in periodOptions" :key="p.value" @click="analyticsPeriod=p.value; fetchAnalytics()" class="px-2 py-0.5 text-[10px] rounded-md transition-colors" :class="analyticsPeriod===p.value ? 'bg-slate-700 dark:bg-slate-200 text-white dark:text-slate-800 font-semibold' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'">{{ p.label }}</button>
          </div>
          <div class="flex items-center gap-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-lg p-1">
            <span class="text-[10px] text-slate-400 px-1">Compare to:</span>
            <button v-for="c in compareOptions" :key="c.value" @click="analyticsCompare=c.value; fetchAnalytics()" class="px-2 py-0.5 text-[10px] rounded-md transition-colors" :class="analyticsCompare===c.value ? 'bg-slate-700 dark:bg-slate-200 text-white dark:text-slate-800 font-semibold' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'">{{ c.label }}</button>
          </div>
        </div>
      </div>

      <div v-if="analyticsData && showAnalytics" class="p-4 space-y-4">

        <!-- KPI Cards -->
        <div class="grid grid-cols-4 gap-3">
          <div v-for="kpi in analyticsKpis" :key="kpi.label" class="rounded-xl p-3 border" :class="kpi.bg">
            <div class="flex items-center justify-between mb-1">
              <span class="text-lg">{{ kpi.icon }}</span>
              <span v-if="analyticsCompare && kpi.change !== null" class="px-1.5 py-0.5 text-[10px] font-bold rounded-full" :class="kpi.change >= 0 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400'">
                {{ kpi.change >= 0 ? '▲' : '▼' }} {{ Math.abs(kpi.change) }}%
              </span>
            </div>
            <p class="text-xl font-bold" :class="[kpi.valueColor, kpi.sensitive && hideRevenue ? 'blur-sm select-none' : '']" >{{ kpi.current }}</p>
            <p class="text-[10px] font-medium" :class="kpi.labelColor">{{ kpi.label }}</p>
            <p v-if="analyticsCompare && kpi.prev !== null" class="text-[10px] mt-0.5" :class="[kpi.subColor, kpi.sensitive && hideRevenue ? 'blur-sm select-none' : '']">Previous: {{ kpi.prev }}</p>
          </div>
        </div>

        <!-- Per-package breakdown -->
        <div class="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div class="px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">📦 Package Breakdown — <span class="text-blue-600 dark:text-blue-400">{{ periodOptions.find(p=>p.value===analyticsPeriod)?.label }}</span></span>
            <span v-if="analyticsCompare" class="text-[10px] text-slate-500">Compared to: <span class="font-medium text-slate-700 dark:text-slate-300">{{ compareOptions.find(c=>c.value===analyticsCompare)?.label }}</span></span>
          </div>
          <div class="divide-y divide-slate-100 dark:divide-slate-700">
            <div v-for="(row, i) in analyticsRows" :key="row.code" class="px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
              <div class="flex items-center gap-3">
                <!-- Rank -->
                <div class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0" :class="i===0?'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400':i===1?'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300':i===2?'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400':'bg-slate-50 text-slate-400 dark:bg-slate-800 dark:text-slate-500'">#{{ i+1 }}</div>
                <!-- Name -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-semibold text-slate-900 dark:text-white">{{ row.name }}</span>
                    <span class="px-1.5 py-0.5 text-[10px] font-mono bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 rounded">{{ row.code }}</span>
                    <span class="px-1.5 py-0.5 text-[10px] rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400">{{ row.tier }}</span>
                  </div>
                  <!-- Progress bar -->
                  <div class="flex items-center gap-2 mt-1">
                    <div class="flex-1 bg-slate-200 dark:bg-slate-700 rounded-full h-1.5">
                      <div class="h-1.5 rounded-full transition-all" :class="i===0?'bg-amber-500':i===1?'bg-blue-500':i===2?'bg-emerald-500':'bg-slate-400'" :style="{width: totalSold>0?(row.sold/totalSold*100)+'%':'0%'}"></div>
                    </div>
                    <span class="text-[10px] text-slate-400 w-8 text-right">{{ totalSold>0?Math.round(row.sold/totalSold*100):0 }}% share</span>
                  </div>
                </div>
                <!-- Stats -->
                <div class="flex items-center gap-4 shrink-0">
                  <div class="text-center">
                    <p class="text-sm font-bold text-slate-900 dark:text-white">{{ row.sold }}</p>
                    <p class="text-[10px] text-slate-500">Vouchers Sold</p>
                  </div>
                  <div v-if="analyticsCompare" class="text-center">
                    <p class="text-sm font-medium text-slate-500">{{ row.prev_sold ?? '-' }}</p>
                    <p class="text-[10px] text-slate-400">Prev Period</p>
                  </div>
                  <div v-if="analyticsCompare && row.prev_sold != null" class="text-center">
                    <p class="text-sm font-bold" :class="(row.sold-row.prev_sold)>=0?'text-emerald-600':'text-red-500'">{{ (row.sold-row.prev_sold)>=0?'+':'' }}{{ row.sold-row.prev_sold }}</p>
                    <p class="text-[10px] text-slate-400">Change</p>
                  </div>
                  <div class="text-center">
                    <p class="text-sm font-bold text-emerald-600 dark:text-emerald-400">{{ row.active }}</p>
                    <p class="text-[10px] text-slate-500">Active Now</p>
                  </div>
                  <div class="text-center">
                    <p class="text-sm font-bold text-blue-600 dark:text-blue-400" :class="hideRevenue ? 'blur-sm select-none' : ''">KSh {{ formatNumber(row.revenue) }}</p>
                    <p class="text-[10px] text-slate-500">Revenue Earned</p>
                  </div>
                  <div class="text-center">
                    <p class="text-sm font-medium text-slate-600 dark:text-slate-400" :class="hideRevenue ? 'blur-sm select-none' : ''">KSh {{ formatNumber(row.avg_price) }}</p>
                    <p class="text-[10px] text-slate-500">Avg per Sale</p>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="!analyticsRows.length" class="px-4 py-8 text-center text-xs text-slate-400">No sales data for this period</div>
          </div>
        </div>

        <!-- All-Time Leaderboard -->
        <div class="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div class="px-4 py-2.5 bg-amber-50 dark:bg-amber-500/10 border-b border-slate-200 dark:border-slate-700">
            <span class="text-xs font-semibold text-amber-700 dark:text-amber-400">🏆 All-Time Leaderboard</span>
            <span class="text-[10px] text-slate-500 ml-2">Total vouchers ever sold per package</span>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-5 divide-x divide-y divide-slate-100 dark:divide-slate-700">
            <div v-for="(p, i) in (analyticsData.all_time || [])"
              :key="p.code"
              class="p-3 relative"
              :class="i===0?'bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-500/10 dark:to-yellow-500/10':''">
              <div class="flex items-start justify-between mb-1">
                <span class="text-[10px] font-bold" :class="i===0?'text-amber-600 dark:text-amber-400':i===1?'text-slate-500':i===2?'text-orange-500':'text-slate-400'">#{{ i+1 }} {{ i===0?'🥇':i===1?'🥈':i===2?'🥉':'' }}</span>
                <span class="px-1.5 py-0.5 text-[10px] rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400">{{ p.tier }}</span>
              </div>
              <p class="text-xs font-bold text-slate-900 dark:text-white">{{ p.name }}</p>
              <p class="text-[10px] font-mono text-slate-400">{{ p.code }}</p>
              <div class="mt-2 space-y-0.5">
                <div class="flex justify-between">
                  <span class="text-[10px] text-slate-500">Total Sold</span>
                  <span class="text-[10px] font-bold text-blue-600 dark:text-blue-400">{{ p.total_sold }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-[10px] text-slate-500">Active Now</span>
                  <span class="text-[10px] font-bold text-emerald-600">{{ p.currently_active }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-[10px] text-slate-500">Revenue</span>
                  <span class="text-[10px] font-bold text-slate-700 dark:text-slate-300" :class="hideRevenue ? 'blur-sm select-none' : ''">KSh {{ formatNumber(p.total_revenue) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
      <div v-else class="p-6 text-center text-xs text-slate-400">🔄 Loading analytics...</div>
    </div>

    <!-- Edit Package Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[88vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700 shrink-0">
          <div>
            <h2 class="text-sm font-semibold text-slate-900 dark:text-white">{{ selectedPackage?.id ? formData.name : 'Add Package' }}</h2>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ formData.code }} · {{ formData.category }} · {{ formData.tier }}</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-2 py-0.5 text-[10px] rounded-full" :class="formData.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'">{{ formData.is_active ? 'Active' : 'Inactive' }}</span>
            <button @click="closeFormModal" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"><svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>
          </div>
        </div>
        <!-- Body -->
        <div class="flex flex-1 overflow-hidden">
          <!-- Sidebar -->
          <div class="w-44 shrink-0 border-r border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 overflow-y-auto p-3 space-y-1">
            <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide px-1 mb-1">Sections</p>
            <button v-for="s in pkgSections" :key="s.id" @click="activePkgSection = s.id" class="w-full text-left px-2.5 py-2 text-xs rounded-lg transition-colors" :class="activePkgSection === s.id ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 font-medium' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'">{{ s.label }}</button>
          </div>
          <!-- Right panel -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <!-- 1. Basic -->
            <div v-show="activePkgSection === 'basic'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="pOpen.basic=!pOpen.basic" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Basic</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="pOpen.basic?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="pOpen.basic" class="p-4 grid grid-cols-2 gap-3">
                <div class="col-span-2">
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Name <span class="text-red-500">*</span></label>
                  <input v-model="formData.name" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Code <span class="text-red-500">*</span></label>
                  <input v-model="formData.code" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Category <span class="text-red-500">*</span></label>
                  <select v-model="formData.category" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="time_based_unlimited">Time-Based Unlimited</option>
                    <option value="data_based">Data-Based</option>
                    <option value="unlimited">Unlimited</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="corporate">Corporate</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Tier <span class="text-red-500">*</span></label>
                  <select v-model="formData.tier" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="basic">Basic</option>
                    <option value="standard">Standard</option>
                    <option value="premium">Premium</option>
                    <option value="business">Business</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </div>
                <div class="col-span-2">
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
                  <textarea v-model="formData.description" rows="2" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"></textarea>
                </div>
              </div>
            </div>

            <!-- 2. Pricing -->
            <div v-show="activePkgSection === 'pricing'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="pOpen.pricing=!pOpen.pricing" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Pricing & Duration</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="pOpen.pricing?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="pOpen.pricing" class="p-4 grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Price (KSh) <span class="text-red-500">*</span></label>
                  <input v-model="formData.price" type="number" step="0.01" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Original Price (KSh)</label>
                  <input v-model="formData.original_price" type="number" step="0.01" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Discount %</label>
                  <div class="px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-500 dark:text-slate-400">
                    {{ formData.original_price > formData.price ? Math.round((1 - formData.price/formData.original_price)*100) + '%' : 'No discount' }}
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Duration (hours) <span class="text-red-500">*</span></label>
                  <input v-model="formData.duration_hours" type="number" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label class="flex items-center gap-2 mt-5 cursor-pointer">
                    <input v-model="formData.auto_renew" type="checkbox" class="w-4 h-4 text-blue-600 rounded" />
                    <span class="text-xs text-slate-700 dark:text-slate-300">Auto Renew</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 3. Technical -->
            <div v-show="activePkgSection === 'technical'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="pOpen.technical=!pOpen.technical" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Technical</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="pOpen.technical?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="pOpen.technical" class="p-4 grid grid-cols-2 gap-3">
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Speed (Mbps)</label><input v-model="formData.speed_limit_mbps" type="number" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Data Limit (MB)</label><input v-model="formData.data_limit_mb" type="number" placeholder="0 = unlimited" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Device Limit</label><input v-model="formData.device_limit" type="number" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">QoS Priority</label>
                  <select v-model="formData.qos_priority" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="standard">Standard</option><option value="premium">Premium</option><option value="business">Business</option><option value="real_time">Real-time</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- 4. Network -->
            <div v-show="activePkgSection === 'network'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="pOpen.network=!pOpen.network" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Network</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="pOpen.network?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="pOpen.network" class="p-4 grid grid-cols-2 gap-3">
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">RADIUS Group</label><input v-model="formData.radius_group" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="flex items-center gap-2 mt-5 cursor-pointer"><input v-model="formData.allow_roaming" type="checkbox" class="w-4 h-4 text-blue-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Allow Roaming</span></label></div>
              </div>
            </div>

            <!-- 5. Display -->
            <div v-show="activePkgSection === 'display'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="pOpen.display=!pOpen.display" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Display</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="pOpen.display?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="pOpen.display" class="p-4 grid grid-cols-2 gap-3">
                <div><label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Active</span></label></div>
                <div><label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_public" type="checkbox" class="w-4 h-4 text-blue-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Public</span></label></div>
                <div><label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_featured" type="checkbox" class="w-4 h-4 text-blue-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Featured</span></label></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Display Order</label><input v-model="formData.display_order" type="number" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Color Code</label><input v-model="formData.color_code" type="text" placeholder="#3B82F6" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div class="col-span-2">
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Tags <span class="text-[10px] text-slate-400">(comma separated)</span></label>
                  <input v-model="formData.tags_input" type="text" placeholder="wifi, home, unlimited" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                  <p class="text-[10px] text-slate-400 mt-0.5">Current: {{ Array.isArray(formData.tags) ? formData.tags.join(', ') : formData.tags || '[]' }}</p>
                </div>
              </div>
            </div>

            <!-- 6. Promotions -->
            <div v-show="activePkgSection === 'promotions'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="pOpen.promotions=!pOpen.promotions" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Promotions</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="pOpen.promotions?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="pOpen.promotions" class="p-4 grid grid-cols-2 gap-3">
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Promotion Start</label><input v-model="formData.promotion_start" type="datetime-local" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Promotion End</label><input v-model="formData.promotion_end" type="datetime-local" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              </div>
            </div>

            <!-- 7. Inventory -->
            <div v-show="activePkgSection === 'inventory'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="pOpen.inventory=!pOpen.inventory" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Inventory</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="pOpen.inventory?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="pOpen.inventory" class="p-4 grid grid-cols-3 gap-3 text-xs">
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Total Qty <span class="text-[10px] text-slate-400">(blank = unlimited)</span></label><input v-model="formData.total_quantity" type="number" placeholder="unlimited" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><span class="text-slate-500 dark:text-slate-400">Sold</span><p class="font-bold text-slate-900 dark:text-white mt-1">{{ selectedPackage?.sold_quantity || 0 }}</p></div>
                <div><span class="text-slate-500 dark:text-slate-400">Available</span><p class="font-bold text-emerald-600 mt-1">{{ formData.total_quantity ? (formData.total_quantity - (selectedPackage?.sold_quantity || 0)) : 'Unlimited' }}</p></div>
                <div v-if="selectedPackage?.id" class="col-span-3 pt-2 border-t border-slate-200 dark:border-slate-700">
                  <button @click="syncSales" class="px-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 rounded-lg">🔄 Sync from Vouchers</button>
                  <p class="text-[10px] text-slate-400 mt-1">Recalculates sold count from actual dispatched vouchers</p>
                </div>
              </div>
            </div>

            <!-- 8. Locations -->
            <div v-show="activePkgSection === 'locations'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="pOpen.locations=!pOpen.locations" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Locations <span class="ml-1 px-1.5 py-0.5 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-full text-[10px] normal-case font-normal">{{ formData.locations?.length || 0 }}</span></span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="pOpen.locations?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="pOpen.locations" class="p-4">
                <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-2">Select locations where this package is available.</p>
                <div class="space-y-1 max-h-48 overflow-y-auto">
                  <label v-for="loc in pkgLocations" :key="loc.id" class="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer">
                    <input type="checkbox" :value="loc.id" v-model="formData.locations" class="w-3.5 h-3.5 text-blue-600 rounded" />
                    <span class="text-xs text-slate-700 dark:text-slate-300">{{ loc.name }}</span>
                    <span class="text-[10px] text-slate-400">{{ loc.code }}</span>
                  </label>
                </div>
              </div>
            </div>

          </div>
        </div>
        <div class="flex items-center justify-end gap-2 px-5 py-3 border-t border-slate-200 dark:border-slate-700 shrink-0">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="savePackage" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{'opacity-50':saveLoading}">{{ saveLoading ? 'Saving...' : (selectedPackage?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>
    <ConfirmDialog :show="showDeleteModal" title="Delete Package" :message="`Delete package ${packageToDelete?.name}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { useApi } from '../composables/useApi'
import { useOptimistic } from '../composables/useOptimistic'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Packages',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest, invalidateCache } = useApi()
    const packages = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const categoryFilter = ref('')
    const tierFilter = ref('')
    const featuredFilter = ref('')
    const selectedIds = ref([])
    const activePkgSection = ref('basic')
    const showSales = ref(false)
    const analyticsData = ref(null)
    const analyticsPackage = ref('')
    const analyticsPeriod = ref('this_week')
    const analyticsCompare = ref('last_week')
    const hideRevenue = ref(true)
    const showAnalytics = ref(true)

    const periodOptions = [
      { value: 'this_week', label: 'This Week' },
      { value: 'this_month', label: 'This Month' },
      { value: 'this_quarter', label: 'This Quarter' },
      { value: 'this_year', label: 'This Year' },
    ]
    const compareOptions = [
      { value: '', label: 'None' },
      { value: 'last_week', label: 'Last Week' },
      { value: 'last_month', label: 'Last Month' },
      { value: 'last_quarter', label: 'Last Quarter' },
    ]
    const pOpen = reactive({ basic: true, pricing: true, technical: false, network: false, display: false, promotions: false, inventory: false, locations: false })
    const pkgSections = [
      { id: 'basic', label: '📝 Basic' },
      { id: 'pricing', label: '💰 Pricing' },
      { id: 'technical', label: '⚙️ Technical' },
      { id: 'network', label: '🌐 Network' },
      { id: 'display', label: '🎨 Display' },
      { id: 'promotions', label: '🎉 Promotions' },
      { id: 'inventory', label: '📦 Inventory' },
      { id: 'locations', label: '📍 Locations' }
    ]
    const pkgLocations = ref([])

    const fetchPkgLocations = async () => {
      try {
        const data = await makeRequest('get', 'suapi/locations/')
        pkgLocations.value = (data.results || data).map(l => ({ id: l.id, name: l.name, code: l.code }))
      } catch (e) { console.error(e) }
    }
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedPackage = ref(null)
    const packageToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({
      name: '',
      code: '',
      category: 'time_based_unlimited',
      tier: 'basic',
      price: 0,
      duration_hours: 1,
      speed_limit_mbps: 10,
      data_limit_mb: null,
      device_limit: 1,
      qos_priority: 'standard',
      description: '',
      is_active: true,
      is_public: true
    })

    const filteredPackages = computed(() => {
      let result = packages.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(p => p.name?.toLowerCase().includes(term) || p.code?.toLowerCase().includes(term) || p.description?.toLowerCase().includes(term))
      }
      if (statusFilter.value) result = result.filter(p => p.is_active === (statusFilter.value === 'true'))
      if (categoryFilter.value) result = result.filter(p => p.category === categoryFilter.value)
      if (tierFilter.value) result = result.filter(p => p.tier === tierFilter.value)
      if (featuredFilter.value) result = result.filter(p => p.is_featured === (featuredFilter.value === 'true'))
      return result
    })

    const maxSales = computed(() => Math.max(...(stats.value.package_sales || []).map(p => p.total_dispatched || 0), 1))

    const fetchAnalytics = async () => {
      try {
        const params = analyticsPackage.value ? `?package_id=${analyticsPackage.value}` : ''
        analyticsData.value = await makeRequest('get', `suapi/packages/analytics/${params}`)
      } catch (e) { console.error(e) }
    }

    const analyticsRows = computed(() => {
      if (!analyticsData.value) return []
      const current = analyticsData.value[analyticsPeriod.value] || []
      const prev = analyticsCompare.value ? (analyticsData.value[analyticsCompare.value] || []) : []
      return current.map(r => ({
        ...r,
        prev_sold: analyticsCompare.value ? (prev.find(p => p.code === r.code)?.sold ?? 0) : null
      }))
    })

    const totalSold = computed(() => analyticsRows.value.reduce((s, r) => s + r.sold, 0))

    const analyticsKpis = computed(() => {
      if (!analyticsData.value) return []
      const cur = analyticsData.value[analyticsPeriod.value] || []
      const prv = analyticsCompare.value ? (analyticsData.value[analyticsCompare.value] || []) : []
      const sum = (arr, key) => arr.reduce((s, r) => s + (r[key] || 0), 0)
      const pct = (a, b) => b > 0 ? Math.round((a - b) / b * 100) : null
      const curSold = sum(cur, 'sold'), prvSold = sum(prv, 'sold')
      const curRev = sum(cur, 'revenue'), prvRev = sum(prv, 'revenue')
      const curActive = sum(cur, 'active'), prvActive = sum(prv, 'active')
      const fmt = (n) => new Intl.NumberFormat().format(Math.round(n))
      return [
        { label: 'Vouchers Sold', icon: '🎫', current: curSold, prev: prvSold || null, change: pct(curSold, prvSold), bg: 'bg-blue-50 dark:bg-blue-500/10 border-blue-200 dark:border-blue-500/20', valueColor: 'text-blue-700 dark:text-blue-300', labelColor: 'text-blue-600 dark:text-blue-400', subColor: 'text-blue-400' },
        { label: 'Revenue Earned', icon: '💰', current: 'KSh ' + fmt(curRev), prev: prvRev ? 'KSh ' + fmt(prvRev) : null, change: pct(curRev, prvRev), bg: 'bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20', valueColor: 'text-emerald-700 dark:text-emerald-300', labelColor: 'text-emerald-600 dark:text-emerald-400', subColor: 'text-emerald-400', sensitive: true },
        { label: 'Currently Active', icon: '⚡', current: curActive, prev: prvActive || null, change: pct(curActive, prvActive), bg: 'bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20', valueColor: 'text-amber-700 dark:text-amber-300', labelColor: 'text-amber-600 dark:text-amber-400', subColor: 'text-amber-400' },
        { label: 'Packages Selling', icon: '📦', current: cur.length, prev: prv.length || null, change: pct(cur.length, prv.length), bg: 'bg-purple-50 dark:bg-purple-500/10 border-purple-200 dark:border-purple-500/20', valueColor: 'text-purple-700 dark:text-purple-300', labelColor: 'text-purple-600 dark:text-purple-400', subColor: 'text-purple-400' },
      ]
    })

    const toggleSelectAll = (e) => { selectedIds.value = e.target.checked ? filteredPackages.value.map(p => p.id) : [] }

    const bulkAction = async (action) => {
      if (!selectedIds.value.length) return
      try {
        await makeRequest('post', 'suapi/packages/bulk_action/', { action, ids: selectedIds.value })
        selectedIds.value = []
        await fetchPackages()
      } catch (e) { console.error(e) }
    }

    const duplicatePackage = async (pkg) => {
      try {
        await makeRequest('post', `suapi/packages/${pkg.id}/duplicate/`, {})
        await fetchPackages()
      } catch (e) { console.error(e) }
    }

    const syncSales = async () => {
      if (!selectedPackage.value?.id) return
      try {
        const res = await makeRequest('post', `suapi/packages/${selectedPackage.value.id}/sync_sales/`, {})
        selectedPackage.value.sold_quantity = res.sold_quantity
      } catch (e) { console.error(e) }
    }

    const fetchPackages = async () => {
      try {
        const data = await makeRequest('get', 'suapi/packages/')
        packages.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/packages/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchPackages(), fetchStats()])
    const { optimisticRemove } = useOptimistic(packages, fetchPackages, invalidateCache, 'suapi/packages')
    const formatNumber = (num) => new Intl.NumberFormat().format(num)
    const formatDuration = (duration) => {
      if (!duration) return 'N/A'
      const match = duration.match(/PT(\d+)H/)
      return match ? `${match[1]}h` : duration
    }
    const formatData = (mb) => {
      if (!mb) return 'Unlimited'
      if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`
      return `${mb} MB`
    }
    
    const openAddModal = () => {
      selectedPackage.value = null
      activePkgSection.value = 'basic'
      formData.value = { name: '', code: '', category: 'time_based_unlimited', tier: 'basic', price: 0, original_price: 0, duration_hours: 1, speed_limit_mbps: 10, data_limit_mb: null, device_limit: 1, qos_priority: 'standard', description: '', is_active: true, is_public: true, is_featured: false, allow_roaming: false, auto_renew: false, radius_group: '', display_order: 0, color_code: '', tags: [], tags_input: '', total_quantity: 0, promotion_start: '', promotion_end: '', locations: [] }
      fetchPkgLocations()
      showFormModal.value = true
    }

    const openEditModal = (pkg) => {
      selectedPackage.value = pkg
      activePkgSection.value = 'basic'
      formData.value = {
        name: pkg.name || '', code: pkg.code || '', category: pkg.category || 'time_based_unlimited',
        tier: pkg.tier || 'basic', price: pkg.price || 0, original_price: pkg.original_price || 0,
        duration_hours: pkg.duration_hours || 1, speed_limit_mbps: pkg.speed_limit_mbps || 10,
        data_limit_mb: pkg.data_limit_mb || null, device_limit: pkg.device_limit || 1,
        qos_priority: pkg.qos_priority || 'standard', description: pkg.description || '',
        is_active: pkg.is_active ?? true, is_public: pkg.is_public ?? true,
        is_featured: pkg.is_featured || false, allow_roaming: pkg.allow_roaming || false,
        auto_renew: pkg.auto_renew || false, radius_group: pkg.radius_group || '',
        display_order: pkg.display_order || 0, color_code: pkg.color_code || '',
        tags: pkg.tags || [], tags_input: Array.isArray(pkg.tags) ? pkg.tags.join(', ') : '',
        total_quantity: pkg.total_quantity || 0,
        promotion_start: pkg.promotion_start ? pkg.promotion_start.slice(0,16) : '',
        promotion_end: pkg.promotion_end ? pkg.promotion_end.slice(0,16) : '',
        locations: (pkg.locations || []).map(l => typeof l === 'object' ? l.id : l)
      }
      fetchPkgLocations()
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedPackage.value = null
      formData.value = {
        name: '',
        price: 0,
        data_limit_gb: 0,
        validity_days: 0,
        description: '',
        is_active: true
      }
    }

    const savePackage = async () => {
      saveLoading.value = true
      try {
        const payload = { ...formData.value }
        payload.duration = `PT${payload.duration_hours}H`
        delete payload.duration_hours
        // Convert tags_input string to array
        if (payload.tags_input !== undefined) {
          payload.tags = payload.tags_input ? payload.tags_input.split(',').map(t => t.trim()).filter(Boolean) : []
          delete payload.tags_input
        }
        
        if (selectedPackage.value?.id) {
          await makeRequest('patch', `suapi/packages/${selectedPackage.value.id}/`, payload)
        } else {
          await makeRequest('post', 'suapi/packages/', payload)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || JSON.stringify(err.response?.data) || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const openDeleteModal = (pkg) => { packageToDelete.value = pkg; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; packageToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      const id = packageToDelete.value.id
      optimisticRemove(id)
      closeDeleteModal()
      try {
        await makeRequest('delete', `suapi/packages/${id}/`)
      } catch (err) {
        await refreshData() // rollback
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    onMounted(() => { refreshData(); fetchAnalytics() })

    return {
      loading, error, packages, stats, searchTerm, statusFilter, categoryFilter, tierFilter, featuredFilter,
      selectedIds, activePkgSection, pkgSections, pOpen,
      showFormModal, showDeleteModal, selectedPackage, packageToDelete,
      saveLoading, deleteLoading, formData, filteredPackages, fetchPackages, refreshData,
      formatNumber, formatDuration, formatData,
      toggleSelectAll, bulkAction, duplicatePackage, syncSales, pkgLocations, showSales, maxSales, analyticsData, analyticsPackage, analyticsPeriod, analyticsCompare, periodOptions, compareOptions, hideRevenue, showAnalytics, fetchAnalytics, analyticsRows, totalSold, analyticsKpis,
      pkgLocations,
      openAddModal, openEditModal, closeFormModal, savePackage, openDeleteModal, closeDeleteModal, confirmDelete
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

<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Vouchers</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage dispatch vouchers</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Voucher
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load vouchers</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchVouchers" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Total</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_vouchers || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Active</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.active_vouchers || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl">
        <span class="text-[10px] text-amber-600 dark:text-amber-400 font-medium">Expired</span>
        <span class="text-sm font-bold text-amber-700 dark:text-amber-300">{{ stats.expired_vouchers || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 rounded-xl">
        <span class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">Revenue</span>
        <span class="text-sm font-bold text-purple-700 dark:text-purple-300" :class="hideRevenue ? 'blur-sm select-none' : ''">KSh {{ formatNumber(stats.total_revenue || 0) }}</span>
        <button @click="hideRevenue=!hideRevenue" class="text-slate-400 hover:text-slate-600">
          <svg v-if="hideRevenue" class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
          <svg v-else class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-5 0-9.27-3.11-11-7.5a10.05 10.05 0 012.38-3.88M1 1l22 22"/></svg>
        </button>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-2 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2 flex-wrap">
        <div class="flex-1 min-w-48">
          <input v-model="searchTerm" type="text" placeholder="Search code, user, account..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="suspended">Suspended</option>
          <option value="cancelled">Cancelled</option>
          <option value="exhausted">Exhausted</option>
        </select>
        <select v-model="roamingFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Roaming</option>
          <option value="true">Roaming</option>
          <option value="false">Home</option>
        </select>
        <select v-model="expiryFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Expiry</option>
          <option value="24h">Expiring 24h</option>
          <option value="7d">Expiring 7d</option>
        </select>
      </div>

      <!-- Bulk Actions -->
      <div v-if="selectedIds.length" class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
        <span class="text-xs text-blue-700 dark:text-blue-400 font-medium">{{ selectedIds.length }} selected</span>
        <button @click="bulkAction('suspend')" class="px-2 py-1 text-[10px] font-medium rounded bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 hover:bg-amber-200">Suspend</button>
        <button @click="bulkAction('reactivate')" class="px-2 py-1 text-[10px] font-medium rounded bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200">Reactivate</button>
        <button @click="bulkAction('cancel')" class="px-2 py-1 text-[10px] font-medium rounded bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400 hover:bg-red-200">Cancel</button>
        <button @click="exportSelected" class="px-2 py-1 text-[10px] font-medium rounded bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 hover:bg-blue-200">Export CSV</button>
        <button @click="selectedIds = []" class="ml-auto text-[10px] text-slate-500 hover:text-slate-700">Clear</button>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 w-6"><input type="checkbox" @change="toggleSelectAll" :checked="selectedIds.length === filteredVouchers.length && filteredVouchers.length > 0" class="rounded" /></th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Voucher Code</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Account</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Package</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Price</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Usage %</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Activated</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Expires</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Roaming</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="voucher in filteredVouchers" :key="voucher.id" @click="openEditModal(voucher)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2" @click.stop><input type="checkbox" :value="voucher.id" v-model="selectedIds" class="rounded" /></td>
                <td class="px-3 py-2">
                  <p class="text-xs font-medium text-slate-900 dark:text-white font-mono">{{ voucher.voucher_code }}</p>
                  <p class="text-[10px] text-slate-500 dark:text-slate-400">Sessions: {{ voucher.session_count || 0 }}</p>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ voucher.user_username || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ voucher.package_name || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs font-semibold text-slate-900 dark:text-white">KSh {{ formatNumber(voucher.price_paid) }}</td>
                <td class="px-3 py-2">
                  <div class="w-20">
                    <div class="flex justify-between text-[10px] text-slate-500 dark:text-slate-400 mb-0.5">
                      <span>{{ usagePct(voucher) }}%</span>
                      <span>{{ formatBytes(voucher.total_usage_mb * 1024 * 1024) }}</span>
                    </div>
                    <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1">
                      <div class="h-1 rounded-full" :class="usagePct(voucher) > 80 ? 'bg-red-500' : usagePct(voucher) > 50 ? 'bg-amber-500' : 'bg-emerald-500'" :style="{width: usagePct(voucher) + '%'}"></div>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getStatusBadge(voucher.status)">{{ voucher.status }}</span>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatDate(voucher.activated_at) }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatDate(voucher.expires_at) }}</td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] rounded-full" :class="voucher.is_roaming ? 'bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'">{{ voucher.is_roaming ? 'Roaming' : 'Home' }}</span>
                </td>
                <td class="px-3 py-2 text-right">
                  <button @click.stop="openDeleteModal(voucher)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                    <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[88vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700 shrink-0">
          <div>
            <h2 class="text-sm font-semibold text-slate-900 dark:text-white font-mono">{{ selectedVoucher?.voucher_code || 'New Voucher' }}</h2>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ selectedVoucher?.user_username || '' }} · {{ selectedVoucher?.package_name || '' }}</p>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="selectedVoucher?.id" class="px-2 py-0.5 text-[10px] rounded-full" :class="getStatusBadge(selectedVoucher.status)">{{ selectedVoucher.status }}</span>
            <button @click="closeFormModal" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"><svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>
          </div>
        </div>
        <!-- Body -->
        <div class="flex flex-1 overflow-hidden">
          <!-- Sidebar -->
          <div class="w-44 shrink-0 border-r border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 overflow-y-auto p-3 space-y-1">
            <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide px-1 mb-1">Sections</p>
            <button v-for="s in voucherSections" :key="s.id" @click="activeVoucherSection = s.id" class="w-full text-left px-2.5 py-2 text-xs rounded-lg transition-colors" :class="activeVoucherSection === s.id ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 font-medium' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'">{{ s.label }}</button>
            <div v-if="selectedVoucher?.id" class="pt-2 mt-2 border-t border-slate-200 dark:border-slate-700 space-y-1.5">
              <button @click="quickAction('suspend')" class="w-full text-left px-2.5 py-1.5 text-xs rounded-lg bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 hover:bg-amber-100">⚠️ Suspend</button>
              <button @click="quickAction('reactivate')" class="w-full text-left px-2.5 py-1.5 text-xs rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100">✅ Reactivate</button>
              <button @click="quickAction('cancel')" class="w-full text-left px-2.5 py-1.5 text-xs rounded-lg bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 hover:bg-red-100">🚫 Cancel</button>
            </div>
          </div>
          <!-- Right panel -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">

            <!-- 1. Voucher Info -->
            <div v-show="activeVoucherSection === 'info'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="vOpen.info=!vOpen.info" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Voucher Information</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="vOpen.info?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="vOpen.info" class="p-4 grid grid-cols-2 gap-3 text-xs">
                <div><span class="text-slate-500 dark:text-slate-400">Voucher Code</span><p class="font-mono font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedVoucher?.voucher_code || 'Auto-generated' }}</p></div>
                <div><span class="text-slate-500 dark:text-slate-400">Status</span><p class="mt-0.5"><span class="px-2 py-0.5 rounded-full text-[10px]" :class="getStatusBadge(formData.status)">{{ formData.status }}</span></p></div>
                <div class="col-span-2">
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Status</label>
                  <select v-model="formData.status" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="active">Active</option>
                    <option value="suspended">Suspended</option>
                    <option value="cancelled">Cancelled</option>
                    <option value="expired">Expired</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Client <span class="text-red-500">*</span></label>
                  <select v-model="formData.user" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="">Select client...</option>
                    <option v-for="c in formOptions.clients" :key="c.id" :value="c.id">{{ c.account }} — {{ c.user__username }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Package <span class="text-red-500">*</span></label>
                  <select v-model="formData.package" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="">Select package...</option>
                    <option v-for="p in formOptions.packages" :key="p.id" :value="p.id">{{ p.name }} — KSh {{ p.price }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Location <span class="text-red-500">*</span></label>
                  <select v-model="formData.location" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="">Select location...</option>
                    <option v-for="l in formOptions.locations" :key="l.id" :value="l.id">{{ l.name }} ({{ l.code }})</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Status</label>
                  <select v-model="formData.status" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="active">Active</option>
                    <option value="suspended">Suspended</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- 2. Purchase Details -->
            <div v-show="activeVoucherSection === 'purchase'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="vOpen.purchase=!vOpen.purchase" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Purchase Details</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="vOpen.purchase?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="vOpen.purchase" class="p-4 grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Price Paid (KSh)</label>
                  <input v-model="formData.price_paid" type="number" step="0.01" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Transaction ID</label>
                  <input v-model="formData.transaction_id" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Payment Reference</label>
                  <input v-model="formData.payment_reference" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Expires At</label>
                  <input v-model="formData.expires_at" type="datetime-local" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div v-if="selectedVoucher?.id" class="text-xs"><span class="text-slate-500 dark:text-slate-400">Activated</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(selectedVoucher.activated_at) }}</p></div>
              </div>
            </div>

            <!-- 3. Usage Tracking -->
            <div v-show="activeVoucherSection === 'usage'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="vOpen.usage=!vOpen.usage" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Usage Tracking</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="vOpen.usage?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="vOpen.usage" class="p-4 space-y-3 text-xs">
                <div class="grid grid-cols-3 gap-2">
                  <div class="p-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg text-center"><p class="text-[10px] text-blue-600 dark:text-blue-400">Download</p><p class="font-bold text-blue-700 dark:text-blue-300">{{ formatBytes(selectedVoucher?.download_bytes) }}</p></div>
                  <div class="p-2 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg text-center"><p class="text-[10px] text-emerald-600 dark:text-emerald-400">Upload</p><p class="font-bold text-emerald-700 dark:text-emerald-300">{{ formatBytes(selectedVoucher?.upload_bytes) }}</p></div>
                  <div class="p-2 bg-purple-50 dark:bg-purple-500/10 rounded-lg text-center"><p class="text-[10px] text-purple-600 dark:text-purple-400">Sessions</p><p class="font-bold text-purple-700 dark:text-purple-300">{{ selectedVoucher?.session_count || 0 }}</p></div>
                </div>
                <div>
                  <div class="flex justify-between mb-1"><span class="text-slate-500 dark:text-slate-400">Usage</span><span class="font-medium text-slate-900 dark:text-white">{{ usagePct(selectedVoucher) }}%</span></div>
                  <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                    <div class="h-2 rounded-full transition-all" :class="usagePct(selectedVoucher) > 80 ? 'bg-red-500' : usagePct(selectedVoucher) > 50 ? 'bg-amber-500' : 'bg-emerald-500'" :style="{width: usagePct(selectedVoucher) + '%'}"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 4. Device Management -->
            <div v-show="activeVoucherSection === 'devices'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="vOpen.devices=!vOpen.devices" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Device Management</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="vOpen.devices?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="vOpen.devices" class="p-4 space-y-3">
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Concurrent Sessions</label>
                  <input v-model="formData.concurrent_sessions" type="number" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Allowed MAC Addresses (one per line)</label>
                  <textarea v-model="macInput" rows="3" placeholder="AA:BB:CC:DD:EE:FF" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-mono"></textarea>
                </div>
              </div>
            </div>

            <!-- 5. Roaming -->
            <div v-show="activeVoucherSection === 'roaming'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="vOpen.roaming=!vOpen.roaming" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Roaming</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="vOpen.roaming?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="vOpen.roaming" class="p-4 space-y-3">
                <label class="flex items-center gap-3 cursor-pointer">
                  <input v-model="formData.is_roaming" type="checkbox" class="w-4 h-4 text-blue-600 rounded" />
                  <div><p class="text-xs font-medium text-slate-900 dark:text-white">Is Roaming</p><p class="text-[10px] text-slate-500 dark:text-slate-400">Voucher is being used outside home location.</p></div>
                </label>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Home Location</label>
                  <select v-model="formData.home_location" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option :value="null">None</option>
                    <option v-for="l in formOptions.locations" :key="l.id" :value="l.id">{{ l.name }} ({{ l.code }})</option>
                  </select>
                </div>
              </div>
            </div>

          </div>
        </div>
        <div class="flex items-center justify-end gap-2 px-5 py-3 border-t border-slate-200 dark:border-slate-700 shrink-0">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveVoucher" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{'opacity-50':saveLoading}">{{ saveLoading ? 'Saving...' : (selectedVoucher?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog :show="showDeleteModal" title="Delete Voucher" :message="`Delete voucher ${voucherToDelete?.voucher_code}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { useApi } from '../composables/useApi'
import { useOptimistic } from '../composables/useOptimistic'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Vouchers',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest, invalidateCache } = useApi()
    const vouchers = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const roamingFilter = ref('')
    const hideRevenue = ref(true)
    const expiryFilter = ref('')
    const selectedIds = ref([])
    const activeVoucherSection = ref('info')
    const macInput = ref('')
    const vOpen = reactive({ info: true, purchase: true, usage: true, devices: false, roaming: false })
    const voucherSections = [
      { id: 'info', label: '🎫 Voucher Info' },
      { id: 'purchase', label: '💰 Purchase' },
      { id: 'usage', label: '📊 Usage' },
      { id: 'devices', label: '📱 Devices' },
      { id: 'roaming', label: '🌐 Roaming' }
    ]
    const formOptions = ref({ clients: [], packages: [], locations: [] })

    const fetchFormOptions = async () => {
      try {
        formOptions.value = await makeRequest('get', 'suapi/vouchers/form_options/')
      } catch (e) { console.error('form options failed', e) }
    }
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedVoucher = ref(null)
    const voucherToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({ user: '', package: '', price_paid: 0, expires_at: '', status: 'active', transaction_id: '', payment_reference: '', concurrent_sessions: 0, is_roaming: false, home_location: null })

    const usagePct = (v) => {
      if (!v || !v.total_usage_mb) return 0
      const packageMb = v.package_data_limit_mb || 0
      if (!packageMb) return 0
      return Math.min(100, Math.round((v.total_usage_mb / packageMb) * 100))
    }

    const toggleSelectAll = (e) => {
      selectedIds.value = e.target.checked ? filteredVouchers.value.map(v => v.id) : []
    }

    const bulkAction = async (action) => {
      if (!selectedIds.value.length) return
      try {
        await makeRequest('post', 'suapi/vouchers/bulk_action/', { action, ids: selectedIds.value })
        selectedIds.value = []
        await fetchVouchers()
      } catch (e) { console.error(e) }
    }

    const quickAction = async (action) => {
      const newStatus = action === 'suspend' ? 'suspended' : action === 'reactivate' ? 'active' : 'cancelled'
      optimisticUpdate(selectedVoucher.value.id, { status: newStatus })
      selectedVoucher.value.status = newStatus
      try {
        await makeRequest('post', `suapi/vouchers/${selectedVoucher.value.id}/${action}/`, {})
      } catch (e) {
        await refreshData() // rollback
        console.error(e)
      }
    }

    const exportSelected = () => {
      const rows = vouchers.value.filter(v => selectedIds.value.includes(v.id))
      const csv = ['code,user,package,status,price,activated,expires'].concat(
        rows.map(v => `${v.voucher_code},${v.user_username},${v.package_name},${v.status},${v.price_paid},${v.activated_at},${v.expires_at}`)
      ).join('\n')
      const a = document.createElement('a'); a.href = 'data:text/csv,' + encodeURIComponent(csv); a.download = 'vouchers.csv'; a.click()
    }

    const filteredVouchers = computed(() => {
      let result = vouchers.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(v => v.user_username?.toLowerCase().includes(term) || v.package_name?.toLowerCase().includes(term) || v.voucher_code?.toLowerCase().includes(term))
      }
      if (statusFilter.value) result = result.filter(v => v.status === statusFilter.value)
      if (roamingFilter.value) result = result.filter(v => String(v.is_roaming) === roamingFilter.value)
      if (expiryFilter.value) {
        const now = new Date()
        const h = expiryFilter.value === '24h' ? 24 : 168
        result = result.filter(v => v.expires_at && new Date(v.expires_at) > now && (new Date(v.expires_at) - now) / 3600000 <= h)
      }
      return result
    })

    const fetchVouchers = async () => {
      try {
        const data = await makeRequest('get', 'suapi/vouchers/')
        vouchers.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/vouchers/stats/')
      } catch (err) { console.error('Error:', err) }
    }

    const refreshData = () => Promise.all([fetchVouchers(), fetchStats()])
    const { optimisticRemove, optimisticUpdate } = useOptimistic(vouchers, fetchVouchers, invalidateCache, 'suapi/vouchers')
    const formatNumber = (num) => new Intl.NumberFormat().format(num || 0)
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
    const formatBytes = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }
    
    const openAddModal = () => {
      selectedVoucher.value = null
      activeVoucherSection.value = 'info'
      macInput.value = ''
      formData.value = { user: '', package: '', location: '', price_paid: 0, expires_at: '', status: 'active', transaction_id: '', payment_reference: '', concurrent_sessions: 0, is_roaming: false, home_location: null }
      fetchFormOptions()
      showFormModal.value = true
    }

    const openEditModal = (voucher) => {
      selectedVoucher.value = voucher
      activeVoucherSection.value = 'info'
      macInput.value = (voucher.allowed_mac_addresses || []).join('\n')
      formData.value = {
        user: voucher.user || '', package: voucher.package || '', location: voucher.location || '',
        price_paid: voucher.price_paid || 0, expires_at: voucher.expires_at ? voucher.expires_at.slice(0,16) : '',
        status: voucher.status || 'active', transaction_id: voucher.transaction_id || '',
        payment_reference: voucher.payment_reference || '',
        concurrent_sessions: voucher.concurrent_sessions || 0,
        is_roaming: voucher.is_roaming || false, home_location: voucher.home_location || null
      }
      fetchFormOptions()
      showFormModal.value = true
    }

    const closeFormModal = () => {
      showFormModal.value = false
      selectedVoucher.value = null
      formData.value = { user: '', package: '', location: '', price_paid: 0, expires_at: '', status: 'active', transaction_id: '', payment_reference: '', concurrent_sessions: 0, is_roaming: false, home_location: null }
    }

    const saveVoucher = async () => {
      saveLoading.value = true
      try {
        if (selectedVoucher.value?.id) {
          await makeRequest('patch', `suapi/vouchers/${selectedVoucher.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/vouchers/', formData.value)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const openDeleteModal = (voucher) => { voucherToDelete.value = voucher; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; voucherToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      const id = voucherToDelete.value.id
      optimisticRemove(id)
      closeDeleteModal()
      try {
        await makeRequest('delete', `suapi/vouchers/${id}/`)
      } catch (err) {
        await refreshData() // rollback
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const getStatusBadge = (status) => {
      const badges = {
        'active': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'expired': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'exhausted': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400',
        'suspended': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400',
        'cancelled': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'
      }
      return badges[status] || badges.suspended
    }

    onMounted(refreshData)

    return {
      loading, error, vouchers, stats, searchTerm, statusFilter, roamingFilter, expiryFilter, hideRevenue,
      selectedIds, activeVoucherSection, voucherSections, vOpen, macInput, formOptions,
      showFormModal, showDeleteModal, selectedVoucher, voucherToDelete,
      saveLoading, deleteLoading, formData, filteredVouchers, fetchVouchers, refreshData,
      formatNumber, formatDate, formatBytes, usagePct, toggleSelectAll, bulkAction, quickAction, exportSelected,
      openAddModal, openEditModal, closeFormModal, saveVoucher, openDeleteModal, closeDeleteModal, confirmDelete, getStatusBadge
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

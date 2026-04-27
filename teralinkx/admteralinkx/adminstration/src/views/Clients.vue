<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Clients</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage client accounts</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="showAddModal = true" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Client
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load clients</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchClients" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Total</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_clients || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-xl">
        <span class="text-[10px] text-rose-600 dark:text-rose-400 font-medium">⚠️ At-Risk</span>
        <span class="text-sm font-bold text-rose-700 dark:text-rose-300">{{ stats.at_risk_clients || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-200 dark:border-cyan-500/20 rounded-xl">
        <div class="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-pulse"></div>
        <span class="text-[10px] text-cyan-600 dark:text-cyan-400 font-medium">Active</span>
        <span class="text-sm font-bold text-cyan-700 dark:text-cyan-300">{{ stats.active_clients || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl">
        <span class="text-[10px] text-amber-600 dark:text-amber-400 font-medium">Suspended</span>
        <span class="text-sm font-bold text-amber-700 dark:text-amber-300">{{ stats.suspended_clients || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">New (7d)</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.new_clients_7d || 0 }}</span>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search by username, phone, or account..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>
        <select v-model="tierFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Tiers</option>
          <option value="basic">Basic</option>
          <option value="premium">Premium</option>
          <option value="business">Business</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <select v-model="churnFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Risk</option>
          <option value="high">High Risk (&gt;0.7)</option>
          <option value="medium">Medium Risk</option>
          <option value="low">Low Risk</option>
        </select>
        <select v-model="rewardTierFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Rewards</option>
          <option value="bronze">Bronze</option>
          <option value="silver">Silver</option>
          <option value="gold">Gold</option>
          <option value="platinum">Platinum</option>
        </select>
        <select v-model="twoFactorFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All 2FA</option>
          <option value="true">2FA On</option>
          <option value="false">2FA Off</option>
        </select>
        <select v-model="homeLocationFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Locations</option>
          <option v-for="loc in locationOptions" :key="loc.id" :value="String(loc.id)">{{ loc.name }}</option>
        </select>
      </div>

      <!-- Bulk Actions -->
      <div v-if="selectedIds.length > 0" class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-lg">
        <span class="text-xs font-medium text-blue-700 dark:text-blue-400">{{ selectedIds.length }} selected</span>
        <button @click="bulkAction('suspend')" class="px-2 py-1 text-[10px] font-medium rounded bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 hover:bg-amber-200">Suspend</button>
        <button @click="bulkAction('activate')" class="px-2 py-1 text-[10px] font-medium rounded bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200">Activate</button>
        <button @click="bulkAction('reset_logins')" class="px-2 py-1 text-[10px] font-medium rounded bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200">Reset Logins</button>
        <button @click="bulkAction('terminate_sessions')" class="px-2 py-1 text-[10px] font-medium rounded bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400 hover:bg-red-200">Terminate Sessions</button>
        <button @click="bulkAction('upgrade_premium')" class="px-2 py-1 text-[10px] font-medium rounded bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 hover:bg-purple-200">⬆ Premium</button>
        <button @click="bulkAction('downgrade_basic')" class="px-2 py-1 text-[10px] font-medium rounded bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200">⬇ Basic</button>
        <button @click="exportSelected" class="px-2 py-1 text-[10px] font-medium rounded bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 hover:bg-blue-200">Export CSV</button>
        <button @click="selectedIds = []" class="ml-auto text-[10px] text-slate-500 hover:text-slate-700">Clear</button>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 w-6"><input type="checkbox" @change="toggleSelectAll" :checked="selectedIds.length === filteredClients.length && filteredClients.length > 0" class="rounded" /></th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Client</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Contact</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Tier</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Balance</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Credit</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Reward</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Devices</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Sessions</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">2FA</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Voucher</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Last Seen</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="client in filteredClients" :key="client.id" @click="viewClient(client)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2" @click.stop>
                  <input type="checkbox" :value="client.id" v-model="selectedIds" class="rounded" />
                </td>
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div v-if="client.profile_image" class="w-7 h-7 rounded-full overflow-hidden flex-shrink-0">
                      <img :src="client.profile_image" alt="Profile" class="w-full h-full object-cover" @error="handleImageError" />
                    </div>
                    <div v-else class="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center flex-shrink-0">
                      <svg class="w-4 h-4 text-slate-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                    </div>
                    <div>
                      <div class="flex items-center gap-1">
                        <p class="text-xs font-medium text-slate-900 dark:text-white">{{ client.user_username }}</p>
                        <span v-if="client.churn_score" class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="client.churn_score > 0.7 ? 'bg-rose-500' : client.churn_score > 0.3 ? 'bg-amber-500' : 'bg-emerald-500'" :title="'Churn risk: ' + (client.churn_score * 100).toFixed(0) + '%'"></span>
                      </div>
                      <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ client.account }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-2">
                  <p class="text-xs text-slate-900 dark:text-white">{{ client.phone_number || 'N/A' }}</p>
                  <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ client.user_email || 'No email' }}</p>
                </td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getTierBadge(client.account_tier)">{{ client.account_tier }}</span>
                </td>
                <td class="px-3 py-2">
                  <p class="text-xs font-semibold text-slate-900 dark:text-white">KSh {{ formatNumber(client.balance) }}</p>
                </td>
                <td class="px-3 py-2">
                  <p class="text-xs text-slate-900 dark:text-white">KSh {{ formatNumber(client.credit_limit || 0) }}</p>
                </td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full capitalize"
                    :class="client.reward_tier==='gold'?'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400':client.reward_tier==='silver'?'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300':client.reward_tier==='platinum'?'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400':'bg-orange-100 dark:bg-orange-500/20 text-orange-700 dark:text-orange-400'">
                    {{ client.reward_tier || 'bronze' }}
                  </span>
                </td>
                <td class="px-3 py-2">
                  <span class="text-xs font-medium" :class="(client.active_devices_count||0) > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'">{{ client.active_devices_count || 0 }}</span>
                </td>
                <td class="px-3 py-2">
                  <span class="text-xs font-medium" :class="(client.active_sessions_count||0) > 0 ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'">{{ client.active_sessions_count || 0 }}</span>
                </td>
                <td class="px-3 py-2">
                  <span class="text-[10px] font-medium" :class="client.two_factor_enabled ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'">{{ client.two_factor_enabled ? '✓ On' : 'Off' }}</span>
                </td>
                <td class="px-3 py-2">
                  <span v-if="client.active_voucher" class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" :title="client.active_voucher">Active</span>
                  <span v-else class="text-[10px] text-slate-400">—</span>
                </td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getStatusBadge(client.status)">{{ client.status }}</span>
                </td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(client.last_seen) }}</td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="viewClient(client)" class="p-1 hover:bg-slate-100 dark:hover:bg-slate-600 rounded" title="View">
                      <svg class="w-3.5 h-3.5 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    </button>
                    <button @click.stop="quickToggleSuspend(client)" class="p-1 rounded" :class="client.status === 'suspended' ? 'hover:bg-emerald-100 dark:hover:bg-emerald-600' : 'hover:bg-amber-100 dark:hover:bg-amber-600'" :title="client.status === 'suspended' ? 'Activate' : 'Suspend'">
                      <svg class="w-3.5 h-3.5" :class="client.status === 'suspended' ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                    </button>
                    <button @click.stop="deleteClient(client)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Client Detail Modal -->
    <ClientDetailModal :show="showDetailModal" :client="selectedClient" @close="showDetailModal = false" @refresh="refreshData" />

    <!-- Add/Edit Client Modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-xl font-semibold text-slate-900 dark:text-white">Add New Client</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Username</label>
              <input v-model="formData.username" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Email</label>
              <input v-model="formData.email" type="email" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Phone Number</label>
              <input v-model="formData.phone_number" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Display Name</label>
              <input v-model="formData.display_name" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Account Tier</label>
              <select v-model="formData.account_tier" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm">
                <option value="basic">Basic</option>
                <option value="premium">Premium</option>
                <option value="business">Business</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Status</label>
              <select v-model="formData.status" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Balance</label>
              <input v-model="formData.balance" type="number" step="0.01" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Credit Limit</label>
              <input v-model="formData.credit_limit" type="number" step="0.01" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm">Cancel</button>
          <button @click="saveClient" class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useOptimistic } from '../composables/useOptimistic'
import ModernMetricCard from '../components/MetricCard.vue'
import ClientDetailModal from '../components/ClientDetailModal.vue'

export default {
  name: 'Clients',
  components: { ModernMetricCard, ClientDetailModal },
  setup() {
    const { loading, error, makeRequest, invalidateCache } = useApi()
    const clients = ref([])
    const stats = ref({ total_clients: 0, active_clients: 0, premium_clients: 0, new_clients_7d: 0, total_balance: 0 })
    const searchTerm = ref('')
    const statusFilter = ref('')
    const tierFilter = ref('')
    const churnFilter = ref('')
    const rewardTierFilter = ref('')
    const twoFactorFilter = ref('')
    const homeLocationFilter = ref('')
    const locationOptions = ref([])
    const selectedIds = ref([])
    const showAddModal = ref(false)
    const showDetailModal = ref(false)
    const selectedClient = ref(null)
    const formData = ref({
      username: '',
      email: '',
      phone_number: '',
      display_name: '',
      account_tier: 'basic',
      status: 'active',
      balance: 0,
      credit_limit: 0
    })

    const filteredClients = computed(() => {
      let result = clients.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(c => 
          c.user_username?.toLowerCase().includes(term) || 
          c.phone_number?.includes(term) ||
          c.account?.toLowerCase().includes(term)
        )
      }
      if (statusFilter.value) {
        result = result.filter(c => c.status === statusFilter.value)
      }
      if (tierFilter.value) {
        result = result.filter(c => c.account_tier === tierFilter.value)
      }
      if (churnFilter.value === 'high') result = result.filter(c => (c.churn_score || 0) > 0.7)
      else if (churnFilter.value === 'medium') result = result.filter(c => (c.churn_score || 0) > 0.3 && (c.churn_score || 0) <= 0.7)
      else if (churnFilter.value === 'low') result = result.filter(c => (c.churn_score || 0) <= 0.3)
      if (rewardTierFilter.value) result = result.filter(c => c.reward_tier === rewardTierFilter.value)
      if (twoFactorFilter.value !== '') result = result.filter(c => String(c.two_factor_enabled) === twoFactorFilter.value)
      if (homeLocationFilter.value) result = result.filter(c => String(c.home_location) === homeLocationFilter.value)
      return result
    })

    const fetchClients = async () => {
      try {
        const data = await makeRequest('get', 'suapi/clients/')
        clients.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        const data = await makeRequest('get', 'suapi/clients/stats/')
        stats.value = data || stats.value
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchClients(), fetchStats()])

    const fetchLocationOptions = async () => {
      try {
        const data = await makeRequest('get', 'suapi/locations/')
        locationOptions.value = (data.results || data).map(l => ({ id: l.id, name: l.name }))
      } catch (e) { console.error(e) }
    }
    const { optimisticRemove, optimisticUpdate } = useOptimistic(clients, fetchClients, invalidateCache, 'suapi/clients')
    
    const viewClient = (client) => {
      selectedClient.value = client
      showDetailModal.value = true
    }

    const deleteClient = async (client) => {
      if (!confirm(`Delete client ${client.user_username}? This cannot be undone.`)) return
      optimisticRemove(client.id)
      try {
        await makeRequest('delete', `suapi/clients/${client.id}/`)
      } catch (err) {
        await refreshData() // rollback
        const msg = err.response?.data?.detail || err.response?.data?.error || 'Delete failed — client may have active sessions or vouchers'
        alert(msg)
      }
    }

    const saveClient = async () => {
      try {
        await makeRequest('post', 'suapi/clients/', formData.value)
        closeFormModal()
        await refreshData()
      } catch (err) {
        console.error('Error saving client:', err)
        alert('Failed to save client')
      }
    }

    const closeFormModal = () => {
      showAddModal.value = false
      formData.value = {
        username: '',
        email: '',
        phone_number: '',
        display_name: '',
        account_tier: 'basic',
        status: 'active',
        balance: 0,
        credit_limit: 0
      }
    }
    
    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }

    const getTierBadge = (tier) => {
      const badges = {
        'basic': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300',
        'premium': 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400',
        'business': 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        'enterprise': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400'
      }
      return badges[tier] || badges.basic
    }

    const getStatusBadge = (status) => {
      const badges = {
        'active': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'inactive': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400',
        'suspended': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400',
        'banned': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
      }
      return badges[status] || badges.inactive
    }

    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num || 0)
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString()
    }

    const handleImageError = (event) => {
      event.target.parentElement.innerHTML = `
        <svg class="w-4 h-4 text-slate-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
      `
    }

    const toggleSelectAll = () => {
      if (selectedIds.value.length === filteredClients.value.length) {
        selectedIds.value = []
      } else {
        selectedIds.value = filteredClients.value.map(c => c.id)
      }
    }

    const quickToggleSuspend = async (client) => {
      const action = client.status === 'suspended' ? 'activate' : 'suspend'
      const newStatus = action === 'suspend' ? 'suspended' : 'active'
      optimisticUpdate(client.id, { status: newStatus })
      try {
        await makeRequest('post', `suapi/clients/${client.id}/${action}/`, { reason: 'Admin quick action' }, false)
      } catch (err) {
        await refreshData() // rollback
        alert(err.response?.data?.error || `${action} failed`)
      }
    }

    const bulkAction = async (action) => {
      if (!selectedIds.value.length) return
      if (!confirm(`Apply '${action}' to ${selectedIds.value.length} clients?`)) return
      try {
        await makeRequest('post', 'suapi/clients/bulk_action/', { ids: selectedIds.value, action })
        selectedIds.value = []
        await refreshData()
      } catch (err) { console.error(err) }
    }

    const exportSelected = () => {
      const data = filteredClients.value.filter(c => selectedIds.value.includes(c.id))
      const headers = ['Account', 'Username', 'Phone', 'Email', 'Tier', 'Status', 'Balance', 'Joined']
      const rows = data.map(c => [c.account, c.user_username, c.phone_number, c.user_email, c.account_tier, c.status, c.balance, c.created_at])
      const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
      const a = document.createElement('a')
      a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
      a.download = `clients_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
    }

    onMounted(() => { refreshData(); fetchLocationOptions() })

    return {
      loading, error, clients, stats, searchTerm, statusFilter, tierFilter, churnFilter, rewardTierFilter, twoFactorFilter, homeLocationFilter, locationOptions, selectedIds,
      filteredClients, fetchClients, refreshData,
      showAddModal, showDetailModal, selectedClient, formData,
      viewClient, deleteClient, saveClient, closeFormModal,
      toggleSelectAll, quickToggleSuspend, bulkAction, exportSelected,
      getInitials, getTierBadge, getStatusBadge, formatNumber, formatDate, handleImageError
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

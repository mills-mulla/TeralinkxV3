<template>
  <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[88vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700 shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center" v-html="getUserIcon()"></div>
          <div>
            <h2 class="text-sm font-semibold text-slate-900 dark:text-white">{{ client.user_username }}</h2>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ client.account }} · {{ client.phone_number }}</p>
          </div>
          <span class="px-2 py-0.5 text-[10px] rounded-full" :class="getStatusBadge(client.status)">{{ client.status }}</span>
          <span class="px-2 py-0.5 text-[10px] rounded-full" :class="getTierBadge(client.account_tier)">{{ client.account_tier }}</span>
        </div>
        <button @click="$emit('close')" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
          <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="flex flex-1 overflow-hidden">
        <!-- SIDEBAR -->
        <div class="w-48 shrink-0 border-r border-slate-200 dark:border-slate-700 flex flex-col bg-slate-50 dark:bg-slate-800/60 overflow-y-auto">
          <!-- Avatar -->
          <div class="p-4 text-center border-b border-slate-200 dark:border-slate-700">
            <div class="relative w-16 h-16 mx-auto mb-2 group cursor-pointer" @click="$refs.photoInput.click()">
              <img v-if="client.profile_image" :src="client.profile_image" class="w-16 h-16 rounded-xl object-cover" />
              <div v-else class="w-16 h-16 rounded-xl bg-slate-200 dark:bg-slate-700 flex items-center justify-center" v-html="getUserIcon()"></div>
              <div class="absolute inset-0 rounded-xl bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              </div>
            </div>
            <input ref="photoInput" type="file" accept="image/*" class="hidden" @change="uploadPhoto" />
            <p class="text-xs font-semibold text-slate-900 dark:text-white truncate">{{ client.display_name || client.user_username }}</p>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 truncate">{{ client.user_email || 'No email' }}</p>
          </div>
          <!-- KPIs -->
          <div class="p-3 space-y-1.5 border-b border-slate-200 dark:border-slate-700">
            <div class="flex justify-between items-center px-2 py-1.5 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
              <span class="text-[10px] text-blue-600 dark:text-blue-400">Balance</span>
              <span class="text-xs font-bold text-blue-700 dark:text-blue-300">KSh {{ formatNumber(client.balance) }}</span>
            </div>
            <div class="flex justify-between items-center px-2 py-1.5 bg-purple-50 dark:bg-purple-500/10 rounded-lg">
              <span class="text-[10px] text-purple-600 dark:text-purple-400">Points</span>
              <span class="text-xs font-bold text-purple-700 dark:text-purple-300">{{ client.reward_points }}</span>
            </div>
            <div class="flex justify-between items-center px-2 py-1.5 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg">
              <span class="text-[10px] text-emerald-600 dark:text-emerald-400">Spent</span>
              <span class="text-xs font-bold text-emerald-700 dark:text-emerald-300">KSh {{ formatNumber(client.total_spent) }}</span>
            </div>
            <div class="flex justify-between items-center px-2 py-1.5 bg-slate-100 dark:bg-slate-700/60 rounded-lg">
              <span class="text-[10px] text-slate-500 dark:text-slate-400">Data</span>
              <span class="text-xs font-bold text-slate-700 dark:text-slate-300">{{ formatBytes(client.lifetime_data_used) }}</span>
            </div>
            <div class="flex justify-between items-center px-2 py-1.5 bg-amber-50 dark:bg-amber-500/10 rounded-lg">
              <span class="text-[10px] text-amber-600 dark:text-amber-400">Credit</span>
              <span class="text-xs font-bold text-amber-700 dark:text-amber-300">KSh {{ formatNumber(client.credit_limit) }}</span>
            </div>
          </div>
          <!-- Actions -->
          <div class="p-3 space-y-1.5">
            <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide px-1 mb-1">Actions</p>
            <button @click="showBalanceModal = true" class="w-full text-left px-2.5 py-2 text-xs font-medium bg-blue-50 dark:bg-blue-500/10 hover:bg-blue-100 dark:hover:bg-blue-500/20 text-blue-700 dark:text-blue-400 rounded-lg transition-colors">💰 Adjust Balance</button>
            <button @click="showPointsModal = true" class="w-full text-left px-2.5 py-2 text-xs font-medium bg-purple-50 dark:bg-purple-500/10 hover:bg-purple-100 dark:hover:bg-purple-500/20 text-purple-700 dark:text-purple-400 rounded-lg transition-colors">⭐ Award Points</button>
            <button @click="toggleSuspend" class="w-full text-left px-2.5 py-2 text-xs font-medium rounded-lg transition-colors" :class="client.status === 'suspended' ? 'bg-emerald-50 dark:bg-emerald-500/10 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-400' : 'bg-amber-50 dark:bg-amber-500/10 hover:bg-amber-100 text-amber-700 dark:text-amber-400'">{{ client.status === 'suspended' ? '✅ Activate' : '⚠️ Suspend' }}</button>
            <button @click="forceLogout" class="w-full text-left px-2.5 py-2 text-xs font-medium bg-red-50 dark:bg-red-500/10 hover:bg-red-100 dark:hover:bg-red-500/20 text-red-700 dark:text-red-400 rounded-lg transition-colors">🚪 Force Logout</button>
          </div>
        </div>

        <!-- RIGHT PANEL -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <!-- General Tab -->
        <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <button @click="open.general = !open.general" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Overview</span>
            <div class="flex items-center gap-2">
              <span @click.stop="editing = !editing" class="px-2 py-0.5 text-[10px] font-medium rounded-md cursor-pointer transition-colors" :class="editing ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400'">{{ editing ? 'Cancel' : '✏️ Edit' }}</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.general ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
          </button>
          <div v-show="open.general" class="p-4 space-y-3">
            <!-- Edit Form -->
            <div v-if="editing" class="grid grid-cols-2 gap-2 pb-3 border-b border-slate-200 dark:border-slate-700">
              <div>
                <label class="block text-[10px] text-slate-500 dark:text-slate-400 mb-1">Username</label>
                <input v-model="editForm.user_username" class="w-full px-2 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div>
                <label class="block text-[10px] text-slate-500 dark:text-slate-400 mb-1">Display Name</label>
                <input v-model="editForm.display_name" class="w-full px-2 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div>
                <label class="block text-[10px] text-slate-500 dark:text-slate-400 mb-1">Email</label>
                <input v-model="editForm.user_email" type="email" class="w-full px-2 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div>
                <label class="block text-[10px] text-slate-500 dark:text-slate-400 mb-1">Phone</label>
                <input v-model="editForm.phone_number" class="w-full px-2 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div>
                <label class="block text-[10px] text-slate-500 dark:text-slate-400 mb-1">Account Tier</label>
                <select v-model="editForm.account_tier" class="w-full px-2 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500">
                  <option value="basic">Basic</option>
                  <option value="premium">Premium</option>
                  <option value="business">Business</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
              <div>
                <label class="block text-[10px] text-slate-500 dark:text-slate-400 mb-1">Credit Limit (KSh)</label>
                <input v-model="editForm.credit_limit" type="number" class="w-full px-2 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div class="col-span-2 flex justify-end gap-2">
                <button @click="editing = false" class="px-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">Cancel</button>
                <button @click="saveEdit" class="px-3 py-1.5 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors">💾 Save Changes</button>
              </div>
            </div>
          <!-- Profile Image & Key Metrics -->
          <div class="flex items-start gap-3 mb-3">
            <div v-if="client.profile_image" class="w-16 h-16 rounded-lg overflow-hidden">
              <img :src="client.profile_image" alt="Profile" class="w-full h-full object-cover" @error="$event.target.parentElement.innerHTML = getUserIcon()" />
            </div>
            <div v-else class="w-16 h-16 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center" v-html="getUserIcon()">
            </div>
            <div class="flex-1 grid grid-cols-2 md:grid-cols-3 gap-2">
              <div class="p-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
                <p class="text-[10px] text-blue-600 dark:text-blue-400">Balance</p>
                <p class="text-sm font-bold text-blue-700 dark:text-blue-300">KSh {{ formatNumber(client.balance) }}</p>
              </div>
              <div class="p-2 bg-purple-50 dark:bg-purple-500/10 rounded-lg">
                <p class="text-[10px] text-purple-600 dark:text-purple-400">Points</p>
                <p class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ client.reward_points }}</p>
              </div>
              <div class="p-2 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg col-span-2 md:col-span-1">
                <p class="text-[10px] text-emerald-600 dark:text-emerald-400">Spent</p>
                <p class="text-sm font-bold text-emerald-700 dark:text-emerald-300">KSh {{ formatNumber(client.total_spent) }}</p>
              </div>
            </div>
          </div>

          <!-- All Client Fields -->
          <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
            <div><span class="text-slate-500 dark:text-slate-400">Account:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.account }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Phone:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.phone_number }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Email:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.user_email || 'N/A' }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Display Name:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.display_name || 'N/A' }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Tier:</span> <span class="px-2 py-0.5 text-xs rounded-full ml-2" :class="getTierBadge(client.account_tier)">{{ client.account_tier }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Status:</span> <span class="px-2 py-0.5 text-xs rounded-full ml-2" :class="getStatusBadge(client.status)">{{ client.status }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Reward Tier:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.reward_tier }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Credit Limit:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">KSh {{ formatNumber(client.credit_limit) }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Data Used:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ formatBytes(client.lifetime_data_used) }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Joined:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ formatDate(client.created_at) }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Last Login:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ formatDate(client.last_login) }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">2FA:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.two_factor_enabled ? 'Enabled' : 'Disabled' }}</span></div>
          </div>

          <!-- Quick Stats -->
          <div class="grid grid-cols-4 gap-2 pt-2 border-t border-slate-200 dark:border-slate-700">
            <div class="text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded">
              <p class="text-[10px] text-slate-500 dark:text-slate-400">Devices</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ profile.stats?.total_devices || 0 }}</p>
            </div>
            <div class="text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded">
              <p class="text-[10px] text-slate-500 dark:text-slate-400">Sessions</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ profile.stats?.active_sessions || 0 }}</p>
            </div>
            <div class="text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded">
              <p class="text-[10px] text-slate-500 dark:text-slate-400">Vouchers</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ profile.stats?.total_vouchers || 0 }}</p>
            </div>
            <div class="text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded">
              <p class="text-[10px] text-slate-500 dark:text-slate-400">Points Earned</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ client.total_points_earned || 0 }}</p>
            </div>
          </div>
          </div>
        </div>

        <!-- Advanced Tab -->
        <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <button @click="open.advanced = !open.advanced" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Intelligence & Actions</span>
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.advanced ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div v-show="open.advanced" class="p-4 space-y-3">
          <!-- Analytics -->
          <div>
            <h4 class="text-xs font-semibold text-slate-900 dark:text-white mb-2">Analytics & Insights</h4>
            <div class="grid grid-cols-2 gap-2">
              <div class="p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <p class="text-[10px] text-slate-600 dark:text-slate-400 mb-0.5">Lifetime Value</p>
                <p class="text-base font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(analytics.ltv) }}</p>
              </div>
              <div class="p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <p class="text-[10px] text-slate-600 dark:text-slate-400 mb-0.5">Engagement Score</p>
                <p class="text-base font-bold text-slate-900 dark:text-white">{{ analytics.engagement_score }}%</p>
              </div>
              <div class="p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <p class="text-[10px] text-slate-600 dark:text-slate-400 mb-0.5">Churn Risk</p>
                <p class="text-base font-bold" :class="analytics.churn_risk === 'low' ? 'text-emerald-600' : 'text-red-600'">{{ analytics.churn_risk }}</p>
              </div>
              <div class="p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <p class="text-[10px] text-slate-600 dark:text-slate-400 mb-0.5">Avg Transaction</p>
                <p class="text-base font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(analytics.avg_transaction) }}</p>
              </div>
            </div>
          </div>
          </div>
        </div>

        <!-- Security & Access -->
        <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <button @click="open.account = !open.account" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Security & Access</span>
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.account ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div v-show="open.account" class="p-4 grid grid-cols-2 gap-x-4 gap-y-3 text-xs">
            <div><span class="text-slate-500 dark:text-slate-400">2FA</span><p class="font-medium mt-0.5" :class="client.two_factor_enabled ? 'text-emerald-600' : 'text-red-500'">{{ client.two_factor_enabled ? '✓ Enabled' : '✗ Disabled' }}</p></div>
            <div><span class="text-slate-500 dark:text-slate-400">Account Status</span><p class="mt-0.5"><span class="px-2 py-0.5 rounded-full text-[10px]" :class="getStatusBadge(client.status)">{{ client.status }}</span></p></div>
            <div><span class="text-slate-500 dark:text-slate-400">Joined</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(client.created_at) }}</p></div>
            <div><span class="text-slate-500 dark:text-slate-400">Last Login</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(client.last_login) }}</p></div>
            <div><span class="text-slate-500 dark:text-slate-400">Location</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ client.location || 'N/A' }}</p></div>
            <div><span class="text-slate-500 dark:text-slate-400">Zone</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ client.zone || 'N/A' }}</p></div>
            <div class="col-span-2"><span class="text-slate-500 dark:text-slate-400">Installation Address</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ client.installation_address || 'N/A' }}</p></div>
          </div>
        </div>

        <!-- Vouchers -->
        <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <button @click="open.vouchers = !open.vouchers" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Vouchers <span class="ml-1 px-1.5 py-0.5 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-full normal-case font-normal">{{ profile.vouchers?.length || 0 }}</span></span>
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.vouchers ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div v-show="open.vouchers" class="divide-y divide-slate-100 dark:divide-slate-700">
            <div v-if="profile.vouchers?.length">
              <div v-for="v in profile.vouchers" :key="v.id" class="flex items-center justify-between px-4 py-2.5 text-xs">
                <div><p class="font-medium text-slate-900 dark:text-white">{{ v.package }}</p><p class="text-[10px] text-slate-500 dark:text-slate-400">Activated: {{ formatDate(v.activated_at) }}</p></div>
                <div class="text-right"><span class="px-2 py-0.5 rounded-full text-[10px]" :class="v.status === 'active' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'">{{ v.status }}</span><p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">Exp: {{ formatDate(v.expires_at) }}</p></div>
              </div>
            </div>
            <p v-else class="text-center py-4 text-xs text-slate-400 dark:text-slate-500">No vouchers found</p>
          </div>
        </div>

        <!-- Devices -->
        <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <button @click="open.devices = !open.devices" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Devices <span class="ml-1 px-1.5 py-0.5 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-full normal-case font-normal">{{ profile.stats?.total_devices || 0 }}</span></span>
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.devices ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div v-show="open.devices" class="divide-y divide-slate-100 dark:divide-slate-700">
            <div v-if="profile.devices?.length">
              <div v-for="d in profile.devices" :key="d.id" class="flex items-center justify-between px-4 py-2.5 text-xs">
                <div><p class="font-medium text-slate-900 dark:text-white">{{ d.name }}</p><p class="text-[10px] text-slate-500 dark:text-slate-400">{{ d.mac }}</p></div>
                <div class="text-right"><span class="px-2 py-0.5 bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 rounded-full text-[10px]">{{ d.type }}</span><p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{{ d.last_seen ? formatDate(d.last_seen) : 'Never' }}</p></div>
              </div>
            </div>
            <p v-else class="text-center py-4 text-xs text-slate-400 dark:text-slate-500">No devices registered</p>
          </div>
        </div>

        <!-- Sessions -->
        <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <button @click="open.sessions = !open.sessions" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Sessions <span class="ml-1 px-1.5 py-0.5 bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 rounded-full normal-case font-normal">{{ profile.stats?.active_sessions || 0 }} active</span></span>
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.sessions ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div v-show="open.sessions" class="divide-y divide-slate-100 dark:divide-slate-700">
            <div v-if="profile.sessions?.length">
              <div v-for="s in profile.sessions" :key="s.id" class="flex items-center justify-between px-4 py-2.5 text-xs">
                <div><p class="font-medium text-slate-900 dark:text-white">{{ s.device }}</p><p class="text-[10px] text-slate-500 dark:text-slate-400">{{ s.ip }}</p></div>
                <div class="text-right"><span class="px-2 py-0.5 rounded-full text-[10px]" :class="s.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'">{{ s.is_active ? 'Active' : 'Ended' }}</span><p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{{ formatDate(s.login_time) }}</p></div>
              </div>
            </div>
            <p v-else class="text-center py-4 text-xs text-slate-400 dark:text-slate-500">No active sessions</p>
          </div>
        </div>

        <!-- Transactions -->
        <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <button @click="open.transactions = !open.transactions" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Transactions <span class="ml-1 px-1.5 py-0.5 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-full normal-case font-normal">{{ profile.transactions?.length || 0 }}</span></span>
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.transactions ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div v-show="open.transactions" class="divide-y divide-slate-100 dark:divide-slate-700">
            <div v-if="profile.transactions?.length">
              <div v-for="t in profile.transactions" :key="t.id" class="flex items-center justify-between px-4 py-2.5 text-xs">
                <div><p class="font-medium text-slate-900 dark:text-white">KSh {{ formatNumber(t.amount) }}</p><p class="text-[10px] text-slate-500 dark:text-slate-400">{{ formatDate(t.transaction_time) }}</p></div>
                <span class="px-2 py-0.5 rounded-full text-[10px]" :class="t.result_code === '0' || t.result_code === 0 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400'">{{ t.result_code === '0' || t.result_code === 0 ? 'Success' : 'Failed' }}</span>
              </div>
            </div>
            <p v-else class="text-center py-4 text-xs text-slate-400 dark:text-slate-500">No transactions found</p>
          </div>
        </div>

        <!-- Rewards -->
        <div class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <button @click="open.rewards = !open.rewards" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Rewards</span>
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.rewards ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <div v-show="open.rewards" class="p-4">
            <div class="grid grid-cols-3 gap-2">
              <div class="p-2 bg-purple-50 dark:bg-purple-500/10 rounded-lg text-center"><p class="text-[10px] text-purple-600 dark:text-purple-400">Points</p><p class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ client.reward_points }}</p></div>
              <div class="p-2 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg text-center"><p class="text-[10px] text-emerald-600 dark:text-emerald-400">Earned</p><p class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ client.total_points_earned || 0 }}</p></div>
              <div class="p-2 bg-amber-50 dark:bg-amber-500/10 rounded-lg text-center"><p class="text-[10px] text-amber-600 dark:text-amber-400">Tier</p><p class="text-sm font-bold text-amber-700 dark:text-amber-300">{{ client.reward_tier || 'N/A' }}</p></div>
            </div>
          </div>
        </div>

        </div>
      </div>
    </div>

    <!-- Balance Modal -->
    <div v-if="showBalanceModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4" @click.self="showBalanceModal = false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-sm w-full p-5">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Adjust Balance</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">Current: KSh {{ formatNumber(client.balance) }}</p>
          </div>
        </div>
        <div class="space-y-2.5 mb-4">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Amount</label>
            <input v-model="balanceAmount" type="number" placeholder="Enter amount (+ or -)" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Reason</label>
            <input v-model="balanceReason" type="text" placeholder="Enter reason" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
          </div>
        </div>
        <div class="flex gap-2">
          <button @click="showBalanceModal = false" class="flex-1 px-3 py-2 text-xs font-medium bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg transition-colors">Cancel</button>
          <button @click="adjustBalance" class="flex-1 px-3 py-2 text-xs font-medium bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors">Confirm</button>
        </div>
      </div>
    </div>

    <!-- Points Modal -->
    <div v-if="showPointsModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4" @click.self="showPointsModal = false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-sm w-full p-5">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-500/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Award Points</h3>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">Current: {{ client.reward_points }} points</p>
          </div>
        </div>
        <div class="space-y-2.5 mb-4">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Points</label>
            <input v-model="pointsAmount" type="number" placeholder="Enter points" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
            <input v-model="pointsReason" type="text" placeholder="Enter description" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
          </div>
        </div>
        <div class="flex gap-2">
          <button @click="showPointsModal = false" class="flex-1 px-3 py-2 text-xs font-medium bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg transition-colors">Cancel</button>
          <button @click="awardPoints" class="flex-1 px-3 py-2 text-xs font-medium bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors">Award</button>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <ConfirmDialog :show="confirmDialog.show" :type="confirmDialog.type" :title="confirmDialog.title" :message="confirmDialog.message" :confirmText="confirmDialog.confirmText" @confirm="confirmDialog.onConfirm" @cancel="confirmDialog.show = false" />
  </div>
</template>

<script>
import { ref, watch, reactive } from 'vue'
import { useApi } from '../composables/useApi'
import ConfirmDialog from './ConfirmDialog.vue'

export default {
  name: 'ClientDetailModal',
  components: { ConfirmDialog },
  props: {
    show: Boolean,
    client: Object
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const { makeRequest } = useApi()
    const activeTab = ref('general')
    const profile = ref({ devices: [], sessions: [], transactions: [], vouchers: [], stats: {} })
    const analytics = ref({})
    const open = reactive({ general: true, advanced: false, account: false, vouchers: false, devices: false, sessions: false, transactions: false, rewards: false })
    const editing = ref(false)
    const editForm = reactive({ user_username: '', user_email: '', display_name: '', phone_number: '', account_tier: '', credit_limit: 0 })

    const saveEdit = async () => {
      try {
        await makeRequest('patch', `suapi/clients/${props.client.id}/`, editForm)
        editing.value = false
        emit('refresh')
        fetchProfile()
      } catch (err) {
        console.error('Save failed:', err)
      }
    }
    const showBalanceModal = ref(false)
    const showPointsModal = ref(false)
    const balanceAmount = ref(0)
    const balanceReason = ref('')
    const pointsAmount = ref(0)
    const pointsReason = ref('')

    const tabs = [
      { id: 'general', label: 'General' },
      { id: 'advanced', label: 'Advanced' }
    ]

    const fetchProfile = async () => {
      if (!props.client?.id) return
      try {
        profile.value = await makeRequest('get', `suapi/clients/${props.client.id}/profile/`)
        try {
          analytics.value = await makeRequest('get', `suapi/clients/${props.client.id}/analytics/`)
        } catch (error) {
          console.error('Error fetching analytics:', error)
          analytics.value = { ltv: 0, engagement_score: 0, churn_risk: 'unknown', avg_transaction: 0 }
        }
      } catch (error) {
        console.error('Error fetching profile:', error)
      }
    }

    const adjustBalance = async () => {
      try {
        await makeRequest('post', `suapi/clients/${props.client.id}/adjust_balance/`, {
          amount: balanceAmount.value,
          reason: balanceReason.value
        })
        showBalanceModal.value = false
        emit('refresh')
        fetchProfile()
      } catch (error) {
        console.error('Error adjusting balance:', error)
      }
    }

    const awardPoints = async () => {
      try {
        await makeRequest('post', `suapi/clients/${props.client.id}/award_points/`, {
          points: pointsAmount.value,
          description: pointsReason.value
        })
        showPointsModal.value = false
        emit('refresh')
        fetchProfile()
      } catch (error) {
        console.error('Error awarding points:', error)
      }
    }

    const confirmDialog = reactive({
      show: false,
      type: 'info',
      title: '',
      message: '',
      confirmText: 'Confirm',
      onConfirm: () => {}
    })

    const toggleSuspend = () => {
      const action = props.client.status === 'suspended' ? 'activate' : 'suspend'
      confirmDialog.show = true
      confirmDialog.type = action === 'suspend' ? 'warning' : 'info'
      confirmDialog.title = action === 'suspend' ? 'Suspend Client' : 'Activate Client'
      confirmDialog.message = action === 'suspend' ? 'This will temporarily disable the client account.' : 'This will reactivate the client account.'
      confirmDialog.confirmText = action === 'suspend' ? 'Suspend' : 'Activate'
      confirmDialog.onConfirm = async () => {
        try {
          await makeRequest('post', `suapi/clients/${props.client.id}/${action}/`, { reason: 'Admin action' })
          confirmDialog.show = false
          emit('refresh')
          emit('close')
        } catch (error) {
          console.error(`Error ${action}ing client:`, error)
        }
      }
    }

    const uploadPhoto = async (e) => {
      const file = e.target.files[0]
      if (!file) return
      const form = new FormData()
      form.append('profile_image', file)
      try {
        await makeRequest('patch', `suapi/clients/${props.client.id}/upload_photo/`, form)
        emit('refresh')
        fetchProfile()
      } catch (err) {
        console.error('Photo upload failed:', err)
      }
    }

    const forceLogout = () => {      confirmDialog.show = true
      confirmDialog.type = 'danger'
      confirmDialog.title = 'Force Logout'
      confirmDialog.message = 'This will end all active sessions for this client.'
      confirmDialog.confirmText = 'Logout'
      confirmDialog.onConfirm = async () => {
        try {
          await makeRequest('post', `suapi/clients/${props.client.id}/force_logout/`, { reason: 'Admin action' })
          confirmDialog.show = false
          fetchProfile()
        } catch (error) {
          console.error('Error forcing logout:', error)
        }
      }
    }

    const getUserIcon = () => {
      return `<svg class="w-10 h-10 text-slate-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>`
    }

    const formatNumber = (num) => new Intl.NumberFormat().format(num || 0)
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
    const formatBytes = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
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

    watch(() => props.show, (newVal) => {
      if (newVal) {
        fetchProfile()
        editForm.user_username = props.client?.user_username || ''
        editForm.user_email = props.client?.user_email || ''
        editForm.display_name = props.client?.display_name || ''
        editForm.phone_number = props.client?.phone_number || ''
        editForm.account_tier = props.client?.account_tier || 'basic'
        editForm.credit_limit = props.client?.credit_limit || 0
      }
    })

    return {
      activeTab, tabs, profile, analytics, open, editing, editForm, saveEdit,
      showBalanceModal, showPointsModal,
      balanceAmount, balanceReason, pointsAmount, pointsReason,
      confirmDialog,
      adjustBalance, awardPoints, uploadPhoto, toggleSuspend, forceLogout,
      getUserIcon, formatNumber, formatDate, formatBytes, getTierBadge, getStatusBadge
    }
  }
}
</script>

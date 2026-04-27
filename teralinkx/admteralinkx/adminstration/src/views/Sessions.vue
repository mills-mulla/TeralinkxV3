<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Sessions</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Monitor active user sessions</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Session
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load sessions</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchSessions" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metric Pills -->
    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Total</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_sessions || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Active</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.active_sessions || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 rounded-xl">
        <span class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">With Voucher</span>
        <span class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ stats.voucher_sessions || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-slate-100 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-xl">
        <span class="text-[10px] text-slate-500 dark:text-slate-400 font-medium">Inactive</span>
        <span class="text-sm font-bold text-slate-700 dark:text-slate-300">{{ stats.inactive_sessions || 0 }}</span>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-2 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2 flex-wrap">
        <div class="flex-1 min-w-48">
          <input v-model="searchTerm" type="text" placeholder="Search session ID, account, device, IP..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
        <select v-model="typeFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Types</option>
          <option value="network">Network</option>
          <option value="hotspot">Hotspot</option>
          <option value="vpn">VPN</option>
        </select>
        <select v-model="ownerFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Owners</option>
          <option value="true">Owner</option>
          <option value="false">Shared</option>
        </select>
      </div>

      <!-- Bulk Actions -->
      <div v-if="selectedIds.length" class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
        <span class="text-xs text-blue-700 dark:text-blue-400 font-medium">{{ selectedIds.length }} selected</span>
        <button @click="bulkAction('terminate')" class="px-2 py-1 text-[10px] font-medium rounded bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400 hover:bg-red-200">🚫 Terminate</button>
        <button @click="bulkAction('extend_voucher')" class="px-2 py-1 text-[10px] font-medium rounded bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200">⏱ Extend 1hr</button>
        <button @click="bulkAction('deactivate_vouchers')" class="px-2 py-1 text-[10px] font-medium rounded bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 hover:bg-amber-200">❌ Deactivate Vouchers</button>
        <button @click="selectedIds = []" class="ml-auto text-[10px] text-slate-500 hover:text-slate-700">Clear</button>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 w-6"><input type="checkbox" @change="toggleSelectAll" :checked="selectedIds.length === filteredSessions.length && filteredSessions.length > 0" class="rounded" /></th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Session ID</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Client</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Device</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Voucher</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Duration</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Data Used</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">IP</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Location</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Login</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="session in filteredSessions" :key="session.id" @click="openEditModal(session)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2" @click.stop><input type="checkbox" :value="session.id" v-model="selectedIds" class="rounded" /></td>
                <td class="px-3 py-2">
                  <p class="text-xs font-mono font-medium text-slate-900 dark:text-white">{{ session.session_id?.substring(0,8) }}...</p>
                  <p class="text-[10px] text-slate-500">{{ session.session_type || 'network' }}</p>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ session.user_account || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ session.device_name || 'Unknown' }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ session.session_type || 'network' }}</span></td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] rounded-full" :class="session.is_active ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'">{{ session.is_active ? 'Active' : 'Ended' }}</span></td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">
                  <span v-if="session.active_voucher" class="px-1.5 py-0.5 text-[10px] rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400">{{ session.active_voucher?.substring(0,8) }}</span>
                  <span v-else class="text-slate-400 text-[10px]">None</span>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ session.duration || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatBytes(session.data_used) }}</td>
                <td class="px-3 py-2 text-xs font-mono text-slate-900 dark:text-white">{{ session.ip_address || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ session.location_name || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-500 dark:text-slate-400">{{ formatDate(session.login_time) }}</td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button v-if="session.is_active" @click.stop="terminateSession(session)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded" title="Terminate">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/></svg>
                    </button>
                    <button @click.stop="openDeleteModal(session)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded" title="Delete">
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

    <!-- Edit Session Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[88vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700 shrink-0">
          <div>
            <h2 class="text-sm font-semibold text-slate-900 dark:text-white font-mono">{{ selectedSession?.session_id?.substring(0,16) || 'New Session' }}</h2>
            <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ selectedSession?.user_account }} · {{ selectedSession?.device_name }} · {{ selectedSession?.ip_address }}</p>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="selectedSession?.id" class="px-2 py-0.5 text-[10px] rounded-full" :class="selectedSession.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'">{{ selectedSession.is_active ? 'Active' : 'Ended' }}</span>
            <button @click="closeFormModal" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"><svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>
          </div>
        </div>
        <!-- Body -->
        <div class="flex flex-1 overflow-hidden">
          <!-- Sidebar -->
          <div class="w-44 shrink-0 border-r border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 overflow-y-auto p-3 space-y-1">
            <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide px-1 mb-1">Sections</p>
            <button v-for="s in sessionSections" :key="s.id" @click="activeSessionSection=s.id"
              class="w-full text-left px-2.5 py-2 text-xs rounded-lg transition-colors"
              :class="activeSessionSection===s.id ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 font-medium' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'">
              {{ s.label }}
            </button>
            <div v-if="selectedSession?.is_active" class="pt-2 mt-2 border-t border-slate-200 dark:border-slate-700">
              <button @click="terminateSession(selectedSession)" class="w-full text-left px-2.5 py-2 text-xs rounded-lg bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 hover:bg-red-100">🚫 Terminate</button>
            </div>
          </div>
          <!-- Right panel -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">

            <!-- 1. Session -->
            <div v-show="activeSessionSection==='session'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="sOpen.session=!sOpen.session" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Session Info</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="sOpen.session?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="sOpen.session" class="p-4 grid grid-cols-2 gap-3 text-xs">
                <div class="col-span-2"><span class="text-slate-500">Session ID</span><p class="font-mono font-medium text-slate-900 dark:text-white mt-0.5 break-all">{{ selectedSession?.session_id || 'N/A' }}</p></div>
                <div><span class="text-slate-500">Client</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedSession?.user_account || 'N/A' }}</p></div>
                <div><span class="text-slate-500">Device</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedSession?.device_name || 'N/A' }}</p></div>
                <div><span class="text-slate-500">Type</span><p class="mt-0.5"><span class="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ selectedSession?.session_type || 'network' }}</span></p></div>
                <div><span class="text-slate-500">Owner</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedSession?.is_owner ? 'Yes' : 'Shared' }}</p></div>
                <div><span class="text-slate-500">Transferred</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedSession?.was_transferred ? 'Yes' : 'No' }}</p></div>
                <div>
                  <label class="flex items-center gap-2 cursor-pointer mt-1">
                    <input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 rounded" />
                    <span class="text-slate-700 dark:text-slate-300">Active</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 2. Network -->
            <div v-show="activeSessionSection==='network'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="sOpen.network=!sOpen.network" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Network</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="sOpen.network?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="sOpen.network" class="p-4 grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">IP Address</label>
                  <input v-model="formData.ip_address" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
                <div><span class="text-slate-500">Location</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedSession?.location_name || 'N/A' }}</p></div>
                <div class="col-span-2"><span class="text-slate-500">User Agent</span><p class="font-medium text-slate-900 dark:text-white mt-0.5 text-[10px] break-all">{{ selectedSession?.user_agent || 'N/A' }}</p></div>
              </div>
            </div>

            <!-- 3. Voucher -->
            <div v-show="activeSessionSection==='voucher'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="sOpen.voucher=!sOpen.voucher" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Voucher</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="sOpen.voucher?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="sOpen.voucher" class="p-4 grid grid-cols-2 gap-3 text-xs">
                <div class="col-span-2"><span class="text-slate-500">Active Voucher</span><p class="font-mono font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedSession?.active_voucher || 'None' }}</p></div>
                <div><span class="text-slate-500">Activated</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(selectedSession?.voucher_activated) }}</p></div>
                <div><span class="text-slate-500">Expires</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(selectedSession?.voucher_expires) }}</p></div>
                <div class="col-span-2"><span class="text-slate-500">Time Remaining</span><p class="font-medium text-emerald-600 dark:text-emerald-400 mt-0.5">{{ selectedSession?.time_remaining || 'N/A' }}</p></div>
              </div>
            </div>

            <!-- 4. Timing -->
            <div v-show="activeSessionSection==='timing'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="sOpen.timing=!sOpen.timing" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Timing</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="sOpen.timing?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="sOpen.timing" class="p-4 grid grid-cols-2 gap-3 text-xs">
                <div><span class="text-slate-500">Login Time</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(selectedSession?.login_time) }}</p></div>
                <div><span class="text-slate-500">Duration</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedSession?.duration || 'N/A' }}</p></div>
                <div><span class="text-slate-500">Expired</span><p class="font-medium mt-0.5" :class="selectedSession?.is_expired ? 'text-red-500' : 'text-emerald-600'">{{ selectedSession?.is_expired ? 'Yes' : 'No' }}</p></div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Auto Logout (min)</label>
                  <input v-model="formData.auto_logout_minutes" type="number" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                </div>
              </div>
            </div>

            <!-- 5. Usage -->
            <div v-show="activeSessionSection==='usage'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="sOpen.usage=!sOpen.usage" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Usage</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="sOpen.usage?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="sOpen.usage" class="p-4 space-y-3 text-xs">
                <div class="grid grid-cols-2 gap-3">
                  <div class="p-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg text-center"><p class="text-[10px] text-blue-600 dark:text-blue-400">Data Used</p><p class="font-bold text-blue-700 dark:text-blue-300">{{ formatBytes(selectedSession?.data_used) }}</p></div>
                  <div class="p-2 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg text-center"><p class="text-[10px] text-emerald-600 dark:text-emerald-400">Last Activity</p><p class="font-bold text-emerald-700 dark:text-emerald-300">{{ formatDate(selectedSession?.last_activity) }}</p></div>
                </div>
                <div v-if="selectedSession?.request_metadata">
                  <p class="text-slate-500 mb-1">Request Metadata</p>
                  <pre class="text-[10px] bg-slate-50 dark:bg-slate-900 rounded-lg p-2 overflow-x-auto text-slate-700 dark:text-slate-300">{{ JSON.stringify(selectedSession.request_metadata, null, 2) }}</pre>
                </div>
              </div>
            </div>

            <!-- 6. Summary -->
            <div v-show="activeSessionSection==='summary'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="sOpen.summary=!sOpen.summary" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Summary</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="sOpen.summary?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="sOpen.summary" class="p-4 text-xs">
                <div v-if="selectedSession?.session_summary" class="space-y-2">
                  <div v-for="(val, key) in selectedSession.session_summary" :key="key" class="flex justify-between py-1 border-b border-slate-100 dark:border-slate-700">
                    <span class="text-slate-500 capitalize">{{ key.replace(/_/g,' ') }}</span>
                    <span class="font-medium text-slate-900 dark:text-white">{{ val }}</span>
                  </div>
                </div>
                <p v-else class="text-slate-400">No summary available</p>
              </div>
            </div>

          </div>
        </div>
        <div class="flex items-center justify-end gap-2 px-5 py-3 border-t border-slate-200 dark:border-slate-700 shrink-0">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Close</button>
          <button @click="saveSession" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{'opacity-50':saveLoading}">{{ saveLoading ? 'Saving...' : 'Save Changes' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog :show="showDeleteModal" title="Delete Session" :message="`Delete session ${sessionToDelete?.session_id?.substring(0, 8)}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useOptimistic } from '../composables/useOptimistic'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Sessions',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest, invalidateCache } = useApi()
    const sessions = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const typeFilter = ref('')
    const ownerFilter = ref('')
    const selectedIds = ref([])

    const toggleSelectAll = (e) => {
      selectedIds.value = e.target.checked ? filteredSessions.value.map(s => s.id) : []
    }

    const bulkAction = async (action) => {
      if (!selectedIds.value.length) return
      try {
        await makeRequest('post', 'suapi/sessions/bulk_action/', { action, ids: selectedIds.value })
        selectedIds.value = []
        await refreshData()
      } catch (e) { console.error(e) }
    }

    const formatBytes = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024, sizes = ['B','KB','MB','GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }
    const showFormModal = ref(false)
    const activeSessionSection = ref('session')
    const sOpen = { session: true, network: true, voucher: false, timing: false, usage: false, summary: false }
    const sessionSections = [
      { id: 'session',  label: '📌 Session Info' },
      { id: 'network',  label: '🌐 Network' },
      { id: 'voucher',  label: '🎫 Voucher' },
      { id: 'timing',   label: '⏱ Timing' },
      { id: 'usage',    label: '📊 Usage' },
      { id: 'summary',  label: '📝 Summary' },
    ]
    const showDeleteModal = ref(false)
    const selectedSession = ref(null)
    const sessionToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({
      session_id: '',
      ip_address: '',
      is_active: true
    })

    const filteredSessions = computed(() => {
      let result = sessions.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(s => s.session_id?.toLowerCase().includes(term) || s.user_account?.toLowerCase().includes(term) || s.ip_address?.includes(term) || s.device_name?.toLowerCase().includes(term))
      }
      if (statusFilter.value) result = result.filter(s => s.is_active === (statusFilter.value === 'true'))
      if (typeFilter.value) result = result.filter(s => s.session_type === typeFilter.value)
      if (ownerFilter.value) result = result.filter(s => s.is_owner === (ownerFilter.value === 'true'))
      return result
    })

    const fetchSessions = async () => {
      try {
        const data = await makeRequest('get', 'suapi/sessions/')
        sessions.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/sessions/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchSessions(), fetchStats()])
    const { optimisticRemove, optimisticUpdate } = useOptimistic(sessions, fetchSessions, invalidateCache, 'suapi/sessions')
    
    const openAddModal = () => {
      selectedSession.value = null
      formData.value = {
        session_id: '',
        ip_address: '',
        is_active: true
      }
      showFormModal.value = true
    }
    
    const openEditModal = (session) => {
      selectedSession.value = session
      activeSessionSection.value = 'session'
      formData.value = {
        session_id: session.session_id || '',
        ip_address: session.ip_address || '',
        is_active: session.is_active || false,
        auto_logout_minutes: session.auto_logout_minutes || 0
      }
      showFormModal.value = true
    }

    const closeFormModal = () => {
      showFormModal.value = false
      selectedSession.value = null
      formData.value = { session_id: '', ip_address: '', is_active: true, auto_logout_minutes: 0 }
    }

    const saveSession = async () => {
      saveLoading.value = true
      try {
        if (selectedSession.value?.id) {
          await makeRequest('patch', `suapi/sessions/${selectedSession.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/sessions/', formData.value)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const terminateSession = async (session) => {
      if (!confirm(`Terminate session ${session.session_id?.substring(0, 8)}?`)) return
      optimisticUpdate(session.id, { is_active: false })
      try {
        await makeRequest('post', `suapi/sessions/${session.id}/terminate/`, { reason: 'Admin action' })
      } catch (err) {
        await refreshData() // rollback
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const openDeleteModal = (session) => { sessionToDelete.value = session; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; sessionToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      const id = sessionToDelete.value.id
      optimisticRemove(id)
      closeDeleteModal()
      try {
        await makeRequest('delete', `suapi/sessions/${id}/`)
      } catch (err) {
        await refreshData() // rollback
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const formatDate = (d) => d ? new Date(d).toLocaleString() : 'N/A'

    onMounted(refreshData)

    return {
      loading, error, sessions, stats, searchTerm, statusFilter, typeFilter, ownerFilter,
      selectedIds, toggleSelectAll, bulkAction, formatBytes, formatDate,
      activeSessionSection, sOpen, sessionSections,
      showFormModal, showDeleteModal, selectedSession, sessionToDelete,
      saveLoading, deleteLoading, formData, filteredSessions, fetchSessions, refreshData,
      openAddModal, openEditModal, closeFormModal, saveSession, terminateSession, openDeleteModal, closeDeleteModal, confirmDelete
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

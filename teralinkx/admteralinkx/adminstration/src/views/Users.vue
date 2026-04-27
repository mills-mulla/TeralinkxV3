<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Users</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage Django user accounts</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add User
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load users</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchUsers" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Total</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_users || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Active</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.active_users || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 rounded-xl">
        <span class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">Staff</span>
        <span class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ stats.staff_users || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl">
        <span class="text-[10px] text-amber-600 dark:text-amber-400 font-medium">⭐ Superusers</span>
        <span class="text-sm font-bold text-amber-700 dark:text-amber-300">{{ stats.superusers || 0 }}</span>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search users..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Email</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Name</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Roles</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="user in filteredUsers" :key="user.id" @click="openEditModal(user)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                      {{ getInitials(user.username) }}
                    </div>
                    <p class="text-xs font-medium text-slate-900 dark:text-white">{{ user.username }}</p>
                  </div>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ user.email || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ user.first_name }} {{ user.last_name }}</td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="user.is_active ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-3 py-2">
                  <div class="flex items-center gap-1">
                    <span v-if="user.is_superuser" class="text-xs text-amber-600 dark:text-amber-400">⭐</span>
                    <span v-if="user.is_staff" class="text-xs text-purple-600 dark:text-purple-400">👔</span>
                  </div>
                </td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="openEditModal(user)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button @click.stop="openDeleteModal(user)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[88vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700 shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-sm font-bold text-slate-600 dark:text-slate-300">{{ getInitials(formData.username) }}</div>
            <div>
              <h2 class="text-sm font-semibold text-slate-900 dark:text-white">{{ selectedUser?.id ? formData.username : 'Add User' }}</h2>
              <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ formData.email || 'No email' }} · {{ selectedUser?.id ? (formData.is_superuser ? 'Superuser' : formData.is_staff ? 'Staff' : 'User') : 'New' }}</p>
            </div>
            <span class="px-2 py-0.5 text-[10px] rounded-full" :class="formData.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400'">{{ formData.is_active ? 'Active' : 'Inactive' }}</span>
          </div>
          <button @click="closeFormModal" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <!-- Body -->
        <div class="flex flex-1 overflow-hidden">
          <!-- Sidebar -->
          <div class="w-44 shrink-0 border-r border-slate-200 dark:border-slate-700 flex flex-col bg-slate-50 dark:bg-slate-800/60 overflow-y-auto p-3 space-y-1">
            <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide px-1 mb-1">Sections</p>
            <button v-for="s in sections" :key="s.id" @click="activeSection = s.id" class="w-full text-left px-2.5 py-2 text-xs rounded-lg transition-colors" :class="activeSection === s.id ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 font-medium' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'">{{ s.label }}</button>
            <div class="pt-2 mt-2 border-t border-slate-200 dark:border-slate-700 space-y-1">
              <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide px-1 mb-1">Flags</p>
              <label class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 cursor-pointer">
                <input v-model="formData.is_active" type="checkbox" class="w-3.5 h-3.5 text-blue-600 rounded" />
                <span class="text-xs text-slate-700 dark:text-slate-300">Active</span>
              </label>
              <label class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 cursor-pointer">
                <input v-model="formData.is_staff" type="checkbox" class="w-3.5 h-3.5 text-blue-600 rounded" />
                <span class="text-xs text-slate-700 dark:text-slate-300">Staff</span>
              </label>
              <label class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 cursor-pointer">
                <input v-model="formData.is_superuser" type="checkbox" class="w-3.5 h-3.5 text-blue-600 rounded" />
                <span class="text-xs text-slate-700 dark:text-slate-300">Superuser</span>
              </label>
            </div>
            <div v-if="selectedUser?.id" class="pt-2 mt-2 border-t border-slate-200 dark:border-slate-700 space-y-1 text-[10px] text-slate-500 dark:text-slate-400">
              <p class="px-1">Joined: {{ formatDate(selectedUser.date_joined) }}</p>
              <p class="px-1">Last login: {{ formatDate(selectedUser.last_login) }}</p>
            </div>
          </div>
          <!-- Right panel -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">

          <!-- 1. Identity -->
          <div v-show="activeSection === 'identity'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
            <button @click="open.identity=!open.identity" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Identity</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.identity?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="open.identity" class="p-4 grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Username <span class="text-red-500">*</span></label>
                <input v-model="formData.username" type="text" :disabled="!!selectedUser?.id" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Email</label>
                <input v-model="formData.email" type="email" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">First Name</label>
                <input v-model="formData.first_name" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Last Name</label>
                <input v-model="formData.last_name" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500" />
              </div>
            </div>
          </div>

          <!-- 2. Password -->
          <div v-show="activeSection === 'password'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
            <button @click="open.password=!open.password" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Password</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.password?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="open.password" class="p-4 space-y-3">
              <div v-if="selectedUser?.id" class="p-2.5 bg-slate-50 dark:bg-slate-900 rounded-lg text-[10px] text-slate-500 dark:text-slate-400 font-mono">algorithm: pbkdf2_sha256 &nbsp;&bull;&nbsp; Raw passwords are not stored.</div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">{{ selectedUser?.id ? 'New Password (blank = keep)' : 'Password *' }}</label>
                  <input v-model="formData.password" type="password" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500" />
                </div>
                <div v-if="!selectedUser?.id">
                  <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Confirm Password *</label>
                  <input v-model="formData.confirm_password" type="password" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-1 focus:ring-blue-500" />
                </div>
              </div>
              <div v-if="selectedUser?.id">
                <button @click="showResetPwd=!showResetPwd" class="text-xs text-blue-600 dark:text-blue-400 hover:underline">🔑 Reset Password</button>
                <div v-if="showResetPwd" class="mt-2 flex gap-2">
                  <input v-model="resetPwdValue" type="password" placeholder="New password" class="flex-1 px-3 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
                  <button @click="doResetPassword" class="px-3 py-1.5 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg">Set</button>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. Permissions -->
          <div v-show="activeSection === 'permissions'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
            <button @click="open.permissions=!open.permissions" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Permissions</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.permissions?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="open.permissions" class="p-4 space-y-1">
              <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer">
                <input v-model="formData.is_active" type="checkbox" class="mt-0.5 w-4 h-4 text-blue-600 rounded" />
                <div><p class="text-xs font-medium text-slate-900 dark:text-white">Active</p><p class="text-[10px] text-slate-500 dark:text-slate-400">Unselect this instead of deleting the account.</p></div>
              </label>
              <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer">
                <input v-model="formData.is_staff" type="checkbox" class="mt-0.5 w-4 h-4 text-blue-600 rounded" />
                <div><p class="text-xs font-medium text-slate-900 dark:text-white">Staff status</p><p class="text-[10px] text-slate-500 dark:text-slate-400">Can log into this admin site.</p></div>
              </label>
              <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer">
                <input v-model="formData.is_superuser" type="checkbox" class="mt-0.5 w-4 h-4 text-blue-600 rounded" />
                <div><p class="text-xs font-medium text-slate-900 dark:text-white">Superuser status</p><p class="text-[10px] text-slate-500 dark:text-slate-400">Has all permissions without explicitly assigning them.</p></div>
              </label>
            </div>
          </div>

          <!-- 4. Groups -->
          <div v-show="activeSection === 'groups'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
            <button @click="open.groups=!open.groups" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Groups <span class="ml-1 px-1.5 py-0.5 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-full text-[10px] normal-case font-normal">{{ formData.groups.length }} chosen</span></span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.groups?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="open.groups" class="p-4">
              <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-3">User gets all permissions granted to each group.</p>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <p class="text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Available</p>
                  <div class="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
                    <input v-model="groupSearch" placeholder="Search..." class="w-full px-2 py-1.5 text-xs border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white" />
                    <div class="max-h-36 overflow-y-auto">
                      <div v-for="g in availableGroups" :key="g.id" @click="addGroup(g)" class="px-3 py-1.5 text-xs text-slate-700 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-500/10 cursor-pointer flex items-center justify-between"><span>{{ g.name }}</span><span class="text-blue-400 text-[10px]">→ add</span></div>
                      <div v-if="!availableGroups.length" class="px-3 py-2 text-xs text-slate-400">None available</div>
                    </div>
                  </div>
                </div>
                <div>
                  <p class="text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Chosen</p>
                  <div class="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
                    <div class="max-h-44 overflow-y-auto">
                      <div v-for="g in formData.groups" :key="g.id" @click="removeGroup(g)" class="flex items-center justify-between px-3 py-1.5 text-xs text-slate-700 dark:text-slate-300 hover:bg-red-50 dark:hover:bg-red-500/10 cursor-pointer"><span>{{ g.name }}</span><span class="text-red-400 text-[10px]">× remove</span></div>
                      <div v-if="!formData.groups.length" class="px-3 py-2 text-xs text-slate-400">No groups chosen</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 5. User Permissions -->
          <div v-show="activeSection === 'user_permissions'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
            <button @click="open.user_permissions=!open.user_permissions" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">User Permissions <span class="ml-1 px-1.5 py-0.5 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-full text-[10px] normal-case font-normal">{{ formData.user_permissions.length }} selected</span></span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.user_permissions?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="open.user_permissions" class="p-4">
              <input v-model="permSearch" placeholder="Search permissions..." class="w-full px-3 py-1.5 text-xs border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white mb-3" />
              <div v-for="(perms, app) in filteredPermissions" :key="app" class="mb-2 border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
                <button @click="openApps[app]=!openApps[app]" class="w-full flex items-center justify-between px-3 py-2 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                  <div class="flex items-center gap-2">
                    <span class="text-[10px] font-bold text-slate-700 dark:text-slate-300 uppercase">{{ app }}</span>
                    <span class="text-[10px] text-slate-400">{{ perms.filter(p=>isPermSelected(p.id)).length }}/{{ perms.length }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span @click.stop="toggleAppPerms(app,perms)" class="text-[10px] text-blue-500 hover:underline">{{ allAppPermsSelected(app,perms) ? 'Deselect all' : 'Select all' }}</span>
                    <svg class="w-3 h-3 text-slate-400 transition-transform" :class="openApps[app]?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                  </div>
                </button>
                <div v-show="openApps[app]" class="p-2 grid grid-cols-2 gap-1">
                  <label v-for="p in perms" :key="p.id" class="flex items-center gap-2 px-2 py-1 rounded hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer">
                    <input type="checkbox" :checked="isPermSelected(p.id)" @change="togglePerm(p)" class="w-3 h-3 text-blue-600 rounded" />
                    <span class="text-[10px] text-slate-600 dark:text-slate-400">{{ p.content_type__model }} | {{ p.codename.split('_')[0] }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- 6. Important Dates -->
          <div v-if="selectedUser?.id" v-show="activeSection === 'dates'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
            <button @click="open.dates=!open.dates" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Important Dates</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="open.dates?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="open.dates" class="p-4 grid grid-cols-2 gap-3 text-xs">
              <div><span class="text-slate-500 dark:text-slate-400">Last Login</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(selectedUser.last_login) }}</p></div>
              <div><span class="text-slate-500 dark:text-slate-400">Date Joined</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(selectedUser.date_joined) }}</p></div>
            </div>
          </div>

          </div>
        </div>
        <div class="flex items-center justify-end gap-2 px-5 py-3 border-t border-slate-200 dark:border-slate-700 shrink-0">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveUser" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{'opacity-50':saveLoading}">{{ saveLoading ? 'Saving...' : (selectedUser?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog :show="showDeleteModal" title="Delete User" :message="`Delete user ${userToDelete?.username}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { useApi } from '../composables/useApi'
import { useOptimistic } from '../composables/useOptimistic'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Users',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest, invalidateCache } = useApi()
    const users = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const allGroups = ref([])
    const allPermissions = ref({})
    const groupSearch = ref('')
    const permSearch = ref('')
    const showResetPwd = ref(false)
    const resetPwdValue = ref('')
    const activeSection = ref('identity')
    const openApps = reactive({})
    const open = reactive({ identity: true, password: true, permissions: true, groups: true, user_permissions: false, dates: true })
    const sections = [
      { id: 'identity', label: '👤 Identity' },
      { id: 'password', label: '🔑 Password' },
      { id: 'permissions', label: '🛡️ Permissions' },
      { id: 'groups', label: '👥 Groups' },
      { id: 'user_permissions', label: '🔐 User Permissions' },
      { id: 'dates', label: '📅 Dates' }
    ]
    const showDeleteModal = ref(false)
    const selectedUser = ref(null)
    const userToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      confirm_password: '',
      is_active: true,
      is_staff: false,
      is_superuser: false,
      groups: [],
      user_permissions: []
    })

    const filteredUsers = computed(() => {
      let result = users.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(u => u.username?.toLowerCase().includes(term) || u.email?.toLowerCase().includes(term) || u.first_name?.toLowerCase().includes(term) || u.last_name?.toLowerCase().includes(term))
      }
      if (statusFilter.value) {
        result = result.filter(u => u.is_active === (statusFilter.value === 'true'))
      }
      return result
    })

    const fetchUsers = async () => {
      try {
        const data = await makeRequest('get', 'suapi/users/')
        users.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/users/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchUsers(), fetchStats()])
    const { optimisticRemove } = useOptimistic(users, fetchUsers, invalidateCache, 'suapi/users')
    
    const fetchGroupsAndPerms = async () => {
      try {
        const [g, p] = await Promise.all([
          makeRequest('get', 'suapi/users/all_groups/'),
          makeRequest('get', 'suapi/users/all_permissions/')
        ])
        allGroups.value = g
        allPermissions.value = p
      } catch (e) { console.error('Failed to load groups/perms', e) }
    }

    const availableGroups = computed(() =>
      allGroups.value.filter(g =>
        !formData.value.groups.find(fg => fg.id === g.id) &&
        g.name.toLowerCase().includes(groupSearch.value.toLowerCase())
      )
    )

    const filteredPermissions = computed(() => {
      if (!permSearch.value) return allPermissions.value
      const q = permSearch.value.toLowerCase()
      const result = {}
      for (const [app, perms] of Object.entries(allPermissions.value)) {
        const filtered = perms.filter(p => p.codename.includes(q) || p.content_type__model.includes(q))
        if (filtered.length) result[app] = filtered
      }
      return result
    })

    const addGroup = (g) => { formData.value.groups.push(g) }
    const removeGroup = (g) => { formData.value.groups = formData.value.groups.filter(fg => fg.id !== g.id) }
    const isPermSelected = (id) => formData.value.user_permissions.some(p => p.id === id)
    const togglePerm = (p) => {
      if (isPermSelected(p.id)) formData.value.user_permissions = formData.value.user_permissions.filter(fp => fp.id !== p.id)
      else formData.value.user_permissions.push(p)
    }
    const allAppPermsSelected = (app, perms) => perms.every(p => isPermSelected(p.id))
    const toggleAppPerms = (app, perms) => {
      if (allAppPermsSelected(app, perms)) formData.value.user_permissions = formData.value.user_permissions.filter(fp => !perms.find(p => p.id === fp.id))
      else perms.forEach(p => { if (!isPermSelected(p.id)) formData.value.user_permissions.push(p) })
    }
    const doResetPassword = async () => {
      if (!resetPwdValue.value) return
      try {
        await makeRequest('post', `suapi/users/${selectedUser.value.id}/reset_password/`, { password: resetPwdValue.value })
        showResetPwd.value = false
        resetPwdValue.value = ''
        alert('Password reset successfully')
      } catch (e) { alert('Reset failed') }
    }

    const openAddModal = () => {
      selectedUser.value = null
      formData.value = { username: '', email: '', first_name: '', last_name: '', password: '', confirm_password: '', is_active: true, is_staff: false, is_superuser: false, groups: [], user_permissions: [] }
      showResetPwd.value = false
      fetchGroupsAndPerms()
      showFormModal.value = true
    }

    const openEditModal = async (user) => {
      selectedUser.value = user
      activeSection.value = 'identity'
      showFormModal.value = true
      showResetPwd.value = false
      fetchGroupsAndPerms()
      try {
        const full = await makeRequest('get', `suapi/users/${user.id}/`)
        selectedUser.value = full
        formData.value = {
          username: full.username,
          email: full.email || '',
          first_name: full.first_name || '',
          last_name: full.last_name || '',
          password: '',
          is_active: full.is_active,
          is_staff: full.is_staff,
          is_superuser: full.is_superuser,
          groups: full.group_names || [],
          user_permissions: full.permission_codenames || []
        }
      } catch (err) {
        console.error('Error fetching user detail:', err)
      }
    }

    const closeFormModal = () => {
      showFormModal.value = false
      selectedUser.value = null
      formData.value = { username: '', email: '', first_name: '', last_name: '', password: '', confirm_password: '', is_active: true, is_staff: false, is_superuser: false, groups: [], user_permissions: [] }
    }

    const saveUser = async () => {
      // Validate passwords match when creating new user
      if (!selectedUser.value?.id) {
        if (!formData.value.password) {
          alert('Password is required for new users')
          return
        }
        if (formData.value.password !== formData.value.confirm_password) {
          alert('Passwords do not match')
          return
        }
      }
      
      saveLoading.value = true
      try {
        const payload = { ...formData.value }
        delete payload.confirm_password
        if (!payload.password) delete payload.password
        payload.groups = formData.value.groups.map(g => g.id)
        payload.user_permissions = formData.value.user_permissions.map(p => p.id)
        
        if (selectedUser.value?.id) {
          await makeRequest('patch', `suapi/users/${selectedUser.value.id}/`, payload)
        } else {
          await makeRequest('post', 'suapi/users/', payload)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const openDeleteModal = (user) => { userToDelete.value = user; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; userToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      const id = userToDelete.value.id
      optimisticRemove(id)
      closeDeleteModal()
      try {
        await makeRequest('delete', `suapi/users/${id}/`)
      } catch (err) {
        await refreshData() // rollback
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const formatDate = (d) => d ? new Date(d).toLocaleString() : 'N/A'

    const getInitials = (name) => {      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }

    onMounted(refreshData)

    return {
      loading, error, users, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedUser, userToDelete,
      saveLoading, deleteLoading, formData, filteredUsers, fetchUsers, refreshData,
      openAddModal, openEditModal, closeFormModal, saveUser, openDeleteModal, closeDeleteModal, confirmDelete, getInitials, formatDate,
      allGroups, allPermissions, groupSearch, permSearch, showResetPwd, resetPwdValue, activeSection, sections, open, openApps,
      availableGroups, filteredPermissions, addGroup, removeGroup, isPermSelected, togglePerm,
      allAppPermsSelected, toggleAppPerms, doResetPassword
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
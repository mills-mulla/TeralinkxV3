<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Custom Dashboard Builder</h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Drag and drop widgets to customize your dashboard</p>
      </div>
      <div class="flex items-center gap-2">
        <button 
          @click="resetLayout"
          class="px-3 py-2 text-xs bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg transition-colors"
        >
          Reset
        </button>
        <button 
          @click="saveLayout"
          class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
        >
          Save Layout
        </button>
      </div>
    </div>

    <!-- Available Widgets -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <h3 class="text-sm font-medium text-slate-900 dark:text-white mb-3">Available Widgets</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
        <button
          v-for="widget in availableWidgets"
          :key="widget.id"
          @click="addWidget(widget)"
          class="p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 transition-colors text-left"
        >
          <div class="flex items-center gap-2 mb-1">
            <span v-html="widget.icon"></span>
            <span class="text-xs font-medium text-slate-900 dark:text-white">{{ widget.name }}</span>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400">{{ widget.description }}</p>
        </button>
      </div>
    </div>

    <!-- Dashboard Preview -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <h3 class="text-sm font-medium text-slate-900 dark:text-white mb-3">Dashboard Preview</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(widget, index) in activeWidgets"
          :key="index"
          class="p-4 rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-600 relative group"
        >
          <button
            @click="removeWidget(index)"
            class="absolute top-2 right-2 p-1 bg-red-500 hover:bg-red-600 text-white rounded opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <div class="flex items-center gap-2 mb-2">
            <span v-html="widget.icon"></span>
            <span class="text-sm font-medium text-slate-900 dark:text-white">{{ widget.name }}</span>
          </div>
          <div class="h-24 bg-slate-100 dark:bg-slate-700 rounded flex items-center justify-center">
            <span class="text-xs text-slate-400">Widget Preview</span>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-if="activeWidgets.length === 0" class="col-span-full text-center py-12">
          <svg class="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-sm text-slate-500 dark:text-slate-400">No widgets added yet</p>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">Click on widgets above to add them</p>
        </div>
      </div>
    </div>

    <!-- Saved Layouts -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <h3 class="text-sm font-medium text-slate-900 dark:text-white mb-3">Saved Layouts</h3>
      <div class="space-y-2">
        <div
          v-for="(layout, index) in savedLayouts"
          :key="index"
          class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
        >
          <div>
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ layout.name }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ layout.widgets.length }} widgets</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="loadLayout(layout)"
              class="px-3 py-1 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
            >
              Load
            </button>
            <button
              @click="deleteLayout(index)"
              class="px-3 py-1 text-xs bg-red-500 hover:bg-red-600 text-white rounded transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
        <div v-if="savedLayouts.length === 0" class="text-center py-4 text-xs text-slate-400">
          No saved layouts
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardBuilder',
  data() {
    return {
      activeWidgets: [],
      savedLayouts: [],
      availableWidgets: [
        { id: 1, name: 'Revenue', icon: '<svg class="w-4 h-4 text-emerald-500" fill="currentColor" viewBox="0 0 24 24"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>', description: 'Track revenue' },
        { id: 2, name: 'Users', icon: '<svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>', description: 'User metrics' },
        { id: 3, name: 'Sessions', icon: '<svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>', description: 'Active sessions' },
        { id: 4, name: 'Packages', icon: '<svg class="w-4 h-4 text-cyan-500" fill="currentColor" viewBox="0 0 24 24"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4z"/></svg>', description: 'Package sales' },
        { id: 5, name: 'Locations', icon: '<svg class="w-4 h-4 text-rose-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>', description: 'Location stats' },
        { id: 6, name: 'Churn Risk', icon: '<svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>', description: 'At-risk users' },
        { id: 7, name: 'Forecast', icon: '<svg class="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>', description: 'Revenue forecast' },
        { id: 8, name: 'Network', icon: '<svg class="w-4 h-4 text-indigo-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>', description: 'Network health' }
      ]
    }
  },
  mounted() {
    this.loadSavedLayouts()
  },
  methods: {
    addWidget(widget) {
      this.activeWidgets.push({ ...widget })
    },
    removeWidget(index) {
      this.activeWidgets.splice(index, 1)
    },
    saveLayout() {
      const name = prompt('Enter layout name:')
      if (name) {
        this.savedLayouts.push({
          name,
          widgets: [...this.activeWidgets],
          createdAt: new Date().toISOString()
        })
        localStorage.setItem('dashboardLayouts', JSON.stringify(this.savedLayouts))
        alert('Layout saved successfully!')
      }
    },
    loadLayout(layout) {
      this.activeWidgets = [...layout.widgets]
    },
    deleteLayout(index) {
      if (confirm('Delete this layout?')) {
        this.savedLayouts.splice(index, 1)
        localStorage.setItem('dashboardLayouts', JSON.stringify(this.savedLayouts))
      }
    },
    resetLayout() {
      if (confirm('Reset to default layout?')) {
        this.activeWidgets = []
      }
    },
    loadSavedLayouts() {
      const saved = localStorage.getItem('dashboardLayouts')
      if (saved) {
        this.savedLayouts = JSON.parse(saved)
      }
    }
  }
}
</script>

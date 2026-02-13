<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Custom Dashboard Builder</h2>
        <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">Create your personalized analytics dashboard</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="showTemplates = true" class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
          </svg>
          Templates
        </button>
        <button @click="resetLayout" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm transition-colors">
          Reset
        </button>
        <button @click="saveLayout" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
          </svg>
          Save Layout
        </button>
      </div>
    </div>

    <!-- Widget Library -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Widget Library</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <button
          v-for="widget in availableWidgets"
          :key="widget.id"
          @click="addWidget(widget)"
          class="p-4 rounded-lg border-2 border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-lg transition-all text-center group"
        >
          <div class="w-12 h-12 mx-auto mb-2 rounded-lg flex items-center justify-center" :class="widget.color">
            <div v-html="widget.icon"></div>
          </div>
          <p class="text-xs font-medium text-slate-900 dark:text-white">{{ widget.name }}</p>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ widget.size }}</p>
        </button>
      </div>
    </div>

    <!-- Dashboard Canvas -->
    <div class="bg-slate-50 dark:bg-slate-900 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 p-6 min-h-[500px]">
      <div v-if="activeWidgets.length === 0" class="flex flex-col items-center justify-center h-96">
        <svg class="w-20 h-20 text-slate-300 dark:text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
        <p class="text-lg font-medium text-slate-600 dark:text-slate-400">Your dashboard is empty</p>
        <p class="text-sm text-slate-500 dark:text-slate-500 mt-2">Click widgets above to add them to your dashboard</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(widget, index) in activeWidgets"
          :key="index"
          :class="getWidgetClass(widget)"
          class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 relative group shadow-sm hover:shadow-md transition-shadow"
        >
          <div class="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click="moveWidget(index, 'up')" v-if="index > 0" class="p-1 bg-blue-500 hover:bg-blue-600 text-white rounded" title="Move Up">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
              </svg>
            </button>
            <button @click="moveWidget(index, 'down')" v-if="index < activeWidgets.length - 1" class="p-1 bg-blue-500 hover:bg-blue-600 text-white rounded" title="Move Down">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <button @click="removeWidget(index)" class="p-1 bg-red-500 hover:bg-red-600 text-white rounded" title="Remove">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <component :is="getWidgetComponent(widget.type)" :data="widgetData[widget.type]" />
        </div>
      </div>
    </div>

    <!-- Saved Layouts -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Saved Layouts</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="(layout, index) in savedLayouts"
          :key="index"
          class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg border border-slate-200 dark:border-slate-600"
        >
          <div class="flex items-start justify-between mb-3">
            <div>
              <p class="font-medium text-slate-900 dark:text-white">{{ layout.name }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ layout.widgets.length }} widgets</p>
            </div>
            <span class="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">{{ formatDate(layout.createdAt) }}</span>
          </div>
          <div class="flex gap-2">
            <button @click="loadLayout(layout)" class="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors">
              Load
            </button>
            <button @click="deleteLayout(index)" class="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors">
              Delete
            </button>
          </div>
        </div>
        <div v-if="savedLayouts.length === 0" class="col-span-full text-center py-8 text-slate-400">
          No saved layouts yet
        </div>
      </div>
    </div>

    <!-- Templates Modal -->
    <div v-if="showTemplates" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="showTemplates = false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Dashboard Templates</h2>
          <button @click="showTemplates = false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              v-for="template in templates"
              :key="template.id"
              @click="applyTemplate(template)"
              class="p-4 border-2 border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 rounded-lg text-left transition-colors"
            >
              <p class="font-semibold text-slate-900 dark:text-white mb-2">{{ template.name }}</p>
              <p class="text-sm text-slate-600 dark:text-slate-400 mb-3">{{ template.description }}</p>
              <div class="flex flex-wrap gap-1">
                <span v-for="widget in template.widgets" :key="widget" class="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                  {{ widget }}
                </span>
              </div>
            </button>
          </div>
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
      showTemplates: false,
      widgetData: {},
      availableWidgets: [
        { id: 1, name: 'Revenue', type: 'revenue', size: 'Medium', color: 'bg-emerald-100 dark:bg-emerald-500/20', icon: '<svg class="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="currentColor" viewBox="0 0 24 24"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>' },
        { id: 2, name: 'Users', type: 'users', size: 'Small', color: 'bg-blue-100 dark:bg-blue-500/20', icon: '<svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>' },
        { id: 3, name: 'Sessions', type: 'sessions', size: 'Small', color: 'bg-purple-100 dark:bg-purple-500/20', icon: '<svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>' },
        { id: 4, name: 'Packages', type: 'packages', size: 'Medium', color: 'bg-cyan-100 dark:bg-cyan-500/20', icon: '<svg class="w-6 h-6 text-cyan-600 dark:text-cyan-400" fill="currentColor" viewBox="0 0 24 24"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4z"/></svg>' },
        { id: 5, name: 'Locations', type: 'locations', size: 'Medium', color: 'bg-rose-100 dark:bg-rose-500/20', icon: '<svg class="w-6 h-6 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>' },
        { id: 6, name: 'Churn', type: 'churn', size: 'Small', color: 'bg-red-100 dark:bg-red-500/20', icon: '<svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>' }
      ],
      templates: [
        { id: 1, name: 'Executive Dashboard', description: 'High-level overview for executives', widgets: ['Revenue', 'Users', 'Sessions'] },
        { id: 2, name: 'Sales Dashboard', description: 'Focus on revenue and packages', widgets: ['Revenue', 'Packages', 'Locations'] },
        { id: 3, name: 'Operations Dashboard', description: 'Monitor system health', widgets: ['Sessions', 'Users', 'Churn'] },
        { id: 4, name: 'Complete Overview', description: 'All key metrics', widgets: ['Revenue', 'Users', 'Sessions', 'Packages', 'Locations', 'Churn'] }
      ]
    }
  },
  mounted() {
    this.loadSavedLayouts()
    this.fetchWidgetData()
  },
  methods: {
    async fetchWidgetData() {
      try {
        const token = localStorage.getItem('access_token')
        const headers = { 'Authorization': `Bearer ${token}` }
        
        const [metrics, packages, locations] = await Promise.all([
          fetch('https://service.teralinkxwaves.uk/suapi/dashboard-metrics/', { headers }).then(r => r.json()),
          fetch('https://service.teralinkxwaves.uk/suapi/dashboard-metrics/package-sales/', { headers }).then(r => r.json()),
          fetch('https://service.teralinkxwaves.uk/suapi/dashboard-metrics/location-performance/', { headers }).then(r => r.json())
        ])
        
        this.widgetData = {
          revenue: { total: metrics.totalRevenue, trend: metrics.revenueTrend },
          users: { total: metrics.totalClients, active: metrics.activeUsers },
          sessions: { active: metrics.activeUsers },
          packages: packages.data || [],
          locations: locations.data || [],
          churn: { rate: 5.2, atRisk: 12 }
        }
      } catch (error) {
        console.error('Error fetching widget data:', error)
      }
    },
    addWidget(widget) {
      this.activeWidgets.push({ ...widget })
    },
    removeWidget(index) {
      this.activeWidgets.splice(index, 1)
    },
    moveWidget(index, direction) {
      const newIndex = direction === 'up' ? index - 1 : index + 1
      const widget = this.activeWidgets.splice(index, 1)[0]
      this.activeWidgets.splice(newIndex, 0, widget)
    },
    getWidgetClass(widget) {
      return widget.size === 'Large' ? 'md:col-span-2' : ''
    },
    getWidgetComponent(type) {
      const components = {
        revenue: { template: '<div><p class="text-xs text-slate-500 dark:text-slate-400 mb-1">Total Revenue</p><p class="text-2xl font-bold text-slate-900 dark:text-white">KES {{ data?.total || 0 }}</p><p class="text-xs text-emerald-600 mt-1">↑ {{ data?.trend || "up" }}</p></div>', props: ['data'] },
        users: { template: '<div><p class="text-xs text-slate-500 dark:text-slate-400 mb-1">Total Users</p><p class="text-2xl font-bold text-slate-900 dark:text-white">{{ data?.total || 0 }}</p><p class="text-xs text-slate-600 dark:text-slate-400 mt-1">{{ data?.active || 0 }} active</p></div>', props: ['data'] },
        sessions: { template: '<div><p class="text-xs text-slate-500 dark:text-slate-400 mb-1">Active Sessions</p><p class="text-2xl font-bold text-slate-900 dark:text-white">{{ data?.active || 0 }}</p></div>', props: ['data'] },
        packages: { template: '<div><p class="text-xs text-slate-500 dark:text-slate-400 mb-2">Top Packages</p><div class="space-y-1"><div v-for="pkg in (data || []).slice(0,3)" :key="pkg.package__name" class="text-xs"><span class="font-medium text-slate-900 dark:text-white">{{ pkg.package__name }}</span><span class="text-slate-500 ml-2">{{ pkg.count }}</span></div></div></div>', props: ['data'] },
        locations: { template: '<div><p class="text-xs text-slate-500 dark:text-slate-400 mb-2">Top Locations</p><div class="space-y-1"><div v-for="loc in (data || []).slice(0,3)" :key="loc.location__name" class="text-xs"><span class="font-medium text-slate-900 dark:text-white">{{ loc.location__name }}</span><span class="text-slate-500 ml-2">{{ loc.sales }}</span></div></div></div>', props: ['data'] },
        churn: { template: '<div><p class="text-xs text-slate-500 dark:text-slate-400 mb-1">Churn Rate</p><p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ data?.rate || 0 }}%</p><p class="text-xs text-slate-600 dark:text-slate-400 mt-1">{{ data?.atRisk || 0 }} at risk</p></div>', props: ['data'] }
      }
      return components[type] || { template: '<div>Widget</div>' }
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
        alert('Layout saved!')
      }
    },
    loadLayout(layout) {
      this.activeWidgets = [...layout.widgets]
      this.showTemplates = false
    },
    deleteLayout(index) {
      if (confirm('Delete this layout?')) {
        this.savedLayouts.splice(index, 1)
        localStorage.setItem('dashboardLayouts', JSON.stringify(this.savedLayouts))
      }
    },
    resetLayout() {
      if (confirm('Clear all widgets?')) {
        this.activeWidgets = []
      }
    },
    applyTemplate(template) {
      this.activeWidgets = template.widgets.map(name => 
        this.availableWidgets.find(w => w.name === name)
      ).filter(Boolean)
      this.showTemplates = false
    },
    loadSavedLayouts() {
      const saved = localStorage.getItem('dashboardLayouts')
      if (saved) this.savedLayouts = JSON.parse(saved)
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }
  }
}
</script>

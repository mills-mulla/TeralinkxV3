<template>
  <div class="relative">
    <button 
      @click="showMenu = !showMenu"
      class="flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors text-sm"
      :disabled="loading"
    >
      <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>Export</span>
    </button>

    <div v-if="showMenu" class="absolute top-full mt-2 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 w-48">
      <div class="py-2">
        <button 
          @click="exportData('csv')"
          class="w-full px-4 py-2 text-left text-sm text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
        >
          <svg class="w-4 h-4 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          </svg>
          <span>Export as CSV</span>
        </button>
        <button 
          @click="exportData('excel')"
          class="w-full px-4 py-2 text-left text-sm text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
        >
          <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          </svg>
          <span>Export as Excel</span>
        </button>
        <button 
          @click="exportData('pdf')"
          class="w-full px-4 py-2 text-left text-sm text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
        >
          <svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/>
          </svg>
          <span>Export as PDF</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExportButton',
  props: {
    data: {
      type: [Array, Object],
      required: true
    },
    filename: {
      type: String,
      default: 'export'
    }
  },
  data() {
    return {
      showMenu: false,
      loading: false
    }
  },
  methods: {
    async exportData(format) {
      this.loading = true
      this.showMenu = false

      try {
        if (format === 'csv') {
          this.exportCSV()
        } else if (format === 'excel') {
          this.exportExcel()
        } else if (format === 'pdf') {
          this.exportPDF()
        }
      } catch (error) {
        console.error('Export error:', error)
        alert('Export failed. Please try again.')
      } finally {
        this.loading = false
      }
    },

    exportCSV() {
      const data = Array.isArray(this.data) ? this.data : [this.data]
      if (data.length === 0) return

      const headers = Object.keys(data[0])
      const csv = [
        headers.join(','),
        ...data.map(row => headers.map(h => JSON.stringify(row[h] || '')).join(','))
      ].join('\n')

      this.downloadFile(csv, `${this.filename}.csv`, 'text/csv')
    },

    exportExcel() {
      // For now, export as CSV with .xlsx extension
      // In production, use a library like xlsx or exceljs
      const data = Array.isArray(this.data) ? this.data : [this.data]
      if (data.length === 0) return

      const headers = Object.keys(data[0])
      const csv = [
        headers.join(','),
        ...data.map(row => headers.map(h => JSON.stringify(row[h] || '')).join(','))
      ].join('\n')

      this.downloadFile(csv, `${this.filename}.xlsx`, 'application/vnd.ms-excel')
    },

    exportPDF() {
      // Basic PDF export - in production use jsPDF or similar
      const data = Array.isArray(this.data) ? this.data : [this.data]
      const content = JSON.stringify(data, null, 2)
      
      this.downloadFile(content, `${this.filename}.pdf`, 'application/pdf')
    },

    downloadFile(content, filename, mimeType) {
      const blob = new Blob([content], { type: mimeType })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
  }
}
</script>

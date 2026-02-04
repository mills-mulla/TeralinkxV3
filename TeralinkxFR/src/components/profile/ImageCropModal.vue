<template>
  <div class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[95vh] overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-xl font-bold text-gray-800 dark:text-white">Crop Profile Image</h3>
        <button @click="cancel" class="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
      
      <div class="p-6 space-y-6">
        <!-- Crop Controls -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Aspect Ratio</label>
            <select v-model="cropSettings.aspectRatio" @change="updateAspectRatio" class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option value="1:1">Square (1:1)</option>
              <option value="4:3">Standard (4:3)</option>
              <option value="16:9">Wide (16:9)</option>
              <option value="free">Free Form</option>
            </select>
          </div>
          
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Zoom</label>
            <input v-model.number="cropSettings.zoom" @input="updateZoom" type="range" min="0.5" max="3" step="0.1" class="w-full">
          </div>
          
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Quality</label>
            <select v-model="cropSettings.quality" class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option value="0.9">High (90%)</option>
              <option value="0.8">Medium (80%)</option>
              <option value="0.7">Low (70%)</option>
            </select>
          </div>
          
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Actions</label>
            <div class="flex space-x-1">
              <button @click="rotateImage(-90)" class="flex-1 p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg">
                <svg class="w-4 h-4 mx-auto" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M7.11 8.53L5.7 7.11C4.8 8.27 4.24 9.61 4.07 11h2.02c.14-.87.49-1.72 1.02-2.47z"/>
                </svg>
              </button>
              <button @click="rotateImage(90)" class="flex-1 p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg">
                <svg class="w-4 h-4 mx-auto" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M15.55 5.55L11 1v3.07C7.06 4.56 4 7.92 4 12s3.05 7.44 7 7.93v-2.02c-2.84-.48-5-2.94-5-5.91s2.16-5.43 5-5.91V10l4.55-4.45z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Crop Area -->
        <div class="relative bg-gray-100 dark:bg-gray-700 rounded-xl overflow-hidden border-2 border-dashed border-gray-300 dark:border-gray-600">
          <canvas
            ref="cropCanvas"
            @mousedown="startCrop"
            @mousemove="updateCrop"
            @mouseup="endCrop"
            @mouseleave="endCrop"
            @touchstart="startCrop"
            @touchmove="updateCrop"
            @touchend="endCrop"
            @wheel="handleWheel"
            width="600"
            height="400"
            class="w-full h-full cursor-crosshair touch-none"
          />
          
          <!-- Crop Info -->
          <div class="absolute top-4 left-4 bg-black bg-opacity-75 text-white px-3 py-2 rounded-lg text-sm">
            <div>{{ Math.round(cropData.width) }} × {{ Math.round(cropData.height) }}px</div>
            <div class="text-xs opacity-75">{{ cropSettings.aspectRatio }} • {{ Math.round(cropSettings.zoom * 100) }}%</div>
          </div>
        </div>
        
        <!-- Preview -->
        <div class="flex items-center space-x-4">
          <div class="text-sm font-medium text-gray-700 dark:text-gray-300">Preview:</div>
          <div class="w-16 h-16 rounded-full overflow-hidden border-2 border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-700">
            <canvas ref="previewCanvas" width="64" height="64" class="w-full h-full"/>
          </div>
          <div class="flex-1 text-sm text-gray-500 dark:text-gray-400">
            This is how your profile image will appear
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="flex space-x-3">
          <button @click="resetCrop" class="flex-1 px-4 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium">
            Reset
          </button>
          <button @click="applyCrop" class="flex-1 px-4 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium">
            Apply & Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

const props = defineProps({
  image: {
    type: File,
    required: true
  }
})

const emit = defineEmits(['save', 'cancel'])

// Refs
const cropCanvas = ref(null)
const previewCanvas = ref(null)
const originalImage = ref(null)

// State
const cropData = ref({ x: 50, y: 50, width: 200, height: 200 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const cropSettings = ref({
  aspectRatio: '1:1',
  zoom: 1,
  rotation: 0,
  quality: 0.9
})

// Methods
const initializeCrop = () => {
  if (!cropCanvas.value || !originalImage.value) return
  
  const canvas = cropCanvas.value
  const ctx = canvas.getContext('2d')
  const img = originalImage.value
  
  canvas.width = 600
  canvas.height = 400
  
  const scale = Math.min(canvas.width / img.width, canvas.height / img.height) * 0.8
  const scaledWidth = img.width * scale
  const scaledHeight = img.height * scale
  const offsetX = (canvas.width - scaledWidth) / 2
  const offsetY = (canvas.height - scaledHeight) / 2
  
  const cropSize = Math.min(scaledWidth, scaledHeight) * 0.8
  cropData.value = {
    x: offsetX + (scaledWidth - cropSize) / 2,
    y: offsetY + (scaledHeight - cropSize) / 2,
    width: cropSize,
    height: cropSize,
    imageOffsetX: offsetX,
    imageOffsetY: offsetY,
    imageWidth: scaledWidth,
    imageHeight: scaledHeight,
    scale: scale
  }
  
  drawCropOverlay()
  updatePreview()
}

const drawCropOverlay = () => {
  if (!cropCanvas.value || !originalImage.value) return
  
  const canvas = cropCanvas.value
  const ctx = canvas.getContext('2d')
  const img = originalImage.value
  const crop = cropData.value
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(img, crop.imageOffsetX, crop.imageOffsetY, crop.imageWidth, crop.imageHeight)
  
  // Overlay
  ctx.fillStyle = 'rgba(0, 0, 0, 0.6)'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  
  // Clear crop area
  ctx.clearRect(crop.x, crop.y, crop.width, crop.height)
  
  // Redraw image in crop area
  const sx = (crop.x - crop.imageOffsetX) / crop.scale
  const sy = (crop.y - crop.imageOffsetY) / crop.scale
  const sw = crop.width / crop.scale
  const sh = crop.height / crop.scale
  
  ctx.drawImage(img, sx, sy, sw, sh, crop.x, crop.y, crop.width, crop.height)
  
  // Crop border
  ctx.strokeStyle = '#3b82f6'
  ctx.lineWidth = 2
  ctx.strokeRect(crop.x, crop.y, crop.width, crop.height)
}

const updatePreview = () => {
  if (!previewCanvas.value || !originalImage.value) return
  
  const canvas = previewCanvas.value
  const ctx = canvas.getContext('2d')
  const img = originalImage.value
  const crop = cropData.value
  
  canvas.width = 64
  canvas.height = 64
  
  ctx.clearRect(0, 0, 64, 64)
  
  // Circular clip
  ctx.beginPath()
  ctx.arc(32, 32, 32, 0, 2 * Math.PI)
  ctx.clip()
  
  const sx = (crop.x - crop.imageOffsetX) / crop.scale
  const sy = (crop.y - crop.imageOffsetY) / crop.scale
  const sw = crop.width / crop.scale
  const sh = crop.height / crop.scale
  
  ctx.drawImage(img, sx, sy, sw, sh, 0, 0, 64, 64)
}

const startCrop = (event) => {
  event.preventDefault()
  isDragging.value = true
  const rect = cropCanvas.value.getBoundingClientRect()
  const x = (event.clientX || event.touches[0].clientX) - rect.left
  const y = (event.clientY || event.touches[0].clientY) - rect.top
  dragStart.value = { x: x - cropData.value.x, y: y - cropData.value.y }
}

const updateCrop = (event) => {
  if (!isDragging.value) return
  event.preventDefault()
  
  const rect = cropCanvas.value.getBoundingClientRect()
  const x = (event.clientX || event.touches[0].clientX) - rect.left
  const y = (event.clientY || event.touches[0].clientY) - rect.top
  
  cropData.value.x = Math.max(cropData.value.imageOffsetX, 
    Math.min(x - dragStart.value.x, cropData.value.imageOffsetX + cropData.value.imageWidth - cropData.value.width))
  cropData.value.y = Math.max(cropData.value.imageOffsetY,
    Math.min(y - dragStart.value.y, cropData.value.imageOffsetY + cropData.value.imageHeight - cropData.value.height))
  
  drawCropOverlay()
  updatePreview()
}

const endCrop = () => {
  isDragging.value = false
}

const handleWheel = (event) => {
  event.preventDefault()
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  cropSettings.value.zoom = Math.max(0.5, Math.min(3, cropSettings.value.zoom + delta))
  updateZoom()
}

const updateAspectRatio = () => {
  // Recalculate crop dimensions based on aspect ratio
  drawCropOverlay()
  updatePreview()
}

const updateZoom = () => {
  drawCropOverlay()
  updatePreview()
}

const rotateImage = (degrees) => {
  cropSettings.value.rotation = (cropSettings.value.rotation + degrees) % 360
  drawCropOverlay()
  updatePreview()
}

const resetCrop = () => {
  cropSettings.value = {
    aspectRatio: '1:1',
    zoom: 1,
    rotation: 0,
    quality: 0.9
  }
  initializeCrop()
}

const applyCrop = () => {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  const crop = cropData.value
  
  canvas.width = 400
  canvas.height = 400
  
  const sx = (crop.x - crop.imageOffsetX) / crop.scale
  const sy = (crop.y - crop.imageOffsetY) / crop.scale
  const sw = crop.width / crop.scale
  const sh = crop.height / crop.scale
  
  ctx.drawImage(originalImage.value, sx, sy, sw, sh, 0, 0, 400, 400)
  
  canvas.toBlob((blob) => {
    const file = new File([blob], 'profile.jpg', { type: 'image/jpeg' })
    emit('save', file)
  }, 'image/jpeg', cropSettings.value.quality)
}

const cancel = () => {
  emit('cancel')
}

// Initialize
onMounted(() => {
  const reader = new FileReader()
  reader.onload = (e) => {
    originalImage.value = new Image()
    originalImage.value.onload = () => {
      nextTick(() => initializeCrop())
    }
    originalImage.value.src = e.target.result
  }
  reader.readAsDataURL(props.image)
})
</script>
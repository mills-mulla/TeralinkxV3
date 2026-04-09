<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto transition-colors duration-300">
      <!-- Header -->
      <div class="p-5 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white flex items-center">
          {{ isEdit ? `✏️ Edit ${title}` : `➕ Add New ${title}` }}
        </h3>
      </div>
      
      <!-- Body -->
      <div class="p-5">
        <div :class="gridClass">
          <div
            v-for="field in fields"
            :key="field.key"
            :class="field.colSpan || 'col-span-1'"
          >
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              {{ field.label }}
              <span v-if="field.required" class="text-rose-500 dark:text-rose-400">*</span>
            </label>
            
            <!-- Text Input -->
            <input
              v-if="field.type === 'text' || field.type === 'email' || field.type === 'password'"
              v-model="formData[field.key]"
              :type="field.type"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :required="field.required"
              class="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900 dark:text-white transition-all duration-200"
            />
            
            <!-- Number Input -->
            <input
              v-else-if="field.type === 'number'"
              v-model.number="formData[field.key]"
              type="number"
              :step="field.step || '1'"
              :min="field.min"
              :max="field.max"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :required="field.required"
              class="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900 dark:text-white transition-all duration-200"
            />
            
            <!-- Select -->
            <select
              v-else-if="field.type === 'select'"
              v-model="formData[field.key]"
              :disabled="field.disabled"
              :required="field.required"
              class="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900 dark:text-white transition-all duration-200"
            >
              <option value="">{{ field.placeholder || 'Select an option' }}</option>
              <option
                v-for="option in field.options"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
            
            <!-- Textarea -->
            <textarea
              v-else-if="field.type === 'textarea'"
              v-model="formData[field.key]"
              :rows="field.rows || 3"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :required="field.required"
              class="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900 dark:text-white transition-all duration-200"
            ></textarea>
            
            <!-- Checkbox -->
            <div v-else-if="field.type === 'checkbox'" class="flex items-center">
              <input
                v-model="formData[field.key]"
                type="checkbox"
                :disabled="field.disabled"
                class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-slate-600 dark:text-slate-400">{{ field.checkboxLabel }}</span>
            </div>
            
            <!-- Date -->
            <input
              v-else-if="field.type === 'date' || field.type === 'datetime-local'"
              v-model="formData[field.key]"
              :type="field.type"
              :disabled="field.disabled"
              :required="field.required"
              class="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900 dark:text-white transition-all duration-200"
            />
            
            <!-- Custom Slot -->
            <slot v-else :name="`field-${field.key}`" :field="field" :formData="formData"></slot>
            
            <!-- Help Text -->
            <p v-if="field.help" class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ field.help }}</p>
            
            <!-- Error Message -->
            <p v-if="errors[field.key]" class="mt-1 text-xs text-rose-600 dark:text-rose-400">{{ errors[field.key] }}</p>
          </div>
        </div>
        
        <!-- Custom Content Slot -->
        <slot name="custom-content" :formData="formData"></slot>
      </div>
      
      <!-- Footer -->
      <div class="flex justify-end gap-3 px-5 py-4 border-t border-slate-200 dark:border-slate-700">
        <button
          @click="$emit('close')"
          class="px-5 py-2 border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-400 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-all duration-200"
        >
          Cancel
        </button>
        <button
          @click="handleSubmit"
          :disabled="loading"
          :class="[
            'px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 shadow-sm hover:shadow flex items-center gap-2',
            loading ? 'opacity-50 cursor-not-allowed' : ''
          ]"
        >
          <ArrowPathIcon v-if="loading" class="w-4 h-4 animate-spin" />
          <span>{{ isEdit ? 'Update' : 'Create' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'FormModal',
  components: {
    ArrowPathIcon
  },
  props: {
    show: { type: Boolean, required: true },
    title: { type: String, required: true },
    fields: { type: Array, required: true },
    initialData: { type: Object, default: () => ({}) },
    loading: { type: Boolean, default: false },
    gridCols: { type: Number, default: 2 }
  },
  emits: ['close', 'submit'],
  setup(props, { emit }) {
    const formData = ref({})
    const errors = ref({})
    
    const gridClass = `grid grid-cols-1 lg:grid-cols-${props.gridCols} gap-6`
    
    const isEdit = computed(() => !!props.initialData?.id)
    
    // Initialize form data
    watch(() => props.show, (newVal) => {
      if (newVal) {
        initializeForm()
      }
    }, { immediate: true })
    
    watch(() => props.initialData, () => {
      if (props.show) {
        initializeForm()
      }
    }, { deep: true })
    
    const initializeForm = () => {
      formData.value = {}
      errors.value = {}
      
      props.fields.forEach(field => {
        if (props.initialData && props.initialData[field.key] !== undefined) {
          formData.value[field.key] = props.initialData[field.key]
        } else {
          formData.value[field.key] = field.default ?? (field.type === 'checkbox' ? false : '')
        }
      })
    }
    
    const validate = () => {
      errors.value = {}
      let isValid = true
      
      props.fields.forEach(field => {
        if (field.required && !formData.value[field.key]) {
          errors.value[field.key] = `${field.label} is required`
          isValid = false
        }
        
        if (field.validate) {
          const error = field.validate(formData.value[field.key], formData.value)
          if (error) {
            errors.value[field.key] = error
            isValid = false
          }
        }
      })
      
      return isValid
    }
    
    const handleSubmit = () => {
      if (validate()) {
        emit('submit', { ...formData.value })
      }
    }
    
    return {
      formData,
      errors,
      gridClass,
      isEdit,
      handleSubmit
    }
  }
}
</script>

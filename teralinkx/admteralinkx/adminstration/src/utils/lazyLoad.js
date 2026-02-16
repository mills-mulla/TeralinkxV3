import { defineAsyncComponent } from 'vue'

export const lazyLoad = (componentPath) => {
  return defineAsyncComponent({
    loader: () => import(componentPath),
    delay: 200,
    timeout: 10000,
    errorComponent: {
      template: '<div class="p-4 text-center text-red-500">Failed to load component</div>'
    },
    loadingComponent: {
      template: '<div class="p-4 text-center"><div class="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div></div>'
    }
  })
}

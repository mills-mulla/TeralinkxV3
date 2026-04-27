/**
 * useOptimistic — Option D: instant local update + background re-fetch to confirm.
 *
 * Usage:
 *   const { optimisticRemove, optimisticUpdate, optimisticAdd } = useOptimistic(listRef, fetchFn, invalidateCache, cachePrefix)
 */
export function useOptimistic(listRef, fetchFn, invalidateCache, cachePrefix = '') {
  // Immediately remove item by id, bust cache, re-fetch silently in background
  const optimisticRemove = (id) => {
    listRef.value = listRef.value.filter(item => item.id !== id)
    invalidateCache(cachePrefix)
    fetchFn().catch(() => {}) // silent background confirm
  }

  // Immediately patch item fields by id, bust cache, re-fetch silently in background
  const optimisticUpdate = (id, patch) => {
    const idx = listRef.value.findIndex(item => item.id === id)
    if (idx !== -1) listRef.value[idx] = { ...listRef.value[idx], ...patch }
    invalidateCache(cachePrefix)
    fetchFn().catch(() => {})
  }

  // Immediately prepend new item, bust cache, re-fetch silently in background
  const optimisticAdd = (item) => {
    listRef.value = [item, ...listRef.value]
    invalidateCache(cachePrefix)
    fetchFn().catch(() => {})
  }

  return { optimisticRemove, optimisticUpdate, optimisticAdd }
}

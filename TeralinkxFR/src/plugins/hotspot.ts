// src/plugins/hotspot.ts
import { reactive, provide, inject, type App } from 'vue';

// Type definitions
interface HotSpotContext {
  mac: string;
  ip: string;
  
}

declare global {
  interface Window {
    hotspotContext?: {
      mac: string;
      ip: string;
     
    };
  }
}

const HotSpotKey = Symbol('hotspot');

// Main plugin object
const hotspotPlugin = {
  install(app: App) {
    // Initialize with reactive data
    const hotspot = reactive<HotSpotContext>({
      mac: window.hotspotContext?.mac || localStorage.getItem('hs_mac') || '',
      ip: window.hotspotContext?.ip || localStorage.getItem('hs_ip') || '',
      ...(window.hotspotContext || {})
    });
    // console.log('Hotspot context check if available in hotspot.ts:',window.hotspotContext)

    // For Options API
    app.config.globalProperties.$hotspot = hotspot;

    // For Composition API
    provide(HotSpotKey, hotspot);

    // Persist data
    if (hotspot.mac) localStorage.setItem('hs_mac', hotspot.mac);
    if (hotspot.ip) localStorage.setItem('hs_ip', hotspot.ip);
  }
};

// Composition API helper
export function useHotspot() {
  const hotspot = inject<HotSpotContext>(HotSpotKey);
  if (!hotspot) {
    throw new Error('HotSpot plugin not installed!');
  }
  return hotspot;
}

// Export the plugin as default
export default hotspotPlugin;
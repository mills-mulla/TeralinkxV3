// src/plugins/hotspot.ts
import { reactive, provide, inject, type App } from 'vue';

// Type definitions
interface HotSpotContext {
  mac: string;
  ip: string;
  timestamp?: number;
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
    // Priority 1: URL parameters (freshest from MikroTik)
    const urlParams = new URLSearchParams(window.location.search);
    const urlIP = urlParams.get('ip');
    const urlMAC = urlParams.get('mac');
    
    // Priority 2: window.hotspotContext (MikroTik injected)
    const windowIP = window.hotspotContext?.ip;
    const windowMAC = window.hotspotContext?.mac;
    
    // Priority 3: sessionStorage
    let sessionContext = null;
    try {
      sessionContext = JSON.parse(sessionStorage.getItem('hotspotContext') || '{}');
    } catch (e) {
      sessionContext = {};
    }
    
    // Priority 4: localStorage
    const localIP = localStorage.getItem('hs_ip');
    const localMAC = localStorage.getItem('hs_mac');
    
    // Determine final values (URL params override everything)
    let finalIP = '';
    let finalMAC = '';
    
    if (urlIP && urlMAC) {
      // URL params present - use them (highest priority)
      finalIP = urlIP;
      finalMAC = urlMAC;
    } else if (windowIP && windowMAC) {
      // window.hotspotContext present
      finalIP = windowIP;
      finalMAC = windowMAC;
    } else if (sessionContext?.ip && sessionContext?.mac) {
      // sessionStorage present
      finalIP = sessionContext.ip;
      finalMAC = sessionContext.mac;
    } else if (localIP && localMAC) {
      // localStorage present
      finalIP = localIP;
      finalMAC = localMAC;
    }
    // If none available, leave empty (will block signin)
    
    // Initialize reactive hotspot data
    const hotspot = reactive<HotSpotContext>({
      mac: finalMAC,
      ip: finalIP,
      timestamp: Date.now()
    });

    // Store in sessionStorage and localStorage if we have valid data
    if (finalIP && finalMAC) {
      sessionStorage.setItem('hotspotContext', JSON.stringify({
        ip: finalIP,
        mac: finalMAC,
        timestamp: Date.now()
      }));
      localStorage.setItem('hs_ip', finalIP);
      localStorage.setItem('hs_mac', finalMAC);
    }

    // For Options API
    app.config.globalProperties.$hotspot = hotspot;

    // For Composition API - provide at app level
    app.provide(HotSpotKey, hotspot);
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
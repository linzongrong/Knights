<script setup>
import { ref, reactive, watch, computed, shallowRef } from 'vue';
import MapContainer from './components/MapContainer.vue';
import StyleSwitcher from './components/StyleSwitcher.vue';
import RegionSelector from './components/RegionSelector.vue';
import DataVisualizer from './components/DataVisualizer.vue';
import FilterBar from './components/FilterBar.vue';
import StatsBasin from './components/StatsBasin.vue'; 
import CustomMap from './components/CustomMap.vue'; 
import CurrentViewStats from './components/CurrentViewStats.vue'; 
import DbhLegend from './components/DbhLegend.vue';
import TopTrees from './components/TopTrees.vue';
import StatsProvince from './components/StatsProvince.vue';
import SystemTime from './components/SystemTime.vue';
import teaPoints from './assets/tea_points.json';
import monitorPoints from './assets/monitor_points.json';
import ecosystemData from './assets/ecosystem.json';

import { useI18n } from './composables/useI18n';

const { t, locale } = useI18n();

const showCustomMap = ref(false);

const mapInstance = ref(null);
const filterParams = ref({ name: '', minDbh: null, maxDbh: null, riverBasin: '' });
const dataVisualizerRef = ref(null);
const currentRegionBoundaries = ref([]);
const currentRegionInfo = ref(null);

// UI Persistence: View Mode
const savedViewMode = localStorage.getItem('app_view_mode');
const currentViewMode = ref(savedViewMode || 'cluster'); 
const currentMapMode = ref('2D'); 

watch(currentViewMode, (val) => {
    localStorage.setItem('app_view_mode', val);
});

// --- Centralized Data Filtering ---
const allDataPoints = ref(teaPoints);
const allMoniterPoints = ref(monitorPoints);
const allEcosystemData = ref(ecosystemData);

// Helper for caching region bounds to avoid re-calculation every filter
const activeRegionBounds = computed(() => {
    if (!currentRegionBoundaries.value || currentRegionBoundaries.value.length === 0) {
        return null;
    }
    let minLng = 180, maxLng = -180, minLat = 90, maxLat = -90;
    currentRegionBoundaries.value.forEach(ring => {
        ring.forEach(coord => {
             const lng = coord.lng || coord[0];
             const lat = coord.lat || coord[1];
             if (lng < minLng) minLng = lng;
             if (lng > maxLng) maxLng = lng;
             if (lat < minLat) minLat = lat;
             if (lat > maxLat) maxLat = lat;
        });
    });
    return { minLng, maxLng, minLat, maxLat };
});

const filteredData = computed(() => {
    const { name, minDbh, maxDbh, riverBasin } = filterParams.value;
    const hasRegionFilter = (currentRegionBoundaries.value && currentRegionBoundaries.value.length > 0) || (currentRegionInfo.value && Object.keys(currentRegionInfo.value).length > 0);
    const bounds = activeRegionBounds.value;
    const regionInfo = currentRegionInfo.value;
    const boundaries = currentRegionBoundaries.value;

    if (!name && (minDbh === null || minDbh === '') && (maxDbh === null || maxDbh === '') && !riverBasin && !hasRegionFilter) {
        return allDataPoints.value;
    }

    return allDataPoints.value.filter(p => {
        // 1. Name Filter
        if (name && !p.name.includes(name)) return false;

        // 2. DBH Filter
        if (minDbh !== null && minDbh !== '' && p.dbh < minDbh) return false;
        if (maxDbh !== null && maxDbh !== '' && p.dbh > maxDbh) return false;

        // 3. Basin Filter
        if (riverBasin) {
            const pBasin = String(p.riverBasin || '').trim();
            if (pBasin !== riverBasin) return false;
        }

        // 4. Region Filter
        // 4. Region Filter
        if (hasRegionFilter) {
            let matchesRegion = false;

            // Optimization 1: Property Match
            if (regionInfo && regionInfo.name) {
                 // Normalize names (remove '省', '市' suffix for loose matching if needed, but data usually aligns)
                 // Actually, let's keep it strict first or use includes?
                 // Current mock data usually has full names or consistent specific overrides.
                 if (regionInfo.level === 'province' && p.province === regionInfo.name) matchesRegion = true;
                 else if (regionInfo.level === 'city' && p.city === regionInfo.name) matchesRegion = true;
                 else if (regionInfo.level === 'district' && p.district === regionInfo.name) matchesRegion = true;
            }

            if (matchesRegion) {
                // Property matched, so it's IN.
                return true;
            }

            // Optimization 2: Bounding Box & Polygon (Spatial Fallback)
            if (bounds) {
                const pLng = Array.isArray(p.lnglat) ? p.lnglat[0] : (p.lnglat.lng || p.lnglat.getLng());
                const pLat = Array.isArray(p.lnglat) ? p.lnglat[1] : (p.lnglat.lat || p.lnglat.getLat());

                if (pLng < bounds.minLng || pLng > bounds.maxLng ||
                    pLat < bounds.minLat || pLat > bounds.maxLat) {
                    return false;
                }
                
                // Exact Check: Point in Polygon
                if (window.AMap && window.AMap.GeometryUtil && boundaries.length > 0) {
                     let inAnyRing = false;
                     for (const ring of boundaries) {
                         if (window.AMap.GeometryUtil.isPointInRing([pLng, pLat], ring)) {
                             inAnyRing = true;
                             break;
                         }
                     }
                     if (!inAnyRing) return false;
                }
            } else {
                // No boundaries available AND property match failed.
                // Must reject to be safe (otherwise we show everything).
                return false;
            }
        }

        return true;
    });
});


// UI Persistence State
// UI Persistence State
const defaultPanelState = {
    filter: true, // Static
    time: true,
    viewStats: true,
    basin_lancang: true,
    basin_ailao: true,
    basin_gaoligong: true,
    styleSwitcher: true,
    regionSelector: true,
    dataVisualizer: true,
    dbhLegend: true,
    topTrees: true,
    statsProvince: true
};

const savedPanelState = localStorage.getItem('app_panel_state');
const panelState = reactive(savedPanelState ? JSON.parse(savedPanelState) : { ...defaultPanelState });

watch(panelState, (newVal) => {
    localStorage.setItem('app_panel_state', JSON.stringify(newVal));
}, { deep: true });

const resetLayout = () => {
    // Restore Layout
    const defL = JSON.parse(JSON.stringify(defaultLayout));
    layout.left = defL.left;
    layout.right = defL.right;
    layout.bottom = defL.bottom;
    
    // Restore Visibility
    Object.assign(panelState, defaultPanelState);
    
    // Clear Storage (optional, but watcher will re-save immediately)
    // localStorage.removeItem('app_layout');
    // localStorage.removeItem('app_panel_state');
};

const componentLabels = computed(() => ({
    filter: t('settings.labels.filter'),
    time: t('settings.labels.time'),
    viewStats: t('settings.labels.viewStats'),
    basin_lancang: t('settings.labels.basin_lancang'),
    basin_ailao: t('settings.labels.basin_ailao'),
    basin_gaoligong: t('settings.labels.basin_gaoligong'),
    styleSwitcher: t('settings.labels.styleSwitcher'),
    regionSelector: t('settings.labels.regionSelector'),
    dataVisualizer: t('settings.labels.dataVisualizer'),
    dbhLegend: t('settings.labels.dbhLegend'),
    topTrees: t('settings.labels.topTrees'),
    statsProvince: t('settings.labels.statsProvince')
}));

const showSettings = ref(false);

const onMapLoad = (map) => {
  mapInstance.value = map;
};

const updateFilters = (params) => {
    filterParams.value = params;
};

const handleConfirm = () => {
    // Direct zoom logic (lifted from DataVisualizer) to avoid dependency on refs in dynamic layout
    if (filteredData.value && filteredData.value.length > 0 && mapInstance.value) {
         const firstPoint = filteredData.value[0];
         // Ensure we have valid coordinates
         if (firstPoint.lnglat) {
             mapInstance.value.setZoomAndCenter(14, firstPoint.lnglat);
         }
    }
};

const onRegionChange = (payload) => {
    if (payload && payload.boundaries) {
        currentRegionBoundaries.value = payload.boundaries;
        currentRegionInfo.value = {
            level: payload.level,
            adcode: payload.adcode,
            name: payload.name
        };
    } else {
        currentRegionBoundaries.value = [];
        currentRegionInfo.value = null;
    }
};

const currentBasinGeoJson = ref(null);

const onBasinSelect = (payload) => {
    // payload: { name, geojson }
    // Toggle logic: if same basin selected, clear it
    if (filterParams.value.riverBasin === payload.name) {
        filterParams.value = { ...filterParams.value, riverBasin: '' };
        currentBasinGeoJson.value = null;
    } else {
        filterParams.value = { ...filterParams.value, riverBasin: payload.name };
        currentBasinGeoJson.value = payload.geojson;
        currentRegionInfo.value = null;
        currentRegionBoundaries.value = []; // Clear region boundaries to allow basin view
        // Also ensure filterParams doesn't conflate
        console.log('Basin Selected:', payload.name, 'Clearing Region Filter');
    }
};


import draggable from 'vuedraggable';

// --- Draggable Layout Setup ---
// --- Draggable Layout Setup ---
const componentRegistry = {
  SystemTime,
  CurrentViewStats,
  StatsBasin,
  StatsProvince,
  TopTrees,
  DbhLegend,
  StyleSwitcher,
  RegionSelector,
  DataVisualizer,
  FilterBar
};

const defaultLayout = {
  left: [
    { id: 'time', component: 'SystemTime' },
    { id: 'viewStats', component: 'CurrentViewStats', props: { data: 'filteredData' } },
    { id: 'basin_lancang', component: 'StatsBasin', props: { basinName: '澜沧江流域', title: 'settings.labels.basin_lancang', color: '#409eff', data: 'allDataPoints' } },
    { id: 'basin_ailao', component: 'StatsBasin', props: { basinName: '哀牢山流域', title: 'settings.labels.basin_ailao', color: '#67c23a', data: 'allDataPoints' } },
    { id: 'basin_gaoligong', component: 'StatsBasin', props: { basinName: '高黎贡山山脉', title: 'settings.labels.basin_gaoligong', color: '#e6a23c', data: 'allDataPoints' } },
  ],
  right: [
    { id: 'styleSwitcher', component: 'StyleSwitcher' },
    { id: 'regionSelector', component: 'RegionSelector' },
    { id: 'dataVisualizer', component: 'DataVisualizer', props: { ecosystemData: 'allEcosystemData' }  },
    { id: 'dbhLegend', component: 'DbhLegend', props: { data: 'filteredData' }},
    { id: 'statsProvince', component: 'StatsProvince', props: { data: 'filteredData' }}
  ],
  bottom: [
       { id: 'topTrees', component: 'TopTrees' },
  ]
};

// Initialize layout from localStorage or default
const savedLayout = localStorage.getItem('app_layout');
const layout = reactive(savedLayout ? JSON.parse(savedLayout) : JSON.parse(JSON.stringify(defaultLayout)));

// Watch and Save Layout
watch(layout, (newVal) => {
    localStorage.setItem('app_layout', JSON.stringify(newVal));
}, { deep: true });

// Helper to resolving props dynamically including Events
const getComponentProps = (item) => {
    const commonProps = {};
    const rawProps = item.props || {};
    
    // Inject common props/events based on Component Type
    if (item.component === 'StyleSwitcher') {
        commonProps.map = mapInstance.value;
        commonProps.mapMode = currentMapMode.value;
        commonProps['onUpdate:mapMode'] = (val) => currentMapMode.value = val;
        commonProps.onStyleChange = onStyleChange;
    } else if (item.component === 'RegionSelector') {
        commonProps.map = mapInstance.value;
        commonProps.onRegionChange = onRegionChange;
    } else if (item.component === 'DataVisualizer') {
        commonProps.map = mapInstance.value;
        commonProps.points = filteredData.value;
        commonProps.regionBoundaries = currentRegionBoundaries.value;
        commonProps.regionInfo = currentRegionInfo.value;
        commonProps.highlightPolygon = currentBasinGeoJson.value;
        commonProps.viewMode = currentViewMode.value;
        commonProps['onUpdate:viewMode'] = (val) => currentViewMode.value = val;
        commonProps.monitorData = allMoniterPoints.value;
        commonProps.ecosystemData = allEcosystemData.value;
    } else if (item.component === 'StatsBasin') {
        commonProps.onDblclick = onBasinSelect;
    }

    // Merge custom props
    const finalProps = { ...commonProps };
    for (const key in rawProps) {
        let val = rawProps[key];
        if (val === 'filteredData') {
            finalProps[key] = filteredData.value;
        } else if (val === 'allDataPoints') {
            finalProps[key] = allDataPoints.value;
        } else if (val === 'allEcosystemData') {
            finalProps[key] = allEcosystemData.value;
        } else {
             // Translate title if it looks like a key
             if (key === 'title' && val.startsWith('settings.labels.')) {
                 finalProps[key] = t(val);
             } else {
                 finalProps[key] = val;
             }
        }
    }
    return finalProps;
};

// Theme State
const isDarkTheme = ref(true); // Default to dark (Grey style is somewhat dark/neutral)

const onStyleChange = (style) => {
    // List of dark styles
    const darkStyles = [
        'amap://styles/dark',
        'amap://styles/grey',
        'amap://styles/midnight',
        'amap://styles/blue',
        'amap://styles/darkblue',
        'amap://styles/wine',
        'amap://styles/graffiti'
    ];
    console.log('Style changed to:', style, 'Is dark:', darkStyles.includes(style));
    isDarkTheme.value = darkStyles.includes(style);
};

// Sync theme with body for global popups (like AMap InfoWindow)
watch(isDarkTheme, (val) => {
    if (val) {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
}, { immediate: true });

// Sync map language with locale
watch(locale, (newVal) => {
    if (mapInstance.value && typeof mapInstance.value.setLang === 'function') {
        const lang = newVal === 'en' ? 'en' : 'zh_cn';
        try {
            mapInstance.value.setLang(lang);
        } catch (e) {
            console.warn('Failed to set map language:', e);
        }
    }
}, { immediate: true });

// Also ensure map gets correct language on initial load if locale is already set
watch(mapInstance, (map) => {
    if (map) {
        const lang = locale.value === 'en' ? 'en' : 'zh_cn';
        // Delay slightly to ensure map is ready
        setTimeout(() => {
             try {
                if (typeof map.setLang === 'function') {
                    map.setLang(lang);
                }
            } catch (e) {
                console.warn('Failed to set map language on init:', e);
            }
        }, 500);
    }
});
</script>

<template>
  <div class="app-container" :class="{ 'dark-theme': isDarkTheme, 'light-theme': !isDarkTheme }">
    <template v-if="!showCustomMap">
    <MapContainer @map-ready="onMapLoad" />
    
    <div class="controls-overlay" v-if="mapInstance">
      <!-- App Title -->
      <div class="app-title">
        <img src="/logo.png" class="app-logo" :alt="t('app.logoAlt')" />
        <h1>{{ t('app.title') }}</h1>
      </div>

       <!-- Filter Bar (Top Center - Restored Static) -->
      <div class="top-center control-wrapper" v-if="panelState.filter">
        <FilterBar @filter="updateFilters" @confirm="handleConfirm" />
      </div>

   

      <!-- Draggable Zone: Left -->
      <div class="draggable-zone zone-left">
          <draggable 
            v-model="layout.left" 
            item-key="id" 
            group="widgets" 
            class="drag-column"
            :animation="200"
          >
             <template #item="{element}">
                 <div class="widget-wrapper" v-if="panelState[element.id]">
                    <component :is="componentRegistry[element.component]" v-bind="getComponentProps(element)" />
                 </div>
             </template>
          </draggable>
      </div>

      <!-- Draggable Zone: Right (Below Tools) -->
      <div class="draggable-zone zone-right">
          <draggable 
            v-model="layout.right" 
            item-key="id" 
            group="widgets" 
            class="drag-column"
            :animation="200"
          >
             <template #item="{element}">
                 <div class="widget-wrapper" v-if="panelState[element.id]">
                    <component :is="componentRegistry[element.component]" v-bind="getComponentProps(element)" />
                 </div>
             </template>
          </draggable>
      </div>

      <!-- Draggable Zone: Bottom -->
      <div class="draggable-zone zone-bottom">
          <draggable 
            v-model="layout.bottom" 
            item-key="id" 
            group="widgets" 
            class="drag-row"
            :animation="200"
          >
             <template #item="{element}">
                 <div class="widget-wrapper" v-if="panelState[element.id]">
                    <component :is="componentRegistry[element.component]" v-bind="getComponentProps(element)" />
                 </div>
             </template>
          </draggable>
      </div>

      <!-- Filter Bar (Top Center - REMOVED, now draggable) -->

       <!-- Tools (Top Right - Fixed - REMOVED, now draggable) -->

     

      <!-- Settings Menu (Bottom Right) -->
      <div class="settings-container">
          <button class="settings-btn" @click="showSettings = !showSettings" :title="t('settings.title')">
             ⚙️
          </button>
          <div class="settings-menu card" v-if="showSettings">
              <div class="menu-title">{{ t('settings.title') }}</div>
              
              <div class="menu-item locale-toggle">
                  <label>Language:</label>
                  <select v-model="locale">
                      <option value="zh">中文</option>
                      <option value="en">English</option>
                  </select>
              </div>
              <div class="menu-divider"></div>

              <div v-for="(label, key) in componentLabels" :key="key" class="menu-item">
                  <label>
                      <input type="checkbox" v-model="panelState[key]"> 
                      {{ label }}
                  </label>
              </div>
              <div class="menu-divider"></div>
              <button @click="resetLayout" class="menu-btn" style="background: #ff4d4f; margin-bottom: 5px;">{{ t('settings.resetLayout') }}</button>
              <button @click="showCustomMap = true" class="menu-btn">{{ t('settings.customMapBtn') }} &rarr;</button>
          </div>
      </div>
    </div>
    </template>
    <CustomMap v-else @back="showCustomMap = false" />
  </div>
</template>

<style scoped>
/* ... removed variables from .app-container ... */
.app-container {
  position: relative;
  width: 100%;
  height: 100%;
  color: var(--text-color); /* Ensure text color applies */
}


.controls-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 0;
  z-index: 100;
  pointer-events: none; /* Allow clicks to pass through empty areas */
}

.top-center {
  position: absolute;
  top: 100px; /* Moved down below title */
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  pointer-events: none; /* Let clicks pass through container, but children enable it */
}

.top-center > * {
    pointer-events: auto;
}

.top-left {
  position: absolute;
  top: 80px;
  left: 20px;
  pointer-events: auto;
}

.bottom-left {
  position: absolute;
  bottom: 20px;
  left: 20px;
  pointer-events: auto;
  z-index: 1000;
  max-height: 80vh; /* Limit height */
  overflow-y: auto; /* Scroll if needed, though hidden scrollbar preferred */
}

/* Hide scrollbar for Chrome/Safari/Opera */
.bottom-left::-webkit-scrollbar {
    display: none;
}

.stats-group {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.row-group {
    display: flex;
    flex-direction: row;
    gap: 15px;
    align-items: flex-start; /* Align tops */
}

.app-title {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  text-align: center;
  pointer-events: none;
  z-index: 500;
  padding-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px; /* Space between logo and text */
}

.app-logo {
  height: 50px; /* Adjust size as needed */
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.app-title h1 {
  margin: 0;
  font-size: 38px;
  color: var(--text-color);
  text-shadow: 0 2px 4px var(--shadow-color);
  font-family: "Microsoft YaHei", sans-serif;
  font-weight: bold;
  letter-spacing: 2px;
}

/* Draggable Zones */
.draggable-zone {
    position: absolute;
    z-index: 2000; /* Increased to ensure visibility */
    pointer-events: none; /* By default, let clicks pass */
}

.zone-left {
    top: 100px;
    left: 20px;
    bottom: 200px; /* Avoid overlap with bottom zone */
    width: auto;
    display: flex;
    flex-direction: column;
    align-items: flex-start; /* Prevent stretch */
}

.zone-right {
    top: 100px; /* Aligned with Left Zone */
    right: 50px;
    bottom: 200px; /* Avoid overlap with bottom zone */
    width: auto;
    display: flex;
    flex-direction: column;
    align-items: flex-end; /* Align to right edge */
}

.zone-bottom {
    bottom: 0;
    left: 0;
    right: 0;
    height: auto;
    padding-bottom: 20px;
    display: flex;
    justify-content: center;
    align-items: flex-end;
    pointer-events: none; /* Container is passthrough */
}

.drag-column {
    min-width: 200px;
    min-height: 200px;
    pointer-events: auto; /* Enable interaction for drop */
    padding-bottom: 50px; 
    display: flex;
    flex-direction: column;
    gap: 15px; /* Margin between vertical items */
}

.drag-row {
    display: flex;
    flex-direction: row;
    gap: 20px; /* Margin between horizontal items */
    align-items: flex-end;
    pointer-events: auto;
    width: 100%; /* Occupy full width of zone-bottom */
    min-height: 150px; /* Taller drop zone */
    padding: 20px;
    flex-wrap: wrap; /* Allow wrapping if too many items */
    justify-content: center;
}

.widget-wrapper {
    margin-bottom: 0px; 
    cursor: move; /* Fallback */
    cursor: grab;
    transition: transform 0.2s;
}

.widget-wrapper:active {
    cursor: grabbing;
}

/* Styles for VueDraggable ghost/drag */
.sortable-ghost {
    opacity: 0.5;
    background: rgba(255, 255, 255, 0.2);
    border: 2px dashed #409eff;
    border-radius: 4px;
}

.system-time-container {
    padding-bottom: 10px;
}

/* Adjust fixed top-right tools */
.top-right {
    top: 80px;
    right: 50px;
    pointer-events: auto;
    display: flex;
    flex-direction: column;
    align-items: flex-end; /* Prevent stretch */
    gap: 10px;
    z-index: 1000; /* Above draggable stats */
}

.settings-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: white;
    border: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    cursor: pointer;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s;
}

.settings-btn:hover {
    transform: rotate(90deg);
}

/* Common card style for overlays */
.card, :deep(.card) {
  background: var(--card-bg);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 4px 12px var(--shadow-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: background 0.3s, color 0.3s;
}

.settings-container {
    position: absolute;
    top: 20px;
    right: 50px;
    z-index: 2100; /* Highest priority */
    pointer-events: auto;
}

.settings-menu {
    position: absolute;
    top: 50px;
    bottom: auto;
    right: 0;
    width: 200px; /* Wider for component names */
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 10px;
    background: var(--card-bg);
    border-radius: 8px;
    box-shadow: 0 4px 12px var(--shadow-color);
    color: var(--text-color);
    border: 1px solid var(--border-color);
    max-height: 80vh;
    overflow-y: auto;
}

.menu-item {
    font-size: 13px;
    cursor: pointer;
}

.menu-item label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.menu-title {
    font-weight: bold;
    font-size: 14px;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
    margin-bottom: 5px;
}

.menu-divider {
    height: 1px;
    background: #eee;
    margin: 5px 0;
}

.menu-btn {
    background: #1890ff;
    color: white;
    border: none;
    padding: 6px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background 0.2s;
    text-align: center;
}

.menu-btn:hover {
    background: #40a9ff;
}

.locale-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.locale-toggle select {
    padding: 2px 5px;
    border-radius: 4px;
}
.locale-toggle select:focus {
    outline: none;
    border-color: #40a9ff;
}

/* Global Styles for Map Markers (rendered by DataVisualizer) */
.monitor-marker-dv {
  width: 30px;
  height: 30px;
  cursor: pointer;
  animation: pulse-red-dv 2s infinite;
}

@keyframes pulse-red-dv {
  0% {
    filter: drop-shadow(0 0 0 rgba(255, 77, 79, 0.4));
    transform: scale(1);
  }
  70% {
    filter: drop-shadow(0 0 10px rgba(255, 77, 79, 0.8));
    transform: scale(1.1);
  }
  100% {
    filter: drop-shadow(0 0 0 rgba(255, 77, 79, 0.0));
    transform: scale(1);
  }
}
/* Dark Theme Variables */
/* We use a class on the root or body, but since we toggle .dark-theme on app-container, 
   we can just make these overrides global for that class. */
.dark-theme {
  --bg-color: #1a1a1a;
  --text-color: #f0f0f0;
  --card-bg: rgba(30, 30, 30, 0.85);
  --border-color: #444444;
  --primary-color: #66b1ff;
  --shadow-color: rgba(0,0,0,0.5);
}

/* Fix for AMap InfoWindow to ensure transparency if default wrapper persists */
.amap-info-content {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.amap-info-sharp {
    display: none !important;
}
</style>

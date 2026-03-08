<template>
  <div class="style-switcher card">
    <div class="style-select">
        <label>{{ t('style.label') }}</label>
        <select v-model="selectedStyle" @change="changeStyle">
        <option value="amap://styles/normal">{{ t('style.types.normal') }}</option>
        <option value="amap://styles/dark">{{ t('style.types.dark') }}</option>
        <option value="amap://styles/light">{{ t('style.types.light') }}</option>
        <option value="amap://styles/whitesmoke">{{ t('style.types.whitesmoke') }}</option>
        <option value="amap://styles/fresh">{{ t('style.types.fresh') }}</option>
        <option value="amap://styles/grey">{{ t('style.types.grey') }}</option>
        <option value="amap://styles/graffiti">{{ t('style.types.graffiti') }}</option>
        <option value="amap://styles/macaron">{{ t('style.types.macaron') }}</option>
        <option value="amap://styles/blue">{{ t('style.types.blue') }}</option>
        <option value="amap://styles/darkblue">{{ t('style.types.darkblue') }}</option>
        <option value="amap://styles/wine">{{ t('style.types.wine') }}</option>
        </select>
    </div>
    
    
    <div class="view-mode-toggle">
        <button :class="{ active: viewMode === '2D' }" @click="setMode('2D')">{{ t('style.modes.2D') }}</button>
        <button :class="{ active: viewMode === '3D' }" @click="setMode('3D')">{{ t('style.modes.3D') }}</button>
        <button :class="{ active: viewMode === 'Satellite' }" @click="setMode('Satellite')">{{ t('style.modes.Satellite') }}</button>
        <button :class="{ active: viewMode === 'Map' }" @click="setMode('Map')">{{ t('style.modes.Map') }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from '../composables/useI18n';

const { t } = useI18n();

const props = defineProps({
  map: Object,
  mapMode: { type: String, default: '2D' }
});

const emit = defineEmits(['update:mapMode', 'style-change']);

const selectedStyle = ref('amap://styles/grey');
import { computed } from 'vue';
const viewMode = computed({
  get: () => props.mapMode,
  set: (val) => emit('update:mapMode', val)
});

const changeStyle = (e) => {
  if (props.map) {
    props.map.setMapStyle(selectedStyle.value);
    emit('style-change', selectedStyle.value);
  }
};

let satelliteLayer = null;
let roadNetLayer = null;

const setMode = (mode) => {
    if (!props.map) return;
    
    // Helper to safely remove specific layer types
    const removeLayerByType = (typeConstructor) => {
        if (!props.map) return;
        const layers = props.map.getLayers();
        layers.forEach(layer => {
            if (layer instanceof typeConstructor) {
                props.map.remove(layer);
            }
        });
    };

    // Handle Satellite & RoadNet Layers
    if (mode === 'Satellite') {
        // Remove existing to avoid duplicates (robustness)
        removeLayerByType(window.AMap.TileLayer.Satellite);
        removeLayerByType(window.AMap.TileLayer.RoadNet);

        if (!satelliteLayer) {
            satelliteLayer = new window.AMap.TileLayer.Satellite();
        }
        if (!roadNetLayer) {
            roadNetLayer = new window.AMap.TileLayer.RoadNet();
        }
        props.map.add([satelliteLayer, roadNetLayer]);
    } else {
        // Robust cleanup: detect and remove any such layers
        if (window.AMap) {
             removeLayerByType(window.AMap.TileLayer.Satellite);
             removeLayerByType(window.AMap.TileLayer.RoadNet);
        }
    }
    
    // Update view pitch
    if (mode === '3D') {
        props.map.setPitch(45);
    } else {
        props.map.setPitch(0);
        props.map.setRotation(0);
    }
    
    // Update state
    if (mode === 'Map') {
       viewMode.value = '2D'; // Treat 'Map' as '2D' internally/visually
    } else {
       viewMode.value = mode;
    }
};
</script>

<style scoped>
.style-switcher {
  display: flex;
  flex-direction: column; /* Stack vertically if needed, or row */
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  min-width: 220px;
}

.style-select {
    display: flex;
    align-items: center;
    gap: 10px;
}

label {
    font-size: 14px;
    font-weight: bold;
    color: var(--text-color);
}
select {
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    outline: none;
    background: var(--bg-color);
    color: var(--text-color);
}

.view-mode-toggle {
    display: flex;
    gap: 5px;
}

.view-mode-toggle button {
    padding: 4px 12px;
    border: 1px solid var(--border-color);
    background: var(--bg-color);
    cursor: pointer;
    border-radius: 4px;
    font-size: 12px;
    color: var(--text-color);
}

.view-mode-toggle button.active {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}
</style>

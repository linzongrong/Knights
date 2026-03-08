<script setup>
import { ref, onMounted, onUnmounted, shallowRef, watch } from 'vue';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import infoData from '../assets/external_geojson/info.json';
import teaPoints from '../assets/tea_points.json';
import { useI18n } from '../composables/useI18n';
const { t } = useI18n();

// --- State ---
const map = shallowRef(null);
const loading = ref(false);
const debugMsg = ref("");


// Layers
// Layer Groups for easy management
const layers = {
    country: new L.LayerGroup(),  // china.json (or base provinces)
    province: new L.LayerGroup(), // Detailed Province Data (City boundaries)
    city: new L.LayerGroup(),      // Detailed City Data (County boundaries)
    provinceLabels: new L.LayerGroup(), // Separate group for manual province labels
    teaTrees: new L.LayerGroup() // Tea Tree markers
};

// Data Cache (prevent re-fetching)
// Store Sets of loaded adcodes
const layersData = { province: new Set(), city: new Set() }; // Fix: previously global var `loadedData`


// Dropdown State
const provinces = ref([]);
const cities = ref([]);
const counties = ref([]);

const selectedProvince = ref(null);
const selectedCity = ref(null);
const selectedCounty = ref(null);

// --- Initialization ---

const initDropdowns = () => {
    const root = infoData['100000'];
    if (root && root.children) {
        provinces.value = root.children.map(c => ({
            id: c.adcode,
            name: c.name
        })).sort((a,b) => Number(a.id) - Number(b.id)); 
    }
    console.log("Provinces init:", provinces.value.length);
};

const initMap = async () => {
    map.value = L.map('custom-map-container', {
        attributionControl: false,
        zoomControl: false,
        minZoom: 3,
        maxZoom: 18,
        background: '#021a2c' // Deep dark blue background
    }).setView([35, 105], 4);
    
    L.control.zoom({ position: 'bottomright' }).addTo(map.value);
    console.log("Map initialized, adding layers...");
    
    // add layer groups to map
    // We can control visibility here or in the update loop
    // specific order: country (bottom), province (mid), city (top)
    layers.country.addTo(map.value);
    layers.provinceLabels.addTo(map.value); // Add label layer
    layers.province.addTo(map.value);
    layers.city.addTo(map.value);
    layers.teaTrees.addTo(map.value); // Add tea tree layer
    
    // Add tea markers
    renderTeaPoints();

    // Initialize dropdowns first to populate provinces list
    initDropdowns();

    // Load all provinces to create the national map with boundaries
    // china.json is likely just the outline, so we load individual provinces
    const loadAllProvinces = async () => {
        if (!provinces.value.length) return;
        
        const promises = provinces.value.map(p => {
             return fetch(`/external_geojson/province/${p.name}.json`)
                .then(res => {
                    if(res.ok) return res.json();
                    return null;
                })
                .then(data => {
                    if(data) {
                        renderRegion(data, 'country'); // Render into country group
                    }
                })
                .catch(e => console.warn(`Failed to load ${p.name}`, e));
        });
        
        console.log("Loading all province data...");
        await Promise.all(promises);
        console.log("All province data loaded.");
        
        // Add Province Labels after data load (or concurrent, doesn't matter much)
        addProvinceLabels();
    };

    await loadAllProvinces();

    // Events
    map.value.on('zoomend', updateVisibleLayers);
    map.value.on('moveend', updateVisibleLayers); // Debounce if needed?
};

// --- Themes ---
const currentTheme = ref('dark'); // 'dark' | 'light'

const THEMES = {
    dark: {
        bgColor: '#021a2c',
        borderColor: '#5B8C9B',
        fillColor: '#09253d',
        hoverColor: '#3076a3',
        labelColor: '#ffffff',
        countyColor: '#e0e0e0', // Light grey for county labels
        lineWeight: 1.5
    },
    light: {
        bgColor: '#f0f2f5',
        borderColor: '#999999',
        fillColor: '#ffffff',
        hoverColor: '#e6f7ff',
        labelColor: '#333333',
        countyColor: '#666666',
        lineWeight: 1.5
    }
};

watch(currentTheme, (newTheme) => {
    const t = THEMES[newTheme];
    
    // Update Map Background
    const container = document.getElementById('custom-map-container');
    if (container) container.style.background = t.bgColor;

    // Update Layer Styles
    const updateStyle = (layerGroup) => {
        layerGroup.eachLayer(layer => {
            // Check if group or feature
            if (layer.setStyle) {
                 // Reset to base style of new theme
                 layer.setStyle({
                     color: t.borderColor,
                     fillColor: t.fillColor,
                     weight: layer.feature?.properties?.level === 'province' ? 1.5 : 1 // simplified check
                 });
                 // Note: Hover listeners in onEachFeature might need updating? 
                 // Actually they use closure 'THEME' which is stale.
                 // We need to update the closure or reference a dynamic theme.
                 // Easy fix: Use currentTheme.value inside event handlers.
            } else if (layer.eachLayer) {
                updateStyle(layer);
            }
        });
    };

    [layers.country, layers.province, layers.city].forEach(g => updateStyle(g));
    
    // Update Labels (CSS mutation or class toggle?)
    // Labels are divIcons with specific classes. We can toggle a global class on the container?
    // Or just use CSS variables?
    // Let's use CSS variables injection for labels.
    document.documentElement.style.setProperty('--map-label-color', t.labelColor);
    document.documentElement.style.setProperty('--map-county-color', t.countyColor);
}, { immediate: true });


// --- LOD Logic ---

const updateVisibleLayers = () => {
    if (!map.value) return;
    const zoom = map.value.getZoom();
    const bounds = map.value.getBounds();

    // Visibility Thresholds
    // Level 1: Zoom 6+ -> Load/Show Province Details (Cells are Cities)
    // Level 2: Zoom 8+ -> Load/Show City Details (Cells are Counties)
    // OR if a specific province is selected, we relax the detail check to allow "Full Content"
    
    const isProvinceSelected = !!selectedProvince.value;
    const SHOW_CITY_DETAILS = zoom >= 8 || isProvinceSelected; // If province selected, user asked to see counties (auto-load)
    const SHOW_PROVINCE_DETAILS = (zoom >= 6 || isProvinceSelected) && !SHOW_CITY_DETAILS; // Hide cities if showing counties
    const SHOW_PROVINCE_LABELS = !isProvinceSelected && !SHOW_PROVINCE_DETAILS && zoom < 6; // Only show main province labels at high level

    // Toggle Groups
    // Province Labels (Manual)
    if (SHOW_PROVINCE_LABELS) {
        if (!map.value.hasLayer(layers.provinceLabels)) map.value.addLayer(layers.provinceLabels);
    } else {
        if (map.value.hasLayer(layers.provinceLabels)) map.value.removeLayer(layers.provinceLabels);
    }

    if (SHOW_PROVINCE_DETAILS) {
        if (!map.value.hasLayer(layers.province)) map.value.addLayer(layers.province);
    } else {
        if (map.value.hasLayer(layers.province)) map.value.removeLayer(layers.province);
    }

    if (SHOW_CITY_DETAILS) {
        if (!map.value.hasLayer(layers.city)) map.value.addLayer(layers.city);
    } else {
        if (map.value.hasLayer(layers.city)) map.value.removeLayer(layers.city);
    }

    // Dynamic Loading
    if (SHOW_PROVINCE_DETAILS) {
        // Iterate over base map (Provinces) to see what is visible
        // Iterate over base map (Provinces) to see what is visible
        layers.country.eachLayer(geoJSONGroup => {
            geoJSONGroup.eachLayer(layer => {
                if (bounds.intersects(layer.getBounds())) {
                    const props = layer.feature.properties;
                    const code = props.adcode || props.id;
                    const name = props.name;
                    loadRegionData(code, name, 'province');
                }
            });
        });
    }

    if (SHOW_CITY_DETAILS) {
        // Iterate over loaded provinces (Cities) to see what is visible
        layers.province.eachLayer(provLayer => {
            // provLayer is likely a GeoJSON Group
            provLayer.eachLayer(cityLayer => {
                if (bounds.intersects(cityLayer.getBounds())) {
                    const props = cityLayer.feature.properties;
                    const code = props.adcode || props.id;
                    const name = props.name;
                    // Only load if it's a city (has children)
                    // We can check info.json if needed
                    loadRegionData(code, name, 'city');
                }
            });
        });
    }
};

const loadRegionData = async (adcode, name, type, skipUpdate = false) => {
    if (layersData[type].has(adcode)) return;
    layersData[type].add(adcode); // Mark loading

    try {
        // Mapping: type 'province' -> loads from province/{name}.json (contains cities)
        // type 'city' -> loads from citys/{name}.json (contains counties)
        
        // Handle naming differences using info.json if possible, or direct name
        let fetchName = name;
        if (infoData[adcode]) fetchName = infoData[adcode].name;

        let url = '';
        if (type === 'province') {
            url = `/external_geojson/province/${fetchName}.json`;
        } else if (type === 'city') {
            url = `/external_geojson/citys/${fetchName}.json`;
        }

        const res = await fetch(url);
        
        // Fallback for city/county ambiguity
        if (!res.ok && type === 'city') {
             // maybe it's a county directly or file structure differs
             // Try county folder just in case
             const url2 = `/external_geojson/county/${name}.json`;
             const res2 = await fetch(url2);
             if (res2.ok) {
                 const data = await res2.json();
                 renderRegion(data, type);
                 return;
             }
        }

        if (res.ok) {
            const data = await res.json();
            renderRegion(data, type);
            // Trigger recursion check if we just loaded something that puts us in deeper zoom context
            // e.g. jumping to city might load province, then we need to load city data immediately
            if (!skipUpdate) updateVisibleLayers();
        } else {
            console.warn(`File not found for ${name} (${type})`);
        }

  
    } catch (e) {
        console.warn(`Failed to load ${type}: ${name}`, e);
        debugMsg.value = `Error loading ${type} ${name}: ${e.message}`;
        // layersData[type].delete(adcode); // Keep blocked to avoid spamming 404s
    }
};

const renderRegion = (data, type) => {
    const targetGroup = layers[type];
    
    // Style Config
    const isCountryLayer = type === 'country';
    const isProvinceLevel = type === 'province'; // Detailed province (contains cities)
    
    const t = THEMES[currentTheme.value];

    // Default style
    // Use opacity to handle layering?
    const style = {
        weight: isCountryLayer ? 1.5 : (isProvinceLevel ? 1 : 0.8),
        color: t.borderColor, 
        fillColor: t.fillColor,
        fillOpacity: 1, // Solid fill to cover background
        opacity: 1
    };

    L.geoJSON(data, {
        style: style,
        onEachFeature: (feature, layer) => {
            const props = feature.properties;
            const name = props.name;

            // Hover
            layer.on('mouseover', () => {
                const hoverT = THEMES[currentTheme.value]; // Dynamic lookup
                layer.setStyle({ 
                    weight: 2, 
                    color: currentTheme.value === 'dark' ? '#fff' : '#000', 
                    fillColor: hoverT.hoverColor,
                    fillOpacity: 1 
                });
            });
            layer.on('mouseout', () => {
                const baseT = THEMES[currentTheme.value];
                layer.setStyle({
                     color: baseT.borderColor,
                     fillColor: baseT.fillColor,
                     weight: isCountryLayer ? 1.5 : (isProvinceLevel ? 1 : 0.8)
                });
            });
            
            // Click to zoom
            layer.on('click', (e) => {
                L.DomEvent.stopPropagation(e);
                
                // If clicking a province on national level, set it as selected
                if(type === 'country') {
                     // Find the option in provinces list
                     const p = provinces.value.find(x => x.name === name);
                     if(p) {
                         selectedProvince.value = p;
                         onProvinceChange(); // Trigger zoom and data load
                     } else {
                         map.value.fitBounds(layer.getBounds());
                     }
                } else {
                    map.value.fitBounds(layer.getBounds());
                }
            });

            // Label
            // Only show feature-based labels for non-country layers (cities/counties)
            // For country layer, we use manual centroid labels to show Province Name instead of City Name
            if (name && !isCountryLayer) {
                layer.bindTooltip(name, {
                    permanent: true,
                    direction: 'center',
                    className: `region-label-${type}`
                });
            }
        }
    }).addTo(targetGroup);
    
    // If this is a country layer render (provinces), check if we need to add the province label
    // We do this globally once, or check if it exists. 
    // Actually, we can just do it in initMap or loadAllProvinces once.
};

// Add Province Labels separately using info.json centroids
const addProvinceLabels = () => {
    // Check if labels already added
    // clearer to just iterate provinces and add markers to a separate label group?
    // Let's add them to layers.country so they toggle with it? Or a dedicated label layer.
    // We need 'provinces' ref to be populated.
    
    if (!provinces.value.length) return;

    provinces.value.forEach(p => {
        const info = infoData[p.id];
        if (info && (info.centroid || info.center)) {
            const center = info.centroid || info.center;
            // Leaflet expects [lat, lng]
            // info.json has [lng, lat] usually? Let's check format.
            // "center":[116.405285,39.904989] -> [lng, lat]
            const latLng = [center[1], center[0]];
            
            L.marker(latLng, {
                icon: L.divIcon({
                    className: 'region-label-province',
                    html: p.name,
                    iconSize: [100, 20], // Adjust as needed
                    iconAnchor: [50, 10]
                })
            }).addTo(layers.provinceLabels); // Add to specific label group
        }
    });
};

const renderTeaPoints = () => {
    teaPoints.forEach(point => {
        // Validation: lnglat must be an array with 2 numbers
        if (!point.lnglat || !Array.isArray(point.lnglat) || point.lnglat.length < 2) return;
        
        const lng = point.lnglat[0];
        const lat = point.lnglat[1];
        
        if (!lat || !lng) return;
        
        // Simple circle marker or Icon
        // Leaflet takes [lat, lng]
        const marker = L.circleMarker([lat, lng], {
            radius: 6,
            fillColor: '#4CAF50', // Green
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Popup Content matches mockData fields
        let popupContent = `<div style="font-size:12px;"><strong>${point.name}</strong><br/>`;
        if(point.tree_id) popupContent += `ID: ${point.tree_id}<br/>`;
        
        // Construct basic location string
        const loc = [point.province, point.city, point.district, point.township].filter(Boolean).join('/');
        if(loc) popupContent += `Location: ${loc}<br/>`;
        
        if(point.dbh) popupContent += `DBH: ${point.dbh} cm<br/>`;
        if(point.riverBasin) popupContent += `Basin: ${point.riverBasin}<br/>`;
        

        
        popupContent += `</div>`;
        
        marker.bindPopup(popupContent);
        marker.addTo(layers.teaTrees);
    });
};


// --- Navigation / Dropdowns ---

const onProvinceChange = async () => {
    // Reset child selections immediately
    selectedCity.value = null;
    selectedCounty.value = null;
    counties.value = [];
    
    if (!selectedProvince.value) {
        cities.value = []; // Clear cities options
        map.value.setView([35, 105], 4);
        setTimeout(updateVisibleLayers, 100); // Trigger layer update to restore national view
        return;
    }
    
    const provId = selectedProvince.value.id;
    // 1. Zoom to Province (using base map layer logic)
    // Find in country layer
    let found = false;
    layers.country.eachLayer(geoJSONGroup => {
        geoJSONGroup.eachLayer(layer => {
            const props = layer.feature.properties;
            if ((props.adcode == provId || props.id == provId)) {
                map.value.fitBounds(layer.getBounds());
                found = true;
            }
        });
    });
    
    // Update Dropdown Options
    const provNode = infoData[provId];
    if (provNode && provNode.children) {
        cities.value = provNode.children.map(c => ({id: c.adcode, name: c.name})).sort((a,b)=>Number(a.id)-Number(b.id)); // Fix: use adcode for ID
        
        // Auto-load all children (Cities) to show County boundaries
        // User request: "Select Province -> Auto load to County"
        // This means fetching citys/{name}.json for all cities in this province
        // Use skipUpdate=true to prevent massive lag
        provNode.children.forEach(city => {
             loadRegionData(city.adcode, city.name, 'city', true);
        });
        
        // Force update visibility ONCE after batch load trigger
        setTimeout(updateVisibleLayers, 200);

    } else {
        cities.value = [];
    }
};

const onCityChange = async () => {
    if (!selectedCity.value) {
        onProvinceChange();
        return;
    }
    const cityId = selectedCity.value.id;
    const cityName = selectedCity.value.name;
    const provId = selectedProvince.value.id;
    const provName = selectedProvince.value.name;

    // Ensure Province Data is Loaded (to see city boundaries)
    await loadRegionData(provId, provName, 'province');

    // Find city feature in Province Group
    let found = false;
    layers.province.eachLayer(provLayer => { // This iterates GeoJSON layers
        provLayer.eachLayer(cityLayer => {
             const props = cityLayer.feature.properties;
             if ((props.adcode == cityId || props.id == cityId)) {
                 map.value.fitBounds(cityLayer.getBounds());
                 found = true;
             }
        });
    });

    if (!found) {
        // Fallback: Use info.json centroid if available? 
        console.warn("City boundary not found in loaded province data.");
    }

    // Update Dropdowns
    const cityNode = infoData[cityId];
    if (cityNode && cityNode.children) {
        counties.value = cityNode.children.map(c => ({id: c.adcode, name: c.name})).sort((a,b)=>Number(a.id)-Number(b.id));
    } else {
        counties.value = [];
    }
    selectedCounty.value = null;
};

const onCountyChange = async () => {
    if (!selectedCounty.value) {
        onCityChange();
        return;
    }
    const countyId = selectedCounty.value.id;
    const cityId = selectedCity.value.id;
    const cityName = selectedCity.value.name;

    // Ensure City Data is Loaded (to see county boundaries)
    await loadRegionData(cityId, cityName, 'city');

    // Find county feature in City Group
    let found = false;
    layers.city.eachLayer(cityLayer => {
        cityLayer.eachLayer(countyLayer => {
            const props = countyLayer.feature.properties;
             if ((props.adcode == countyId || props.id == countyId)) {
                 map.value.fitBounds(countyLayer.getBounds());
                 found = true;
             }
        });
    });
};


onMounted(() => {
    initMap();
});

onUnmounted(() => {
    if(map.value) map.value.remove();
});

const emit = defineEmits(['back']);
</script>

<template>
    <div class="custom-map-wrapper">
        <div class="sidebar">
            <div class="header">
                <button @click="$emit('back')" class="back-btn">← {{ t('customMap.back') }}</button>
                <h2>{{ t('customMap.title') }}</h2>
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <label>{{ t('customMap.province') }}</label>
                    <select v-model="selectedProvince" @change="onProvinceChange">
                        <option :value="null">{{ t('customMap.national') }}</option>
                        <option v-for="p in provinces" :key="p.id" :value="p">{{ p.name }}</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>{{ t('customMap.style') }}</label>
                    <div class="theme-switch">
                        <button :class="{active: currentTheme === 'dark'}" @click="currentTheme = 'dark'">{{ t('customMap.dark') }}</button>
                        <button :class="{active: currentTheme === 'light'}" @click="currentTheme = 'light'">{{ t('customMap.light') }}</button>
                    </div>
                </div>

                <div class="control-group" v-if="selectedProvince">
                    <label>{{ t('customMap.city') }}</label>
                    <select v-model="selectedCity" @change="onCityChange">
                        <option :value="null">{{ t('customMap.allProvince') }}</option>
                        <option v-for="c in cities" :key="c.id" :value="c">{{ c.name }}</option>
                    </select>
                </div>

                <div class="control-group" v-if="selectedCity && counties.length > 0">
                    <label>{{ t('customMap.county') }}</label>
                    <select v-model="selectedCounty" @change="onCountyChange">
                        <option :value="null">{{ t('customMap.allCity') }}</option>
                        <option v-for="c in counties" :key="c.id" :value="c">{{ c.name }}</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="map-area">
            <div id="custom-map-container"></div>
            <div class="loading-overlay" v-if="loading">加载中...</div>
            <div class="debug-overlay" v-if="provinces.length === 0 || debugMsg">{{ debugMsg || 'No provinces loaded' }}</div>
        </div>
    </div>
</template>

<style scoped>
.custom-map-wrapper {
    display: flex;
    width: 100vw;
    height: 100vh;
    background: #fff;
}

.sidebar {
    width: 300px;
    background: #021a2c;
    display: flex;
    flex-direction: column;
    box-shadow: 2px 0 8px rgba(0,0,0,0.5);
    z-index: 1001;
    color: white;
}

.header {
    padding: 20px;
    border-bottom: 1px solid #1a3a5a;
    background: #021a2c;
}

.back-btn {
    border: none;
    background: none;
    cursor: pointer;
    font-size: 14px;
    color: #90caf9;
    margin-bottom: 10px;
    padding: 0;
}

.back-btn:hover {
    color: #fff;
    text-decoration: underline;
}

.header h2 {
    margin: 0;
    font-size: 20px;
    color: white;
}

.controls {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.control-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.control-group label {
    font-size: 14px;
    color: #90caf9;
    font-weight: bold;
}

select {
    padding: 8px;
    border: 1px solid #1a3a5a;
    border-radius: 4px;
    font-size: 14px;
    outline: none;
    background: #053053;
    color: white;
}

select:focus {
    border-color: #64b5f6;
}

.map-area {
    flex: 1;
    position: relative;
    z-index: 0; 
}

.theme-switch {
    display: flex;
    gap: 10px;
}
.theme-switch button {
    flex: 1;
    padding: 5px 10px;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: white; /* Sidebar text is white probably? */
    cursor: pointer;
    border-radius: 4px;
}
.theme-switch button.active {
    background: #4A90E2;
    border-color: #4A90E2;
    color: white;
}

#custom-map-container {
    width: 100%;
    height: 100%;
    z-index: 1;
    background: #021a2c;
}

.loading-overlay {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 15px 30px;
    border-radius: 4px;
    pointer-events: none;
    z-index: 2000;
}

/* Label Styles with Text Shadows for readability */
:deep(.region-label-country),
:deep(.region-label-province) {
    background: transparent;
    border: none;
    box-shadow: none;
    color: var(--map-label-color, #ffffff); /* Use Var */
    font-weight: bold;
    font-size: 14px;
    text-shadow: none; 
    white-space: nowrap; 
    text-align: center; 
    width: auto !important; 
    transition: color 0.3s;
}

:deep(.region-label-city) {
    background: transparent;
    border: none;
    box-shadow: none;
    color: var(--map-county-color, #e0e0e0); /* Use var */
    font-weight: bold; /* Bold for readability */
    font-size: 12px;
    text-shadow: none;
    white-space: nowrap;
    transition: color 0.3s;
}

:deep(.region-label-county) {
    background: transparent;
    border: none;
    box-shadow: none;
    font-size: 10px;
    text-shadow: none;
}

.debug-overlay {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255,0,0,0.8);
    color: white;
    padding: 10px;
    z-index: 2000;
    pointer-events: none;
}
</style>

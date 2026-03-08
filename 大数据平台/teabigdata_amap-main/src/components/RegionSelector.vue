<template>
  <div class="region-selector card">
    <div class="selector-item">
      <label>{{ t('region.province') }}</label>
      <select v-model="selectedProvince" @change="onProvinceChange">
        <option :value="null">{{ t('region.placeholder') }}</option>
        <option v-for="p in provinces" :key="p.adcode" :value="p">{{ p.name }}</option>
      </select>
    </div>

    <div class="selector-item">
      <label>{{ t('region.city') }}</label>
      <select v-model="selectedCity" @change="onCityChange" :disabled="!selectedProvince">
        <option :value="null">{{ t('region.placeholder') }}</option>
        <option v-for="c in cities" :key="c.adcode" :value="c">{{ c.name }}</option>
      </select>
    </div>

    <div class="selector-item">
      <label>{{ t('region.district') }}</label>
      <select v-model="selectedDistrict" @change="onDistrictChange" :disabled="!selectedCity">
        <option :value="null">{{ t('region.placeholder') }}</option>
        <option v-for="d in districts" :key="d.adcode" :value="d">{{ d.name }}</option>
      </select>
    </div>

    <div class="selector-item" style="display: none;">
      <label>{{ t('region.town') }}</label>
      <select v-model="selectedTown" @change="onTownChange" :disabled="!selectedDistrict">
        <option :value="null">{{ t('region.placeholder') }}</option>
        <option v-for="t in towns" :key="t.adcode" :value="t">{{ t.name }}</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useI18n } from '../composables/useI18n';

const { t } = useI18n();

const props = defineProps({
  map: Object
});

const emit = defineEmits(['region-change']);

const provinces = ref([]);
const cities = ref([]);
const districts = ref([]);
const towns = ref([]);
const debugMsg = ref('');

const selectedProvince = ref(null);
const selectedCity = ref(null);
const selectedDistrict = ref(null);
const selectedTown = ref(null);

let districtSearch = null;

// Initialize DistrictSearch
const initDistrictSearch = () => {
  if (!window.AMap) {
    debugMsg.value = 'AMap not found in window';
    return;
  }
  
  try {
      // Instance for fetching lists (lighter payload)
      districtSearch = new window.AMap.DistrictSearch({
        subdistrict: 1, 
        extensions: 'base', // Use 'base' for list to avoid heavy boundary data
        level: 'country' 
      });
      loadProvinces();
  } catch (e) {
      console.error('Error init DistrictSearch: ' + e.message);
  }
};

const loadProvinces = () => {
  // Use 'base' for list loading to be fast and reliable
  districtSearch.setExtensions('base');
  districtSearch.setLevel('country');
  districtSearch.search('中国', (status, result) => {
    if (status === 'complete') {
        if (result.districtList && result.districtList.length > 0) {
             provinces.value = result.districtList[0].districtList;
        }
    } else {
         console.error(`Province search failed: ${status}`, result);
         // Fallback or retry logic could go here
    }
  });
};

const onProvinceChange = () => {
  selectedCity.value = null;
  selectedDistrict.value = null;
  selectedTown.value = null;
  cities.value = [];
  districts.value = [];
  towns.value = [];

  if (selectedProvince.value) {
    searchAndZoom(selectedProvince.value, 'province', (list) => {
        cities.value = list;
    });

  } else {
    // Clear filter
    emit('region-change', null);
    // Remove polygon
    if (currentPolygon.value) {
        props.map.remove(currentPolygon.value);
        currentPolygon.value = null;
    }
  }
};

const onCityChange = () => {
  selectedDistrict.value = null;
  selectedTown.value = null;
  districts.value = [];
  towns.value = [];

  if (selectedCity.value) {
     searchAndZoom(selectedCity.value, 'city', (list) => {
        districts.value = list;
    });
  } else {
      // Revert to Province
      if (selectedProvince.value) {
          searchAndZoom(selectedProvince.value, 'province');
      }
  }
};

const onDistrictChange = () => {
  selectedTown.value = null;
  towns.value = [];

  if (selectedDistrict.value) {
     searchAndZoom(selectedDistrict.value, 'district', (list) => {
        towns.value = list;
    });
  } else {
      // Revert to City
      if (selectedCity.value) {
          searchAndZoom(selectedCity.value, 'city');
      }
  }
};

const onTownChange = () => {
  if (selectedTown.value) {
    searchAndZoom(selectedTown.value, 'biz_area', () => {});
  } else {
      // Revert to District
      if (selectedDistrict.value) {
          searchAndZoom(selectedDistrict.value, 'district');
      }
  }
};

const currentPolygon = ref(null);

// Search and Zoom Logic
// 1. Uses AMap.DistrictSearch to find region boundaries (polygons).
// 2. Draws the polygon to highlight the region.
// 3. Emits region data (boundary + metadata) to parent.
// Refactored Search Logic: Separate List and Boundary fetching for robustness
const searchAndZoom = (node, level, callback) => {
  if (!districtSearch || !props.map) return;

  // 1. Fetch List (Dropdown Data) - Lightweight
  districtSearch.setExtensions('base');
  districtSearch.setSubdistrict(1); // Ensure we get children
  districtSearch.setLevel(level);
  
  districtSearch.search(node.adcode, (status, result) => {
      if (status === 'complete' && result.districtList && result.districtList.length > 0) {
          const data = result.districtList[0];
          // Populate Dropdown via callback
          if (callback && data.districtList) {
              callback(data.districtList);
          }
      }
  });

  // 2. Fetch Boundary (Map Data) - Heavyweight
  // We create a separate instance or run sequentially? 
  // AMap.DistrictSearch instance might handle concurrent calls, but to be safe/clean let's assume valid.
  // Actually, modifying options sharing the same instance immediately might race.
  // Let's instantiate a second "BoundarySearch" or just chain the calls inside the first callback?
  // Chaining is safer to avoid option overwrite race conditions.
  
  // Actually, creating a transient instance for boundary might be cleaner to avoid races with the List search.
  // Or just simply:
  const boundarySearch = new window.AMap.DistrictSearch({
      subdistrict: 0, // We don't need children for boundary check
      extensions: 'all',
      level: level
  });
  
  boundarySearch.search(node.adcode, (status, result) => {
      if (status === 'complete' && result.districtList && result.districtList.length > 0) {
          const data = result.districtList[0];
          
          // Clear previous polygon
          if (currentPolygon.value) {
              props.map.remove(currentPolygon.value);
              currentPolygon.value = null;
          }

          if (data.boundaries && data.boundaries.length) {
              // Create Polygon for highlighting
              currentPolygon.value = new window.AMap.Polygon({
                  path: data.boundaries,
                  strokeColor: '#00D3FC', 
                  strokeWeight: 2,
                  strokeOpacity: 1,
                  fillOpacity: 0, 
                  bubble: true 
              });
              props.map.add(currentPolygon.value);

              // Calculate bounds
              let minLng = 1000, maxLng = -1000, minLat = 1000, maxLat = -1000;
              data.boundaries.forEach(polygon => {
                  polygon.forEach(coord => {
                      const lng = coord.lng || coord[0];
                      const lat = coord.lat || coord[1];
                      if (lng < minLng) minLng = lng;
                      if (lng > maxLng) maxLng = lng;
                      if (lat < minLat) minLat = lat;
                      if (lat > maxLat) maxLat = lat;
                  });
              });
              const bounds = new window.AMap.Bounds([minLng, minLat], [maxLng, maxLat]);
              props.map.setBounds(bounds);
              
              // Emit full payload
               const payload = {
                  boundaries: data.boundaries,
                  level: level,
                  adcode: node.adcode,
                  name: node.name
              };
              emit('region-change', payload);

          } else {
               // Fallback
               props.map.setCenter(data.center);
               props.map.setZoom(12);
               emit('region-change', { ...node, boundaries: [] });
          }
      }
  });
};

watch(() => props.map, (newMap) => {
  if (newMap && window.AMap) {
    initDistrictSearch();
  }
}, { immediate: true });


</script>

<style scoped>
.region-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  min-width: 220px; /* Ensure sufficient width */
}
.selector-item {
  display: flex;
  flex-direction: column;
}
label {
    font-size: 12px;
    font-weight: bold;
    color: var(--text-color);
    opacity: 0.8;
    margin-bottom: 2px;
}
select {
    padding: 4px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-color);
    color: var(--text-color);
}
</style>

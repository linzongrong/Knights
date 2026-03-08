<template>
  <div id="container"></div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";
import infoData from '../assets/external_geojson/info.json';

let map = null;
const provinceMarkers = ref([]);

// Configure security key
window._AMapSecurityConfig = {
  securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE,
};

onMounted(() => {
  AMapLoader.load({
    key: import.meta.env.VITE_AMAP_KEY, // Application Key
    version: "2.0",
    plugins: ["AMap.DistrictLayer", "AMap.Scale", "AMap.ToolBar", "AMap.DistrictSearch", "AMap.MassMarks", "AMap.MarkerCluster", "AMap.GeoJSON"],
  })
    .then((AMap) => {
      window.AMap = AMap; // Make AMap global for other components
      map = new AMap.Map("container", {
        viewMode: "3D",
        zoom: 4,
        center: [105.602725, 35.076636], // Center of China
        layers: [
          // Create a standard tile layer
          AMap.createDefaultLayer()
        ],
        mapStyle: "amap://styles/grey"
      });
      
      // Add Province Boundaries Layer (DistrictLayer.Country)
      // This displays the country with province boundaries
      const disCountry = new AMap.DistrictLayer.Country({
        zIndex: 10,
        SOC: "CHN",
        depth: 1, // Depth 1 means provinces
        styles: {
          "nation-stroke": "#22ffff",
          "coastline-stroke": [0.8, 0.63, 0.94, 1],
          "province-stroke": "white",
          fill: function (props) {
            return "rgba(255, 255, 255, 0.1)";
          },
        },
      });
      
      map.add(disCountry);

      map.addControl(new AMap.Scale());
      map.addControl(new AMap.ToolBar());
      
      // Initialize DistrictSearch to fetch province names
      const districtSearch = new AMap.DistrictSearch({
        subdistrict: 1,
        extensions: "base",
        level: "country"
      });
      
      districtSearch.search('中国', (status, result) => {
        if (status === 'complete' && result.districtList.length > 0) {
          const provinces = result.districtList[0].districtList;
          provinces.forEach(prov => {
             // TEMPORARILY DISABLED: White province labels are offset from basemap labels
             // Using info.json centroid data still shows offset issue
             // Uncomment below to re-enable custom labels
             /*
             let position = prov.center;
             const infoNode = infoData[prov.adcode];
             if (infoNode && (infoNode.centroid || infoNode.center)) {
                 position = infoNode.centroid || infoNode.center;
             }
             
             const marker = new AMap.Text({
                text: prov.name,
                position: position,
                extData: { cnName: prov.name },
                style: {
                    'background-color': 'transparent',
                    'border': 'none',
                    'color': '#fff',
                    'font-size': '12px',
                    'font-weight': 'bold',
                    'text-shadow': '1px 1px 2px black'
                },
                zIndex: 20
             });
             if (map.getZoom() < 4) {
                 marker.hide();
             }
             marker.setMap(map);
             provinceMarkers.value.push(marker);
             */
          });
        }
      });
      
      // Monitor zoom changes
      map.on('zoomchange', () => {
         const zoom = map.getZoom();
         const shouldShow = zoom >= 4;
         provinceMarkers.value.forEach(m => {
             if (shouldShow) m.show();
             else m.hide();
         });
      });
      
      // Initial translation
      updateMarkerLabels();
      
      // Expose map instance for parent access if needed
      window.amapInstance = map; 
      emit('map-ready', map);
    })
    .catch((e) => {
      console.error(e);
    });
});

// Translation Logic
import { useI18n } from '../composables/useI18n';
import { provinceTranslations } from '../utils/provinceTranslations';
import { watch } from 'vue'; // Ensure watch is imported

const { locale } = useI18n();

const updateMarkerLabels = () => {
    provinceMarkers.value.forEach(marker => {
        // We store the original CN name in extData or just infer it?
        // Wait, text is overwritten. We need to store the CN name as source of truth.
        // Let's attach sourceName to marker object or extData
        const cnName = marker.getExtData()?.cnName;
        if (cnName) {
            const newLabel = locale.value === 'en' ? (provinceTranslations[cnName] || cnName) : cnName;
            marker.setText(newLabel);
        }
    });
};

watch(locale, () => {
    updateMarkerLabels();
});

const emit = defineEmits(['map-ready']);

onUnmounted(() => {
  if (map) {
    map.destroy();
  }
});
</script>

<style scoped>
#container {
  padding: 0px;
  margin: 0px;
  width: 100%;
  height: 100%;
}
</style>

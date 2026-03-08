<template>
  <div class="data-visualizer card">
    
    <div class="controls-wrapper" style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
        <div class="control-group" style="display: flex; flex-direction: column; gap: 5px;">
            <label class="switch-mode">
                <input type="radio" value="mass" v-model="viewMode">
                {{ t('visualizer.mass') }}
            </label>
            <label class="switch-mode">
                <input type="radio" value="cluster" v-model="viewMode">
                {{ t('visualizer.cluster') }}
            </label>
        </div>
        
        <div style="width: 1px; height: 40px; background: #ddd;"></div>

        <div class="control-group" style="display: flex; flex-direction: column; gap: 5px;">
            <label class="switch-mode">
                <input type="checkbox" v-model="showMonitor">
                {{ t('visualizer.monitor') }}
            </label>
            <label class="switch-mode">
                <input type="checkbox" v-model="showEcology">
                {{ t('visualizer.ecosystem') }}
            </label>
        </div>
    </div>
    
    <!-- Hidden Info Window Content Template -->
    <div ref="infoWindowTemplate" style="display: none;">
        <div class="custom-info-window">
            <h4 id="info-title"></h4>
            <p><strong>{{ t('visualizer.popup.address') }}</strong> <span id="info-address"></span></p>
            <p><strong>{{ t('visualizer.popup.dbh') }}</strong> <span id="info-dbh"></span> cm</p>
            <a href="#" id="info-details" style="color: #409eff;">{{ t('visualizer.popup.details') }} &rarr;</a>
        </div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeModal">×</button>
        <iframe :src="iframeUrl" class="detail-iframe"></iframe>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
}

.modal-content {
    background: white;
    width: 100%;
    height: 85%;
    max-width: 1380px;
    border-radius: 8px;
    position: relative;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    overflow: hidden;
}

.close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(0,0,0,0.5);
    color: white;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    font-size: 20px;
    cursor: pointer;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
}
.close-btn:hover {
    background: rgba(0,0,0,0.8);
}

.detail-iframe {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    border: none;
}
</style>



<script setup>
import { ref, watch, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useI18n } from '../composables/useI18n';
const { t } = useI18n();

const props = defineProps({
  map: Object, 
  filterParams: Object,
  regionBoundaries: Array,
  regionInfo: Object,
  highlightPolygon: Array,
  viewMode: { type: String, default: 'mass' },
  points: { type: Array, required: true },
  monitorData: { type: Array, default: () => [] },
  ecosystemData: {
      type: Array,
      default: () => []
  }
});

// Ecosystem Logic
let ecosystemPolygons = []; // Array of AMap.Polygon
let ecosystemInfoWindow = null;

const removeEcosystemPolygons = () => {
    if (ecosystemPolygons.length > 0) {
        if (props.map) {
             props.map.remove(ecosystemPolygons);
        } else {
             ecosystemPolygons.forEach(p => p.setMap(null));
        }
        ecosystemPolygons = [];
    }
};

const renderEcologyLayer = () => {
    if (!props.map || !window.AMap) return;

    removeEcosystemPolygons();

    if (!showEcology.value || !props.ecosystemData || props.ecosystemData.length === 0) {
        return;
    }

    if (!ecosystemInfoWindow) {
        ecosystemInfoWindow = new window.AMap.InfoWindow({
            offset: new window.AMap.Pixel(0, -10),
            isCustom: false // Use default style for simplicity or customize later
        });
    }

    const newPolygons = [];

    // Separate info window for clicks (persistent)
    let ecosystemClickInfoWindow = null;
const hoverWindow = new window.AMap.InfoWindow({
          offset: new window.AMap.Pixel(0, -10),
          isCustom: true,
          closeWhenClickMap: true // Optional
      });
    props.ecosystemData.forEach((eco) => {
        if (eco.path && eco.path.length > 0) {
            const polygon = new window.AMap.Polygon({
                path: eco.path,
                fillColor: '#52c41a', // Green
                fillOpacity: 0.3,
                strokeColor: '#237804', // Darker Green
                strokeWeight: 1,
                strokeOpacity: 0.8,
                zIndex: 50,
                extData: eco,
                map: props.map
            });

            

            // Hover effect
            polygon.on('mouseover', (e) => {
                polygon.setOptions({
                    fillOpacity: 0.6,
                    fillColor: '#73d13d'
                });
                
                const infoContent = `
                    <div style="padding: 5px 10px; font-size: 12px; background: rgba(0,0,0,0.7);">
                        ${eco.name}
                    </div>
                `;
                hoverWindow.setContent(infoContent);
                hoverWindow.open(props.map, eco.lnglat || e.lnglat); // Use calculated center or mouse pos
            });

            polygon.on('mouseout', () => {
                polygon.setOptions({
                    fillOpacity: 0.3,
                    fillColor: '#52c41a'
                });
                hoverWindow.close();
            });

            // Click effect - Show details
            polygon.on('click', (e) => {
                 if (!ecosystemClickInfoWindow) {
                     ecosystemClickInfoWindow = new window.AMap.InfoWindow({
                         offset: new window.AMap.Pixel(0, -10),
                         isCustom: true,
                         closeWhenClickMap: true,
                         autoMove: true
                     });
                 }

                 const content = `
                    <div style="position: relative; padding: 15px; font-size: 13px; background: var(--card-bg); color: var(--text-color); border-radius: 4px; box-shadow: 0 4px 12px var(--shadow-color); border: 1px solid var(--border-color); min-width: 300px; max-width: 400px;">
                         <a href="javascript:void(0)" onclick="this.parentNode.parentNode.style.display='none'" style="position: absolute; top: 10px; right: 10px; color: var(--text-color); opacity: 0.6; text-decoration: none; font-size: 18px; line-height: 1;">&times;</a>
                         <h3 style="margin: 0 0 10px 0; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; font-size: 16px; color: var(--primary-color);">${eco.name}</h3>
                         
                         <div style="margin-bottom: 8px;"><strong>区域:</strong> ${eco.region || '未知'}</div>
                         
                         <div style="margin-bottom: 8px; max-height: 100px; overflow-y: auto;">
                            ${eco.brief || ''}
                         </div>
                         
                         ${eco.story ? `
                         <div style="margin-bottom: 8px;">
                             ${eco.story}
                         </div>
                         ` : ''}
                         
                         ${eco.protection ? `
                         <div style="margin-bottom: 5px; color: #faad14;">
                            ${eco.protection}
                         </div>
                         ` : ''}
                    </div>
                 `;
                 
                 ecosystemClickInfoWindow.setContent(content);
                 ecosystemClickInfoWindow.open(props.map, e.lnglat); // Open at clicked position
            });
            
            newPolygons.push(polygon);
        }
    });

    ecosystemPolygons = newPolygons;
};

// Handle Highlight Polygon (e.g. River Basin)
let highlightPolygonLayer = null;

const renderHighlightPolygon = () => {
    if (!props.map || !window.AMap) return;

    // Clear existing
    if (highlightPolygonLayer) {
        props.map.remove(highlightPolygonLayer);
        highlightPolygonLayer = null;
    }

    if (props.highlightPolygon) {
         const geoJSON = new window.AMap.GeoJSON({
            geoJSON: props.highlightPolygon,
            getPolygon: (geojson, lnglats) => {
                return new window.AMap.Polygon({
                    path: lnglats,
                    fillColor: '#409eff',
                    strokeColor: '#409eff',
                    strokeWeight: 2,
                    fillOpacity: 0.15,
                    strokeOpacity: 0.8,
                    bubble: true
                });
            }
        });
        highlightPolygonLayer = geoJSON;
        props.map.add(highlightPolygonLayer);
        // AMap.GeoJSON is a wrapper/OverlayGroup. setFitView expects arrays of Overlay (Polygon/Marker).
        // Safest to pass the inner overlays.
        if (highlightPolygonLayer.getOverlays) {
             props.map.setFitView(highlightPolygonLayer.getOverlays()); 
        } else {
             // Fallback for older versions or if it acts as overlay
             props.map.setFitView([highlightPolygonLayer]);
        }
    }
};

watch(() => props.highlightPolygon, () => {
    renderHighlightPolygon();
});

const showModal = ref(false);
const iframeUrl = ref('');
const closeModal = () => {
    showModal.value = false;
    iframeUrl.value = '';
};

// Expose function for Popup onclick
window.openTeaDetail = (treeId) => {
    if (treeId) {
        iframeUrl.value = `https://teabigdata.swfu.edu.cn/tea/bigscreen/details/${treeId}`;
        showModal.value = true;
    }
};

const emit = defineEmits(['update:viewMode']); 

const showData = ref(true);

const viewMode = computed({
  get: () => props.viewMode,
  set: (val) => emit('update:viewMode', val)
});
let massMarksLayer = null;
let clusterLayer = null;


const initData = () => {
    updateLayersData();
};

const updateLayersData = () => {
    const displayedPoints = props.points || [];

    if (viewMode.value === 'mass' && massMarksLayer) {
        // Must transform data again to include style index
        const massData = displayedPoints.map(p => {
          let styleIdx = 5;
          const dbh = parseFloat(p.dbh);
          if (isNaN(dbh)) styleIdx = 5;
          else if (dbh < 30) styleIdx = 0;
          else if (dbh >= 30 && dbh < 50) styleIdx = 1;
          else if (dbh >= 50 && dbh < 80) styleIdx = 2;
          else if (dbh >= 80 && dbh < 100) styleIdx = 3;
          else if (dbh >= 100) styleIdx = 4;
          
          return {
              ...p,
              style: styleIdx
          };
      });
        massMarksLayer.setData(massData);
    } else if (viewMode.value === 'cluster' && clusterLayer) {
        clusterLayer.setData(displayedPoints);
    }
};

watch(() => props.points, () => {
    updateLayersData();
});

watch(viewMode, () => {
    changeViewMode();
});


const initMassMarks = () => {
  if (!props.map || !window.AMap) return;
  
  if (!massMarksLayer) {
      // Style for MassMarks
      // DBH Ranges: <30, 30-50, 50-80, 80-100, >100
      const svgPin = (color) => `data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='24' height='24'%3E%3Cpath fill='${encodeURIComponent(color)}' stroke='white' stroke-width='1' d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z'/%3E%3Ccircle cx='12' cy='9' r='2.5' fill='white'/%3E%3C/svg%3E`;
      
      const styles = [
          { 
            // 0: < 30 (Fresh Green)
            url: svgPin('#BB271A'), 
            anchor: new window.AMap.Pixel(12, 24),
            size: new window.AMap.Size(24, 24),
            zIndex: 100
          },
          { 
            // 1: 30-50 (Olive Green)
            url: svgPin('#EE782F'),
            anchor: new window.AMap.Pixel(12, 24),
            size: new window.AMap.Size(24, 24),
            zIndex: 101
          },
          { 
            // 2: 50-80 (Bronze/Light Brown)
            url: svgPin('#4EACEA'),
            anchor: new window.AMap.Pixel(12, 24),
            size: new window.AMap.Size(24, 24),
            zIndex: 102
          },
          { 
            // 3: 80-100 (Deep Brown)
            url: svgPin('#8C1AC4'),
            anchor: new window.AMap.Pixel(12, 24),
            size: new window.AMap.Size(24, 24),
            zIndex: 103
          },
          { 
            // 4: > 100 (Red)
            url: svgPin('#5CC93B'),
            anchor: new window.AMap.Pixel(12, 24),
            size: new window.AMap.Size(24, 24),
            zIndex: 104
          },
          { 
            // 5: Unknown (Grey)
            url: svgPin('#CCCCCC'),
            anchor: new window.AMap.Pixel(12, 24),
            size: new window.AMap.Size(24, 24),
            zIndex: 99
          }
      ];
      
      // Data needs to be processed to include 'style' index
      const massData = (props.points || []).map(p => {
          let styleIdx = 5;
          const dbh = parseFloat(p.dbh);
          if (isNaN(dbh)) styleIdx = 5;
          else if (dbh < 30) styleIdx = 0;
          else if (dbh >= 30 && dbh < 50) styleIdx = 1;
          else if (dbh >= 50 && dbh < 80) styleIdx = 2;
          else if (dbh >= 80 && dbh < 100) styleIdx = 3;
          else if (dbh >= 100) styleIdx = 4;
          
          return {
              ...p,
              style: styleIdx
          };
      });

      massMarksLayer = new window.AMap.MassMarks(massData, {
          zIndex: 200,
          style: styles,
          opacity: 1,
          cursor: 'pointer'
      });
      
      const infoWindow = new window.AMap.InfoWindow({offset: new window.AMap.Pixel(0, -10), isCustom: true});
      const hoverWindow = new window.AMap.InfoWindow({
          offset: new window.AMap.Pixel(0, -10),
          isCustom: true,
          closeWhenClickMap: true // Optional
      });

      massMarksLayer.on('mouseover', function (e) {
          const content = `
            <div style="padding: 5px 10px; font-size: 12px; background: var(--card-bg); color: var(--text-color);  border-radius: 4px; pointer-events: none; white-space: nowrap;">
                ${e.data.name}
            </div>
          `;
          hoverWindow.setContent(content);
          hoverWindow.open(props.map, e.data.lnglat);
      });

      massMarksLayer.on('mouseout', function () {
          hoverWindow.close();
      });

      massMarksLayer.on('click', function (e) {
          const content = `
            <div style="position: relative; padding: 10px; font-size: 13px; background: var(--card-bg); color: var(--text-color); border-radius: 4px; box-shadow: 0 2px 6px var(--shadow-color); border: 1px solid var(--border-color); min-width: 220px;">
                <a href="javascript:void(0)" onclick="this.parentNode.parentNode.style.display='none'" style="position: absolute; top: 5px; right: 5px; color: var(--text-color); opacity: 0.6; text-decoration: none; font-size: 16px; line-height: 1;">&times;</a>
                <div style="font-weight: bold; margin-bottom: 4px; padding-right: 15px;">${e.data.name}</div>
                <div>地址: ${e.data.province}${e.data.city}${e.data.district}</div>
                <div>${e.data.township}</div>
                <div>胸径: ${e.data.dbh} cm</div>
                <div style="margin-top:5px; text-align:right;">
                    <a href="javascript:void(0)" onclick="openTeaDetail('${e.data.tree_id}')" style="color:var(--primary-color);">[详细信息]</a>
                </div>
            </div>
          `;
          infoWindow.setContent(content);
          infoWindow.open(props.map, e.data.lnglat);
      });
  }
};

const initCluster = () => {
    if (!props.map || !window.AMap) return;
    
    if (!clusterLayer) {
        clusterLayer = new window.AMap.MarkerCluster(props.map, props.points || [], {
            gridSize: 60,
            renderClusterMarker: (context) => {
                const count = context.count;
                const total = props.points.length || 1;
                const size = Math.round(30 + Math.pow(count / total, 1 / 5) * 20);
                
                // AMap Example Style (Orange -> Blue -> Red) - Avoid Green (Ecosystem)
                let bgColor = 'rgba(250, 173, 20, 0.8)'; // Orange (< 100)
                let borderColor = 'rgba(250, 173, 20, 1)';
                
                if (count > 1000) {
                    bgColor = 'rgba(255, 77, 79, 0.8)'; // Red
                    borderColor = 'rgba(255, 77, 79, 1)';
                } else if (count > 100) {
                    bgColor = 'rgba(64, 158, 255, 0.8)'; // Blue
                    borderColor = 'rgba(64, 158, 255, 1)';
                }
                
                const div = document.createElement('div');
                div.style.backgroundColor = bgColor;
                div.style.width = div.style.height = size + 'px';
                div.style.border = `1px solid ${borderColor}`;
                div.style.borderRadius = '50%';
                div.style.boxShadow = '0 0 5px rgba(0,0,0,0.3)';
                div.innerHTML = context.count;
                div.style.lineHeight = size + 'px';
                div.style.color = '#ffffff';
                div.style.fontSize = '14px';
                div.style.textAlign = 'center';
                div.style.fontFamily = 'Arial';
                div.style.fontWeight = 'bold';
                
                context.marker.setOffset(new window.AMap.Pixel(-size / 2, -size / 2));
                context.marker.setContent(div);
            }
        });
        // Note: MarkerCluster automatically adds itself to map usually, or needs setMap?
        // In 2.0 new AMap.MarkerCluster(map, data, opts) adds it.
        // We probably need to manage its visibility by setting data to empty or removing it.
        // Or setMap(null)
        // Open Modal on Single Point Click (Water Drop Icon)
        clusterLayer.on('click', (e) => {
            // e.clusterData contains the points in the clicked cluster/marker
            if (e.clusterData && e.clusterData.length === 1) {
                const point = e.clusterData[0];
                const infoWindow = new window.AMap.InfoWindow({offset: new window.AMap.Pixel(0, -10), isCustom: true});
                
                const content = `
                    <div style="position: relative; padding: 10px; font-size: 13px; background: var(--card-bg); color: var(--text-color); border-radius: 4px; box-shadow: 0 2px 6px var(--shadow-color); border: 1px solid var(--border-color); min-width: 220px;">
                        <a href="javascript:void(0)" onclick="this.parentNode.parentNode.style.display='none'" style="position: absolute; top: 5px; right: 5px; color: var(--text-color); opacity: 0.6; text-decoration: none; font-size: 16px; line-height: 1;">&times;</a>
                        <div style="font-weight: bold; margin-bottom: 4px; padding-right: 15px;">${point.name}</div>
                        <div>地址: ${point.province}${point.city}${point.district}</div>
                        <div>${point.township}</div>
                        <div>胸径: ${point.dbh} cm</div>
                        <div style="margin-top:5px; text-align:right;">
                            <a href="javascript:void(0)" onclick="openTeaDetail('${point.tree_id}')" style="color:var(--primary-color);">[详细信息]</a>
                        </div>
                    </div>
                `;
                infoWindow.setContent(content);
                infoWindow.open(props.map, point.lnglat);
            }
        });
    }
};



const clearLayers = () => {
    if (massMarksLayer) {
        massMarksLayer.setMap(null);
        massMarksLayer.setData([]); // Ensure visual clearing
    }
    if (clusterLayer) {
        clusterLayer.setMap(null);
        clusterLayer.setData([]); // Ensure visual clearing
    }
   // removeMonitorMarkers();
   // removeEcosystemPolygons();
};

const changeViewMode = () => {
    if (!props.map) return;
    clearLayers();
    
    if (viewMode.value === 'mass') {
        initMassMarks();
        if (massMarksLayer) {
            massMarksLayer.setMap(props.map);
            updateLayersData(); // Use this to ensure styles are re-calculated and applied
        }
    } else if (viewMode.value === 'cluster') {
        initCluster();
        if (clusterLayer) {
            clusterLayer.setMap(props.map);
            clusterLayer.setData(props.points || []); // Cluster usually handles raw data
        }
    }
};

// UI Persistence: Checkboxes
const savedShowMonitor = localStorage.getItem('dv_show_monitor');
const showMonitor = ref(savedShowMonitor !== null ? savedShowMonitor === 'true' : true);

const savedShowEcology = localStorage.getItem('dv_show_ecology');
const showEcology = ref(savedShowEcology !== null ? savedShowEcology === 'true' : true);

// Update localStorage when changed
watch(showMonitor, (val) => {
    localStorage.setItem('dv_show_monitor', val);
    // Rendering logic handles itself via other watchers, but we need to ensure they trigger.
    // The existing watcher on showMonitor will handle the render call.
});

watch(showEcology, (val) => {
    localStorage.setItem('dv_show_ecology', val);
    // The existing watcher on showEcology will handle the render call.
});

let monitorMarkers = []; // Array of AMap.Marker
let monitorInfoWindow = null;

const removeMonitorMarkers = () => {
    if (monitorMarkers.length > 0) {
        // map.remove(markersArray) helps remove multiple at once
        if (props.map) {
             props.map.remove(monitorMarkers);
        } else {
             // Fallback
             monitorMarkers.forEach(m => m.setMap(null));
        }
        monitorMarkers = [];
    }
};

const renderMonitorPoints = () => {
    if (!props.map || !window.AMap) return;

    // Always clear first to ensure clean state
    removeMonitorMarkers();

    if (!showMonitor.value || !props.monitorData || props.monitorData.length === 0) {
        return;
    }

    if (!monitorInfoWindow) {
        monitorInfoWindow = new window.AMap.InfoWindow({
            offset: new window.AMap.Pixel(0, -10),
            isCustom: true,
            closeWhenClickMap: true
        });
    }

    const start = performance.now();
    const newMarkers = [];
    
    props.monitorData.forEach((point) => {
          const pathData = point.symbol ? point.symbol.replace('path://', '') : '';
          
          if (pathData) {
            const marker = new window.AMap.Marker({
                position: point.lnglat,
                // Using content as per example
                content: `<div class="monitor-marker-dv" style="width: 30px; height: 30px;">
                            <svg viewBox="0 0 16 16" width="100%" height="100%">
                                <path d="${pathData}" fill="#ff4d4f" />
                            </svg>
                          </div>`,
                offset: new window.AMap.Pixel(-15, -15),
                title: point.name,
                zIndex: 500,
                extData: { url: point.url, name: point.name },
                map: props.map // Add directly to map on creation
            });
            
            marker.on('click', (e) => {
                const url = e.target.getExtData().url;
                if (url) {
                    window.open(url, '_blank');
                }
            });

            marker.on('mouseover', function (e) {
                const content = `
                    <div style="padding: 5px 10px; font-size: 12px; background: rgba(0,0,0,0.7); color: #fff; border: 1px solid #ff4d4f; border-radius: 4px; pointer-events: none; white-space: nowrap; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
                        ${e.target.getExtData().name}
                    </div>
                `;
                monitorInfoWindow.setContent(content);
                monitorInfoWindow.open(props.map, e.target.getPosition());
            });

            marker.on('mouseout', function () {
                monitorInfoWindow.close();
            });
            
            newMarkers.push(marker);
          }
    });

    monitorMarkers = newMarkers;
    // console.log('Visualizer: Rendered markers:', monitorMarkers.length, 'Time:', performance.now() - start);
};

watch(showMonitor, (val) => {
    if (val) {
        renderMonitorPoints();
    } else {
        removeMonitorMarkers();
    }
});

watch(() => props.monitorData, () => {
    if (showMonitor.value) {
        renderMonitorPoints();
    }
}, { deep: true });

watch(showEcology, (val) => {
    if (val) {
        renderEcologyLayer();
    } else {
        removeEcosystemPolygons();
    }
});

watch(() => props.ecosystemData, () => {
    if (showEcology.value) {
        renderEcologyLayer();
    }
}, { deep: true });

// Watch for map readiness
watch(() => props.map, (newMap) => {
    if (newMap && showData.value) {
        initData();
        changeViewMode();
        // Init Monitor
        renderMonitorPoints();
        // Init Ecology
        renderEcologyLayer();
    }
}, { immediate: true });

onUnmounted(() => {
    clearLayers();
});
const zoomToFirstRecord = () => {
    if (props.points && props.points.length > 0 && props.map) {
        const firstPoint = props.points[0];
        props.map.setZoomAndCenter(14, firstPoint.lnglat);
    }
};

defineExpose({
    zoomToFirstRecord
});
</script>

<style scoped>
.data-visualizer {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
    min-width: 220px;
}
.control-header {
    font-weight: bold;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
    margin-bottom: 5px;
}
.control-options {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin-left: 10px;
}
label {
    font-size: 13px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
}

:deep(.monitor-marker-dv) {
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
</style>

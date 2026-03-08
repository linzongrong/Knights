<template>
  <div class="stats-basin card" @dblclick="handleCardDblClick" title="Double click to filter map">
    <div class="header" :style="{ borderLeftColor: color }">
      <h3>{{ title }}</h3>
    </div>
    <div class="content">
        <div class="chart-container" ref="chartRef"></div>
        <div class="info-grid">
            <div class="info-item">
                <span class="label">{{ t('stats.area') }}</span>
                <span class="value">{{ stats.area }} <small>{{ t('stats.unitArea') }}</small></span>
            </div>
            <div class="info-item">
                <span class="label">{{ t('stats.totalCount') }}</span>
                <span class="value">{{ stats.count }} <small>{{ t('stats.unitCount') }}</small></span>
            </div>
            <div class="info-item">
                <span class="label">{{ t('stats.avgDbh') }}</span>
                <span class="value">{{ stats.avgDbh }} <small>{{ t('stats.unitDbh') }}</small></span>
            </div>
            <div class="info-item">
                 <span class="label">{{ t('stats.maxDbh') }}</span>
                 <span class="value">{{ stats.maxDbh }} <small>{{ t('stats.unitDbh') }}</small></span>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import { useI18n } from '../composables/useI18n';
const { t } = useI18n();

const props = defineProps({
  basinName: String, 
  title: String,
  color: { type: String, default: '#409eff' },
  data: { type: Array, default: () => [] } 
});

const emit = defineEmits(['dblclick']);

import lancangJson from '../assets/riverbasin/lcjly.json';
import ailaoJson from '../assets/riverbasin/als.json';
import gaoligongJson from '../assets/riverbasin/glgs.json';

const chartRef = ref(null);
let myChart = null;

const stats = ref({
  area: '-',
  count: 0,
  avgDbh: 0,
  maxDbh: 0,
  minDbh: 0
});

// Computed Stats Logic (Moved from malformed part)
const calculateStats = () => {
    // 1. Filter data for this basin
    const pointsData = (props.data || []).filter(p => {
        const pBasin = String(p.riverBasin || '').trim();
        return pBasin.includes(props.basinName);
    });

    stats.value.count = pointsData.length;

    // Area (Hardcoded based on name, similar to before)
    if (props.basinName === '澜沧江流域') stats.value.area = '16,500,000';
    else if (props.basinName === '哀牢山流域') stats.value.area = '1,000,000';
    else if (props.basinName === '高黎贡山山脉') stats.value.area = '405,500';
    else stats.value.area = '-';

    if (pointsData.length > 0) {
        const dbhs = pointsData.map(p => parseFloat(p.dbh) || 0);
        const total = dbhs.reduce((a, b) => a + b, 0);
        stats.value.avgDbh = (total / pointsData.length).toFixed(1);
        stats.value.maxDbh = Math.max(...dbhs).toFixed(1);
        stats.value.minDbh = Math.min(...dbhs).toFixed(1);
    } else {
        stats.value.avgDbh = 0;
        stats.value.maxDbh = 0;
        stats.value.minDbh = 0;
    }
    
    return pointsData;
};

const initChart = () => {
    if (!chartRef.value) return;
    myChart = echarts.init(chartRef.value);
    updateChart();
};

const updateChart = () => {
    if (!myChart) return;

    let geoJson = null;
    let mapName = '';
    if (props.basinName === '澜沧江流域') { geoJson = lancangJson; mapName = 'Lancang'; }
    else if (props.basinName === '哀牢山流域') { geoJson = ailaoJson; mapName = 'Ailao'; }
    else if (props.basinName === '高黎贡山山脉') { geoJson = gaoligongJson; mapName = 'Gaoligong'; }

    if (!geoJson) return;

    echarts.registerMap(mapName, geoJson);

    const pointsData = calculateStats().map(p => ({
        name: p.name,
        value: p.lnglat
    }));

    myChart.setOption({
        tooltip: {
            trigger: 'item',
            formatter: '{b}'
        },
        geo: {
            map: mapName,
            roam: true,
            label: { show: false },
            itemStyle: {
                areaColor: '#f3f4f6',
                borderColor: props.color,
                borderWidth: 1
            },
            emphasis: { itemStyle: { areaColor: '#e6ebf5' } }
        },
        series: [{
            name: 'Tea Trees',
            type: 'scatter',
            coordinateSystem: 'geo',
            data: pointsData,
            symbolSize: 2,
            itemStyle: { color: props.color, opacity: 0.8 }
        }]
    });
};

const handleCardDblClick = () => {
     let geoJson = null;
     if (props.basinName === '澜沧江流域') geoJson = lancangJson;
     else if (props.basinName === '哀牢山流域') geoJson = ailaoJson;
     else if (props.basinName === '高黎贡山山脉') geoJson = gaoligongJson;
     emit('dblclick', { name: props.basinName, geojson: geoJson });
};

watch(() => props.data, () => {
    updateChart();
}, { deep: true });

onMounted(() => {
    nextTick(() => {
        initChart();
        window.addEventListener('resize', handleResize);
    });
});

onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    if (myChart) myChart.dispose();
});

const handleResize = () => {
    if (myChart) myChart.resize();
};
</script>

<style scoped>
.stats-basin {
  width: 100%;
  min-width: 220px;
  background: var(--card-bg);
  display: flex;
  flex-direction: column;
  margin-top: 5px;
  cursor: pointer;
  transition: transform 0.2s, background 0.3s;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden; 
}
.stats-basin:hover {
    transform: translateX(5px);
}

.header {
    font-size: 14px;
    font-weight: bold;
    color: var(--text-color);
    padding: 8px 10px;
    border-bottom: 1px solid var(--border-color);
    background: rgba(0,0,0,0.02);
    border-left: 4px solid; /* Prop color */
}
.header h3 {
    margin: 0;
    font-size: 14px;
}

.content {
    display: flex;
    flex-direction: row;
    padding: 10px;
    gap: 10px;
}

.chart-container {
    height: 80px;
    width: 80px; 
    flex-shrink: 0;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.info-grid {
    display: flex;
    flex-direction: column;
    flex: 1;
    justify-content: space-around;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
}

.label {
    opacity: 0.8;
}

.value {
    font-weight: bold;
}
</style>

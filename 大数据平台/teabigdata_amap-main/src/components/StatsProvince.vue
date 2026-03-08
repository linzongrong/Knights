<template>
  <div class="stats-province card">
    <div class="chart-header">省份分布</div>
    <div class="chart-container">
      <div ref="chartRef" class="chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import { useI18n } from '../composables/useI18n';
const { t } = useI18n();

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
});

const chartRef = ref(null);
let chartInstance = null;

const initChart = () => {
    if (!chartRef.value) return;
    chartInstance = echarts.init(chartRef.value);
    updateChart();
};

const updateChart = () => {
    if (!chartInstance) return;

    // Aggregate data by province
    const counts = {};
    (props.data || []).forEach(p => {
        const prov = p.province || '未知';
        if (prov) {
            counts[prov] = (counts[prov] || 0) + 1;
        }
    });

    // Convert to ECharts Pie/Ring format [{ value, name }]
    let data = Object.keys(counts)
        .filter(key => counts[key] > 0) 
        .map(key => ({
            name: key,
            value: counts[key]
        }))
        .sort((a, b) => b.value - a.value);

    // Take top 5
    if (data.length > 5) {
        data = data.slice(0, 5);
    }

    // Get primary color from CSS variable
    const primaryColor = getComputedStyle(document.body).getPropertyValue('--primary-color').trim() || '#409eff';

    // Find Max Value for Primary Color Highlight
    if (data.length > 0) {
        const maxVal = data[0].value; 
        data = data.map((item) => {
            const isMax = item.value === maxVal; 
            return {
                ...item,
                itemStyle: {
                    color: isMax ? primaryColor : undefined, 
                    borderRadius: 4,
                    borderColor: '#fff',
                    borderWidth: 2
                }
            };
        });
    }

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} ({d}%)'
        },
        legend: {
            show: true,
            orient: 'vertical',
            right: 5,
            top: 'middle',
            itemGap: 8,
            itemWidth: 10,
            itemHeight: 10,
            textStyle: {
                fontSize: 12,
                color: '#666',
                rich: {
                    name: {
                        width: 50, 
                        align: 'left'
                    },
                    val: {
                        width: 40,
                        align: 'right',
                        fontWeight: 'bold',
                        color: '#333'
                    }
                }
            },
            formatter: function(name) {
                const item = data.find(p => p.name === name);
                const val = item ? item.value : '';
                let dName = name.length > 3 ? name.slice(0, 3) : name;
                return `{name|${dName}}{val|${val}}`;
            }
        },
        series: [
            {
                name: '省份分布',
                type: 'pie',
                radius: ['40%', '65%'], 
                center: ['25%', '50%'], // Left side
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 4,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false, // Hide labels, use legend
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: '14',
                        fontWeight: 'bold',
                        formatter: '{b}\n{c}'
                    }
                },
                labelLine: {
                    show: false
                },
                data: data
            }
        ]
    };

    chartInstance.setOption(option);
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
    if (chartInstance) chartInstance.dispose();
});

const handleResize = () => {
    if (chartInstance) chartInstance.resize();
};
</script>

<style scoped>
.stats-province {
  width: 100%;
  min-width: 220px;
  background: var(--card-bg);
  display: flex;
  flex-direction: column;
  margin-top: 5px;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden; 
}

.chart-header {
    font-size: 15px;
    font-weight: bold;
    color: var(--text-color);
    padding: 5px 6px;
    border-bottom: 1px solid var(--border-color);
    background: rgba(0,0,0,0.02); 
}

.chart-container {
    height: 180px; 
    width: 100%;
    padding: 10px;
}

.chart {
    width: 100%;
    height: 100%;
}
</style>

<template>
  <div class="dashboard-container">
    <header class="header">
      <div class="header-title">中国古茶树大数据 | 数据可视化平台 (Vue版)</div>
      <div class="header-time">{{ currentTime }}</div>
    </header>

    <main class="main-content">
      
      <section class="column col-left">
        <div class="panel">
          <div class="panel-title">澜沧江流域统计</div>
          <div class="chart-container" ref="chartLancangRef"></div>
          <div class="stat-list">
            <div class="stat-row" v-for="(item, index) in stats.lancang" :key="index">
              <span class="stat-label">{{ item.label }}</span>
              <span class="stat-value">{{ item.value }} <span class="unit">{{ item.unit }}</span></span>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">哀牢山山脉统计</div>
          <div class="chart-container" ref="chartAilaoRef"></div>
          <div class="stat-list">
             <div class="stat-row" v-for="(item, index) in stats.ailao" :key="index">
              <span class="stat-label">{{ item.label }}</span>
              <span class="stat-value">{{ item.value }} <span class="unit">{{ item.unit }}</span></span>
            </div>
          </div>
        </div>
      </section>

      <section class="column col-center">
        <div class="filter-bar">
          <select v-model="filterState.logic">
            <option value="union">并集</option>
            <option value="intersection">交集</option>
          </select>
          <select v-model="filterState.type">
            <option value="">= 茶种 =</option>
            <option value="puer">普洱茶</option>
          </select>
          <button class="btn-search" @click="handleSearch">查询</button>
        </div>

        <div class="panel map-panel">
          <div class="chart-container" ref="chartMapRef"></div>
        </div>

        <div class="bottom-section">
          <div class="panel top3-panel">
            <div class="panel-title">TOP 3 名古茶树</div>
            <div class="rank-list">
              <div class="rank-card" v-for="(tree, i) in topTrees" :key="i">
                <div class="rank-header">{{ i + 1 }}. {{ tree.name }}</div>
                <div class="rank-body">{{ tree.desc }}</div>
              </div>
            </div>
          </div>
          
          <div class="panel table-panel">
            <div class="panel-title">基径总量分布</div>
            <table class="data-table">
              <thead>
                <tr><th>基径</th><th>&lt;30</th><th>50</th><th>80</th></tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in tableData" :key="i">
                  <th>{{ row.row }}</th>
                  <td>{{ row.c1 }}</td>
                  <td>{{ row.c2 }}</td>
                  <td>{{ row.c3 }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section class="column col-right">
        <div class="panel">
          <div class="panel-title">各省份分布</div>
          <div class="chart-container" ref="chartProvinceRef"></div>
        </div>
        
        <div class="panel">
          <div class="panel-title">基径统计 (Top 5)</div>
          <div class="chart-container" ref="chartDiameterRef"></div>
        </div>

        <div class="panel">
          <div class="panel-title">高黎贡山走势</div>
          <div class="chart-container" ref="chartGaoligongRef"></div>
        </div>
      </section>

    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

// --- 状态数据 (响应式) ---
const currentTime = ref('');
const timer = ref(null);

const filterState = reactive({ logic: 'union', type: '' });

// 模拟数据：统计文本
const stats = reactive({
  lancang: [
    { label: '流域面积', value: '8,005,251', unit: '公顷' },
    { label: '总株数', value: '282', unit: '株' },
    { label: '平均基径', value: '37.08', unit: 'cm' }
  ],
  ailao: [
    { label: '山脉面积', value: '2,870,172', unit: '公顷' },
    { label: '总株数', value: '68', unit: '株' },
    { label: '最大基径', value: '105.1', unit: 'cm' }
  ]
});

// 模拟数据：Top 3
const topTrees = reactive([
  { name: '版纳勐海南糯山', desc: '栽培型，树龄800年，树高8.8m' },
  { name: '版纳勐海巴达', desc: '野生型，树龄1700年，基径100cm' },
  { name: '普洱澜沧邦威', desc: '过渡型，基径78.9cm' }
]);

// 模拟数据：表格
const tableData = reactive([
  { row: '50', c1: 1935, c2: 236, c3: '-' },
  { row: '80', c1: 1948, c2: 249, c3: 13 },
  { row: '100', c1: 2301, c2: 602, c3: 366 }
]);

// --- DOM 引用 (Refs) ---
const chartMapRef = ref(null);
const chartLancangRef = ref(null);
const chartAilaoRef = ref(null);
const chartProvinceRef = ref(null);
const chartDiameterRef = ref(null);
const chartGaoligongRef = ref(null);

// 保存 ECharts 实例以便 resize
let chartInstances = [];

// --- 方法 ---

const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleString('zh-CN', { 
    year: 'numeric', month: '2-digit', day: '2-digit', 
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    weekday: 'long'
  });
};

const handleSearch = () => {
  alert(`正在查询: 逻辑=${filterState.logic}, 茶种=${filterState.type || '全部'}`);
  // 这里可以调用 API 刷新图表数据
};

// 通用图表配置
const getBaseOption = () => ({
  backgroundColor: 'transparent',
  textStyle: { fontFamily: 'Microsoft YaHei' },
  tooltip: { trigger: 'item', backgroundColor: 'rgba(50,50,50,0.9)', textStyle: { color: '#fff' } },
  grid: { top: 30, bottom: 20, left: 40, right: 10, containLabel: true }
});

// 初始化图表
const initCharts = async () => {
  await nextTick(); // 确保 DOM 已渲染

  // 1. 澜沧江雷达图
  const chartLancang = echarts.init(chartLancangRef.value);
  chartLancang.setOption({
    ...getBaseOption(),
    radar: {
      indicator: [
        { name: '树高', max: 20 }, { name: '树幅', max: 20 },
        { name: '基径', max: 100 }, { name: '树龄', max: 1000 }, { name: '密度', max: 100 }
      ],
      axisName: { color: '#999' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    series: [{
      type: 'radar',
      data: [{ value: [7.14, 5.32, 37.08, 300, 50], name: '属性' }],
      areaStyle: { color: 'rgba(0, 240, 255, 0.3)' },
      lineStyle: { color: '#00f0ff' }
    }]
  });
  chartInstances.push(chartLancang);

  // 2. 哀牢山仪表盘
  const chartAilao = echarts.init(chartAilaoRef.value);
  chartAilao.setOption({
    ...getBaseOption(),
    series: [{
      type: 'gauge',
      radius: '90%',
      progress: { show: true, width: 8, itemStyle: { color: '#00f0ff' } },
      axisLine: { lineStyle: { width: 8, color: [[1, '#333']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      pointer: { length: '50%', width: 3, itemStyle: { color: '#fff' } },
      detail: { valueAnimation: true, fontSize: 16, offsetCenter: [0, '70%'], color: '#fff', formatter: '{value}株' },
      data: [{ value: 68 }]
    }]
  });
  chartInstances.push(chartAilao);

  // 3. 省份饼图
  const chartProv = echarts.init(chartProvinceRef.value);
  chartProv.setOption({
    ...getBaseOption(),
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      label: { color: '#ccc' },
      data: [
        { value: 1048, name: '云南', itemStyle: { color: '#5470c6' } },
        { value: 300, name: '贵州', itemStyle: { color: '#91cc75' } },
        { value: 200, name: '四川', itemStyle: { color: '#fac858' } },
        { value: 50, name: '其他', itemStyle: { color: '#73c0de' } }
      ]
    }]
  });
  chartInstances.push(chartProv);

  // 4. 基径柱状图
  const chartDia = echarts.init(chartDiameterRef.value);
  chartDia.setOption({
    ...getBaseOption(),
    xAxis: { type: 'category', data: ['<30', '30-50', '50-80', '>80'], axisLabel: { color: '#aaa' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#333' } }, axisLabel: { color: '#aaa' } },
    series: [{
      data: [120, 200, 150, 80],
      type: 'bar',
      itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#83bff6' }, { offset: 1, color: '#188df0' }]) }
    }]
  });
  chartInstances.push(chartDia);

  // 5. 高黎贡山折线图
  const chartGao = echarts.init(chartGaoligongRef.value);
  chartGao.setOption({
    ...getBaseOption(),
    xAxis: { type: 'category', boundaryGap: false, data: ['1月', '3月', '6月', '9月'], axisLabel: { color: '#aaa' } },
    yAxis: { type: 'value', splitLine: { show: false }, axisLabel: { show: false } },
    series: [{
      data: [10, 25, 18, 38],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3, color: '#ff0' },
      itemStyle: { color: '#ff0' }
    }]
  });
  chartInstances.push(chartGao);

  // 6. 中国地图 (需要获取 GeoJSON)
  // 注意：这里使用在线 GeoJSON 地址，如果不可用请替换为本地 JSON
  try {
    const mapRes = await axios.get('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json');
    echarts.registerMap('china', mapRes.data);
    
    const chartMap = echarts.init(chartMapRef.value);
    chartMap.setOption({
      ...getBaseOption(),
      geo: {
        map: 'china',
        roam: true,
        itemStyle: { areaColor: '#0a1a36', borderColor: '#1e4878', borderWidth: 1 },
        emphasis: { itemStyle: { areaColor: '#2a333d' } }
      },
      series: [{
        type: 'scatter',
        coordinateSystem: 'geo',
        data: [
          { name: '西双版纳', value: [100.80, 22.02, 100] },
          { name: '普洱', value: [100.97, 22.98, 80] }
        ],
        symbolSize: 8,
        itemStyle: { color: '#00f0ff', shadowBlur: 10 }
      }]
    });
    chartInstances.push(chartMap);
  } catch (error) {
    console.error("地图加载失败", error);
    chartMapRef.value.innerHTML = "<div style='color:white;text-align:center;padding-top:100px'>地图数据加载中...</div>";
  }
};

// --- 生命周期 ---
onMounted(() => {
  updateTime();
  timer.value = setInterval(updateTime, 1000);
  initCharts();
  
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  clearInterval(timer.value);
  window.removeEventListener('resize', handleResize);
  chartInstances.forEach(chart => chart.dispose());
});

const handleResize = () => {
  chartInstances.forEach(chart => chart.resize());
};
</script>

<style scoped>
/* CSS 变量定义在组件作用域内，或者推荐放在全局 css 文件中 */
.dashboard-container {
  --bg-color: #050d21;
  --panel-bg: rgba(16, 33, 64, 0.6);
  --border-color: #1c3e75;
  --text-main: #ffffff;
  --text-sub: #a0cfff;
  --accent-color: #00f0ff;
  
  width: 100vw;
  height: 100vh;
  background-color: var(--bg-color);
  background-image: radial-gradient(circle at 50% 50%, #0d1e3d 0%, #050d21 80%);
  color: var(--text-main);
  font-family: "Microsoft YaHei", sans-serif;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Header */
.header {
  height: 60px;
  background: rgba(0,0,0,0.2);
  border-bottom: 2px solid var(--border-color);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.1);
}
.header-title {
  font-size: 24px;
  font-weight: bold;
  letter-spacing: 3px;
  background: linear-gradient(to bottom, #fff, #84b7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.header-time {
  position: absolute;
  right: 20px;
  font-family: 'Courier New', monospace;
  color: var(--accent-color);
}

/* Layout */
.main-content {
  flex: 1;
  display: flex;
  padding: 10px;
  gap: 10px;
  overflow: hidden;
}
.column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.col-left, .col-right { width: 25%; }
.col-center { width: 50%; }

/* Panels */
.panel {
  flex: 1;
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 10px;
  position: relative;
  display: flex;
  flex-direction: column;
}
/* 装饰角标 */
.panel::before {
  content: ""; position: absolute; top: 0; left: 0;
  width: 8px; height: 8px;
  border-top: 2px solid var(--accent-color); border-left: 2px solid var(--accent-color);
}
.panel::after {
  content: ""; position: absolute; bottom: 0; right: 0;
  width: 8px; height: 8px;
  border-bottom: 2px solid var(--accent-color); border-right: 2px solid var(--accent-color);
}

.panel-title {
  font-size: 14px;
  color: var(--text-sub);
  border-left: 3px solid var(--accent-color);
  padding-left: 8px;
  margin-bottom: 8px;
  height: 20px;
  line-height: 20px;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 0; /* Flexbox 溢出修复 */
}

/* Stats Text */
.stat-list {
  margin-top: auto;
  padding-top: 5px;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed rgba(255,255,255,0.1);
  font-size: 12px;
  padding: 2px 0;
}
.stat-value {
  color: var(--accent-color);
  font-weight: bold;
}
.unit {
  font-size: 10px;
  color: #888;
}

/* Center Section */
.filter-bar {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 5px;
}
.filter-bar select, .btn-search {
  background: rgba(0,0,0,0.4);
  border: 1px solid var(--border-color);
  color: #ccc;
  padding: 4px 8px;
  border-radius: 2px;
  cursor: pointer;
}
.btn-search:hover {
  background: var(--accent-color);
  color: #000;
}

.map-panel {
  flex: 2 !important; /* 地图占更大空间 */
}
.bottom-section {
  flex: 1;
  display: flex;
  gap: 10px;
}
.top3-panel, .table-panel {
  flex: 1;
}

/* Rank List */
.rank-list {
  overflow-y: auto;
  flex: 1;
}
.rank-card {
  background: rgba(255,255,255,0.05);
  margin-bottom: 5px;
  padding: 5px;
  border: 1px solid #333;
}
.rank-header {
  color: #fff;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 2px;
}
.rank-body {
  font-size: 11px;
  color: #aaa;
}

/* Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  text-align: center;
}
.data-table th, .data-table td {
  border: 1px solid #333;
  padding: 3px;
  color: #ddd;
}
.data-table th {
  background: rgba(255,255,255,0.1);
  color: var(--text-sub);
}
</style>

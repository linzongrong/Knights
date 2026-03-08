<script setup>
import { computed, ref, watch } from 'vue';
import { useI18n } from '../composables/useI18n';
const { t } = useI18n();

const props = defineProps({
  data: { type: Array, default: () => [] }
});

const count = computed(() => props.data.length);
const displayCount = ref(0);

watch(count, (newVal) => {
    // Simple easing animation
    const start = displayCount.value;
    const end = newVal;
    const duration = 1000; // 1s
    const startTime = performance.now();

    const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out quart
        const ease = 1 - Math.pow(1 - progress, 4);
        
        displayCount.value = Math.floor(start + (end - start) * ease);

        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    requestAnimationFrame(animate);
}, { immediate: true });

const avgDbh = computed(() => {
    if (props.data.length === 0) return 0;
    const total = props.data.reduce((sum, p) => sum + (p.dbh || 0), 0);
    return (total / props.data.length).toFixed(1);
});

const maxDbh = computed(() => {
    if (props.data.length === 0) return 0;
    // ensure dbh is number
    return Math.max(...props.data.map(p => parseFloat(p.dbh) || 0)).toFixed(1);
});
</script>

<template>
  <div class="current-view-stats card">
    <h3>{{ t('currentStats.title') }}</h3>
    <div style="text-align: center; margin-bottom: 20px;">
        <strong  class="hero-number">{{ displayCount }}</strong>
        <div style="font-size: 12px; color: #999; margin-top: 5px;">{{ t('currentStats.count') }}</div>
    </div>
    
    <div class="stat-row">
        <span>{{ t('currentStats.avgDbh') }}</span>
        <strong class="sub-number">{{ avgDbh }} <small>cm</small></strong>
    </div>
    <div class="stat-row">
        <span>{{ t('currentStats.maxDbh') }}</span>
        <strong class="sub-number">{{ maxDbh }} <small>cm</small></strong>
    </div>
  </div>
</template>

<style scoped>
.current-view-stats {
    width: 100%;
    min-width: 220px;
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.9), rgba(50, 50, 50, 0.9));
    padding: 15px; 
    border-radius: 8px;
    color: var(--text-color);
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}

.current-view-stats h3 {
    margin: 0 0 15px 0;
    font-size: 14px;
    font-weight: bold;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 8px;
    color: var(--text-color);
    letter-spacing: 1px;
    text-transform: uppercase;
    opacity: 0.8;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-size: 13px;
}

.stat-row:last-child {
    margin-bottom: 0;
}

.stat-row span {
    opacity: 0.7;
    font-size: 12px;
}

.hero-number {
    font-family: 'Courier New', Courier, monospace; /* Placeholder for digital font */
    font-size: 42px;
    font-weight: bold;
    color: #e6a23c;
    text-shadow: 0 0 15px rgba(230, 162, 60, 0.5);
    line-height: 1;
    display: block; /* Ensure it takes full width for centering context */
}

.sub-number {
    font-family: 'Courier New', Courier, monospace;
    font-size: 18px;
    font-weight: bold;
    color: #409eff;
    text-shadow: 0 0 5px rgba(230, 162, 60, 0.3);
}

.sub-number small {
    font-size: 12px;
    opacity: 0.7;
    margin-left: 2px;
}
</style>

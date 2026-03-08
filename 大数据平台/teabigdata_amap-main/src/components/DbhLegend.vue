<script setup>
import { computed } from 'vue';
import { useI18n } from '../composables/useI18n';
const { t } = useI18n();

const props = defineProps({
  data: { type: Array, default: () => [] }
});

const calculateCounts = (data) => {
    const counts = [0, 0, 0, 0, 0];
    for (const p of data) {
        const dbh = parseFloat(p.dbh);
        if (isNaN(dbh)) {
            // counts[0]++; // Treat as small or ignore? Let's ignore or use first
            continue;
        }
        if (dbh < 30) counts[0]++;
        else if (dbh >= 30 && dbh < 50) counts[1]++;
        else if (dbh >= 50 && dbh < 80) counts[2]++;
        else if (dbh >= 80 && dbh < 100) counts[3]++;
        else if (dbh >= 100) counts[4]++;
    }
    return counts;
};

const legendItems = computed(() => {
    const counts = calculateCounts(props.data);
    return [
        { color: '#52c41a', label: t('legend.labels.l30'), count: counts[0] },
        { color: '#faad14', label: t('legend.labels.l30_50'), count: counts[1] },
        { color: '#fa8c16', label: t('legend.labels.l50_80'), count: counts[2] },
        { color: '#f5222d', label: t('legend.labels.l80_100'), count: counts[3] },
        { color: '#722ed1', label: t('legend.labels.g100'), count: counts[4] }
    ];
});
</script>

<template>
  <div class="dbh-legend card">
      <div class="header">{{ t('legend.title') }}</div>
      <div class="legend-list">
          <div v-for="(item, index) in legendItems" :key="index" class="legend-item">
              <span class="color-box" :style="{ backgroundColor: item.color }"></span>
              <span class="label">{{ item.label }}</span>
              <span class="count" v-if="data.length > 0">{{ item.count }}</span>
          </div>
      </div>
  </div>
</template>

<style scoped>
.dbh-legend {
    width: 100%;
    min-width: 220px;
    background: var(--card-bg);
    padding: 10px;
    border-radius: 8px;
    color: var(--text-color);
    border: 1px solid var(--border-color);
}

.header {
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 5px;
}

.legend-list {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
}

.color-box {
    width: 12px;
    height: 12px;
    border-radius: 2px;
}

.label {
    opacity: 0.9;
    flex: 1;
}

.count {
    font-weight: bold;
    opacity: 0.7;
    margin-left: auto; /* Push to right */
}
</style>

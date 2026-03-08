<script setup>
import { ref } from 'vue';
import { useI18n } from '../composables/useI18n';
const { t } = useI18n();

const topTrees = ref([
    {
        rank: 1,
        name: "锦绣茶祖",
        location: "凤庆县小湾镇",
        age: "3200+",
        dbh: "185",
        height: "10.6",
        image: "/images/top1.jpg" // Placeholder
    },
    {
        rank: 2,
        name: "千家寨1号",
        location: "镇沅县九甲镇",
        age: "2700+",
        dbh: "120",
        height: "25.6",
        image: "/images/top2.jpg"
    },
    {
        rank: 3,
        name: "邦崴古茶王",
        location: "澜沧县富东乡",
        age: "1000+",
        dbh: "118", // Actually somewhat debated, using approx
        height: "11.8",
        image: "/images/top3.jpg"
    }
]);
</script>

<template>
  <div class="top-trees card">
      <div class="header">
          <h3>{{ t('topTrees.title') }}</h3>
      </div>
      <div class="tree-list">
          <div v-for="tree in topTrees" :key="tree.rank" class="tree-item">
              <div class="tree-rank" :class="'rank-' + tree.rank">{{ tree.rank }}</div>
              <div class="tree-info">
                  <div class="tree-name">{{ tree.name }}</div>
                  <div class="tree-detail">
                      <span>{{ tree.location }}</span> | 
                      <span>{{ tree.age }}年</span>
                  </div>
              </div>
          </div>
      </div>
  </div>
</template>

<style scoped>
.top-trees {
    width: 100%;
    min-width: 300px; /* Adjust width as needed */
    background: var(--card-bg);
    color: var(--text-color);
    border: 1px solid var(--border-color);
    padding: 10px;
    border-radius: 8px;
}

.header h3 {
    margin: 0 0 10px 0;
    font-size: 14px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 5px;
    color: var(--text-color);
}

.tree-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.tree-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 5px;
    border-bottom: 1px dashed var(--border-color);
}

.tree-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.tree-rank {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #eee;
    color: #666;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    flex-shrink: 0;
}

.rank-1 { background: #ff4d4f; color: white; }
.rank-2 { background: #faad14; color: white; }
.rank-3 { background: #52c41a; color: white; }

.tree-info {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.tree-name {
    font-weight: bold;
    font-size: 13px;
    color: var(--text-color);
}

.tree-detail {
    font-size: 11px;
    color: var(--text-color);
    opacity: 0.7;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>

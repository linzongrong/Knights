<!-- src/widgets/CoreSearchMap/CoreSearchMap.vue -->
<template>
  <div class="core-search-map">
    <div class="widget-header">
      <h3>{{ title }}</h3>
      <el-button 
        v-if="widgetId" 
        size="small" 
        @click="$emit('close')"
        style="margin-left: auto"
      >
        关闭
      </el-button>
    </div>
    <div class="map-placeholder">
      🗺️ 古茶树地图探索模块（开发中）
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  widgetId?: string
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>

<style scoped>
.core-search-map {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.widget-header {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
}
.map-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #edf2f7;
  color: #64748b;
  font-size: 16px;
}
</style>
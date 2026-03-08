<!-- src/widgets/AIAssistant/AIAssistant.vue -->
<template>
  <div class="ai-assistant">
    <div class="widget-header">
      <h3>{{ title }}</h3>
      <!-- 可选：加个关闭按钮 -->
      <el-button 
        v-if="widgetId" 
        size="small" 
        @click="$emit('close')"
        style="margin-left: auto"
      >
        关闭
      </el-button>
    </div>
    <div class="widget-content">
      <p>🤖 AI 助手已加载！</p>
      <p>这是一个占位组件，后续可集成大模型对话功能。</p>
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
.ai-assistant {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
}
.widget-header {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
}
.widget-content {
  padding: 16px;
  flex: 1;
  overflow: auto;
}
</style>
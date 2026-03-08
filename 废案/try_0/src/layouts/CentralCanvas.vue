<!-- src/layouts/CentralCanvas.vue -->
<template>
  <div class="central-canvas">
    <GridLayout
      v-if="layout.length > 0"
      :layout="layout"
      :col-num="24"
      :row-height="30"
      :is-draggable="true"
      :is-resizable="true"
      :vertical-compact="true"
      :margin="[10, 10]"
      @layout-updated="onLayoutUpdated"
    >
      <GridItem
        v-for="item in layout"
        :key="item.i"
        :x="item.x"
        :y="item.y"
        :w="item.w"
        :h="item.h"
        :i="item.i"
        class="grid-item"
      >
        <div class="widget-wrapper">
          <component
            :is="loadedComponents[item.type]"
            :widget-id="item.i"
            :title="item.title"
            @close="handleClose(item.i)"
          />
        </div>
      </GridItem>
    </GridLayout>

    <div v-else class="empty-canvas">
      <p>请从左侧添加组件到画布</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { GridLayout, GridItem } from 'vue-grid-layout'
import { useDashboardStore } from '@/stores/dashboard'

// 异步组件映射（保留你的设计）
const componentMap = {
  CoreSearchMap: () => import('@/widgets/CoreSearchMap/CoreSearchMap.vue'),
  BaseDiameterBar: () => import('@/widgets/BaseDiameterBar/BaseDiameterBar.vue'),
  AIAssistant: () => import('@/widgets/AIAssistant/AIAssistant.vue')
}

// 缓存已加载的组件
const loadedComponents = ref<Record<string, any>>({})

// 预加载所有组件
Object.entries(componentMap).forEach(([type, loader]) => {
  loader().then((mod) => {
    loadedComponents.value[type] = mod.default || mod
  })
})

const dashboardStore = useDashboardStore()
const visibleWidgets = computed(() => dashboardStore.visibleWidgets)

// 转换为 vue-grid-layout 所需格式
interface LayoutItem {
  i: string
  x: number
  y: number
  w: number
  h: number
  type: string
  title: string
}

const layout = ref<LayoutItem[]>([])

// 同步 widgets → layout，并处理 y: Infinity
watch(
  visibleWidgets,
  (widgets) => {
    // 计算当前最大 Y 值，用于新组件自动放置
    const maxY = widgets.reduce((max, w) => Math.max(max, w.grid.y + w.grid.h), 0)

    layout.value = widgets.map(widget => {
      let y = widget.grid.y
      if (y === Infinity) {
        y = maxY // 自动放到最底部
      }
      return {
        i: widget.id,
        x: widget.grid.x,
        y,
        w: widget.grid.w,
        h: widget.grid.h,
        type: widget.type,
        title: widget.title
      }
    })
  },
  { immediate: true }
)

const handleClose = (id: string) => {
  dashboardStore.closeWidget(id)
}

const onLayoutUpdated = (newLayout: LayoutItem[]) => {
  newLayout.forEach(item => {
    dashboardStore.updateWidgetLayout(item.i, {
      x: item.x,
      y: item.y,
      w: item.w,
      h: item.h
    })
  })
}
</script>

<style scoped>
.central-canvas {
  height: 100%;
  padding: 16px;
  overflow: auto;
  background: #f5f7fa;
}

.grid-item {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
}

.widget-wrapper {
  width: 100%;
  height: 100%;
}

.empty-canvas {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 16px;
}
</style>
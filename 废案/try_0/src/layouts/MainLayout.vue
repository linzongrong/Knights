<!-- file: src/layouts/MainLayout.vue -->
<template>
  <div class="main-layout">
    <!-- 左侧控制栏 (可隐藏) -->
    <div 
      class="left-sidebar" 
      :class="{ 'left-sidebar--collapsed': isSidebarCollapsed }"
      @mouseenter="isSidebarCollapsed = false"
      @mouseleave="isSidebarCollapsed = true"
    >
      <!-- 顶部用户区域 -->
      <div class="user-area">
         <UserProfile :collapsed="isSidebarCollapsed"@command="handleUserCommand"/>
      </div>

      <!-- 分割线 -->
      <el-divider v-if="!isSidebarCollapsed" />

      <!-- 模块管理区域：已打开的组件列表 -->
      <div class="module-section" v-if="!isSidebarCollapsed">
        <div class="section-title">
          <el-icon><folder-opened /></el-icon>
          <span>已打开模块</span>
        </div>
        <div class="module-list">
          <div 
            v-for="widget in dashboardStore.activeWidgets" 
            :key="widget.id"
            class="module-item"
            :class="{ 'module-item--active': widget.status === 'active' }"
            @click="toggleWidget(widget)"
          >
            <div class="module-icon">
              <el-icon>
                <component :is="getWidgetIcon(widget.type)" />
              </el-icon>
            </div>
            <div class="module-info">
              <div class="module-title">{{ widget.title }}</div>
              <div class="module-status">{{ widget.status === 'active' ? '已显示' : '已隐藏' }}</div>
            </div>
            <div class="module-actions">
              <el-icon 
                v-if="widget.status === 'active'"
                @click.stop="dashboardStore.hideWidget(widget.id)"
                class="action-icon"
              >
                <minus />
              </el-icon>
              <el-icon 
                v-if="widget.status === 'hidden'"
                @click.stop="dashboardStore.activateWidget(widget.id)"
                class="action-icon"
              >
                <full-screen />
              </el-icon>
              <el-icon 
                @click.stop="dashboardStore.closeWidget(widget.id)"
                class="action-icon action-icon--close"
              >
                <close />
              </el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 组件库区域 -->
      <div class="library-section" v-if="!isSidebarCollapsed">
        <div class="section-title">
          <el-icon><plus /></el-icon>
          <span>添加组件</span>
        </div>
        <div class="library-grid">
          <div 
            v-for="item in dashboardStore.chartLibrary"
            :key="item.type"
            class="library-item"
            @click="dashboardStore.addWidget(item.type)"
          >
            <div class="library-icon">
              <el-icon :size="24">
                <component :is="item.icon" />
              </el-icon>
            </div>
            <div class="library-name">{{ item.name }}</div>
            <div class="library-group">{{ item.group }}</div>
          </div>
        </div>
      </div>

      <!-- 折叠状态下的最小化提示 -->
      <div class="collapsed-hint" v-if="isSidebarCollapsed">
        <el-tooltip
          placement="right"
          content="鼠标移入展开侧边栏"
        >
          <el-icon :size="24"><d-arrow-right /></el-icon>
        </el-tooltip>
      </div>
    </div>

    <!-- 中央画布区域 -->
    <div class="central-canvas-wrapper">
      <CentralCanvas />
    </div>
  </div>
</template>

<script setup>
import CentralCanvas from '@/layouts/CentralCanvas.vue'
import { ref } from 'vue'
import UserProfile from '@/components/global/UserProfile.vue'
import { useDashboardStore } from '@/stores/dashboard'
import {
  FolderOpened,
  Minus,
  FullScreen,
  Close,
  Plus,
  DArrowRight,
  Location,
  Histogram,
  ChatDotSquare
} from '@element-plus/icons-vue'

// 响应式数据
const isSidebarCollapsed = ref(true)
const dashboardStore = useDashboardStore()

// 用户命令处理
const handleUserCommand = (command) => {
  console.log('User command:', command)
  // 这里可以添加更多的用户命令处理逻辑
}

// 切换组件显示状态
const toggleWidget = (widget) => {
  if (widget.status === 'active') {
    dashboardStore.hideWidget(widget.id)
  } else {
    dashboardStore.activateWidget(widget.id)
  }
}

// 获取组件图标
const getWidgetIcon = (type) => {
  console.log('Type:', type)
  const iconMap = {
    CoreSearchMap: Location,
    BaseDiameterBar: Histogram,
    AIAssistant: ChatDotSquare
  }
  const icon = iconMap[type] || FolderOpened
  console.log('Icon:', icon)
  return icon
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* 左侧栏样式 */
.left-sidebar {
  width: 280px;
  background: linear-gradient(180deg, #1a2b3c 0%, #2c3e50 100%);
  color: #ecf0f1;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 100;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.left-sidebar--collapsed {
  width: 60px;
}

/* 用户区域 */
.user-area {
  padding: 0;
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
}

.user-role {
  font-size: 12px;
  color: #95a5a6;
  margin-top: 2px;
}

/* 模块区域 */
.module-section {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #bdc3c7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.module-item:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(52, 152, 219, 0.3);
}

.module-item--active {
  background: rgba(52, 152, 219, 0.15);
  border-color: rgba(52, 152, 219, 0.5);
}

.module-icon {
  margin-right: 12px;
  color: #3498db;
}

.module-info {
  flex: 1;
}

.module-title {
  font-size: 13px;
  font-weight: 500;
}

.module-status {
  font-size: 11px;
  color: #95a5a6;
}

.module-actions {
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.module-item:hover .module-actions {
  opacity: 1;
}

.action-icon {
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-icon:hover {
  background: rgba(255, 255, 255, 0.1);
}

.action-icon--close:hover {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

/* 组件库区域 */
.library-section {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.library-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.library-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.library-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(46, 204, 113, 0.3);
  transform: translateY(-2px);
}

.library-icon {
  margin-bottom: 6px;
  color: #2ecc71;
}

.library-name {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 2px;
}

.library-group {
  font-size: 10px;
  color: #95a5a6;
}

/* 折叠提示 */
.collapsed-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #7f8c8d;
}

/* 中央画布区域 */
.central-canvas-wrapper {
  flex: 1;
  overflow: hidden;
  background: #f5f7fa;
}
</style>

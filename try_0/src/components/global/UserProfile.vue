<template>
  <div class="user-profile">
    <!-- 紧凑模式：侧边栏折叠时显示 -->
    <div 
      v-if="collapsed" 
      class="user-compact"
      @click="toggleDropdown"
    >
      <el-avatar :size="32" :src="user.avatar" />
      <el-icon class="dropdown-icon" :class="{ 'dropdown-icon--open': dropdownVisible }">
        <arrow-down />
      </el-icon>
    </div>

    <!-- 完整模式：侧边栏展开时显示 -->
    <div v-else class="user-full">
      <div class="user-info" @click="toggleDropdown">
        <el-avatar :size="40" :src="user.avatar" class="user-avatar" />
        <div class="user-details">
          <div class="user-name">{{ user.name }}</div>
          <div class="user-role">{{ user.role }}</div>
        </div>
        <el-icon class="dropdown-icon" :class="{ 'dropdown-icon--open': dropdownVisible }">
          <arrow-down />
        </el-icon>
      </div>

      <!-- 下拉菜单 -->
      <div v-if="dropdownVisible" class="user-dropdown">
        <div class="dropdown-section">
          <div class="dropdown-item" @click="handleCommand('profile')">
            <el-icon><user /></el-icon>
            <span>个人中心</span>
          </div>
          <div class="dropdown-item" @click="handleCommand('notifications')">
            <el-icon><bell /></el-icon>
            <span>消息通知</span>
            <el-badge :value="unreadCount" class="notification-badge" />
          </div>
        </div>
        
        <el-divider class="dropdown-divider" />
        
        <div class="dropdown-section">
          <div class="dropdown-item" @click="handleCommand('settings')">
            <el-icon><setting /></el-icon>
            <span>系统设置</span>
          </div>
          <div class="dropdown-item dropdown-item--danger" @click="handleCommand('logout')">
            <el-icon><switch-button /></el-icon>
            <span>退出登录</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  ArrowDown, User, Bell, Setting, SwitchButton
} from '@element-plus/icons-vue'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['command'])

// 使用用户状态管理
const userStore = useUserStore()
const user = computed(() => userStore.currentUser)
const unreadCount = computed(() => userStore.unreadNotifications)

// 下拉菜单状态
const dropdownVisible = ref(false)

const toggleDropdown = () => {
  dropdownVisible.value = !dropdownVisible.value
}

const handleCommand = (command) => {
  dropdownVisible.value = false
  emit('command', command)
  
  // 你也可以在这里直接调用 userStore 的方法
  switch (command) {
    case 'logout':
      userStore.logout()
      break
    // 其他命令处理...
  }
}

// 点击外部关闭下拉菜单
import { onClickOutside } from '@vueuse/core'
const dropdownRef = ref(null)
onClickOutside(dropdownRef, () => {
  dropdownVisible.value = false
})
</script>

<style scoped>
.user-profile {
  position: relative;
  user-select: none;
}

/* 紧凑模式 */
.user-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px 0;
  cursor: pointer;
  transition: background-coler 0.2s;
  border-radius: 6px;
}

.user-compact:hover {
  background: rgba(255, 255, 255, 0.1);
}

.dropdown-icon {
  margin-left: 4px;
  transition: transform 0.2s;
}

.dropdown-icon--open {
  transform: rotate(180deg);
}

/* 完整模式 */
.user-full {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background-coler 0.2s;
  border-radius: 8px;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.08);
}

.user-avatar {
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  margin-left: 12px;
  min-width: 0; /* 防止文本溢出 */
}

.user-name {
  font-weight: 600;
  font-size: 14px;
  color: #fff;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  color: #95a5a6;
}

/* 下拉菜单 */
.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 20px;
  right: 20px;
  background: #2c3e50;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dropdown-section {
  padding: 8px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: background-coler 0.2s;
  color: #ecf0f1;
  font-size: 13px;
}

.dropdown-item:hover {
  background: rgba(52, 152, 219, 0.2);
}

.dropdown-item .el-icon {
  margin-right: 12px;
  font-size: 16px;
  color: #3498db;
}

.dropdown-item--danger .el-icon {
  color: #e74c3c;
}

.dropdown-item--danger:hover {
  background: rgba(231, 76, 60, 0.2);
}

.notification-badge {
  margin-left: auto;
}

.dropdown-divider {
  margin: 4px 0;
  border-color: rgba(255, 255, 255, 0.1);
}
</style>
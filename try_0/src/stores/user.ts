import { defineStore } from 'pinia'

interface User {
  id: string;
  name: string;
  role: string;
  avatar: string;
  email: string;
}

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: {
      id: '001',
      name: '古茶树研究员',
      role: '高级管理员',
      avatar: '',
      email: 'researcher@tea-conservation.org'
    } as User,
    unreadNotifications: 3,
    isLoggedIn: true
  }),

  actions: {
    logout() {
      // 登出逻辑
      this.isLoggedIn = false
      // 实际项目中这里会有 API 调用
    },

    updateProfile(data: Partial<User>) {
      this.currentUser = { ...this.currentUser, ...data }
    },

    markNotificationsAsRead() {
      this.unreadNotifications = 0
    }
  }
})

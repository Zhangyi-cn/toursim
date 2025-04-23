import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    primaryColor: '#1890ff',
    isDarkMode: false
  }),

  actions: {
    initTheme() {
      // 从 localStorage 获取主题设置
      const savedPrimaryColor = localStorage.getItem('primaryColor')
      const savedDarkMode = localStorage.getItem('darkMode')

      if (savedPrimaryColor) {
        this.primaryColor = savedPrimaryColor
      }

      if (savedDarkMode) {
        this.isDarkMode = savedDarkMode === 'true'
      }

      // 应用主题
      this.applyTheme()
    },

    setPrimaryColor(color: string) {
      this.primaryColor = color
      localStorage.setItem('primaryColor', color)
      this.applyTheme()
    },

    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode
      localStorage.setItem('darkMode', String(this.isDarkMode))
      this.applyTheme()
    },

    applyTheme() {
      // 应用主题色
      document.documentElement.style.setProperty('--primary-color', this.primaryColor)
      
      // 应用暗色/亮色模式
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }
}) 
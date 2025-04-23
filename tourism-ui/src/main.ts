import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import App from './App.vue'
import router from './router'
import pinia from './stores/pinia'

// 先导入Element Plus的默认样式
import 'element-plus/dist/index.css'
// 再导入我们的自定义样式
import './styles/main.scss'

const app = createApp(App)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 配置Element Plus
app.use(ElementPlus, {
  locale: zhCn,
})

app.use(pinia)
app.use(router)

app.mount('#app') 
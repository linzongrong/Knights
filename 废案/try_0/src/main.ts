import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css' // 样式必须引入！

const app = createApp(App)

app.use(createPinia())
app.use(ElementPlus) //  全局注册所有 Element Plus 组件

app.mount('#app')
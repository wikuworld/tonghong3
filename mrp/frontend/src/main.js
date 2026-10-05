import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

const app = createApp(App)

// Element Plus menu/transition masih memicu peringatan slot di Vue 3.5+ (bukan error app).
app.config.warnHandler = (msg, _instance, trace) => {
  if (
    typeof msg === 'string' &&
    msg.includes('Slot "default" invoked outside of the render function') &&
    (trace?.includes('element-plus') ||
      /ElCollapseTransition|ElMenuCollapseTransition|ElSubMenu/i.test(trace || ''))
  ) {
    return
  }
  console.warn(msg, trace)
}

app.use(router).use(i18n).use(ElementPlus).mount('#app')

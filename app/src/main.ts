import './lib/webawesome'
import './styles/basis.css'

import '@awesome.me/webawesome/dist/components/page/page.js'
import '@awesome.me/webawesome/dist/components/callout/callout.js'
import '@awesome.me/webawesome/dist/components/icon/icon.js'
import '@awesome.me/webawesome/dist/components/skeleton/skeleton.js'
import '@awesome.me/webawesome/dist/components/format-number/format-number.js'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

app.mount('#app')

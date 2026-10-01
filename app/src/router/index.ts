import { createRouter, createWebHashHistory } from 'vue-router'
import StartPage from '@/pages/StartPage.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'start', component: StartPage },
    { path: '/:pathMatch(.*)*', redirect: { name: 'start' } },
  ],
})

export default router

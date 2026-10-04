import { createRouter, createWebHashHistory } from 'vue-router'
import StartPage from '@/pages/StartPage.vue'
import EinnahmenPage from '@/pages/EinnahmenPage.vue'

declare module 'vue-router' {
  interface RouteMeta {
    /** Seitentitel für `document.title` und die Ansage nach einem Seitenwechsel (D-13). */
    titel: string
  }
}

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'start', component: StartPage, meta: { titel: 'Start' } },
    {
      path: '/einnahmen',
      name: 'einnahmen',
      component: EinnahmenPage,
      meta: { titel: 'Woher kommt das Geld?' },
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'start' } },
  ],
})

export default router

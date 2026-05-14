import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: () => import('@/views/Login.vue') // El "/" garantiza que sea la primera pantalla
  },
  {
    path: '/select-ficha',
    name: 'SelectFicha',
    component: () => import('@/views/display/SelectFicha.vue')
  },
  {
    path: '/tablet-dashboard',
    name: 'TabletDashboard',
    component: () => import('@/views/display/Dashboard.vue')
  },
  {
    path: '/mobile-card',
    name: 'MobileCard',
    component: () => import('@/views/mobile/Card.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
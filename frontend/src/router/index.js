import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/auth/Login.vue"),
    meta: { title: "VoltMind Access - Iniciar Sesión" },
  },
  {
    path: "/route-selector",
    name: "RouteSelector",
    component: () => import("@/views/auth/routeSelector.vue"),
    meta: { title: "Entorno de Desarrollo - Selector de Rutas" },
  },
  {
    path: "/select-ficha",
    name: "SelectFicha",
    component: () => import("@/views/display/SelectFicha.vue"),
    meta: { title: "VoltMind - Selección de Ficha y Ambiente" },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("@/views/display/Dashboard.vue"),
    meta: { title: "VoltMind - Panel de Control IoT" },
  },
  {
    path: "/card",
    name: "CardAprendiz",
    component: () => import("@/views/mobile/cardAprendiz.vue"),
    meta: { title: "VoltMind - Carnet Digital" },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// ── GUARD GLOBAL PARA ACTUALIZAR EL TÍTULO DE LA PESTAÑA ──
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  next();
});

export default router;

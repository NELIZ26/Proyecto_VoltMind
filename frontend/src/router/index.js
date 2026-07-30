import { createRouter, createWebHistory } from "vue-router"; // <-- Cambiado aquí

const routes = [
  {
    path: "/",
    redirect: "/login", // Apuntamos directo al login por ahora
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/auth/Login.vue"),
    meta: { title: "VoltMind Access - Iniciar Sesión", requiresAuth: false },
  },
  {
    path: "/route-selector",
    name: "RouteSelector",
    component: () => import("@/views/auth/routeSelector.vue"),
    meta: { title: "Entorno de Desarrollo - Sandbox", requiresAuth: false },
  },
  {
    path: "/select-ficha",
    name: "SelectFicha",
    component: () => import("@/views/display/SelectFicha.vue"),
    meta: {
      title: "VoltMind - Selección de Ambiente",
      requiresAuth: true,
      roles: ["instructor"], // Solo el instructor asigna la ficha
    },
  },
  {
    path: "/tablet",
    name: "TabletView",
    component: () => import("@/views/display/TabletView.vue"),
    meta: {
      title: "VoltMind - Modo Tablet",
      requiresAuth: false,
    },
  },
  {
    path: "/solicitud-complementaria",
    name: "SolicitudComplementaria",
    component: () => import("@/views/display/SolicitudComplementaria.vue"),
    meta: {
      title: "VoltMind - Solicitud de Ficha Complementaria",
      requiresAuth: true,
      roles: ["instructor"], // El instructor solicita; el admin crea la ficha
    },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("@/views/display/DashboardInstru.vue"),
    meta: {
      title: "VoltMind - Panel de Control IoT",
      requiresAuth: true,
      roles: ["instructor"],
    },
  },
  {
    path: "/dashboard-admin",
    name: "DashboardAdmin",
    component: () => import("@/views/display/DashboardCST.vue"),
    meta: {
      title: "VoltMind - Consola Global",
      requiresAuth: true,
      roles: ["dinamizador"], // Acceso exclusivo Superadmin
    },
  },
  {
    path: "/dashboard-seguridad",
    name: "DashboardSeguridad",
    component: () => import("@/views/display/DashboardCelador.vue"), // Este será el que crearemos luego
    meta: {
      title: "VoltMind - Panel de Seguridad",
      requiresAuth: true,
      roles: ["celador"], // Acceso exclusivo Celador
    },
  },
  {
    path: "/card",
    name: "CardAprendiz",
    component: () => import("@/views/mobile/cardAprendiz.vue"),
    meta: {
      title: "VoltMind - Carnet Digital",
      requiresAuth: true,
      roles: ["aprendiz"],
    },
  },
  {
    path: "/admin",
    component: () => import("@/layouts/AdminLayout.vue"),
    // Sección administrativa: solo el dinamizador (el instructor NO accede)
    meta: { requiresAuth: true, roles: ["dinamizador"] },
    children: [
      {
        path: "dashboard",
        name: "AdminDashboard",
        component: () => import("@/views/admin/DashboardView.vue"),
        meta: { title: "VoltMind Admin - Dashboard" }
      },
      {
        path: "complementarias",
        name: "AdminComplementarias",
        component: () => import("@/views/admin/FichasComplementariasView.vue"),
        meta: { title: "VoltMind Admin - Fichas Complementarias" }
      },
      {
        path: "calculadora",
        name: "AdminCalculadora",
        component: () => import("@/views/admin/CalculadoraHorasView.vue"),
        meta: { title: "VoltMind Admin - Calculadora" }
      },
      {
        path: "fichas",
        name: "AdminFichas",
        component: () => import("@/views/admin/GestionFichasView.vue"),
        meta: { title: "VoltMind Admin - Fichas" }
      },
      {
        path: "instructores",
        name: "AdminInstructores",
        component: () => import("@/views/admin/InstructoresView.vue"),
        meta: { title: "VoltMind Admin - Instructores" }
      },
      {
        path: "aprendices",
        name: "AdminAprendices",
        component: () => import("@/views/admin/AprendicesView.vue"),
        meta: { title: "VoltMind Admin - Aprendices" }
      },
      {
        path: "ambientes",
        name: "AdminAmbientes",
        component: () => import("@/views/admin/AmbientesHorariosView.vue"),
        meta: { title: "VoltMind Admin - Ambientes y Horarios" }
      },
      {
        path: "iot",
        name: "AdminIoT",
        component: () => import("@/views/admin/ConfiguracionIoTView.vue"),
        meta: { title: "VoltMind Admin - Configuración IoT" }
      }
    ]
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // <-- Cambiado aquí también
  routes,
});

// ── GUARD GLOBAL: GESTIÓN DE TÍTULOS Y ROLES (RBAC) ──
router.beforeEach((to, from, next) => {
  // 1. Actualizar el título de la pestaña del navegador
  if (to.meta.title) {
    document.title = to.meta.title;
  }

  // 2. Verificación de Roles
  const userRole = localStorage.getItem("user_role"); // Lee el rol inyectado por el Simulador

  // Si la ruta exige estar autenticado...
  if (to.meta.requiresAuth) {
    // Si no hay rol (nadie ha iniciado sesión o no pasaron por el selector)
    if (!userRole) {
      return next("/login"); // En producción, redirigirá a '/login'
    }

    // Si el usuario tiene un rol, pero ese rol no está en la lista permitida de la ruta
    if (to.meta.roles && !to.meta.roles.includes(userRole)) {
      console.warn(
        `Bloqueo de seguridad: El rol '${userRole}' intentó acceder a '${to.path}'`,
      );
      return next("/login"); // Rechazado. Lo devolvemos al login.
    }
  }

  // Si pasa todas las validaciones, permitimos la navegación
  next();
});

export default router;
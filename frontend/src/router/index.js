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
      roles: ["instructor", "instructor_directo"],
    },
  },
  {
    path: "/mi-programacion",
    name: "MiProgramacion",
    component: () => import("@/views/display/MiProgramacionView.vue"),
    meta: {
      title: "VoltMind - Mi Programación",
      requiresAuth: true,
      // Calendario personal del instructor; el dinamizador puede consultarlo para verificar
      roles: ["instructor", "dinamizador"],
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
         // Permitir acceso a Yolima
        
  
  path: "instructores",
  name: "AdminInstructores",
  component: () => import("@/views/admin/InstructoresView.vue"),
  meta: { 
    title: "VoltMind Admin - Instructores",
    requiresAuth: true, 
    roles: ['dinamizador', 'admin', 'yolima', 'YOLIMA'] 
  }
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
      },
      {
        path: "monitor-aulas",
        name: "AdminMonitorAulas",
        component: () => import("@/views/admin/monitor/MonitorAulasList.vue"),
        meta: { title: "VoltMind Admin - Monitor de Aulas" }
      },
      {
        path: "monitor-aulas/:id",
        name: "AdminMonitorAulaDetail",
        component: () => import("@/views/admin/monitor/MonitorAulaDetail.vue"),
        meta: { title: "VoltMind Admin - Control de Aula" }
      },
      {
        path: "monitor-aulas/:id/edit",
        name: "AdminMonitorAulaEditor",
        component: () => import("@/views/admin/monitor/MonitorAulaEditor.vue"),
        meta: { title: "VoltMind Admin - Editor de Aula" }
      }
    ]
  },
  {
    path: "/programador-academico",
    component: () => import("@/layouts/ProgramadorAcademicoLayout.vue"),
    meta: { requiresAuth: true, roles: ["programador_academico"] },
    children: [
      {
        path: "tituladas",
        name: "AcademicoTituladas",
        component: () => import("@/views/admin/FichasTituladasView.vue"),
        meta: { title: "VoltMind - Panel Principal" }
      },
      {
        path: "directorio",
        name: "AcademicoDirectorio",
        component: () => import("@/views/admin/DirectorioTituladasView.vue"),
        meta: { title: "VoltMind - Directorio de Fichas" }
      },
      {
        path: "tituladas/:id",
        name: "AcademicoTituladaDetalle",
        component: () => import("@/views/admin/FichaTituladaDetalleView.vue"),
        meta: { title: "VoltMind - Detalle de Ficha Titulada" }
      }
    ]
  },
  {
    path: "/programador-complementarios",
    component: () => import("@/layouts/ProgramadorComplementariosLayout.vue"),
    meta: { requiresAuth: true, roles: ["programador_complementarios"] },
    children: [
      {
        path: "dashboard",
        name: "ComplementariosDashboard",
        component: () => import("@/views/admin/complementarias/DashboardView.vue"),
        meta: { title: "VoltMind - Dashboard Complementarias" }
      },
      {
        path: "",
        redirect: "/programador-complementarios/dashboard"
      },
      {
        path: "fichas",
        redirect: "/programador-complementarios/fichas/tablero",
        component: () => import("@/views/admin/complementarias/ComplementariasLayout.vue"),
        meta: { title: "VoltMind - Fichas Complementarias" },
        children: [
          {
            path: "tablero",
            name: "ComplementariosTablero",
            component: () => import("@/views/admin/complementarias/TableroView.vue"),
            meta: { title: "VoltMind - Tablero de Complementarias" }
          },
          {
            path: "archivo",
            name: "ComplementariosArchivo",
            component: () => import("@/views/admin/complementarias/ArchivoView.vue"),
            meta: { title: "VoltMind - Archivo Histórico" }
          }
        ]
      },
      {
        path: "directorio",
        name: "ComplementariasDirectorio",
        component: () => import("@/views/admin/complementarias/DirectorioFichasView.vue"),
        meta: { title: "VoltMind - Directorio de Fichas" }
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
// — GUARD GLOBAL: GESTIÓN DE TÍTULOS Y ROLES (RBAC) —
router.beforeEach((to, from, next) => {
  const userRole = localStorage.getItem("user_role");

  // 1. Bypass directo para Yolima
  if (userRole && userRole.toLowerCase() === "yolima") {
    if (to.meta && to.meta.title) document.title = to.meta.title;
    return next();
  }

  // 2. Título de la pestaña para el resto de usuarios
  if (to.meta && to.meta.title) {
    document.title = to.meta.title;
  }
  return next(); // Auth suspendida temporalmente

  // 3. Verificación de Roles para el resto
  if (to.meta && to.meta.requiresAuth) {
    if (!userRole) {
      return next("/login");
    }

    const roleNormalized = userRole.toLowerCase();

    const tienePermiso = to.matched.every((record) => {
      if (!record.meta || !record.meta.roles) return true;
      return record.meta.roles.some(
        (r) => String(r).toLowerCase() === roleNormalized
      );
    });

    if (!tienePermiso) {
      console.warn(
        `Bloqueo de seguridad: El rol '${userRole}' intentó acceder a '${to.path}'`
      );
      return next("/login");
    }
  }

  next();
});

export default router;
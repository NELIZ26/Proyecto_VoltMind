<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { PublicClientApplication } from "@azure/msal-browser";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const toast = useToast();
const authStore = useAuthStore();
const isLoggingIn = ref(false);

// 1. Configuración de MSAL
const msalConfig = {
  auth: {
    // Ahora Vite irá a buscar el ID correcto a tu archivo .env
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID, 
    // Y también buscará tu inquilino específico en lugar del genérico
    authority: import.meta.env.VITE_AZURE_AUTHORITY, 
    redirectUri: window.location.origin, 
    navigateToLoginRequestUrl: false, 
  },
  cache: {
    cacheLocation: "sessionStorage", 
    storeAuthStateInCookie: false,
  }
};

const msalInstance = new PublicClientApplication(msalConfig);

// 2. FUNCIÓN CENTRALIZADA: Enrutamiento Inteligente con Enriquecimiento de Perfil (RBAC)
const processLoginSuccess = async (account) => {
  const userName = account.name;
  const userEmail = account.username;
  
  // Guardamos inicialmente en el store de Pinia
  authStore.setSession(userEmail, userName);
  
  // Extraemos el dominio del correo pasándolo todo a minúsculas
  const domain = userEmail.split('@')[1]?.toLowerCase();

  if (domain === 'soy.sena.edu.co') {
    toast.info("Verificando registro académico en Dataverse...");

    try {
      // 🟢 CONSULTA AL BACKEND: Cruzamos el correo de Microsoft con Dataverse
      const response = await fetch(`/api/usuarios/perfil?email=${userEmail}`);
      
      if (response.ok) {
        const perfilCompleto = await response.json();

        // Guardamos el objeto estructurado JSON (el que lee JSON.parse en el carnet)
        localStorage.setItem("userData", JSON.stringify(perfilCompleto));
        
        // Guardamos las llaves individuales para asegurar compatibilidad total en el almacenamiento
        localStorage.setItem("microsoft_user_name", perfilCompleto.full_name);
        localStorage.setItem("microsoft_user_email", perfilCompleto.email);
        localStorage.setItem("microsoft_user_doc", perfilCompleto.documento);
        localStorage.setItem("microsoft_user_ficha", perfilCompleto.ficha);
        localStorage.setItem("fichaActiva", perfilCompleto.ficha);
        
        localStorage.setItem("user_role", "aprendiz");
        
        toast.success(`¡Bienvenido, ${perfilCompleto.full_name}! Cargando carnet digital...`);
        
        // Redirección directa al carnet ahora que la memoria está llena y es dinámica
        router.push("/card"); 

      } else {
        const err = await response.json();
        console.error("Error de vinculación:", err.detail);
        toast.error(err.detail || "Autenticado en Microsoft, pero no estás registrado en Dataverse.");
      }
    } catch (error) {
      console.error("Error conectando con FastAPI:", error);
      toast.error("Error de conexión con el servidor central al validar tu perfil.");
    }

  } else if (domain === 'sena.edu.co' || domain === 'voltmind746.onmicrosoft.com') {
    // RUTA DEL INSTRUCTOR
    localStorage.setItem("user_role", "instructor");
    localStorage.setItem("instructorEmail", userEmail); 
    localStorage.setItem("instructorName", userName);
    localStorage.setItem("nombreInstructor", userName.split(' ')[0]); // Primer nombre para el saludo corta
    
    toast.success(`Instructor Autenticado. Cargando panel operativo...`);
    
    // Cambiado directamente a la selección de ficha oficial
    router.push("/select-ficha"); 

  } else {
    // SEGURIDAD: Bloquea dominios externos no autorizados
    toast.error("Acceso denegado. Utilice exclusivamente su correo institucional del SENA.");
  }
};

// 3. Procesar el regreso de la redirección de Microsoft (Modificado para soportar la función async)
onMounted(async () => {
  try {
    await msalInstance.initialize();
    
    const response = await msalInstance.handleRedirectPromise();
    
    if (response) {
      await processLoginSuccess(response.account);
    } else {
      const currentAccounts = msalInstance.getAllAccounts();
      if (currentAccounts.length > 0) {
        await processLoginSuccess(currentAccounts[0]);
      }
    }
  } catch (error) {
    console.error("Error procesando el regreso de MSAL:", error);
    toast.error("Error al validar credenciales institucionales.");
  }
});

// 4. Función del botón para iniciar el flujo
const handleAzureLogin = async () => {
  if (isLoggingIn.value) return;
  isLoggingIn.value = true;

  try {
    const loginRequest = {
      scopes: ["User.Read", "profile", "email"]
    };

    await msalInstance.loginRedirect(loginRequest);

  } catch (error) {
    console.error("Error al iniciar redirección:", error);
    isLoggingIn.value = false;
  }
};
</script>
<template>
  <div class="login-shell">
    <div class="login-card">
      <div class="card-corner top-left"></div>
      <div class="card-corner bottom-right"></div>

      <header class="login-header">
        <div class="brand-assets">
          <img
            src="@/assets/VoltMindAccess.svg"
            alt="VoltMind Logo"
            class="logo-voltmind"
          />
          <div class="brand-divider"></div>
          <img src="@/assets/LogoSena.png" alt="SENA Logo" class="logo-sena" />
        </div>
        <h1>VoltMind Access</h1>
        <p class="subtitle">
          Gestión IoT de Asistencia y Eficiencia Energética para Ambientes de
          Formación
        </p>
      </header>

      <main class="login-body">
        <div class="notice-box">
          <div class="icon-glow-wrapper">
            <font-awesome-icon
              icon="fa-solid fa-shield-halved"
              class="icon-notice"
            />
          </div>
          <div class="notice-text">
            <span>SISTEMA DE CONTROL RESTRINGIDO</span>
            <p>
              Acceso exclusivo para Instructores y Personal Administrativo
              autorizado.
            </p>
          </div>
        </div>

        <button class="btn-azure" @click="handleAzureLogin">
          <div class="microsoft-icon">
            <span class="ms-box red"></span>
            <span class="ms-box green"></span>
            <span class="ms-box blue"></span>
            <span class="ms-box yellow"></span>
          </div>
          <span>Autenticación Institucional Azure AD</span>
        </button>
      </main>

      <footer class="login-footer">
        <p>&copy; 2026 VoltMind Ecosystem. Todos los derechos reservados.</p>
        <div class="terminal-badge">
          <span class="pulse-dot"></span>
          <small>ESTACIÓN DE CONTROL LOCAL • TABLET ED. v2.4</small>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   CONSOLA DE AUTENTICACIÓN - TERMINAL PRINCIPAL (Caso 1: Blanco SENA 2024)
   ========================================================================== */
.login-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  background: var(--fondo-app);
  font-family: var(--fuente-principal);
  position: relative;
}

/* Rejilla de fondo sutil adaptada a fondo claro usando el azul oscuro SENA */
.login-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 48, 64, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 48, 64, 0.03) 1px, transparent 1px);
  background-size: 30px 30px;
  mask-image: radial-gradient(circle at center, black 40%, transparent 80%);
  pointer-events: none;
}

.login-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 18px;
  width: 100%;
  max-width: 450px;
  padding: 3rem 2.25rem;
  text-align: center;
  box-shadow:
    0 20px 40px rgba(0, 48, 64, 0.06),
    0 1px 3px rgba(0, 0, 0, 0.05);
  position: relative;
  transition: all 0.4s ease;
  z-index: 1;
}

/* Efecto Hover predictivo limpio */
.login-card:hover {
  border-color: var(--sena-verde);
  box-shadow:
    0 30px 60px rgba(0, 48, 64, 0.1),
    0 0 0 1px var(--sena-verde);
}

/* Micro-Detalles de Esquinas */
.card-corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border: 2px solid transparent;
  pointer-events: none;
  opacity: 0.3;
  transition: opacity 0.3s ease;
}

.login-card:hover .card-corner {
  opacity: 0.8;
}

.top-left {
  top: 14px;
  left: 14px;
  border-top-color: var(--borde);
  border-left-color: var(--borde);
}

.login-card:hover .top-left {
  border-top-color: var(--sena-verde);
  border-left-color: var(--sena-verde);
}

.bottom-right {
  bottom: 14px;
  right: 14px;
  border-bottom-color: var(--sena-verde);
  border-right-color: var(--sena-verde);
}

/* ==========================================================================
   IDENTIDAD VISUAL SUPERIOR (BRAND HEADER)
   ========================================================================== */
.brand-assets {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-bottom: 1.75rem;
}

.logo-voltmind {
  height: 34px;
  width: auto;
}

.logo-sena {
  height: 38px;
  width: auto;
}

.brand-divider {
  width: 1px;
  height: 24px;
  background: var(--borde);
}

.login-header h1 {
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--texto-principal);
  margin: 0 0 0.6rem 0;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  line-height: 1.5;
  margin: 0;
  padding: 0 10px;
}

/* ==========================================================================
   CUERPO DE ACCIÓN (LOGIN CORE)
   ========================================================================== */
.login-body {
  margin: 2.75rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Caja de Aviso Técnico */
.notice-box {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  text-align: left;
}

/* Icono reemplazado por la alerta del Amarillo institucional SENA */
.icon-glow-wrapper {
  background: rgba(253, 195, 0, 0.15);
  border: 1px solid rgba(253, 195, 0, 0.3);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-notice {
  color: var(--sena-amarillo);
  font-size: 1rem;
}

.notice-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notice-text span {
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--texto-principal);
  letter-spacing: 0.05em;
}

.notice-text p {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  margin: 0;
  line-height: 1.35;
}

/* ==========================================================================
   BOTÓN ACRÍLICO PERSONALIZADO (AZURE INTEGRATION)
   ========================================================================== */
.btn-azure {
  background: var(--fondo-tarjetas);
  color: var(--texto-principal);
  border: 1px solid var(--borde);
  padding: 13px 18px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-azure:hover {
  background: var(--fondo-app);
  border-color: var(--sena-azul-oscuro);
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.08);
  transform: translateY(-1px);
}

.btn-azure:active {
  transform: translateY(0);
  background: var(--fondo-tarjetas);
}

/* Icono Nativo Centrado (Se mantienen estáticos porque son colores corporativos exclusivos de Microsoft) */
.microsoft-icon {
  width: 16px;
  height: 16px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2px;
  flex-shrink: 0;
}

.ms-box {
  width: 7px;
  height: 7px;
}
.ms-box.red { background-color: #f25022; }
.ms-box.green { background-color: #7fba00; }
.ms-box.blue { background-color: #00a4ef; }
.ms-box.yellow { background-color: #ffb900; }

/* ==========================================================================
   FOOTER CORPORATIVO DE LA TERMINAL
   ========================================================================== */
.login-footer {
  border-top: 1px solid var(--borde);
  padding-top: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.login-footer p {
  font-size: 0.68rem;
  color: var(--texto-secundario);
  margin: 0;
}

/* Badge de Estado Activo Local */
.terminal-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(57, 169, 0, 0.08);
  border: 1px solid rgba(57, 169, 0, 0.2);
  padding: 4px 10px;
  border-radius: 4px;
}

.pulse-dot {
  width: 5px;
  height: 5px;
  background-color: var(--sena-verde);
  border-radius: 50%;
  box-shadow: 0 0 6px var(--sena-verde);
  animation: hardwarePulse 2s infinite;
}

@keyframes hardwarePulse {
  50% {
    opacity: 0.3;
  }
}

.terminal-badge small {
  font-size: 0.6rem;
  color: var(--sena-verde-oscuro);
  font-weight: 700;
  letter-spacing: 0.04em;
}
</style>
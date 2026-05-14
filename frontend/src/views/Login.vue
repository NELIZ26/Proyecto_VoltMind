<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logos">
        <img src="../assets/LogoSena.png" alt="SENA" class="logo-sena" />
        <div class="divider"></div>
        <h2 class="brand-name">Volt<span>Mind</span></h2>
      </div>

      <div class="welcome-text">
        <h1>Bienvenido</h1>
        <p>Sistema de gestión de ambientes e identidad digital</p>
      </div>

      <button @click="handleLogin" class="btn-azure">
        <img src="https://authjs.dev/img/providers/azure.svg" alt="Azure" />
        Iniciar sesión con cuenta SENA
      </button>

      <p class="footer-text">
        Al ingresar, aceptas los términos de uso y seguridad del Centro de formación.
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';

const router = useRouter();
const userStore = useUserStore();

const handleLogin = () => {
  // 1. Aquí se validaría con Azure...
  // Simulamos que el login fue exitoso:
  const userRole = 'instructor'; 

  // 2. Ejecutamos la detección de pantalla tras el login exitoso
  const isNative = Capacitor.isNativePlatform();
  const isTablet = window.innerWidth >= 768;

  if (isNative) {
    // Escenario 3: Si es App móvil -> Carnet Digital
    router.push('/mobile-card');
  } else if (isTablet) {
    // Escenario 2: Si es Tablet -> Selección de Ficha
    router.push('/select-ficha');
  } else {
    // Si es un celular por navegador, también podemos mandarlo al carnet
    router.push('/mobile-card');
  }
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--sena-azul) 0%, #001a29 100%);
  padding: 20px;
}

.login-card {
  background: var(--sena-blanco);
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
  width: 100%;
  max-width: 450px;
  text-align: center;
  border-bottom: 8px solid var(--sena-verde);
}

.logos {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.logo-sena {
  height: 60px;
}

.divider {
  width: 2px;
  height: 40px;
  background-color: var(--borde);
}

.brand-name {
  font-size: 1.8rem;
  color: var(--sena-azul);
  font-weight: 700;
}

.brand-name span {
  color: var(--sena-verde);
}

.welcome-text h1 {
  font-size: 2rem;
  color: var(--sena-azul);
  margin-bottom: 10px;
}

.welcome-text p {
  color: var(--texto-secundario);
  margin-bottom: 30px;
  font-size: 0.9rem;
}

.btn-azure {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background-color: #2f2f2f;
  color: white;
  border: none;
  padding: 15px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, background 0.3s;
}

.btn-azure:hover {
  background-color: #000;
  transform: translateY(-2px);
}

.btn-azure img {
  width: 20px;
}

.footer-text {
  margin-top: 30px;
  font-size: 0.75rem;
  color: #999;
}
</style>
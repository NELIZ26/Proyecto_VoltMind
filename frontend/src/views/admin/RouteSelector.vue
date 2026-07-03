<template>
  <div class="selector-shell">
    <div class="selector-container">
      <div class="brand-header">
        <span class="text-volt">Volt</span><span class="text-mind">Mind</span>
        <h2>Hola, {{ userStore.name }}</h2>
        <p>Selecciona tu entorno de trabajo</p>
      </div>

      <div class="options-grid">
        <!-- Opción 1: Panel de Control -->
        <button class="option-card" @click="goToDashboard">
          <div class="icon-wrapper bg-blue">
            <font-awesome-icon icon="fa-solid fa-desktop" />
          </div>
          <h3>Panel de Control</h3>
          <p>Gestiona el aula de forma remota.</p>
        </button>

        <!-- Opción 2: Carnet Digital -->
        <button class="option-card" @click="goToCard">
          <div class="icon-wrapper bg-green">
            <font-awesome-icon icon="fa-solid fa-id-badge" />
          </div>
          <h3>Carnet Maestro</h3>
          <p>Utiliza tu dispositivo para encender el aula presencialmente.</p>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();

onMounted(() => {
  // Rescatamos los datos del instructor que guardó el Login
  const nombreGuardado = localStorage.getItem('instructorName');
  const correoGuardado = localStorage.getItem('instructorEmail');
  const rolGuardado = localStorage.getItem('user_role');

  if (nombreGuardado && correoGuardado) {
    // 🟢 Repoblamos Pinia para que el Dashboard tenga con qué buscar las fichas
    userStore.name = nombreGuardado;
    userStore.email = correoGuardado; 
    userStore.role = rolGuardado || 'instructor';
  } else {
    // Si por alguna razón el instructor llegó aquí sin iniciar sesión, lo devolvemos
    router.push('/login');
  }
});

const goToDashboard = () => {
  // Tu vista SelectFicha / Dashboard ahora sí tendrá el correo en Pinia para hacer el fetch
  router.push('/select-ficha'); // O la ruta que use tu instructor para activar el aula
};

const goToCard = () => {
  router.push('/card');
};
</script>

<style scoped>
.selector-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--fondo-app);
  font-family: var(--fuente-principal);
}
.selector-container {
  text-align: center;
  max-width: 600px;
  padding: 2rem;
}
.brand-header {
  margin-bottom: 3rem;
}
.text-volt { color: var(--sena-azul-oscuro); font-size: 2rem; font-weight: 800; }
.text-mind { color: var(--sena-verde); font-size: 2rem; font-weight: 800; }
.brand-header h2 { margin-top: 1rem; color: var(--texto-principal); }
.brand-header p { color: var(--texto-secundario); }

.options-grid {
  display: flex;
  gap: 2rem;
  justify-content: center;
}
.option-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 2rem;
  width: 250px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  border-color: var(--sena-verde);
}
.icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: white;
}
.bg-blue { background-color: var(--sena-azul-oscuro); }
.bg-green { background-color: var(--sena-verde); }
.option-card h3 { color: var(--texto-principal); margin: 0 0 0.5rem 0; font-size: 1.2rem; }
.option-card p { color: var(--texto-secundario); font-size: 0.9rem; margin: 0; }
</style>
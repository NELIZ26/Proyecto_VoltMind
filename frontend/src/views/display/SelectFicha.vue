<template>
  <div class="select-container">
    <div class="header">
      <img src="@/assets/LogoSena.png" alt="SENA" class="logo">
      <h1>Panel de Control VoltMind</h1>
      <p>Seleccione la ficha que inicia formación en el ambiente</p>
    </div>

    <div class="fichas-grid">
      <div v-for="ficha in fichas" :key="ficha.id" 
           @click="seleccionarFicha(ficha)" 
           class="ficha-card">
        <font-awesome-icon icon="fa-solid fa-user-check" class="icon" />
        <h2>{{ ficha.numero }}</h2>
        <p>{{ ficha.programa }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
const fichas = [
  { id: 1, numero: '2997671', programa: 'Análisis y Desarrollo de Software' },
  { id: 2, numero: '2800500', programa: 'Sistemas' }
];

const seleccionarFicha = (ficha) => {
  console.log(`Iniciando formación para ficha: ${ficha.numero}`);
  // Aquí puedes guardar la ficha seleccionada en Pinia
  router.push('/tablet-dashboard');
};
</script>

<style scoped>
.select-container {
  padding: 40px;
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
}
.fichas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
  margin-top: 50px;
}
.ficha-card {
  background: var(--sena-blanco);
  padding: 30px;
  border-radius: 20px;
  border-bottom: 6px solid var(--sena-verde-claro);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
}
.ficha-card:hover {
  transform: translateY(-10px);
  border-bottom-color: var(--sena-verde);
  box-shadow: 0 15px 30px rgba(57, 169, 0, 0.2);
}
.icon {
  font-size: 2.5rem;
  color: var(--sena-verde);
  margin-bottom: 15px;
}
</style>
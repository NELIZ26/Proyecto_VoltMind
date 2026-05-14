<template>
  <router-view />
</template>

<script setup>
/*import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Capacitor } from '@capacitor/core';

const router = useRouter();

onMounted(() => {
  detectDevice();
});

const detectDevice = () => {
  // 1. Verificamos si estamos corriendo como App Nativa (Android/iOS)
  const isNative = Capacitor.isNativePlatform();
  
  // 2. Verificamos el ancho de la pantalla (Breakpoint de 768px para Tablets)
  const isTablet = window.innerWidth >= 768;

  if (isNative) {
    // Si es App nativa, lo mandamos al carnet digital (Vista Móvil)
    router.push('/mobile-card');
  } else if (isTablet) {
    // Si es navegador pero pantalla grande, mandamos al Dashboard (Tablet)
    router.push('/tablet-dashboard');
  } else {
    // Por defecto, que inicie en el Login
    router.push('/');
  }
};*/
</script>

<style>
/* Estilos globales para que la app se vea limpia en ambos dispositivos */
body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
  background-color: #f4f7f6; /* Un gris muy claro inspirado en naturaleza */
}
</style>
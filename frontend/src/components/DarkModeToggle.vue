<template>
  <button
    class="floating-theme-btn"
    @click="toggleTheme"
    :title="isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
  >
    <font-awesome-icon :icon="['fas', isDark ? 'lightbulb' : 'moon']" />
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const isDark = ref(false);

const toggleTheme = () => {
  isDark.value = !isDark.value;
  updateTheme();
};

const updateTheme = () => {
  if (isDark.value) {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
  }
};

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  const currentHour = new Date().getHours();
  const isNightTime = currentHour >= 19 || currentHour < 6;

  if (savedTheme === 'dark' || (!savedTheme && isNightTime)) {
    isDark.value = true;
    document.documentElement.setAttribute('data-theme', 'dark');
  }
});
</script>

<style scoped>
.floating-theme-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--texto-principal);
  color: var(--fondo-app);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.floating-theme-btn:hover {
  background-color: var(--sena-verde);
  transform: scale(1.1);
}
</style>

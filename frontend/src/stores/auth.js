import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  // Estado
  const instructorEmail = ref(localStorage.getItem("instructorEmail") || null);
  const instructorName = ref(localStorage.getItem("instructorName") || null);

  // Getters
  const isAuthenticated = computed(() => !!instructorEmail.value);

  // Acciones
  function setSession(email, name) {
    instructorEmail.value = email;
    instructorName.value = name;
    localStorage.setItem("instructorEmail", email);
    localStorage.setItem("instructorName", name);
  }

  function clearSession() {
    instructorEmail.value = null;
    instructorName.value = null;
    localStorage.removeItem("instructorEmail");
    localStorage.removeItem("instructorName");
  }

  return {
    instructorEmail,
    instructorName,
    isAuthenticated,
    setSession,
    clearSession,
  };
});
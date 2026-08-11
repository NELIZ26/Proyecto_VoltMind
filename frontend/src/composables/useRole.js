// src/composables/useRole.js
import { computed } from 'vue';

// Aquí simulamos que obtenemos el rol del estado global (puedes ajustarlo a tu store de Pinia o Auth)
// Por ahora, asumo que guardas el rol en localStorage o un store global
export function useRole() {
  const userRole = computed(() => localStorage.getItem('user_role') || 'guest');

  const roles = {
    dinamizador: ['all'],
    instructor: ['gestionar_aula', 'ver_telemetria', 'exportar_reportes'],
    celador: ['ver_alertas', 'monitoreo_periferico'],
    aprendiz: ['ver_carnet', 'validar_ingreso']
  };

  /**
   * Verifica si el usuario actual tiene un permiso específico
   * @param {string} permission 
   */
  const hasPermission = (permission) => {
    const permissions = roles[userRole.value] || [];
    return permissions.includes('all') || permissions.includes(permission);
  };

  /**
   * Verifica si el usuario tiene al menos uno de los roles indicados
   * @param {string[]} allowedRoles 
   */
  const hasRole = (allowedRoles) => {
    return allowedRoles.includes(userRole.value);
  };

  return { userRole, hasPermission, hasRole };
}
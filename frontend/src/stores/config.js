import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useConfigStore = defineStore('config', () => {
  // Estado inicial con valores por defecto
  const duracionClase = ref(90); // Minutos
  const horaApertura = ref('06:00');
  const horaCierre = ref('22:00'); // Cambiamos a 22:00 o la que ingrese el usuario
  
  const preEncendido = ref(15);
  const margenApagado = ref(10);
  const sedePrueba = ref('CAAA');
  const ambientePrueba = ref('101');
  
  const bloquearCruces = ref(true);
  const notificacionesCorreo = ref(true);

  // Funciones utilitarias para tiempos
  const timeToMinutes = (timeStr) => {
    if (!timeStr) return 0;
    const [h, m] = timeStr.split(':').map(Number);
    return h * 60 + (m || 0);
  };

  const formatTime = (minutesTotal) => {
    let h = Math.floor(minutesTotal / 60) % 24;
    let m = minutesTotal % 60;
    const ampm = h >= 12 ? 'pm' : 'am';
    h = h % 12;
    h = h ? h : 12; // 0 se convierte en 12
    const mm = m < 10 ? '0' + m : m;
    const hh = h < 10 ? '0' + h : h;
    return `${hh}:${mm} ${ampm}`;
  };

  // Generación matemática de bloques horarios
  const bloquesHorarios = computed(() => {
    let start = timeToMinutes(horaApertura.value);
    let end = timeToMinutes(horaCierre.value);
    const duracion = parseInt(duracionClase.value);

    if (isNaN(duracion) || duracion <= 0) return [];
    
    // Si la hora de cierre es menor a la de apertura, asumimos que cierra al día siguiente
    if (end <= start) end += 24 * 60;

    const bloques = [];
    let current = start;

    while (current + duracion <= end) {
      const next = current + duracion;
      bloques.push(`${formatTime(current)} - ${formatTime(next)}`);
      current = next;
    }

    return bloques;
  });

  // Cargar desde localStorage si existe
  const loadConfig = () => {
    const savedState = localStorage.getItem('voltmind_config');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        if (parsed.duracionClase !== undefined) duracionClase.value = parsed.duracionClase;
        if (parsed.horaApertura !== undefined) horaApertura.value = parsed.horaApertura;
        if (parsed.horaCierre !== undefined) horaCierre.value = parsed.horaCierre;
        if (parsed.preEncendido !== undefined) preEncendido.value = parsed.preEncendido;
        if (parsed.margenApagado !== undefined) margenApagado.value = parsed.margenApagado;
        if (parsed.sedePrueba !== undefined) sedePrueba.value = parsed.sedePrueba;
        if (parsed.ambientePrueba !== undefined) ambientePrueba.value = parsed.ambientePrueba;
        if (parsed.bloquearCruces !== undefined) bloquearCruces.value = parsed.bloquearCruces;
        if (parsed.notificacionesCorreo !== undefined) notificacionesCorreo.value = parsed.notificacionesCorreo;
      } catch (e) {
        console.error('Error cargando configuración desde localStorage:', e);
      }
    }
  };

  // Cargar configuración al inicializar el store
  loadConfig();

  // Acción para persistir la configuración
  const saveConfig = () => {
    const currentState = {
      duracionClase: duracionClase.value,
      horaApertura: horaApertura.value,
      horaCierre: horaCierre.value,
      preEncendido: preEncendido.value,
      margenApagado: margenApagado.value,
      sedePrueba: sedePrueba.value,
      ambientePrueba: ambientePrueba.value,
      bloquearCruces: bloquearCruces.value,
      notificacionesCorreo: notificacionesCorreo.value
    };
    localStorage.setItem('voltmind_config', JSON.stringify(currentState));
    // TODO: Integración con apiService cuando exista un endpoint en backend
    return true; // Indicador de éxito
  };

  return {
    duracionClase,
    horaApertura,
    horaCierre,
    preEncendido,
    margenApagado,
    sedePrueba,
    ambientePrueba,
    bloquearCruces,
    notificacionesCorreo,
    saveConfig,
    loadConfig,
    bloquesHorarios
  };
});

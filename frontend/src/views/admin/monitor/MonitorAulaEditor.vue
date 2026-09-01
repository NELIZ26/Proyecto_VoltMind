<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import DarkModeToggle from "@/components/DarkModeToggle.vue";

const route = useRoute();
const router = useRouter();
const toast = useToast();

const aulaId = ref(route.params.id);
const aulaName = ref(`Aula ${aulaId.value.toUpperCase()}`);

// Configuración de Hardware
const numeroLuminarias = ref(16);

// Generar o ajustar luminarias dinámicamente según el número total
const hardwareMap = ref(
  Array.from({ length: numeroLuminarias.value }, (_, i) => ({
    id: i + 1,
    nombre: `Luminaria ${i + 1}`,
    canalFisico: `RELAY_${String(i + 1).padStart(2, '0')}`,
    tipoCarga: 'LED'
  }))
);

const rebuildHardwareMap = () => {
  if (numeroLuminarias.value < 1) numeroLuminarias.value = 1;
  if (numeroLuminarias.value > 32) numeroLuminarias.value = 32;

  const currentLength = hardwareMap.value.length;
  if (numeroLuminarias.value > currentLength) {
    // Add more
    for (let i = currentLength; i < numeroLuminarias.value; i++) {
      hardwareMap.value.push({
        id: i + 1,
        nombre: `Luminaria ${i + 1}`,
        canalFisico: `RELAY_${String(i + 1).padStart(2, '0')}`,
        tipoCarga: 'LED'
      });
    }
  } else if (numeroLuminarias.value < currentLength) {
    // Remove excess
    hardwareMap.value.splice(numeroLuminarias.value);
  }
};

const guardarConfiguracion = () => {
  console.log("Configuración Hardware:", hardwareMap.value);
  toast.success(`Configuración física del ${aulaName.value} guardada exitosamente.`);
  setTimeout(() => {
    router.push(`/admin/monitor-aulas/${aulaId.value}`);
  }, 1000);
};

// Opciones de mapeo de relés (simuladas)
const opcionesRelay = computed(() => {
  let opciones = [];
  for(let i=1; i<=32; i++) {
    opciones.push(`RELAY_${String(i).padStart(2, '0')}`);
  }
  return opciones;
});
</script>

<template>
  <div class="monitor-editor-shell">
    <header class="page-header">
      <div class="header-left">
        <button class="btn-icon" @click="router.push(`/admin/monitor-aulas/${aulaId}`)">
          <font-awesome-icon icon="fa-solid fa-xmark" />
        </button>
        <div class="header-content">
          <h1>Editor de Hardware: {{ aulaName }}</h1>
          <p>Mapeo físico de relevadores IoT y circuitos del aula</p>
        </div>
      </div>
      <div class="header-right">
        <button class="btn-action btn-save" @click="guardarConfiguracion">
          <font-awesome-icon icon="fa-solid fa-cloud-arrow-up" /> Guardar y Sincronizar
        </button>
      </div>
    </header>

    <div class="editor-container">
      
      <!-- Panel Configuración General -->
      <section class="config-panel">
        <h2>Parámetros del Ambiente</h2>
        <div class="form-group">
          <label>Cantidad Total de Puntos de Iluminación:</label>
          <div class="input-with-button">
            <input 
              type="number" 
              v-model.number="numeroLuminarias" 
              min="1" 
              max="32" 
              class="number-input"
            />
            <button class="btn-apply" @click="rebuildHardwareMap">Actualizar Filas</button>
          </div>
          <small>Esto define cuántos switches aparecerán en el Monitor de Aula.</small>
        </div>
      </section>

      <!-- Panel Mapeo de Hardware -->
      <section class="hardware-panel">
        <h2>Asignación de Pines y Relés</h2>
        <div class="table-wrapper">
          <table class="hardware-table">
            <thead>
              <tr>
                <th width="10%">ID</th>
                <th width="30%">Nombre en Interfaz</th>
                <th width="30%">Tipo de Carga</th>
                <th width="30%">Canal Físico IoT (Relé)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in hardwareMap" :key="item.id">
                <td class="td-id">#{{ item.id }}</td>
                <td>
                  <input type="text" v-model="item.nombre" class="form-input" />
                </td>
                <td>
                  <select v-model="item.tipoCarga" class="form-select">
                    <option value="LED">Panel LED</option>
                    <option value="FLUO">Fluorescente</option>
                    <option value="TOMA">Tomacorriente</option>
                    <option value="AA">Aire Acondicionado</option>
                  </select>
                </td>
                <td>
                  <select v-model="item.canalFisico" class="form-select select-relay">
                    <option v-for="rel in opcionesRelay" :key="rel" :value="rel">{{ rel }}</option>
                    <option value="DESCONECTADO">-- No Asignado --</option>
                  </select>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>
    
    <DarkModeToggle />
  </div>
</template>

<style scoped>
.monitor-editor-shell {
  padding: 2rem;
  background-color: var(--fondo-app);
  min-height: 100vh;
  font-family: var(--fuente-principal);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.header-left { display: flex; align-items: center; gap: 1.5rem; }
.btn-icon {
  background: var(--fondo-tarjetas);
  color: var(--texto-principal);
  border: 1px solid var(--borde);
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: background 0.2s;
}
.btn-icon:hover { background: #e2e8f0; }
.header-content h1 {
  font-size: 1.6rem;
  color: var(--sena-azul-oscuro);
  margin: 0 0 4px 0;
}
.header-content p { color: var(--texto-secundario); margin: 0; font-size: 0.9rem; }

.header-right { display: flex; gap: 1rem; }
.btn-action {
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
}
.btn-save { background: var(--sena-verde); color: white; transition: background 0.2s;}
.btn-save:hover { background: var(--sena-verde-oscuro); }

.editor-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

section {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 2rem;
}
section h2 {
  font-size: 1.2rem;
  color: var(--sena-azul-oscuro);
  margin: 0 0 1.5rem 0;
  border-bottom: 2px solid var(--borde);
  padding-bottom: 10px;
}

/* Panel Config */
.form-group { display: flex; flex-direction: column; gap: 8px; max-width: 400px; }
.form-group label { font-weight: 700; color: var(--texto-principal); }
.input-with-button { display: flex; gap: 10px; }
.number-input {
  width: 80px;
  padding: 10px;
  border: 1px solid var(--borde);
  border-radius: 8px;
  font-size: 1.1rem;
  text-align: center;
  font-weight: 700;
}
.btn-apply {
  background: var(--sena-azul-oscuro);
  color: white;
  border: none;
  padding: 0 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.form-group small { color: var(--texto-secundario); }

/* Tabla Hardware */
.table-wrapper { overflow-x: auto; }
.hardware-table {
  width: 100%;
  border-collapse: collapse;
}
.hardware-table th {
  background: var(--fondo-app);
  padding: 12px;
  text-align: left;
  font-size: 0.85rem;
  color: var(--texto-secundario);
  border-bottom: 2px solid var(--borde);
}
.hardware-table td {
  padding: 12px;
  border-bottom: 1px solid var(--borde);
}
.hardware-table tr:last-child td { border-bottom: none; }
.td-id { font-weight: 800; color: var(--sena-azul-oscuro); }

.form-input, .form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.95rem;
  color: var(--texto-principal);
}
.form-input:focus, .form-select:focus {
  outline: none;
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57,169,0,0.1);
}
.select-relay {
  font-family: monospace;
  font-weight: 600;
  color: #c2410c; /* naranja fuerte para hardware */
  background: #fff7ed;
}
</style>

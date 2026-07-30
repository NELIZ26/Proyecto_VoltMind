<template>
  <div class="admin-view-shell config-view">
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>CONFIGURACION DEL SISTEMA</h1>
          <p class="header-meta">
            Ajustes técnicos, parámetros académicos y automatización de hardware | <span class="time">{{ currentTime }}</span>
          </p>
        </div>
      </div>
      <div class="header-actions">
        <div class="user-profile">
          <div class="user-info">
            <span class="user-name">Nelson Contreras</span>
            <span class="user-status">En línea</span>
          </div>
          <font-awesome-icon icon="fa-solid fa-circle-user" class="user-icon" />
        </div>
      </div>
    </header>

    <main class="config-main">
      <div class="config-sections">
        <!-- PARAMETROS DEL CALENDARIO -->
        <section class="config-section">
          <h2 class="section-title">
            <font-awesome-icon icon="fa-regular fa-calendar-days" />
            PARAMETROS DEL CALENDARIO
          </h2>
          <div class="params-row">
            <div class="param-group">
              <label>Duración Min. de Clases por Bloque</label>
              <div class="duration-input-wrapper">
                <div class="badge-input-container small-input">
                  <input type="number" v-model="duracionClase" class="base-input text-green-dark text-right" />
                </div>
                <span class="duration-label">{{ duracionTexto }}</span>
              </div>
            </div>
            <div class="param-group">
              <label>Hora de Apertura de Sede</label>
              <div class="time-input">
                <input type="time" v-model="horaApertura" class="base-input" />
                <font-awesome-icon icon="fa-solid fa-clock" class="time-icon text-green" />
              </div>
            </div>
            <div class="param-group">
              <label>Hora de Cierre de Sede</label>
              <div class="time-input">
                <input type="time" v-model="horaCierre" class="base-input" />
                <font-awesome-icon icon="fa-solid fa-clock" class="time-icon text-green" />
              </div>
            </div>
          </div>
        </section>

        <!-- CONTROLES IOT / RELÉS -->
        <section class="config-section">
          <h2 class="section-title">
            <font-awesome-icon icon="fa-solid fa-microchip" />
            CONTROLES IOT / RELÉS
          </h2>
          <p class="section-desc">Configure el comportamiento de los interruptores inteligentes asignados a cada ambiente de formación.</p>
          
          <div class="iot-control-list">
            <div class="iot-control-item">
              <div class="iot-control-info">
                <h3>Pre-encendido de Climatización (Relé AC)</h3>
                <p>Tiempo de activación del aire acondicionado antes de iniciar la formación.</p>
              </div>
              <div class="number-input">
                <input type="number" v-model="preEncendido" class="num-input text-green" />
                <span class="unit">minutos</span>
              </div>
            </div>

            <div class="iot-control-item">
              <div class="iot-control-info">
                <h3>Margen de Tolerancia de Apagado General (Luces/Energía)</h3>
                <p>Tiempo de espera para cortar la energía general tras terminar el horario de formación establecida.</p>
              </div>
              <div class="number-input">
                <input type="number" v-model="margenApagado" class="num-input text-green" />
                <span class="unit">minutos</span>
              </div>
            </div>
          </div>

          <div class="relay-test-section">
            <div class="relay-test-header">
              <span class="test-title">Prueba de Estado de Relés en Red</span>
              <div class="selectors">
                <span class="selector-label">Sede:</span>
                <select v-model="sedePrueba" class="custom-select-native">
                  <option value="CAAA">C.A.A.A</option>
                  <option value="Sede2">Sede Principal</option>
                </select>
                <span class="selector-label">Ambiente:</span>
                <select v-model="ambientePrueba" class="custom-select-native">
                  <option value="101">101</option>
                  <option value="102">102</option>
                </select>
              </div>
            </div>
            <div class="relay-badges">
              <div class="relay-badge badge-green">Luces y Tomas <span class="dot dot-green"></span></div>
              <div class="relay-badge badge-green">Rack <span class="dot dot-green"></span></div>
              <div class="relay-badge badge-yellow">Televisor <span class="dot dot-yellow"></span></div>
              <div class="relay-badge badge-red">Computadores <span class="dot dot-red"></span></div>
            </div>
          </div>
        </section>

        <!-- RESTRICCIONES Y ALERTAS -->
        <section class="config-section">
          <h2 class="section-title">
            <font-awesome-icon icon="fa-solid fa-shield-halved" />
            RESTRICCIONES Y ALERTAS DE CONFLICTO
          </h2>
          
          <div class="checkbox-group">
            <label class="custom-checkbox-wrapper">
              <div class="checkbox-input">
                <input type="checkbox" v-model="bloquearCruces" />
                <span class="checkmark" :class="{ 'checked': bloquearCruces }">
                  <font-awesome-icon icon="fa-solid fa-check" v-if="bloquearCruces" />
                </span>
              </div>
              <div class="checkbox-content">
                <span class="check-title">Bloquear cruces de horarios automáticamente</span>
                <span class="check-desc">Impide asignar un instructor o ambiente a dos fichas diferentes en el mismo rango horario.</span>
              </div>
            </label>
            
            <label class="custom-checkbox-wrapper">
              <div class="checkbox-input">
                <input type="checkbox" v-model="notificacionesCorreo" />
                <span class="checkmark" :class="{ 'checked': notificacionesCorreo }">
                  <font-awesome-icon icon="fa-solid fa-check" v-if="notificacionesCorreo" />
                </span>
              </div>
              <div class="checkbox-content">
                <span class="check-title">Notificaciones de inasistencia vía correo</span>
                <span class="check-desc">Alerta al coordinador si un ambiente no registra apertura biométrica tras 20 minutos de iniciada la clase.</span>
              </div>
            </label>
          </div>
        </section>

        <!-- GESTIÓN DE MÓDULOS IOT (Antigua Vista) -->
        <section class="config-section">
          <div class="section-header-row">
            <h2 class="section-title mb-0">
              <font-awesome-icon icon="fa-solid fa-network-wired" />
              GESTIÓN DE MÓDULOS IOT (ESP32)
            </h2>
            <button class="btn-action" @click="showModal = true">
              <font-awesome-icon icon="fa-solid fa-plus" />
              <span>NUEVO MÓDULO</span>
            </button>
          </div>
          <p class="section-desc">Gestión y telemetría de módulos hardware en la red.</p>

          <div class="dash-grid iot-grid">
            <div v-for="(modulo, i) in modulos" :key="modulo.id" class="module-card iot-card" :style="{ animationDelay: `${i * 50}ms` }">
              <div class="card-header border-b">
                <div class="module-info-group">
                  <div class="icon-box">
                    <font-awesome-icon icon="fa-solid fa-microchip" />
                  </div>
                  <div class="module-text">
                    <h3 class="module-name">{{ modulo.name }}</h3>
                    <span class="module-mac">{{ modulo.mac }}</span>
                  </div>
                </div>
                <div class="status-indicator" :title="modulo.online ? 'En línea' : 'Desconectado'">
                  <span :class="['dot', modulo.online ? 'dot-online' : 'dot-offline']"></span>
                </div>
              </div>

              <div class="card-body module-details">
                <div class="detail-row">
                  <span class="detail-label">Ambiente Asignado:</span>
                  <strong class="detail-value text-primary">{{ modulo.room }}</strong>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Dirección IP Local:</span>
                  <code class="detail-ip">{{ modulo.ip }}</code>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Último Ping:</span>
                  <span class="time-cell">{{ modulo.lastPing }}</span>
                </div>
              </div>

              <div class="card-footer relay-control border-t">
                <span class="footer-label">
                  <font-awesome-icon icon="fa-solid fa-power-off" class="footer-icon" />
                  Control de Energía (Relé)
                </span>
                
                <label class="toggle-switch">
                  <input 
                    type="checkbox" 
                    v-model="modulo.powerOn" 
                    :disabled="!modulo.online"
                    @change="toggleRelay(modulo)"
                  >
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div class="action-buttons">
        <button class="btn-cancel">Cancelar</button>
        <button class="btn-save" @click="handleSaveConfig">Guardar Configuración</button>
      </div>
    </main>

    <ModalFormModuleIoT 
      :show="showModal"
      @update:show="showModal = $event"
      @close="showModal = false"
      @save="handleAddModule"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import Swal from 'sweetalert2';
import { useConfigStore } from '@/stores/config';
import ModalFormModuleIoT from '@/components/admin/modals/ModalFormModuleIoT.vue';

// Time functionality
const currentTime = ref('');

const updateTime = () => {
  const now = new Date();
  let hours = now.getHours();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12;
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');
  currentTime.value = `${hours.toString().padStart(2, '0')}:${minutes}:${seconds} ${ampm}`;
};

let timer;
onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});

// Configuración Global desde el Store (Pinia)
const configStore = useConfigStore();
const { 
  duracionClase, 
  horaApertura, 
  horaCierre, 
  preEncendido, 
  margenApagado, 
  sedePrueba, 
  ambientePrueba, 
  bloquearCruces, 
  notificacionesCorreo 
} = storeToRefs(configStore);

const duracionTexto = computed(() => {
  const mins = parseInt(duracionClase.value) || 0;
  const hrs = Math.floor(mins / 60);
  const rMins = mins % 60;
  let res = [];
  if (hrs > 0) res.push(`${hrs} Hora${hrs>1?'s':''}`);
  if (rMins > 0) res.push(`${rMins} Minuto${rMins>1?'s':''}`);
  return res.join(' y ') || '0 Minutos';
});

const handleSaveConfig = () => {
  const success = configStore.saveConfig();
  if (success) {
    Swal.fire({
      icon: 'success',
      title: '¡Guardado!',
      text: 'La configuración global se ha guardado correctamente y está disponible en todo el sistema.',
      confirmButtonColor: '#39a900'
    });
  }
};

// Antiguo Mock Data y Funcionalidad de Módulos
const modulos = reactive([
  { id: 1, name: 'ESP32 - Master Control 401', mac: 'A1:B2:C3:D4:E5:F6', room: 'Ambiente 401', ip: '192.168.1.101', lastPing: 'Hace 5s', online: true, powerOn: true },
  { id: 2, name: 'ESP32 - Control Luces 402', mac: '12:34:56:78:90:AB', room: 'Ambiente 402', ip: '192.168.1.102', lastPing: 'Hace 2s', online: true, powerOn: false },
  { id: 3, name: 'ESP32 - Lab Redes Principal', mac: 'FF:EE:DD:CC:BB:AA', room: 'Laboratorio de Redes', ip: '192.168.1.105', lastPing: 'Hace 2m', online: true, powerOn: true },
  { id: 4, name: 'ESP32 - Bilingüismo', mac: '00:11:22:33:44:55', room: 'Sala de Bilingüismo', ip: '192.168.1.110', lastPing: 'Hace 1h', online: false, powerOn: false },
]);

const showModal = ref(false);

const toggleRelay = async (modulo) => {
  if (modulo.online) {
    console.log(`Enviando señal a ${modulo.ip} - Estado: ${modulo.powerOn ? 'ENCENDIDO' : 'APAGADO'}`);
    
    // Si es el módulo Master (ID: 1), enviamos comando global al backend
    if (modulo.id === 1) {
      try {
        await fetch(`http://127.0.0.1:8000/api/iot/master`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ estado: modulo.powerOn ? "1" : "0" })
        });
        
        // Mostrar alerta simple para feedback
        Swal.fire({
          icon: 'success',
          title: 'Orden Maestra Enviada',
          text: `Todos los bombillos se han ${modulo.powerOn ? 'encendido' : 'apagado'}.`,
          timer: 2000,
          showConfirmButton: false
        });
      } catch (error) {
        console.error("Error enviando comando maestro desde admin:", error);
        Swal.fire({
          icon: 'error',
          title: 'Error de Comunicación',
          text: 'No se pudo contactar con el backend (Raspberry Pi).'
        });
      }
    }
  }
};

const handleAddModule = (newModule) => {
  modulos.push(newModule);
};
</script>

<style scoped>
.admin-view-shell {
  font-family: var(--fuente-principal);
  color: var(--texto-principal);
  box-sizing: border-box;
  padding: 0 0 2rem 0;
  width: 100%;
  margin: 0 auto;
}

.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  border-radius: 12px;
  border: 1px solid var(--borde);
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.environment-badge h1 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.5px;
}

.header-meta {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  margin: 0;
}

.header-meta .time {
  font-weight: 600;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.user-name {
  font-weight: 800;
  font-size: 1rem;
  color: var(--texto-principal);
}

.user-status {
  font-size: 0.75rem;
  color: var(--sena-verde);
  font-weight: 700;
}

.user-icon {
  font-size: 2.5rem;
  color: var(--texto-principal);
}

.config-main {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.config-sections {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.config-section {
  background: var(--fondo-tarjetas);
  border-radius: 12px;
  padding: 1.5rem 2rem;
  border: 1px solid var(--borde);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-title.mb-0 {
  margin-bottom: 0;
}

.section-title svg {
  color: var(--texto-secundario);
}

.section-desc {
  font-size: 0.9rem;
  color: var(--texto-secundario);
  margin: -0.5rem 0 1.5rem 0;
}

.params-row {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
}

.param-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.param-group label {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  font-weight: 600;
}

/* Unificar anchos de inputs base */
.duration-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.badge-input-container {
  display: flex;
  align-items: center;
  background: rgba(57, 169, 0, 0.1);
  border: 1px solid var(--sena-verde);
  border-radius: 8px;
  width: 220px;
  box-sizing: border-box;
  height: 48px;
}

.badge-input-container.small-input {
  width: 60px;
  align-items: center;
}

.duration-label {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  background: var(--fondo-tarjetas);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--borde);
  display: flex;
  align-items: center;
  height: 48px;
  box-sizing: border-box;
}

.time-input {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  width: 220px;
  box-sizing: border-box;
  height: 48px;
}

.base-input {
  border: none;
  background: transparent;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--texto-principal);
  width: 100%;
  outline: none;
}

.text-right {
  text-align: right;
}

.text-green-dark {
  color: var(--sena-verde-oscuro) !important;
}

.time-icon {
  position: absolute;
  right: 1rem;
  font-size: 1.2rem;
  z-index: 1;
  pointer-events: none;
}

.text-green {
  color: var(--sena-verde) !important;
}

.iot-control-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.iot-control-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--borde);
}

.iot-control-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.iot-control-info h3 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  margin: 0 0 0.25rem 0;
}

.iot-control-info p {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  margin: 0;
}

.number-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.num-input {
  width: 60px;
  border: none;
  background: transparent;
  font-size: 1.2rem;
  font-weight: 800;
  text-align: right;
  outline: none;
  color: var(--sena-verde);
}

input[type="time"]::-webkit-calendar-picker-indicator {
  position: absolute;
  right: 1rem;
  width: 24px;
  height: 24px;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.number-input .unit {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  font-weight: 600;
  margin-left: 4px;
}

.relay-test-section {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1.5rem;
}

.relay-test-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.test-title {
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  font-size: 0.95rem;
}

.selectors {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.selector-label {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  font-weight: 600;
}

.custom-select-native {
  font-size: 0.85rem;
  color: var(--texto-principal);
  font-weight: 700;
  cursor: pointer;
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 4px;
  padding: 2px 4px;
  outline: none;
}

.relay-badges {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.relay-badge {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.badge-green {
  background: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde-oscuro);
  border: 1px solid var(--sena-verde);
}

.badge-yellow {
  background: rgba(253, 195, 0, 0.1);
  color: #854d0e;
  border: 1px solid var(--sena-amarillo);
}

.badge-red {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-green {
  background: var(--sena-verde);
  box-shadow: 0 0 4px var(--sena-verde);
}

.dot-yellow {
  background: var(--sena-amarillo);
  box-shadow: 0 0 4px var(--sena-amarillo);
}

.dot-red {
  background: #ef4444;
  box-shadow: 0 0 4px #ef4444;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.custom-checkbox-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  cursor: pointer;
}

.checkbox-input {
  position: relative;
  width: 20px;
  height: 20px;
  margin-top: 2px;
}

.checkbox-input input {
  opacity: 0;
  position: absolute;
  width: 0;
  height: 0;
  cursor: pointer;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  width: 20px;
  height: 20px;
  background: var(--borde);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  transition: background 0.2s;
}

.checkmark.checked {
  background: var(--sena-verde);
}

.checkbox-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.check-title {
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  font-size: 1rem;
}

.check-desc {
  font-size: 0.85rem;
  color: var(--texto-secundario);
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1.5rem;
  margin-top: 1rem;
}

.btn-cancel {
  background: transparent;
  border: none;
  color: var(--texto-principal);
  font-weight: 800;
  font-size: 0.95rem;
  cursor: pointer;
}

.btn-save {
  background: var(--sena-verde);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 800;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.2);
  transition: all 0.2s ease;
}

.btn-save:hover {
  background: var(--sena-verde-oscuro);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(57, 169, 0, 0.3);
}

.btn-action {
  background: var(--sena-verde);
  color: #ffffff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.2);
}

.btn-action:hover {
  background: var(--sena-verde-oscuro);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(57, 169, 0, 0.3);
}

.iot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-top: 4px solid var(--sena-verde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.iot-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 48, 64, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
}

.border-b {
  border-bottom: 1px solid var(--borde);
}

.border-t {
  border-top: 1px solid var(--borde);
}

.module-info-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--fondo-app);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  color: var(--sena-verde);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.module-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.module-name {
  font-size: 1rem;
  font-weight: 800;
  color: var(--texto-principal);
  margin: 0;
}

.module-mac {
  font-size: 0.75rem;
  font-family: monospace;
  color: var(--texto-secundario);
  letter-spacing: 0.5px;
}

.status-indicator {
  display: flex;
  align-items: center;
}

.dot-online {
  background-color: var(--sena-verde);
  box-shadow: 0 0 10px rgba(57, 169, 0, 0.6);
}

.dot-offline {
  background-color: #E53E3E;
  box-shadow: 0 0 10px rgba(229, 62, 62, 0.6);
}

.card-body {
  padding: 1.25rem 0;
}

.module-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.detail-label {
  color: var(--texto-secundario);
  font-weight: 700;
}

.text-primary {
  color: var(--texto-principal);
  font-weight: 800;
}

.detail-ip {
  background-color: rgba(80, 229, 249, 0.1);
  color: var(--sena-azul-oscuro);
  padding: 4px 8px;
  border-radius: 6px;
  font-family: monospace;
  font-weight: 700;
  border: 1px solid var(--sena-azul-claro);
}

.time-cell {
  font-family: monospace;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--texto-principal);
  background: var(--fondo-app);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--borde);
}

.card-footer {
  margin-top: auto;
  padding-top: 1rem;
}

.relay-control {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-label {
  font-weight: 800;
  color: var(--texto-secundario);
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.5px;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 52px;
  height: 30px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: var(--borde);
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

input:checked + .slider {
  background-color: var(--sena-verde);
}

input:focus + .slider {
  box-shadow: 0 0 1px var(--sena-verde);
}

input:checked + .slider:before {
  transform: translateX(22px);
}

input:disabled + .slider {
  background-color: rgba(226, 232, 240, 0.5);
  cursor: not-allowed;
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}
</style>

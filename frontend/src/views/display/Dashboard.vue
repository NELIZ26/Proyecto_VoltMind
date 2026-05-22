<script setup>
import { ref, onMounted } from "vue";
import { useToast } from "vue-toastification";

// IMPORTACIÓN DE LOS COMPONENTES DE MODAL EXTRAÍDOS
import ProfileModal from "@/components/profileModal.vue";
import AttendanceModal from "@/components/attendanceModal.vue";
import ExitModal from "@/components/exitModal.vue";

const toast = useToast();

// --- ESTADOS REACTIVOS PRINCIPALES ---
const isPowerOn = ref(false);
const nfcScanning = ref(false);
const qrProjected = ref(false);
const currentTime = ref(new Date().toLocaleTimeString());

// --- MANEJO DE MODALES ---
const activeModal = ref(null); // 'profile' | 'attendance' | 'exit'
const selectedApprentice = ref(null);

// --- MOCK DATA ---
const meters = ref([
  { id: 1, label: "Iluminación Aula", value: 120 },
  { id: 2, label: "Bancos de Cómputo", value: 850 },
  { id: 3, label: "Rack de Comunicaciones", value: 450 },
]);

const roomNodes = ref(
  Array.from({ length: 16 }, (_, i) => ({
    id: i + 1,
    energized: false,
    load: Math.floor(Math.random() * 90) + 10,
  })),
);

const apprentices = ref([
  {
    id: "001",
    name: "Carlos Mario Ruiz",
    status: "present",
    lastSeen: "08:05 AM",
    absences: 0,
    doc: "10234567",
    email: "carlos.ruiz@misena.edu.co",
    enum: "3001234567",
    history: ["02/05 (P)", "03/05 (P)", "04/05 (P)"],
  },
  {
    id: "002",
    name: "Ana Sofía Beltrán",
    status: "absent",
    lastSeen: "Ayer",
    absences: 4,
    doc: "11934568",
    email: "ana.beltran@misena.edu.co",
    enum: "3007654321",
    history: ["02/05 (F)", "03/05 (F)", "04/05 (F)"],
  },
  {
    id: "003",
    name: "Jorge Iván López",
    status: "present",
    lastSeen: "08:12 AM",
    absences: 1,
    doc: "10056789",
    email: "jorge.lopez@misena.edu.co",
    enum: "3009876543",
    history: ["02/05 (P)", "03/05 (F)", "04/05 (P)"],
  },
  {
    id: "004",
    name: "Elena Maria Paz",
    status: "absent",
    lastSeen: "Hace 3 días",
    absences: 3,
    doc: "10876543",
    email: "elena.paz@misena.edu.co",
    enum: "3001928374",
    history: ["02/05 (F)", "03/05 (F)", "04/05 (F)"],
  },
]);

const toggleMasterPower = () => {
  isPowerOn.value = !isPowerOn.value;
  roomNodes.value.forEach((node) => {
    node.energized = isPowerOn.value;
  });
  isPowerOn.value
    ? toast.success("Aula completamente Energizada")
    : toast.error("Cierre Maestro: Aula sin Energía");
};

const toggleNodePower = (node) => {
  node.energized = !node.energized;
  if (!node.energized) {
    if (!roomNodes.value.some((n) => n.energized)) isPowerOn.value = false;
  } else {
    isPowerOn.value = true;
  }
};

// --- ACCIONES DE DISPARO ---
const openModal = (type, apprentice) => {
  selectedApprentice.value = apprentice;
  activeModal.value = type;
};

const closeModal = () => {
  activeModal.value = null;
  selectedApprentice.value = null;
};

const handleExitConfirm = (reason) => {
  if (selectedApprentice.value) {
    selectedApprentice.value.status = "absent";
    selectedApprentice.value.lastSeen = "Salida Inesperada";
    toast.warning(`Salida anticipada registrada. Motivo: ${reason}`);
  }
  closeModal();
};

onMounted(() => {
  setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString();
  }, 1000);
});
</script>

<template>
  <div class="dashboard-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="logo-duo">
          <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
          <div class="logo-divider" />
          <img
            src="@/assets/VoltMindAccess.svg"
            alt="VoltMind"
            class="logo-volt"
          />
        </div>
        <div class="environment-badge">
          <h1>AMBIENTE 402</h1>
          <p class="header-meta">
            Ficha: 2997671 | Instructor: Diego Tobar |
            <span>{{ currentTime }}</span>
          </p>
        </div>
      </div>

      <div class="power-master-box">
        <span class="power-label">{{
          isPowerOn ? "AULA ENERGIZADA" : "AULA APAGADA"
        }}</span>
        <button
          class="power-switch"
          :class="{ 'power-active': isPowerOn }"
          @click="toggleMasterPower"
        >
          <font-awesome-icon icon="fa-solid fa-power-off" />
        </button>
      </div>
    </header>

    <main class="dash-grid">
      <section class="dash-col energy-section">
        <div class="module-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-microchip" /> TELEMETRÍA DE CONSUMO
          </h2>
          <div class="meters-grid">
            <div v-for="m in meters" :key="m.id" class="meter-pill">
              <span class="meter-label">{{ m.label }}</span>
              <span class="meter-val"
                >{{ isPowerOn ? m.value : 0 }}<small>W</small></span
              >
              <div class="meter-bar">
                <div
                  class="bar-fill"
                  :style="{ width: isPowerOn ? m.value / 10 + '%' : '0%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="module-card map-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-plug" /> CONTROL DE ENERGÍA POR ESTACIÓN
          </h2>
          <p class="map-instruction">
            Haz clic sobre un puesto para conmutar su flujo eléctrico de forma independiente.
          </p>
          <div class="room-map">
            <button
              v-for="node in roomNodes"
              :key="node.id"
              class="map-node"
              :class="{ 'node-on': node.energized }"
              @click="toggleNodePower(node)"
            >
              <small>PUESTO {{ node.id }}</small>
              <font-awesome-icon icon="fa-solid fa-bolt" class="node-bolt" />
              <span v-if="node.energized" class="node-watts">{{ node.load }}W</span>
              <span v-else class="node-watts">OFF</span>
            </button>
          </div>
        </div>
      </section>

      <section class="dash-col attendance-section">
        <div class="actions-group">
          <button
            class="btn-action nfc"
            :class="{ 'btn-active': nfcScanning }"
            @click="nfcScanning = !nfcScanning"
          >
            <font-awesome-icon icon="fa-solid fa-wifi" />
            <span>{{ nfcScanning ? "NFC ESCANEANDO" : "ACTIVAR NFC" }}</span>
          </button>
          <button
            class="btn-action qr"
            :class="{ 'btn-active': qrProjected }"
            @click="qrProjected = !qrProjected"
          >
            <font-awesome-icon icon="fa-solid fa-qrcode" />
            <span>{{ qrProjected ? "OCULTAR QR" : "PROYECTAR QR" }}</span>
          </button>
        </div>

        <div class="module-card alert-card">
          <h2 class="module-title text-alert">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> ALERTA DE DESERCIÓN (>3 INASISTENCIAS)
          </h2>
          <div class="alert-list">
            <div
              v-for="a in apprentices.filter((x) => x.absences >= 3)"
              :key="a.id"
              class="alert-item"
            >
              <span class="alert-name">{{ a.name }}</span>
              <span class="badge-alert">{{ a.absences }} FALLAS</span>
            </div>
          </div>
        </div>
      </section>

      <section class="dash-footer-table">
        <div class="module-card table-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-users" /> LISTADO OPERATIVO DE APRENDICES
          </h2>
          <div class="table-responsive-wrapper">
            <table class="apprentices-table">
              <thead>
                <tr>
                  <th>APRENDIZ</th>
                  <th>ESTADO</th>
                  <th>INGRESO</th>
                  <th class="text-center">ACCIONES</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in apprentices" :key="a.id">
                  <td>
                    <div class="table-user-info">
                      <strong>{{ a.name }}</strong>
                      <small>ID: VM-{{ a.id }}</small>
                    </div>
                  </td>
                  <td>
                    <span :class="a.status === 'present' ? 'status-green' : 'status-gray'">
                      {{ a.status === "present" ? "EN CLASE" : "AUSENTE" }}
                    </span>
                  </td>
                  <td>
                    <span class="time-cell">{{ a.lastSeen }}</span>
                  </td>
                  <td>
                    <div class="actions-cell">
                      <button
                        class="btn-table action-view"
                        title="Ver Datos"
                        @click="openModal('profile', a)"
                      >
                        <font-awesome-icon icon="fa-solid fa-user" />
                      </button>
                      <button
                        class="btn-table action-chart"
                        title="Historial"
                        @click="openModal('attendance', a)"
                      >
                        <font-awesome-icon icon="fa-solid fa-calendar-days" />
                      </button>
                      <button
                        v-if="a.status === 'present'"
                        class="btn-table action-exit"
                        title="Salida Inesperada"
                        @click="openModal('exit', a)"
                      >
                        <font-awesome-icon icon="fa-solid fa-right-from-bracket" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>

    <div v-if="qrProjected" class="qr-overlay" @click="qrProjected = false">
      <div class="qr-modal" @click.stop>
        <h3>CÓDIGO QR DE ASISTENCIA AMBIENTE 402</h3>
        <font-awesome-icon icon="fa-solid fa-qrcode" class="big-qr" />
        <p>Abre VoltMind Access en tu teléfono y escanea la pantalla para validar tu ingreso.</p>
        <button class="btn-close-overlay" @click="qrProjected = false">
          CERRAR PANTALLA COMPARTIDA
        </button>
      </div>
    </div>

    <ProfileModal
      v-if="activeModal === 'profile' && selectedApprentice"
      :apprentice="selectedApprentice"
      @close="closeModal"
    />

    <AttendanceModal
      v-if="activeModal === 'attendance' && selectedApprentice"
      :apprentice="selectedApprentice"
      @close="closeModal"
    />

    <ExitModal
      v-if="activeModal === 'exit' && selectedApprentice"
      :apprentice="selectedApprentice"
      @close="closeModal"
      @confirm="handleExitConfirm"
    />
  </div>
</template>

<style scoped>
/* ==========================================================================
   DASHBOARD PRINCIPAL - ESTÉTICA MINIMALISTA Y LIMPIA (SENA 2024)
   ========================================================================== */

.dashboard-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  background-color: var(--fondo-app); /* Gris claro de fondo */
  color: var(--texto-principal);
  padding: 1.5rem;
  box-sizing: border-box;
}

/* --- HEADER --- */
.dash-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: var(--fondo-tarjetas); /* Blanco */
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03); /* Sombra muy sutil */
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.logo-duo {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-sena {
  height: 38px;
  width: auto;
  object-fit: contain;
}

.logo-volt {
  height: 34px;
  width: auto;
  object-fit: contain;
}

.logo-divider {
  width: 1px;
  height: 28px;
  background: var(--borde);
}

.environment-badge h1 {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
  letter-spacing: -0.02em;
}

.header-meta {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--texto-secundario);
}

.header-meta span {
  color: var(--sena-azul-oscuro);
  font-family: monospace;
  font-weight: 600;
}

.power-master-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
}

.power-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--texto-secundario);
  letter-spacing: 0.08em;
}

.power-switch {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid var(--borde);
  background: var(--fondo-tarjetas);
  color: var(--texto-secundario);
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.power-switch.power-active {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border-color: var(--sena-verde-oscuro);
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25);
}

@media (min-width: 992px) {
  .dash-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 2rem;
  }
  .header-left {
    flex-direction: row;
    align-items: center;
    gap: 2.5rem;
  }
  .logo-sena { height: 44px; }
  .logo-volt { height: 40px; }
  .environment-badge h1 { font-size: 1.4rem; }
  .power-master-box {
    background: transparent;
    border: none;
    padding: 0;
    gap: 1.5rem;
  }
}

/* --- GRID PRINCIPAL --- */
.dash-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}
@media (min-width: 992px) {
  .dash-grid {
    grid-template-columns: 1fr 380px;
  }
}

.dash-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* --- TARJETAS MODULARES (CLEAN DESIGN) --- */
.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.02);
}

.module-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  margin: 0 0 1.25rem 0;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* --- TELEMETRÍA --- */
.meters-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
@media (min-width: 576px) {
  .meters-grid { grid-template-columns: repeat(3, 1fr); }
}

.meter-pill {
  background: var(--fondo-app);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--borde);
  transition: transform 0.2s ease;
}

.meter-pill:hover {
  transform: translateY(-2px);
  border-color: var(--sena-verde);
}

.meter-label {
  font-size: 0.65rem;
  color: var(--texto-secundario);
  font-weight: 600;
  display: block;
  margin-bottom: 6px;
}

.meter-val {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}

.meter-val small {
  font-size: 0.75rem;
  color: var(--sena-verde);
  margin-left: 3px;
}

.meter-bar {
  height: 4px;
  background: var(--borde);
  margin-top: 10px;
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--sena-verde);
  transition: width 0.4s ease;
}

/* --- MAPA DE ENERGÍA --- */
.map-instruction {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  margin: -0.5rem 0 1.25rem 0;
}

.room-map {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
@media (min-width: 400px) { .room-map { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 576px) { .room-map { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 1200px) { .room-map { grid-template-columns: repeat(8, 1fr); } }

.map-node {
  aspect-ratio: 1 / 1;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  color: var(--texto-secundario);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0.5rem;
}

.map-node:hover {
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.map-node small {
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.node-bolt {
  font-size: 1.2rem;
  opacity: 0.5;
}

.node-watts {
  font-size: 0.7rem;
  font-weight: 700;
  font-family: monospace;
}

.map-node.node-on {
  background: rgba(57, 169, 0, 0.06);
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
}
.map-node.node-on .node-bolt {
  color: var(--sena-verde);
  opacity: 1;
}

/* --- BOTONES DE ACCIÓN LATERAL --- */
.actions-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.btn-action {
  padding: 1.25rem 1rem;
  border-radius: 14px;
  border: 1px solid var(--borde);
  background: var(--fondo-tarjetas);
  color: var(--texto-secundario);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.7rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.btn-action:hover {
  background: var(--fondo-app);
  color: var(--sena-azul-oscuro);
}

.btn-action.nfc.btn-active {
  background: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
  border-color: var(--sena-azul-oscuro);
}

.btn-action.qr.btn-active {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border-color: var(--sena-verde-oscuro);
}

/* --- ALERTAS --- */
.text-alert {
  color: var(--sena-amarillo);
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 10px 14px;
  border-radius: 8px;
}

.alert-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--sena-azul-oscuro);
}

.badge-alert {
  background: rgba(253, 195, 0, 0.15); /* Fondo basado en el amarillo */
  color: var(--sena-azul-oscuro);
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 800;
  font-size: 0.65rem;
}

/* --- TABLA MINIMALISTA --- */
.dash-footer-table {
  grid-column: 1 / -1;
}

.table-responsive-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.apprentices-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  min-width: 500px;
}

.apprentices-table th {
  padding: 12px 10px;
  border-bottom: 2px solid var(--fondo-app);
  font-size: 0.7rem;
  color: var(--texto-secundario);
  text-transform: uppercase;
  font-weight: 700;
}

.apprentices-table td {
  padding: 14px 10px;
  border-bottom: 1px solid var(--fondo-app);
  font-size: 0.8rem;
  vertical-align: middle;
}

.table-user-info {
  display: flex;
  flex-direction: column;
}
.table-user-info strong {
  color: var(--sena-azul-oscuro);
  font-weight: 600;
}
.table-user-info small {
  color: var(--texto-secundario);
  font-size: 0.65rem;
  margin-top: 2px;
}

.status-green {
  display: inline-block;
  color: var(--sena-verde-oscuro);
  background: rgba(57, 169, 0, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.65rem;
}

.status-gray {
  display: inline-block;
  color: var(--texto-secundario);
  background: var(--fondo-app);
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.65rem;
}

.time-cell {
  font-family: monospace;
  color: var(--texto-secundario);
  font-size: 0.8rem;
}

/* --- ACCIONES DE TABLA --- */
.actions-cell {
  display: flex;
  gap: 8px;
}

.btn-table {
  border: 1px solid var(--borde);
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  background: var(--fondo-app);
  color: var(--texto-secundario);
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.btn-table:hover {
  color: var(--sena-azul-oscuro);
  background: var(--borde);
}

.btn-table.action-view:hover {
  border-color: var(--sena-azul-claro);
  color: var(--sena-azul-oscuro);
  background: rgba(80, 229, 249, 0.1);
}

.btn-table.action-chart:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
  background: rgba(57, 169, 0, 0.1);
}

.btn-table.action-exit:hover {
  border-color: var(--sena-amarillo);
  color: var(--sena-azul-oscuro);
  background: rgba(253, 195, 0, 0.15);
}

/* --- OVERLAY QR --- */
.qr-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 48, 64, 0.6); /* Azul oscuro con transparencia */
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.qr-modal {
  background: var(--sena-blanco);
  color: var(--sena-azul-oscuro);
  text-align: center;
  max-width: 400px;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.qr-modal h3 {
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  margin: 0;
}

.big-qr {
  font-size: 10rem;
  margin: 2rem 0;
  color: var(--sena-azul-oscuro);
}

.qr-modal p {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  line-height: 1.5;
  margin-bottom: 2rem;
}

.btn-close-overlay {
  background: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
  border: none;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 700;
  width: 100%;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-close-overlay:hover {
  background: var(--sena-verde-oscuro);
}
</style>
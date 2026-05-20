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
            <font-awesome-icon icon="fa-solid fa-microchip" /> TELEMETRÍA DE
            CONSUMO
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
            <font-awesome-icon icon="fa-solid fa-plug" /> CONTROL DE ENERGÍA POR
            ESTACIÓN
          </h2>
          <p class="map-instruction">
            Haz clic sobre un puesto para conmutar su flujo eléctrico de forma
            independiente.
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
              <span v-if="node.energized" class="node-watts"
                >{{ node.load }}W</span
              >
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
          <h2 class="module-title text-orange">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> ALERTA
            DE DESERCIÓN (>3 INASISTENCIAS)
          </h2>
          <div class="alert-list">
            <div
              v-for="a in apprentices.filter((x) => x.absences >= 3)"
              :key="a.id"
              class="alert-item"
            >
              <span>{{ a.name }}</span>
              <span class="badge-red">{{ a.absences }} FALLAS</span>
            </div>
          </div>
        </div>
      </section>

      <section class="dash-footer-table">
        <div class="module-card table-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-users" /> LISTADO OPERATIVO DE
            APRENDICES
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
                    <span
                      :class="
                        a.status === 'present' ? 'status-green' : 'status-gray'
                      "
                    >
                      {{ a.status === "present" ? "EN CLASE" : "AUSENTE" }}
                    </span>
                  </td>
                  <td>{{ a.lastSeen }}</td>
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
                        <font-awesome-icon
                          icon="fa-solid fa-right-from-bracket"
                        />
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
        <p>
          Abre VoltMind Access en tu teléfono y escanea la pantalla para validar
          tu ingreso.
        </p>
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
/* (Se mantienen exactamente los mismos estilos limpios de la estructura del dashboard, grillas, mapa y header provistos en el mensaje anterior) */
.dashboard-shell {
  font-family: "Inter", sans-serif;
  min-height: 100vh;
  background-color: #050a0e;
  color: #ffffff;
  padding: 1rem;
  box-sizing: border-box;
}
.dash-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: #001e30;
  padding: 1.25rem;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 1.25rem;
}
.header-left {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.logo-duo {
  display: flex;
  align-items: center;
  gap: 12px;
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
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(255, 255, 255, 0.15),
    transparent
  );
}
.environment-badge h1 {
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.02em;
}
.header-meta {
  margin-top: 4px;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
}
.header-meta span {
  color: #ffffff;
  font-family: monospace;
}
.power-master-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.75rem 1rem;
  border-radius: 12px;
}
.power-label {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}
.power-switch {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 3px solid #111;
  background: #222;
  color: #555;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
}
.power-switch.power-active {
  background: #39a900;
  color: #fff;
  border-color: #deff9a;
  box-shadow: 0 0 15px rgba(57, 169, 0, 0.4);
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
    gap: 2rem;
  }
  .logo-sena {
    height: 44px;
  }
  .logo-volt {
    height: 40px;
  }
  .environment-badge h1 {
    font-size: 1.4rem;
  }
  .power-master-box {
    background: transparent;
    padding: 0;
    gap: 1.5rem;
  }
}

.dash-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}
@media (min-width: 992px) {
  .dash-grid {
    grid-template-columns: 1fr 380px;
    gap: 1.5rem;
  }
}
.dash-col {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.module-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.25rem;
}
.module-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 1.25rem 0;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.04em;
}

.meters-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
@media (min-width: 576px) {
  .meters-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
.meter-pill {
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.02);
}
.meter-label {
  font-size: 0.65rem;
  color: #666;
  display: block;
  margin-bottom: 4px;
}
.meter-val {
  font-size: 1.25rem;
  font-weight: 800;
}
.meter-val small {
  font-size: 0.7rem;
  color: #39a900;
  margin-left: 2px;
}
.meter-bar {
  height: 3px;
  background: #111;
  margin-top: 8px;
  border-radius: 2px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: #39a900;
  transition: width 0.4s ease;
}

.map-instruction {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.35);
  margin: -0.5rem 0 1rem 0;
}
.room-map {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
@media (min-width: 400px) {
  .room-map {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (min-width: 576px) {
  .room-map {
    grid-template-columns: repeat(4, 1fr);
  }
}
@media (min-width: 1200px) {
  .room-map {
    grid-template-columns: repeat(8, 1fr);
  }
}

.map-node {
  aspect-ratio: 1 / 1;
  background: #0b141a;
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.15);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0.5rem;
}
.map-node small {
  font-size: 0.55rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.node-bolt {
  font-size: 1.1rem;
}
.node-watts {
  font-size: 0.65rem;
  font-weight: 700;
  font-family: monospace;
}
.map-node.node-on {
  background: rgba(57, 169, 0, 0.08);
  border-color: #39a900;
  color: #39a900;
  box-shadow: inset 0 0 10px rgba(57, 169, 0, 0.15);
}

.actions-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.btn-action {
  padding: 1rem;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: #0f1a24;
  color: rgba(255, 255, 255, 0.4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.7rem;
  transition: all 0.2s ease;
}
.btn-action.nfc.btn-active {
  background: #00324d;
  color: #39a900;
  border-color: #39a900;
}
.btn-action.qr.btn-active {
  background: #1c3d1c;
  color: #deff9a;
  border-color: #39a900;
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
  background: rgba(0, 0, 0, 0.2);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
}
.badge-red {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.65rem;
}

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
  padding: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.3);
  text-transform: uppercase;
}
.apprentices-table td {
  padding: 12px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
  font-size: 0.8rem;
}
.table-user-info {
  display: flex;
  flex-direction: column;
}
.table-user-info small {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.65rem;
  margin-top: 2px;
}
.status-green {
  color: #39a900;
  font-weight: 700;
  font-size: 0.7rem;
}
.status-gray {
  color: rgba(255, 255, 255, 0.25);
  font-size: 0.7_rem;
}

.actions-cell {
  display: flex;
  gap: 6px;
}
.btn-table {
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.02);
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.75rem;
  transition: all 0.2s ease;
}
.btn-table:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}
.btn-table.action-view:hover {
  border-color: #00b4ff;
  color: #00b4ff;
}
.btn-table.action-chart:hover {
  border-color: #39a900;
  color: #39a900;
}
.btn-table.action-exit:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.qr-overlay {
  position: fixed;
  inset: 0;
  background: rgba(3, 7, 10, 0.8);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.qr-modal {
  background: #ffffff;
  color: #050a0e;
  text-align: center;
  max-width: 400px;
  padding: 1.5rem;
  border-radius: 20px;
}
.qr-modal h3 {
  font-size: 0.95rem;
  font-weight: 900;
  letter-spacing: -0.01em;
  margin: 0;
}
.big-qr {
  font-size: 9rem;
  margin: 1.5rem 0;
  color: #050a0e;
}
.qr-modal p {
  font-size: 0.8rem;
  color: #444;
  line-height: 1.4;
  margin-bottom: 1.5rem;
}
.btn-close-overlay {
  background: #050a0e;
  color: #fff;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  width: 100%;
  cursor: pointer;
}
</style>

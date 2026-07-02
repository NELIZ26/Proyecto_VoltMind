<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
  apprenticeName: {
    type: String,
    default: "Aprendiz"
  }
});

const emit = defineEmits(['close', 'save']);

// Referencia al elemento canvas en el HTML
const canvasRef = ref(null);
let ctx = null;

// Variables de estado para el dibujo
const isDrawing = ref(false);
let lastX = 0;
let lastY = 0;

onMounted(() => {
  const canvas = canvasRef.value;
  ctx = canvas.getContext('2d');
  
  // Ajustar la resolución del canvas para que el trazo sea nítido
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;

  // Estilo del "esfero"
  ctx.strokeStyle = '#0f172a'; // Color de la tinta (azul muy oscuro/negro)
  ctx.lineWidth = 3; // Grosor
  ctx.lineCap = 'round'; // Puntas redondeadas
  ctx.lineJoin = 'round';
});

// --- LÓGICA DE DIBUJO ---
const getCoordinates = (e) => {
  const canvas = canvasRef.value;
  const rect = canvas.getBoundingClientRect();
  // Diferenciar entre toque táctil o clic de mouse
  if (e.touches && e.touches.length > 0) {
    return {
      x: e.touches[0].clientX - rect.left,
      y: e.touches[0].clientY - rect.top
    };
  } else {
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  }
};

const startDrawing = (e) => {
  e.preventDefault(); // Evita que la tablet haga scroll al dibujar
  isDrawing.value = true;
  const { x, y } = getCoordinates(e);
  lastX = x;
  lastY = y;
};

const draw = (e) => {
  e.preventDefault();
  if (!isDrawing.value) return;

  const { x, y } = getCoordinates(e);

  ctx.beginPath();
  ctx.moveTo(lastX, lastY); // Desde donde estaba
  ctx.lineTo(x, y); // Hasta donde se movió
  ctx.stroke(); // Dibuja la línea

  lastX = x;
  lastY = y;
};

const stopDrawing = () => {
  isDrawing.value = false;
};

// --- ACCIONES DE LOS BOTONES ---
const clearCanvas = () => {
  const canvas = canvasRef.value;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
};

const saveSignature = () => {
  const canvas = canvasRef.value;
  
  // Verificamos si el canvas está en blanco (opcional, básico)
  const blank = document.createElement('canvas');
  blank.width = canvas.width;
  blank.height = canvas.height;
  if (canvas.toDataURL() === blank.toDataURL()) {
    alert("Por favor, registre su firma antes de continuar.");
    return;
  }

  // Convertimos el dibujo a una cadena de texto Base64 (formato imagen PNG)
  const signatureBase64 = canvas.toDataURL('image/png');
  
  // Enviamos la firma al componente padre (DashboardInstru.vue)
  emit('save', signatureBase64);
};
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="firma-modal">
      
      <div class="modal-header">
        <h3>CONFIRMAR ASISTENCIA</h3>
        <p>Aprendiz: <strong>{{ apprenticeName }}</strong></p>
      </div>

      <div class="canvas-container">
        <canvas 
          ref="canvasRef" 
          class="signature-pad"
          @mousedown="startDrawing" 
          @mousemove="draw" 
          @mouseup="stopDrawing" 
          @mouseleave="stopDrawing"
          @touchstart="startDrawing" 
          @touchmove="draw" 
          @touchend="stopDrawing"
        ></canvas>
        <span class="watermark">Firme aquí</span>
      </div>

      <div class="modal-actions">
        <button class="btn-clear" @click="clearCanvas">
          Limpiar
        </button>
        <div class="right-actions">
          <button class="btn-cancel" @click="emit('close')">
            Cancelar
          </button>
          <button class="btn-save" @click="saveSignature">
            Guardar Asistencia
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Estilos básicos para que se vea como un modal centrado */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.firma-modal {
  background: white;
  width: 90%;
  max-width: 600px;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal-header h3 { margin: 0 0 8px 0; color: #1e293b; }
.modal-header p { margin: 0 0 16px 0; color: #475569; font-size: 1.1rem; }

.canvas-container {
  position: relative;
  width: 100%;
  height: 250px;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  background-color: #f8fafc;
  overflow: hidden;
  margin-bottom: 20px;
}

.signature-pad {
  width: 100%;
  height: 100%;
  cursor: crosshair;
  position: relative;
  z-index: 2;
}

.watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #e2e8f0;
  font-size: 2rem;
  font-weight: bold;
  pointer-events: none; /* Para que no estorbe al dibujar */
  z-index: 1;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.right-actions { display: flex; gap: 10px; }

/* Botones (Ajusta los colores a tu diseño) */
button { padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; border: none;}
.btn-clear { background: #e2e8f0; color: #475569; }
.btn-cancel { background: white; color: #ef4444; border: 1px solid #ef4444; }
.btn-save { background: #10b981; color: white; }
</style>
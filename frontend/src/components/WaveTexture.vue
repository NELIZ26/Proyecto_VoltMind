<template>
  <canvas ref="waveCanvas" class="wave-texture-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const props = defineProps({
  direction: {
    type: String,
    default: "horizontal", // Opciones: 'horizontal', 'vertical', 'diagonal'
  }
});

const waveCanvas = ref(null);
let animationId = null;
let offset = 0;

const initWaveTexture = () => {
  const canvas = waveCanvas.value;
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const resizeCanvas = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();

  const drawWaves = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Configuración de las líneas de onda
    const lines = [
      { color: "rgba(0, 48, 64, 0.08)", amplitude: 50, speed: 0.003, offsetFactor: 0.25, frequency: 0.0025 },
      { color: "rgba(57, 169, 0, 0.06)", amplitude: 70, speed: 0.0015, offsetFactor: 0.45, frequency: 0.002 },
      { color: "rgba(0, 48, 64, 0.07)", amplitude: 35, speed: 0.004, offsetFactor: 0.65, frequency: 0.0035 },
      { color: "rgba(57, 169, 0, 0.05)", amplitude: 85, speed: 0.001, offsetFactor: 0.8, frequency: 0.0015 }
    ];

    lines.forEach((line) => {
      ctx.beginPath();
      ctx.lineWidth = 2.0;
      ctx.strokeStyle = line.color;

      if (props.direction === "vertical") {
        // --- FLUJO VERTICAL (De arriba a abajo / abajo a arriba) ---
        for (let y = 0; y < canvas.height; y += 2) {
          const x = canvas.width * line.offsetFactor +
                    Math.sin(y * line.frequency + offset * line.speed * 100) * line.amplitude +
                    Math.cos(y * 0.0015 - offset * 0.08) * (line.amplitude * 0.35);
          
          if (y === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
      } else if (props.direction === "diagonal") {
        // --- FLUJO DIAGONAL ---
        for (let x = 0; x < canvas.width; x += 2) {
          // El centro base se desplaza diagonalmente en base a X
          const basePercent = (x / canvas.width) * 0.5 + (line.offsetFactor * 0.5);
          const y = canvas.height * basePercent +
                    Math.sin(x * line.frequency + offset * line.speed * 100) * line.amplitude +
                    Math.cos(x * 0.0015 - offset * 0.08) * (line.amplitude * 0.35);
          
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
      } else {
        // --- FLUJO HORIZONTAL (El tuyo original por defecto) ---
        for (let x = 0; x < canvas.width; x += 2) {
          const y = canvas.height * line.offsetFactor +
                    Math.sin(x * line.frequency + offset * line.speed * 100) * line.amplitude +
                    Math.cos(x * 0.0015 - offset * 0.08) * (line.amplitude * 0.35);
          
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    });

    offset += 0.04;
    animationId = requestAnimationFrame(drawWaves);
  };

  drawWaves();
};

onMounted(() => {
  initWaveTexture();
});

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId);
});
</script>

<style scoped>
.wave-texture-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
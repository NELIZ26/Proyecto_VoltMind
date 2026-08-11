<template>
  <div class="chart-container">
    <h3 v-if="title" class="chart-title">{{ title }}</h3>
    
    <div class="canvas-wrapper">
      <Doughnut :data="chartData" :options="chartOptions" :plugins="plugins" />
    </div>

    <div class="speedometer-value" :style="{ color: currentColor }">
      <span>{{ currentValue }}</span>
      <small>{{ unit }}</small>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, ArcElement);

const props = defineProps({
  currentValue: {
    type: Number,
    required: true,
    default: 0
  },
  maxValue: {
    type: Number,
    default: 100
  },
  unit: {
    type: String,
    default: 'W'
  },
  title: {
    type: String,
    default: ''
  }
});

// Color dinámico basado en el consumo
const currentColor = computed(() => {
  const value = Math.min(props.currentValue, props.maxValue);
  if (value > props.maxValue * 0.8) {
    return '#ef4444'; // Rojo
  } else if (value > props.maxValue * 0.5) {
    return '#eab308'; // Amarillo
  }
  return '#4ade80'; // Verde
});

const chartData = computed(() => {
  const value = Math.min(props.currentValue, props.maxValue);
  const remainder = props.maxValue - value;

  return {
    labels: ['Consumo', 'Restante'],
    datasets: [
      {
        data: [value, remainder],
        backgroundColor: [currentColor.value, '#e5e7eb'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270
      }
    ]
  };
});

// Plugin personalizado para dibujar la aguja y los números del contorno
const speedometerPlugin = {
  id: 'speedometerPlugin',
  afterDraw(chart) {
    const { ctx, config, data, chartArea: { width, height } } = chart;
    ctx.save();
    
    const dataTotal = props.maxValue;
    let actualValue = props.currentValue;
    
    if (actualValue > dataTotal) {
      actualValue = dataTotal + (dataTotal * 0.05); 
    }

    const cx = chart.getDatasetMeta(0).data[0].x;
    const cy = chart.getDatasetMeta(0).data[0].y;
    const outerRadius = chart.getDatasetMeta(0).data[0].outerRadius;

    // --- 1. Dibujar números en el contorno ---
    const steps = 4; // 0%, 25%, 50%, 75%, 100%
    ctx.fillStyle = '#6b7280';
    ctx.font = 'bold 11px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 0; i <= steps; i++) {
      const stepValue = (dataTotal / steps) * i;
      const angle = Math.PI + (Math.PI / steps) * i;
      
      // Radio para el texto (un poco por fuera del arco)
      const textRadius = outerRadius + 15; 
      const tx = cx + Math.cos(angle) * textRadius;
      const ty = cy + Math.sin(angle) * textRadius;

      ctx.fillText(Math.round(stepValue), tx, ty);
    }

    // --- 2. Dibujar la aguja ---
    const needleValue = actualValue;
    const needleAngle = Math.PI + (1 / dataTotal) * needleValue * Math.PI;

    ctx.translate(cx, cy);
    ctx.rotate(needleAngle);
    
    // Base de la aguja (ligeramente más delgada)
    ctx.beginPath();
    ctx.moveTo(0, -4);
    ctx.lineTo(outerRadius * 0.85, 0); 
    ctx.lineTo(0, 4);
    ctx.fillStyle = '#1f2937'; 
    ctx.fill();
    
    // Círculo central (pivote)
    ctx.beginPath();
    ctx.arc(0, 0, 8, 0, needleAngle * Math.PI);
    ctx.fillStyle = '#1f2937';
    ctx.fill();
    
    // Círculo interno decorativo
    ctx.beginPath();
    ctx.arc(0, 0, 3, 0, needleAngle * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    ctx.restore();
  }
};

const plugins = [speedometerPlugin];

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '82%', 
  layout: {
    padding: {
      left: 25,
      right: 25,
      top: 10,
      bottom: 10
    }
  },
  animation: {
    duration: 500,
    animateRotate: true,
    animateScale: false
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          return context.label === 'Consumo' ? `${props.currentValue} ${props.unit}` : '';
        }
      }
    }
  }
};
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.canvas-wrapper {
  position: relative;
  height: 150px; 
  width: 100%;
}

.chart-title {
  text-align: center;
  font-size: 0.95rem;
  font-weight: bold;
  color: #4b5563;
  margin: 0;
  padding-top: 5px;
  text-transform: uppercase;
}

.speedometer-value {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  transition: color 0.3s ease;
  margin-top: -10px; /* Acercarlo un poco al gráfico para que no se vea tan separado */
}

.speedometer-value span {
  font-size: 2rem;
  font-weight: bold;
  line-height: 1;
}

.speedometer-value small {
  font-size: 1rem;
  font-weight: 500;
  opacity: 0.8;
}
</style>

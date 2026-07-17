<template>
  <div class="thermometer-chart-container">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps({
  currentValue: {
    type: Number,
    required: true,
  },
  label: {
    type: String,
    default: "Temperatura",
  }
});

const getTempColor = (val) => {
  if (val < 20) return "rgba(59, 130, 246, 0.8)"; // Blue
  if (val > 26) return "rgba(239, 68, 68, 0.8)"; // Red
  return "rgba(34, 197, 94, 0.8)"; // Green
};

const chartData = computed(() => ({
  labels: [props.label],
  datasets: [
    {
      label: 'Temperatura °C',
      data: [props.currentValue],
      backgroundColor: getTempColor(props.currentValue),
      borderColor: getTempColor(props.currentValue).replace('0.8', '1'),
      borderWidth: 1,
      borderRadius: 10,
      borderSkipped: false,
      barThickness: 30, // Makes it look like a tube
    },
    {
      label: 'Fondo',
      data: [40 - props.currentValue], // Remaining height
      backgroundColor: 'rgba(229, 231, 235, 0.3)', // gray-200
      borderColor: 'rgba(209, 213, 219, 0.5)',
      borderWidth: 1,
      borderRadius: 10,
      borderSkipped: false,
      barThickness: 30,
    }
  ]
}));

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 1000
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 40,
      grid: {
        display: false
      },
      ticks: {
        callback: function(value) {
          return value + '°';
        },
        font: {
          family: "'Inter', monospace",
          size: 10
        }
      }
    },
    x: {
      stacked: true,
      grid: {
        display: false
      },
      ticks: {
        font: {
          family: "'Inter', monospace",
          size: 12,
          weight: 'bold'
        }
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          if (context.datasetIndex === 1) return null; // hide tooltip for background
          return context.raw + ' °C';
        }
      }
    }
  }
}));
</script>

<style scoped>
.thermometer-chart-container {
  width: 100%;
  height: 220px;
  position: relative;
  display: flex;
  justify-content: center;
}
</style>

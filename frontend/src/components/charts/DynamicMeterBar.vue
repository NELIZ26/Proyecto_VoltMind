<template>
  <div class="meter-pill">
    <span class="meter-label">{{ label }}</span>
    <span class="meter-val">{{ isActive ? value : 0 }}<small>{{ unit }}</small></span>
    <div class="meter-bar">
      <div class="bar-fill" :style="{ width: isActive ? (value / maxValue * 100) + '%' : '0%' }"></div>
    </div>
    <div class="meter-slot" v-if="$slots.default">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: { type: Number, default: 0 },
  maxValue: { type: Number, default: 1000 },
  unit: { type: String, default: 'W' },
  isActive: { type: Boolean, default: false }
});
</script>

<style scoped>
.meter-pill {
  background: var(--fondo-app);
  padding: 0.85rem;
  border-radius: 12px;
  border: 1px solid var(--borde);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.meter-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-secundario);
  text-transform: uppercase;
}
.meter-val {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  display: flex;
  align-items: baseline;
  gap: 2px;
}
.meter-val small {
  font-size: 0.85rem;
  color: var(--texto-secundario);
}
.meter-bar {
  width: 100%;
  height: 8px;
  background: var(--borde);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 4px;
}
.bar-fill {
  height: 100%;
  background: var(--sena-verde);
  border-radius: 4px;
  transition: width 0.5s ease-out;
}
.meter-slot {
  margin-top: 1rem;
}
</style>

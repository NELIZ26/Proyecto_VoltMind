<template>
  <div class="chart-container">
    <h3 v-if="title" class="chart-title">{{ title }}</h3>
    
    <div class="speedometer-wrapper">
      <vue-speedometer
        :value="currentValue"
        :minValue="0"
        :maxValue="maxValue"
        :segments="3"
        :customSegmentStops="[0, maxValue * 0.5, maxValue * 0.8, maxValue]"
        :segmentColors="['#4ade80', '#eab308', '#ef4444']"
        :needleColor="'#374151'"
        :textColor="'#9ca3af'"
        :currentValueText="`${currentValue} ${unit}`"
        :valueTextFontSize="'18px'"
        :labelFontSize="'10px'"
        :width="180"
        :height="120"
        :ringWidth="15"
        :needleHeightRatio="0.75"
        :needleTransitionDuration="500"
        needleTransition="easeElastic"
      />
    </div>
  </div>
</template>

<script setup>
import VueSpeedometer from 'vue-speedometer';

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
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.chart-title {
  text-align: center;
  font-size: 0.95rem;
  font-weight: bold;
  color: #4b5563;
  margin: 0;
  padding-top: 5px;
  padding-bottom: 10px;
  text-transform: uppercase;
}

.speedometer-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}
</style>

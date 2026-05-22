<template>
  <div 
    class="avatar-ring" 
    :class="{ 
      'nfc-pulse': isTransmitting,
      'is-validated': isValidated 
    }"
  >
    <div class="avatar-inner">
      <img
        v-if="src"
        :src="src"
        :alt="alt"
        class="avatar-img"
      />

      <div v-else class="avatar-robot-fallback">
        <svg
          viewBox="0 0 100 100"
          class="robot-svg"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M42 20 L35 10 M58 20 L65 10"
            stroke="#A0AEC0"
            stroke-width="3"
            stroke-linecap="round"
          />
          <circle cx="35" cy="10" r="3" :fill="isTransmitting ? '#39A900' : '#003040'" />
          <circle cx="65" cy="10" r="3" :fill="isTransmitting ? '#39A900' : '#003040'" />
          <rect x="20" y="42" width="6" height="16" rx="2" fill="#718096" />
          <rect x="74" y="42" width="6" height="16" rx="2" fill="#718096" />
          <circle cx="23" cy="50" r="1.5" :fill="isTransmitting ? '#39A900' : '#003040'" />
          <circle cx="77" cy="50" r="1.5" :fill="isTransmitting ? '#39A900' : '#003040'" />
          <rect x="25" y="25" width="50" height="50" rx="14" fill="#E2E8F0" stroke="#003040" stroke-width="2" />
          <rect x="32" y="38" width="36" height="18" rx="6" fill="#003040" />
          <circle cx="43" cy="47" r="4.5" :fill="isTransmitting ? '#39A900' : '#FDC300'" />
          <circle cx="57" cy="47" r="4.5" :fill="isTransmitting ? '#39A900' : '#FDC300'" />
          <circle cx="44" cy="46" r="1.5" fill="#ffffff" />
          <circle cx="58" cy="46" r="1.5" fill="#ffffff" />
          <path d="M42 63 L58 63" stroke="#003040" stroke-width="2" stroke-linecap="round" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  src: {
    type: String,
    default: "",
  },
  alt: {
    type: String,
    default: "Avatar del usuario",
  },
  isTransmitting: {
    type: Boolean,
    default: false,
  },
  isValidated: {
    type: Boolean,
    default: false,
  }
});
</script>

<style scoped>
.avatar-ring {
  position: relative;
  flex-shrink: 0;
  width: 76px;
  height: 76px;
  border-radius: 50%;
  border: 2px solid #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

/* Estado Validado: Borde Verde */
.avatar-ring.is-validated {
  border-color: #39A900;
}

/* Animación de pulso cuando está transmitiendo por NFC */
.avatar-ring.nfc-pulse {
  border-color: #39A900;
  animation: ring-pulse 1.5s infinite;
}

@keyframes ring-pulse {
  0% { box-shadow: 0 0 0 0 rgba(57, 169, 0, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(57, 169, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(57, 169, 0, 0); }
}

.avatar-inner {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #F6F6F6;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-robot-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.robot-svg {
  width: 85%;
  height: 85%;
  transition: all 0.3s ease;
}
</style>
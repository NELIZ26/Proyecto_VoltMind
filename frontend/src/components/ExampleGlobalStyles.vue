<!-- =============================================================================
     EJEMPLO DE USO RÁPIDO - SISTEMA DE ESTILOS GLOBAL
     VoltMind Access v2.4 | Vue 3 + CSS Puro Nativo
     ============================================================================= -->

<!-- ═══════════════════════════════════════════════════════════════════════════
     COMPONENTE: ExampleCard.vue
     Demostración de uso del sistema de estilos global con animaciones
     ═══════════════════════════════════════════════════════════════════════════ -->

<template>
  <div class="example-container flex-col-center py-xl">
    <!-- Título de la Sección -->
    <h1 class="text-3xl font-bold text-sena-azul-oscuro mb-lg">
      📚 Sistema de Estilos Global en Acción
    </h1>

    <!-- ╔═════════════════════════════════════════════════════════════════════╗
         ║ EJEMPLO 1: CARD BÁSICA CON ANIMACIÓN FADE-IN
         ╚═════════════════════════════════════════════════════════════════════╝ -->
    <div class="card animate-fade-in w-full max-w-md shadow-lg rounded-lg">
      <div class="flex-row-between mb-md">
        <h2 class="text-2xl font-semibold text-sena-verde">
          Ficha de Aprendiz
        </h2>
        <span class="text-sm font-medium text-secondary">ID: 12345</span>
      </div>

      <!-- Contenido de la Card con Flex Utilities -->
      <div class="flex-col gap-md">
        <!-- Fila: Nombre y Estado -->
        <div class="flex-row-between bg-gris-claro px-md py-sm rounded-md">
          <div class="flex-col">
            <span class="text-xs text-secondary font-medium">NOMBRE</span>
            <p class="text-lg font-semibold text-primary">
              Carlos Martínez López
            </p>
          </div>
          <span class="px-md py-sm bg-sena-verde text-white rounded-full text-xs font-bold">
            ACTIVO
          </span>
        </div>

        <!-- Fila: Datos Académicos -->
        <div class="flex-row-between gap-lg">
          <div class="flex-col flex-1">
            <span class="text-xs text-secondary font-medium">FICHA</span>
            <p class="text-base font-semibold text-primary">2404-1234</p>
          </div>
          <div class="flex-col flex-1">
            <span class="text-xs text-secondary font-medium">PROG. FORM.</span>
            <p class="text-base font-semibold text-primary">
              Electrónica Industrial
            </p>
          </div>
        </div>

        <!-- Fila: Asistencia -->
        <div class="flex-row-between bg-sena-gris-claro px-md py-md rounded-md border border-sena-gris-medio">
          <div class="flex-col">
            <span class="text-xs text-secondary font-medium">ASISTENCIA</span>
            <p class="text-2xl font-bold text-sena-verde">18/20</p>
          </div>
          <div class="text-right">
            <p class="text-xs text-secondary">Última sesión</p>
            <p class="text-sm font-semibold text-primary">3 junio 2026</p>
          </div>
        </div>
      </div>

      <!-- Botones con Flexbox y Animación -->
      <div class="flex-row-between gap-md mt-lg">
        <button class="btn-secondary flex-1">
          Ver Detalles
        </button>
        <button class="btn-primary flex-1">
          Registrar Asistencia
        </button>
      </div>
    </div>

    <!-- ╔═════════════════════════════════════════════════════════════════════╗
         ║ EJEMPLO 2: LISTA CON ANIMACIÓN SLIDE-UP (Stagger)
         ╚═════════════════════════════════════════════════════════════════════╝ -->
    <div class="mt-3xl w-full max-w-md">
      <h3 class="text-xl font-bold text-sena-azul-oscuro mb-lg">
        📋 Listado de Sesiones
      </h3>

      <div class="flex-col gap-md">
        <div
          v-for="(session, index) in sessions"
          :key="index"
          class="card animate-slide-up shadow-sm hover:shadow-md transition-base"
          :style="{ animationDelay: `${index * 100}ms` }"
        >
          <div class="flex-row-between gap-md align-center">
            <!-- Ícono de sesión (placeholder) -->
            <div class="flex-center-all w-12 h-12 bg-sena-verde rounded-lg text-white font-bold text-lg">
              {{ index + 1 }}
            </div>

            <!-- Información de sesión -->
            <div class="flex-col flex-1">
              <p class="font-semibold text-primary">{{ session.titulo }}</p>
              <span class="text-sm text-secondary">{{ session.fecha }}</span>
            </div>

            <!-- Badge de estado -->
            <span
              :class="[
                'text-xs font-bold px-md py-sm rounded-full',
                session.estado === 'Completada'
                  ? 'bg-sena-verde text-white'
                  : session.estado === 'En Progreso'
                  ? 'bg-sena-naranja text-sena-negro animate-pulse'
                  : 'bg-sena-gris-claro text-secondary'
              ]"
            >
              {{ session.estado }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- ╔═════════════════════════════════════════════════════════════════════╗
         ║ EJEMPLO 3: BOTÓN CON ANIMACIÓN PULSE (Estados de Carga)
         ╚═════════════════════════════════════════════════════════════════════╝ -->
    <div class="mt-3xl w-full max-w-md flex-col-center gap-lg">
      <h3 class="text-xl font-bold text-sena-azul-oscuro">
        ⚡ Estados de Botones
      </h3>

      <!-- Botón Normal -->
      <button class="btn-primary w-full">
        ✓ Botón Normal
      </button>

      <!-- Botón Cargando con Pulse -->
      <button class="btn-primary w-full animate-pulse" disabled>
        ⏳ Registrando... (Pulse)
      </button>

      <!-- Botón Secundario -->
      <button class="btn-secondary w-full">
        → Botón Secundario
      </button>
    </div>

    <!-- ╔═════════════════════════════════════════════════════════════════════╗
         ║ EJEMPLO 4: CONTENEDOR CON ANIMACIÓN SCALE-IN
         ╚═════════════════════════════════════════════════════════════════════╝ -->
    <div class="mt-3xl w-full max-w-md">
      <div class="card bg-sena-verde text-white animate-scale-in shadow-lg">
        <div class="flex-col-center text-center gap-md">
          <div class="text-5xl">🎉</div>
          <h2 class="text-2xl font-bold">¡Éxito!</h2>
          <p class="text-base">Tu asistencia ha sido registrada correctamente</p>
          <button class="btn-secondary" style="border-color: white; color: white">
            Continuar
          </button>
        </div>
      </div>
    </div>

    <!-- ╔═════════════════════════════════════════════════════════════════════╗
         ║ EJEMPLO 5: DEMO DE COLORES Y ESPACIADOS
         ╚═════════════════════════════════════════════════════════════════════╝ -->
    <div class="mt-3xl w-full max-w-md">
      <h3 class="text-xl font-bold text-sena-azul-oscuro mb-lg">
        🎨 Paleta SENA
      </h3>

      <div class="grid grid-cols-2 gap-md">
        <div class="flex-col gap-sm">
          <div class="h-16 bg-sena-verde rounded-lg flex-center-all text-white font-bold text-sm">
            Verde
          </div>
        </div>
        <div class="flex-col gap-sm">
          <div class="h-16 bg-sena-azul-oscuro rounded-lg flex-center-all text-white font-bold text-sm">
            Azul
          </div>
        </div>
        <div class="flex-col gap-sm">
          <div class="h-16 bg-sena-naranja rounded-lg flex-center-all text-sena-negro font-bold text-sm">
            Naranja
          </div>
        </div>
        <div class="flex-col gap-sm">
          <div class="h-16 bg-sena-violeta rounded-lg flex-center-all text-white font-bold text-sm">
            Violeta
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Datos de ejemplo para la lista de sesiones
const sessions = [
  {
    titulo: "Sesión 1: Introducción a IoT",
    fecha: "2 junio 2026",
    estado: "Completada"
  },
  {
    titulo: "Sesión 2: Sensores y Actuadores",
    fecha: "3 junio 2026",
    estado: "Completada"
  },
  {
    titulo: "Sesión 3: Comunicación TCP/IP",
    fecha: "4 junio 2026",
    estado: "En Progreso"
  },
  {
    titulo: "Sesión 4: Análisis de Datos",
    fecha: "5 junio 2026",
    estado: "Pendiente"
  }
];
</script>

<style scoped>
.example-container {
  max-width: 100%;
  padding: 2rem;
  background: linear-gradient(135deg, var(--sena-gris-claro) 0%, white 100%);
  border-radius: var(--border-radius-lg);
}

.w-full {
  width: 100%;
}

.max-w-md {
  max-width: 28rem;
}

.h-16 {
  height: 4rem;
}

.grid {
  display: grid;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

/* ── Animaciones con Stagger ── */
.animate-slide-up {
  opacity: 0;
  animation: slideUp var(--transition-base) var(--timing-ease-out) forwards;
}

/* Ajuste marginal para demostración */
.mb-lg {
  margin-bottom: var(--spacing-lg);
}

.mb-md {
  margin-bottom: var(--spacing-md);
}

.mt-lg {
  margin-top: var(--spacing-lg);
}

.mt-3xl {
  margin-top: var(--spacing-3xl);
}
</style>

<!-- =============================================================================
     GUÍA DE USO RÁPIDO
     
     ✅ CLASES UTILIZADAS EN ESTE EJEMPLO:
     
     1. FLEXBOX:
        - flex-row-between: display flex + justify-content space-between + align-items center
        - flex-col-center: flex column + center todo
        - flex-center-all: centra horizontal y verticalmente
        - gap-lg, gap-md: espacio entre elementos
     
     2. ESPACIADO:
        - px-md, py-sm, py-lg: padding horizontal/vertical
        - mb-lg, mt-3xl: margen bottom/top
     
     3. TIPOGRAFÍA:
        - text-3xl, text-2xl, text-base: tamaños de fuente
        - font-bold, font-semibold: pesos de fuente
        - text-sena-verde, text-sena-azul-oscuro: colores SENA
        - text-white, text-secondary: colores estándar
     
     4. COLORES DE FONDO:
        - bg-sena-verde, bg-sena-azul-oscuro: fondos SENA
        - bg-gris-claro: fondo neutro
     
     5. ANIMACIONES:
        - animate-fade-in: entrada suave por opacidad
        - animate-slide-up: entrada desde abajo
        - animate-scale-in: entrada con zoom
        - animate-pulse: efecto de carga (parpadeo)
     
     6. COMPONENTES:
        - .card: tarjeta con sombra y radio
        - .btn-primary, .btn-secondary: botones SENA
        - .rounded-lg: bordes redondeados
        - .shadow-lg: sombra profunda
     
     7. UTILIDADES ADICIONALES:
        - .border: borde gris sutil
        - .rounded-full: borde redondo completo
        - .transition-base: transición suave
        - .hidden-mobile, .hidden-desktop: responsive
     
     ═════════════════════════════════════════════════════════════════════════
     EJEMPLO DE IMPLEMENTACIÓN EN UN COMPONENTE REAL:
     
     <template>
       <div class="card animate-fade-in">
         <div class="flex-row-between gap-lg">
           <h2 class="text-2xl font-bold text-sena-verde">Título</h2>
           <span class="text-sm text-secondary">Info</span>
         </div>
         <p class="text-base text-primary py-lg">Contenido aquí</p>
         <button class="btn-primary">Acción</button>
       </div>
     </template>
     
     <style scoped>
       /* Los estilos globales ya están disponibles sin importar */
     </style>
     
     ═════════════════════════════════════════════════════════════════════════ -->

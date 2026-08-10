<template>
  <div class="mi-programacion">
    <!-- Encabezado -->
    <header class="dash-header">
      <div class="header-left">
        <button class="btn-volver" title="Volver al panel del instructor" @click="volver">
          <font-awesome-icon icon="fa-solid fa-arrow-left" />
        </button>
        <div class="environment-badge">
          <h1>MI PROGRAMACIÓN</h1>
          <p class="header-meta">
            Calendario personal del instructor (matriz por instructor)
          </p>
        </div>
      </div>
      <div v-if="datos" class="header-actions">
        <span class="chip-instructor">
          <span class="punto-color" :style="{ background: datos.instructor.color }"></span>
          {{ datos.instructor.nombre }}
          <small>({{ datos.instructor.iniciales }} · {{ datos.instructor.tipo_vinculacion }})</small>
        </span>
      </div>
    </header>

    <!-- Estado: cargando -->
    <div v-if="cargando" class="module-card estado-panel">
      <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="estado-icono" />
      <p>Cargando su programación...</p>
    </div>

    <!-- Estado: sin instructor identificado (selector para demo/pruebas) -->
    <div v-else-if="!datos" class="module-card estado-panel">
      <font-awesome-icon icon="fa-solid fa-chalkboard-user" class="estado-icono" />
      <div class="seleccion">
        <strong>¿De quién es la programación que desea consultar?</strong>
        <p v-if="error" class="texto-error">{{ error }}</p>
        <p v-else>
          No se pudo identificar su correo institucional en la programación,
          seleccione su nombre para abrir su calendario.
        </p>
        <div class="fila-seleccion">
          <select v-model="instructorElegido" class="form-input">
            <option value="" disabled>Seleccione el instructor...</option>
            <option v-for="i in instructores" :key="i.id" :value="i.id">
              {{ i.nombre }} ({{ i.tipo_vinculacion }})
            </option>
          </select>
          <button class="btn-action" :disabled="!instructorElegido" @click="cargarPorId">
            <font-awesome-icon icon="fa-solid fa-eye" /> VER CALENDARIO
          </button>
        </div>
      </div>
    </div>

    <template v-else>
      <!-- Resumen del mes -->
      <section class="resumen-grid">
        <article class="module-card resumen-card">
          <p class="resumen-titulo">HORAS DE {{ etiquetaMes.toUpperCase() }}</p>
          <div class="resumen-valor">
            <span class="resumen-numero" :class="{ excedida: horasMes > datos.instructor.limite_mensual }">
              {{ horasMes }} h
            </span>
            <span class="resumen-contexto">de {{ datos.instructor.limite_mensual }} h mensuales</span>
          </div>
          <div class="barra">
            <div
              class="barra-relleno"
              :class="horasMes > datos.instructor.limite_mensual ? 'barra-roja' : 'barra-ok'"
              :style="{ width: Math.min((horasMes / datos.instructor.limite_mensual) * 100, 100) + '%' }"
            ></div>
          </div>
        </article>

        <article class="module-card resumen-card">
          <p class="resumen-titulo">FICHAS ESTE MES</p>
          <div class="resumen-valor">
            <span class="resumen-numero">{{ leyendaMes.length }}</span>
            <span class="resumen-contexto">
              {{ leyendaMes.length === 1 ? 'ficha asignada' : 'fichas asignadas' }} ·
              {{ asignacionesMes.length }} {{ asignacionesMes.length === 1 ? 'asignación' : 'asignaciones' }}
            </span>
          </div>
          <p v-if="datos.instructor.fin_contrato" class="resumen-nota">
            <font-awesome-icon icon="fa-solid fa-file-contract" />
            Contrato vigente hasta el {{ formatearFecha(datos.instructor.fin_contrato) }}.
          </p>
        </article>
      </section>

      <!-- Calendario mensual -->
      <main class="module-card calendario-card">
        <div class="calendario-toolbar">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-calendar-days" /> CALENDARIO PERSONAL
          </h2>
          <div class="mes-nav">
            <button class="mes-flecha" aria-label="Mes anterior" @click="cambiarMes(-1)">
              <font-awesome-icon icon="fa-solid fa-chevron-left" />
            </button>
            <span class="mes-actual">{{ etiquetaMes }}</span>
            <button class="mes-flecha" aria-label="Mes siguiente" @click="cambiarMes(1)">
              <font-awesome-icon icon="fa-solid fa-chevron-right" />
            </button>
            <button class="btn-hoy" @click="irAHoy">Hoy</button>
          </div>
        </div>

        <div class="calendario-scroll">
          <div class="calendario-grid">
            <div v-for="dia in DIAS_SEMANA" :key="dia" class="cal-encabezado">{{ dia }}</div>
            <div
              v-for="celda in celdasMes"
              :key="celda.iso"
              class="cal-dia"
              :class="{
                'fuera-mes': !celda.esDelMes,
                'fin-semana': celda.finDeSemana,
                hoy: celda.iso === hoyIso,
              }"
            >
              <span class="cal-numero">{{ celda.dia }}</span>
              <div
                v-for="a in celda.asignaciones"
                :key="a.id"
                class="cal-chip"
                :style="estiloChip(a)"
                :title="`Ficha ${a.ficha_codigo} · ${a.ficha_programa}\n` +
                  `${a.competencia?.nombre} (${a.competencia?.tipo}) · Jornada ${a.jornada}\n` +
                  `${formatearFecha(a.fecha_inicio)} → ${formatearFecha(a.fecha_fin)} · ${a.horas} h · ` +
                  `Ambiente: ${a.ambiente?.nombre || '—'}`"
              >
                <strong>{{ a.ficha_codigo }}</strong>
                <span class="cal-chip-texto">{{ a.competencia?.nombre }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Convenciones: color por ficha, como en el Excel -->
        <div v-if="leyendaMes.length" class="leyenda leyenda-calendario">
          <span class="leyenda-etiqueta">Convenciones del mes:</span>
          <span v-for="f in leyendaMes" :key="f.codigo" class="leyenda-item">
            <span class="punto-color" :style="{ background: f.color }"></span>
            <strong>{{ f.codigo }}</strong> = {{ f.programa }} ({{ f.jornada }})
          </span>
        </div>
        <p v-else class="calendario-vacio">
          No tiene asignaciones programadas en este mes.
        </p>
      </main>

      <!-- Detalle del mes (solo lectura) -->
      <section v-if="asignacionesMes.length" class="module-card">
        <h2 class="module-title titulo-lista">
          <font-awesome-icon icon="fa-solid fa-table-list" /> DETALLE DE {{ etiquetaMes.toUpperCase() }}
        </h2>
        <ul class="lista-asignaciones">
          <li v-for="a in asignacionesMes" :key="a.id" class="asig-fila">
            <span class="asig-franja" :style="{ background: colorFicha(a.ficha_codigo) }"></span>
            <div class="asig-info">
              <span class="asig-principal">
                <strong>Ficha {{ a.ficha_codigo }}</strong> · {{ a.competencia?.nombre }}
                <small>({{ a.competencia?.tipo }})</small>
              </span>
              <span class="asig-secundario">
                {{ formatearFecha(a.fecha_inicio) }} → {{ formatearFecha(a.fecha_fin) }}
                · Jornada {{ a.jornada }} ({{ horarioJornada(a.jornada) }})
                · {{ a.horas }} h · {{ a.ambiente?.nombre }} ({{ a.ambiente?.sede }})
              </span>
            </div>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
// Calendario personal del instructor: la "matriz por instructor" del Excel de la
// coordinadora, en solo lectura. Cada ficha se pinta con su propio color y la
// leyenda de convenciones se arma automáticamente con las fichas del mes.
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { tituladasService } from '@/services/tituladasService';
import { horarioJornada, formatearFecha } from '@/stores/tituladas';

const router = useRouter();
const auth = useAuthStore();

const datos = ref(null);          // { instructor, asignaciones }
const instructores = ref([]);     // selector de respaldo (demo/pruebas)
const instructorElegido = ref('');
const cargando = ref(true);
const error = ref('');

const NOMBRES_MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];
const DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

// Paleta para diferenciar las fichas dentro del calendario personal
const PALETA_FICHAS = ['#39A900', '#2980B9', '#E67E22', '#8E44AD', '#C0392B', '#16A085', '#B7950B', '#1F618D'];

// ── Carga de datos ──
const cargarPorCorreo = async (correo) => {
  try {
    datos.value = await tituladasService.getCalendarioInstructor({ correo });
    return true;
  } catch (e) {
    if (e.esConexion) error.value = e.message;
    return false;
  }
};

const cargarPorId = async () => {
  if (!instructorElegido.value) return;
  cargando.value = true;
  error.value = '';
  try {
    datos.value = await tituladasService.getCalendarioInstructor({ instructorId: instructorElegido.value });
  } catch (e) {
    error.value = e.message;
  } finally {
    cargando.value = false;
  }
};

onMounted(async () => {
  // 1º intento: el correo de la sesión del instructor; si no coincide, selector
  if (auth.instructorEmail) await cargarPorCorreo(auth.instructorEmail);
  if (!datos.value) {
    try {
      instructores.value = await tituladasService.getInstructores();
    } catch (e) {
      error.value = e.message;
    }
  }
  cargando.value = false;
});

// ── Calendario mensual ──
const hoy = new Date();
const hoyIso = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`;
const periodo = ref({ anio: hoy.getFullYear(), mes: hoy.getMonth() }); // mes: 0-11

const etiquetaMes = computed(() => `${NOMBRES_MESES[periodo.value.mes]} ${periodo.value.anio}`);

const cambiarMes = (delta) => {
  const fecha = new Date(periodo.value.anio, periodo.value.mes + delta, 1);
  periodo.value = { anio: fecha.getFullYear(), mes: fecha.getMonth() };
};

const irAHoy = () => {
  periodo.value = { anio: hoy.getFullYear(), mes: hoy.getMonth() };
};

const aIso = (fecha) =>
  `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`;

const asignacionesDe = (iso, finDeSemana) => {
  if (finDeSemana || !datos.value) return [];
  return datos.value.asignaciones.filter((a) => a.fecha_inicio <= iso && iso <= a.fecha_fin);
};

const celdasMes = computed(() => {
  if (!datos.value) return [];
  const { anio, mes } = periodo.value;
  const primerDia = new Date(anio, mes, 1);
  const desplazamiento = (primerDia.getDay() + 6) % 7; // lunes = 0
  const celdas = [];
  for (let i = 0; i < 42; i++) {
    const fecha = new Date(anio, mes, 1 - desplazamiento + i);
    const finDeSemana = fecha.getDay() === 0 || fecha.getDay() === 6;
    const iso = aIso(fecha);
    celdas.push({
      iso,
      dia: fecha.getDate(),
      esDelMes: fecha.getMonth() === mes,
      finDeSemana,
      asignaciones: asignacionesDe(iso, finDeSemana),
    });
  }
  const semanas = [];
  for (let i = 0; i < 42; i += 7) semanas.push(celdas.slice(i, i + 7));
  return semanas.filter((s) => s.some((c) => c.esDelMes)).flat();
});

const asignacionesMes = computed(() => {
  if (!datos.value) return [];
  const { anio, mes } = periodo.value;
  const inicioMes = aIso(new Date(anio, mes, 1));
  const finMes = aIso(new Date(anio, mes + 1, 0));
  return datos.value.asignaciones.filter(
    (a) => a.fecha_inicio <= finMes && inicioMes <= a.fecha_fin
  );
});

/** Horas del mes visible: días hábiles cubiertos por cada asignación × 6 h. */
const horasMes = computed(() => {
  const { anio, mes } = periodo.value;
  let total = 0;
  for (const a of asignacionesMes.value) {
    const inicio = new Date(Math.max(new Date(a.fecha_inicio + 'T00:00'), new Date(anio, mes, 1)));
    const fin = new Date(Math.min(new Date(a.fecha_fin + 'T00:00'), new Date(anio, mes + 1, 0)));
    for (let d = new Date(inicio); d <= fin; d.setDate(d.getDate() + 1)) {
      if (d.getDay() !== 0 && d.getDay() !== 6) total += 6;
    }
  }
  return total;
});

// ── Colores y leyenda por ficha (las "convenciones" del Excel) ──
const colorFicha = (codigo) => {
  if (!datos.value) return PALETA_FICHAS[0];
  const codigos = [...new Set(datos.value.asignaciones.map((a) => a.ficha_codigo))].sort();
  return PALETA_FICHAS[codigos.indexOf(codigo) % PALETA_FICHAS.length];
};

const leyendaMes = computed(() => {
  const vistos = new Map();
  for (const a of asignacionesMes.value) {
    if (!vistos.has(a.ficha_codigo)) {
      vistos.set(a.ficha_codigo, {
        codigo: a.ficha_codigo,
        programa: a.ficha_programa,
        jornada: a.jornada,
        color: colorFicha(a.ficha_codigo),
      });
    }
  }
  return [...vistos.values()];
});

const estiloChip = (a) => {
  const color = colorFicha(a.ficha_codigo);
  return {
    background: hexARgba(color, 0.14),
    borderLeft: `3px solid ${color}`,
    color: 'var(--texto-principal)',
  };
};

function hexARgba(hex, alfa) {
  if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return hex;
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alfa})`;
}

const volver = () => router.push('/dashboard');
</script>

<style scoped>
.mi-programacion {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  color: var(--texto-principal);
  background: var(--fondo-app);
  box-sizing: border-box;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Encabezado ── */
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  border-left: 5px solid var(--sena-verde);
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
  gap: 1rem;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.btn-volver {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  width: 42px;
  height: 42px;
  color: var(--texto-secundario);
  cursor: pointer;
  font-size: 1rem;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.btn-volver:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.environment-badge h1 {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
}

.header-meta {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.chip-demo {
  background: rgba(253, 195, 0, 0.18);
  color: #8a6d00;
  border: 1px solid rgba(253, 195, 0, 0.5);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

[data-theme="dark"] .chip-demo { color: var(--sena-amarillo); }

.chip-instructor {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 0.55rem 1rem;
  font-size: 0.85rem;
  font-weight: 800;
}

.chip-instructor small { font-weight: 600; color: var(--texto-secundario); }

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
}

/* ── Resumen ── */
.resumen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.resumen-card { display: flex; flex-direction: column; gap: 0.7rem; }

.resumen-titulo {
  margin: 0;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--texto-secundario);
}

.resumen-valor {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.resumen-numero {
  font-size: 1.7rem;
  font-weight: 800;
  color: var(--sena-verde);
  line-height: 1;
}

.resumen-numero.excedida { color: #e53e3e; }

.resumen-contexto { font-size: 0.74rem; color: var(--texto-secundario); }

.resumen-nota {
  margin: 0;
  font-size: 0.72rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 6px;
}

.barra {
  position: relative;
  height: 8px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  overflow: hidden;
}

.barra-relleno { height: 100%; border-radius: 6px; transition: width 0.4s ease; }
.barra-ok { background: var(--sena-verde); }
.barra-roja { background: #e53e3e; }

/* ── Selector de respaldo ── */
.seleccion {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 480px;
}

.fila-seleccion { display: flex; gap: 10px; flex-wrap: wrap; }

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.65rem 1rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  cursor: pointer;
  flex: 1;
  min-width: 220px;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.texto-error { color: #c53030; font-weight: 700; }
[data-theme="dark"] .texto-error { color: #fc8181; }

.btn-action {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border: none;
  padding: 0.65rem 1.3rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.2);
}

.btn-action:hover:not(:disabled) {
  background: var(--sena-verde-oscuro);
  transform: translateY(-2px);
}

.btn-action:disabled { opacity: 0.6; cursor: not-allowed; }

/* ── Calendario (mismo lenguaje visual del detalle de ficha) ── */
.calendario-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.module-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.module-title svg { color: var(--sena-verde); }

.mes-nav { display: flex; align-items: center; gap: 6px; }

.mes-flecha {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  width: 30px;
  height: 30px;
  color: var(--texto-secundario);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.mes-flecha:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.mes-actual {
  font-size: 0.85rem;
  font-weight: 800;
  min-width: 140px;
  text-align: center;
}

.btn-hoy {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 0.35rem 0.8rem;
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-hoy:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.calendario-scroll { overflow-x: auto; }

.calendario-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(120px, 1fr));
  gap: 4px;
  min-width: 860px;
}

.cal-encabezado {
  text-align: center;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-secundario);
  padding: 0.4rem 0;
}

.cal-dia {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  min-height: 86px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cal-dia.fuera-mes { opacity: 0.35; }

.cal-dia.fin-semana {
  background: repeating-linear-gradient(
    -45deg,
    var(--fondo-app),
    var(--fondo-app) 6px,
    rgba(0, 48, 64, 0.04) 6px,
    rgba(0, 48, 64, 0.04) 12px
  );
}

.cal-dia.hoy { border-color: var(--sena-verde); box-shadow: inset 0 0 0 1px var(--sena-verde); }

.cal-numero {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--texto-secundario);
}

.cal-dia.hoy .cal-numero { color: var(--sena-verde); }

.cal-chip {
  border-radius: 6px;
  padding: 3px 6px;
  font-size: 0.64rem;
  display: flex;
  flex-direction: column;
  gap: 1px;
  line-height: 1.25;
}

.cal-chip strong { font-size: 0.66rem; font-family: monospace; }

.cal-chip-texto {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  color: var(--texto-secundario);
}

.leyenda-calendario {
  margin-top: 1rem;
  padding-top: 0.9rem;
  border-top: 1px dashed var(--borde);
}

.leyenda {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  font-size: 0.72rem;
  color: var(--texto-secundario);
}

.leyenda-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
}

.leyenda-etiqueta { font-weight: 800; color: var(--texto-principal); }

.punto-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.15);
}

.calendario-vacio {
  margin: 1rem 0 0;
  padding: 1.25rem;
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.8rem;
  border: 1px dashed var(--borde);
  border-radius: 12px;
}

/* ── Detalle del mes ── */
.titulo-lista { margin-bottom: 1rem; }

.lista-asignaciones {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.asig-fila {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 0.7rem 0.9rem;
}

.asig-franja {
  width: 5px;
  align-self: stretch;
  border-radius: 3px;
  flex-shrink: 0;
}

.asig-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}

.asig-principal {
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.asig-principal small { color: var(--texto-secundario); }

.asig-secundario { font-size: 0.72rem; color: var(--texto-secundario); }

/* ── Estados ── */
.estado-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  padding: 2.5rem 2rem;
  text-align: left;
  flex-wrap: wrap;
  color: var(--texto-secundario);
}

.estado-panel strong { color: var(--texto-principal); display: block; margin-bottom: 4px; }
.estado-panel p { margin: 0; font-size: 0.85rem; }
.estado-icono { font-size: 1.8rem; color: var(--sena-verde); }

@media (max-width: 992px) {
  .mi-programacion { padding: 1rem; }
  .dash-header { flex-direction: column; align-items: stretch; }
}
</style>

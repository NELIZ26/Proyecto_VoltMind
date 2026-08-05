/**
 * tituladasService.js
 * ───────────────────
 * Centraliza las llamadas HTTP del módulo de Fichas Tituladas y Asignación de
 * Ambientes hacia el backend FastAPI (/api/tituladas/*).
 *
 * El backend calcula horas, disponibilidad y valida los cruces (409); este
 * servicio solo transporta datos y normaliza los errores para la UI.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/** Helper genérico: ejecuta fetch y normaliza los errores del backend.
 *  Si el cuerpo es FormData (subida de archivos) el navegador arma solo
 *  el Content-Type multipart, por eso no se fuerza el encabezado JSON. */
async function solicitar(ruta, opciones = {}) {
  const esFormulario = opciones.body instanceof FormData;
  let response;
  try {
    response = await fetch(`${BASE_URL}/api/tituladas${ruta}`, {
      ...(esFormulario ? {} : { headers: { 'Content-Type': 'application/json' } }),
      ...opciones,
    });
  } catch {
    const err = new Error(
      'No se pudo conectar con el servidor VoltMind. Verifica que el backend esté en ejecución (uvicorn main:app --reload).'
    );
    err.esConexion = true;
    throw err;
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    // Los errores 422 de Pydantic llegan como lista; se toma el primer mensaje
    const detalle = Array.isArray(errorData.detail)
      ? errorData.detail[0]?.msg || 'Datos inválidos en la solicitud.'
      : errorData.detail;
    const err = new Error(detalle || `Error ${response.status} en el servidor.`);
    err.status = response.status;
    err.esConflicto = response.status === 409;
    throw err;
  }
  return await response.json();
}

export const tituladasService = {
  // ── FICHAS ─────────────────────────────────────────────────────────────
  getFichas({ buscar = null, jornada = null, sede = null } = {}) {
    const params = new URLSearchParams();
    if (buscar) params.set('buscar', buscar);
    if (jornada) params.set('jornada', jornada);
    if (sede) params.set('sede', sede);
    const query = params.toString() ? `?${params.toString()}` : '';
    return solicitar(`/fichas${query}`);
  },

  getFicha(fichaId) {
    return solicitar(`/fichas/${fichaId}`);
  },

  createFicha(datos) {
    return solicitar('/fichas', { method: 'POST', body: JSON.stringify(datos) });
  },

  updateDiagnostico(fichaId, competencias) {
    return solicitar(`/fichas/${fichaId}/diagnostico`, {
      method: 'PUT',
      body: JSON.stringify({ competencias }),
    });
  },

  // ── RESPALDO DE ARCHIVOS (Excel históricos de la ficha) ────────────────
  subirArchivoFicha(fichaId, archivo) {
    const formulario = new FormData();
    formulario.append('archivo', archivo);
    return solicitar(`/fichas/${fichaId}/archivos`, { method: 'POST', body: formulario });
  },

  /** URL directa de descarga (para usarla en un enlace <a>). */
  urlArchivoFicha(fichaId, archivoId) {
    return `${BASE_URL}/api/tituladas/fichas/${fichaId}/archivos/${archivoId}`;
  },

  deleteArchivoFicha(fichaId, archivoId) {
    return solicitar(`/fichas/${fichaId}/archivos/${archivoId}`, { method: 'DELETE' });
  },

  // ── CATÁLOGOS ──────────────────────────────────────────────────────────
  getInstructores() {
    return solicitar('/instructores');
  },

  getAmbientes() {
    return solicitar('/ambientes');
  },

  getProgramas() {
    return solicitar('/programas');
  },

  createPrograma(datos) {
    return solicitar('/programas', { method: 'POST', body: JSON.stringify(datos) });
  },

  // ── CALENDARIO DEL INSTRUCTOR ──────────────────────────────────────────
  getCalendarioInstructor({ correo = null, instructorId = null } = {}) {
    const params = new URLSearchParams();
    if (correo) params.set('correo', correo);
    if (instructorId) params.set('instructor_id', instructorId);
    return solicitar(`/calendario-instructor?${params.toString()}`);
  },

  // ── DISPONIBILIDAD (semáforo 🟢/🔴/⚪ de la pantalla de programación) ──
  getDisponibilidad({ fichaId, fechaInicio, fechaFin, excluirAsignacion = null }) {
    const params = new URLSearchParams({
      ficha_id: fichaId,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
    });
    if (excluirAsignacion) params.set('excluir_asignacion', excluirAsignacion);
    return solicitar(`/disponibilidad?${params.toString()}`);
  },

  // ── ASIGNACIONES ───────────────────────────────────────────────────────
  createAsignacion(datos) {
    return solicitar('/asignaciones', { method: 'POST', body: JSON.stringify(datos) });
  },

  updateAsignacion(id, datos) {
    return solicitar(`/asignaciones/${id}`, { method: 'PATCH', body: JSON.stringify(datos) });
  },

  deleteAsignacion(id) {
    return solicitar(`/asignaciones/${id}`, { method: 'DELETE' });
  },

  // ── INDICADORES ────────────────────────────────────────────────────────
  getIndicadores(mes = null) {
    const query = mes ? `?mes=${mes}` : '';
    return solicitar(`/indicadores${query}`);
  },
};

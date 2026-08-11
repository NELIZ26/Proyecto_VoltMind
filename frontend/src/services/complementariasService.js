/**
 * complementariasService.js
 * ─────────────────────────
 * Centraliza las llamadas HTTP del módulo de Fichas Complementarias
 * (solicitudes de formación complementaria) hacia el backend FastAPI
 * (/api/complementarias/*).
 *
 * El backend decide automáticamente entre Dataverse y el modo demo local,
 * por lo que este servicio no cambia cuando se conecte la base real.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/** Helper genérico: ejecuta fetch y normaliza los errores del backend. */
async function solicitar(ruta, opciones = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}/api/complementarias${ruta}`, {
      headers: { 'Content-Type': 'application/json' },
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

export const complementariasService = {
  // ── SOLICITUDES ────────────────────────────────────────────────────────
  getSolicitudes({ estado = null, municipio = null, jornada = null, instructor = null, buscar = null, correo = null } = {}) {
    const params = new URLSearchParams();
    if (estado) params.set('estado', estado);
    if (municipio) params.set('municipio', municipio);
    if (jornada) params.set('jornada', jornada);
    if (instructor) params.set('instructor', instructor);
    if (buscar) params.set('buscar', buscar);
    if (correo) params.set('correo', correo);
    const query = params.toString() ? `?${params.toString()}` : '';
    return solicitar(`/solicitudes${query}`);
  },

  createSolicitud(datos) {
    return solicitar('/solicitudes', { method: 'POST', body: JSON.stringify(datos) });
  },

  /**
   * Flujo del instructor: envía el formulario + archivos en multipart/form-data.
   * `archivos`: { matriz: File, plano: File, adicional?: File }.
   * No se fija Content-Type: el navegador agrega el boundary automáticamente.
   */
  createSolicitudConArchivos(datos, archivos) {
    const formData = new FormData();
    formData.append('datos', JSON.stringify(datos));
    formData.append('archivo_matriz', archivos.matriz);
    formData.append('archivo_plano', archivos.plano);
    if (archivos.adicional) formData.append('archivo_adicional', archivos.adicional);
    return solicitar('/solicitudes/con-archivos', { method: 'POST', body: formData, headers: {} });
  },

  /**
   * Flujo del administrador: adjunta (o reemplaza) el Excel de resultados de
   * aprendices inscritos de la ficha. Multipart: el navegador pone el boundary.
   */
  subirResultados(solicitudId, archivo) {
    const formData = new FormData();
    formData.append('archivo', archivo);
    return solicitar(`/solicitudes/${solicitudId}/archivos/resultados`, {
      method: 'POST',
      body: formData,
      headers: {},
    });
  },

  /** URL de un archivo subido (campo: matriz | plano | adicional | resultados).
   *  Con `inline: true` el navegador lo muestra (vista previa) en vez de descargarlo. */
  urlArchivo(solicitudId, campo, { inline = false } = {}) {
    const sufijo = inline ? '?inline=true' : '';
    return `${BASE_URL}/api/complementarias/solicitudes/${solicitudId}/archivos/${campo}${sufijo}`;
  },

  updateSolicitud(id, datos) {
    return solicitar(`/solicitudes/${id}`, { method: 'PATCH', body: JSON.stringify(datos) });
  },

  /** Reenvía al instructor el aviso de ficha Publicada (correo + campana). */
  reenviarAviso(id) {
    return solicitar(`/solicitudes/${id}/reenviar-aviso`, { method: 'POST' });
  },

  deleteSolicitud(id) {
    return solicitar(`/solicitudes/${id}`, { method: 'DELETE' });
  },

  // ── INDICADORES ────────────────────────────────────────────────────────
  getIndicadores() {
    return solicitar('/indicadores');
  },

  // ── NOTIFICACIONES (campana del panel admin) ──────────────────────────
  getNotificaciones({ destinatario = 'admin', soloNoLeidas = false } = {}) {
    const params = new URLSearchParams({ destinatario });
    if (soloNoLeidas) params.set('solo_no_leidas', 'true');
    return solicitar(`/notificaciones?${params.toString()}`);
  },

  marcarNotificacionLeida(id) {
    return solicitar(`/notificaciones/${id}/leida`, { method: 'PATCH' });
  },
};

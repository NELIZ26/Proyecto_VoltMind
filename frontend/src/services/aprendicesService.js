const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const aprendicesService = {
  async obtenerFichasRapido() {
    const response = await fetch(`${BASE_URL}/api/fichas/todas`);
    if (!response.ok) {
      throw new Error(`Error ${response.status}: No se pudieron cargar las fichas`);
    }
    return await response.json();
  },

  async obtenerTodosAprendices() {
    const response = await fetch(`${BASE_URL}/api/fichas/aprendices`);
    if (!response.ok) {
      throw new Error(`Error ${response.status}: No se pudieron cargar los aprendices`);
    }
    return await response.json();
  },

  async obtenerAprendicesPorFicha(numeroFicha) {
    const response = await fetch(`${BASE_URL}/api/fichas/${numeroFicha}/aprendices`);
    if (!response.ok) {
      if (response.status === 404) return []; // Si no existe o no tiene aprendices
      throw new Error(`Error ${response.status}: No se pudieron cargar los aprendices de la ficha ${numeroFicha}`);
    }
    return await response.json();
  },

  async buscarAprendicesGlobal(criterio) {
    const response = await fetch(`${BASE_URL}/api/fichas/busqueda?q=${encodeURIComponent(criterio)}`);
    if (!response.ok) {
      if (response.status === 404) return [];
      throw new Error(`Error ${response.status}: No se pudo buscar al aprendiz`);
    }
    return await response.json();
  },

  async crearAprendiz(datos) {
    const response = await fetch(`${BASE_URL}/api/fichas/aprendiz`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(datos)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const detalle = Array.isArray(errorData.detail)
        ? errorData.detail[0]?.msg || 'Error de validación.'
        : errorData.detail;
      const err = new Error(detalle || `Error ${response.status} en el servidor.`);
      err.status = response.status;
      throw err;
    }
    
    // Dataverse returns 204 no content on success generally, but we can parse if there's content.
    return response.status !== 204 ? await response.json() : null;
  }
};

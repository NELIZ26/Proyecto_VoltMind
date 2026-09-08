const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const ambientesService = {
  async getAll() {
    const response = await fetch(`${BASE_URL}/api/ambientes/`);
    if (!response.ok) throw new Error('Error al cargar ambientes');
    return await response.json();
  },

  async create(data) {
    const response = await fetch(`${BASE_URL}/api/ambientes/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Error al crear ambiente');
    return await response.json();
  },

  async update(id, data) {
    const response = await fetch(`${BASE_URL}/api/ambientes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Error al actualizar ambiente');
    return await response.json();
  },

  async delete(id) {
    const response = await fetch(`${BASE_URL}/api/ambientes/${id}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Error al eliminar ambiente');
    return await response.json();
  },

  async getCalendario(id) {
    const response = await fetch(`${BASE_URL}/api/tituladas/calendario-ambiente?ambiente_id=${id}`);
    if (!response.ok) throw new Error('Error al cargar calendario del ambiente');
    return await response.json();
  },

  async getSedes() {
    const response = await fetch(`${BASE_URL}/api/ambientes/sedes/lista`);
    if (!response.ok) throw new Error('Error al cargar sedes');
    return await response.json();
  },

  async createSede(data) {
    const response = await fetch(`${BASE_URL}/api/ambientes/sedes/crear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Error al crear sede');
    return await response.json();
  }
};

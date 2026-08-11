import { defineStore } from 'pinia';

const LOCAL_STORAGE_KEY = 'voltmind_programacion_data';

const defaultInstructores = [
  { id: 1, name: 'Carlos Díaz', specialty: 'Desarrollo de Software', type: 'Planta', hours: 154, maxHours: 160, statusLabel: 'Alta', progressColor: '#F59E0B', fichas: 4, available: '6 horas', discipline: 'software' },
  { id: 2, name: 'Luisa Bañól', specialty: 'Redes y Comunicaciones', type: 'Contratista', hours: 140, maxHours: 160, statusLabel: 'Medio', progressColor: '#10B981', fichas: 4, available: '20 horas', discipline: 'hardware' },
  { id: 3, name: 'Juan Pérez', specialty: 'Diseño Multimedia', type: 'Contratista', hours: 165, maxHours: 160, statusLabel: 'Límite', progressColor: '#EF4444', fichas: 1, available: '-5 horas', discipline: 'design' },
  { id: 4, name: 'Elena Martínez', specialty: 'Emprendimiento', type: 'Planta', hours: 80, maxHours: 160, statusLabel: 'Normal', progressColor: '#10B981', fichas: 10, available: '80 horas', discipline: 'language' },
];

const defaultAmbientes = [
  { id: 1, name: 'Ambiente 101', capacity: 30 },
  { id: 2, name: 'Ambiente 102', capacity: 35 },
  { id: 3, name: 'Ambiente 103', capacity: 20 },
  { id: 4, name: 'Ambiente 104', capacity: 25 },
  { id: 5, name: 'Ambiente Lego', capacity: 30 },
  { id: 6, name: 'Biblioteca', capacity: 50 },
  { id: 7, name: 'Bilingüismo', capacity: 20 },
  { id: 8, name: 'Cocina', capacity: 15 },
];

export const useProgramacionStore = defineStore('programacion', {
  state: () => ({
    instructores: [],
    ambientes: [],
    schedule: []
  }),
  actions: {
    initStore() {
      const storedData = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (storedData) {
        const parsed = JSON.parse(storedData);
        this.instructores = parsed.instructores || [];
        this.ambientes = parsed.ambientes || [];
        this.schedule = parsed.schedule || [];
      } else {
        this.instructores = [...defaultInstructores];
        this.ambientes = [...defaultAmbientes];
        this.schedule = [];
        this.saveToLocalStorage();
      }
    },
    
    saveToLocalStorage() {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify({
        instructores: this.instructores,
        ambientes: this.ambientes,
        schedule: this.schedule
      }));
    },

    assignSchedule({ instructorId, ambienteId, bloque, ficha }) {
      const instructor = this.instructores.find(i => i.id === instructorId);
      const ambiente = this.ambientes.find(a => a.id === ambienteId);
      
      if (!instructor || !ambiente) {
        return { success: false, error: 'Instructor o Ambiente no encontrado.' };
      }

      // Check if this environment is already booked at this block
      const roomConflict = this.schedule.find(s => s.ambienteId === ambienteId && s.bloque === bloque);
      if (roomConflict) {
        return {
          success: false,
          error: `El ambiente "${ambiente.name}" ya tiene asignada una clase en el horario "${bloque}" (Instructor: ${roomConflict.instructor}, Ficha: ${roomConflict.ficha}).`
        };
      }

      // Check if this instructor is already busy at this block
      const instructorConflict = this.schedule.find(s => s.instructorId === instructorId && s.bloque === bloque);
      if (instructorConflict) {
        const conflictingAmbiente = this.ambientes.find(a => a.id === instructorConflict.ambienteId);
        const roomName = conflictingAmbiente ? conflictingAmbiente.name : 'otro ambiente';
        return {
          success: false,
          error: `El instructor "${instructor.name}" ya está asignado al "${roomName}" en el horario "${bloque}" (Ficha: ${instructorConflict.ficha}).`
        };
      }

      // Add to schedule
      this.schedule.push({
        id: Date.now(),
        ambienteId,
        bloque,
        ficha,
        instructor: instructor.name, // Name saved for fast rendering
        instructorId,
        discipline: instructor.discipline || 'software'
      });

      // Update instructor hours and fichas
      instructor.hours += 3; // Adding 3 hours per block assigned
      instructor.fichas += 1; // Increment number of fichas assigned

      // Recalculate available hours string
      const remaining = instructor.maxHours - instructor.hours;
      instructor.available = `${remaining} horas`;

      // Update progress color based on usage
      const percent = (instructor.hours / instructor.maxHours) * 100;
      if (percent >= 100) {
        instructor.statusLabel = 'Límite';
        instructor.progressColor = '#EF4444';
      } else if (percent >= 90) {
        instructor.statusLabel = 'Alta';
        instructor.progressColor = '#F59E0B';
      } else if (percent >= 70) {
        instructor.statusLabel = 'Medio';
        instructor.progressColor = '#10B981';
      } else {
        instructor.statusLabel = 'Normal';
        instructor.progressColor = '#10B981';
      }

      this.saveToLocalStorage();
      return { success: true };
    }
  }
});

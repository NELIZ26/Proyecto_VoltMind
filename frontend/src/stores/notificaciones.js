// src/stores/notificaciones.js
// ─────────────────────────────────────────────────────────────────────────────
// Store de la campana de notificaciones del panel admin.
//
// ✔ SIN tiempo real: actualización por POLLING cada ~45 segundos contra
//   /api/complementarias/notificaciones (el backend decide Dataverse o demo).
// ✔ Cuando en un ciclo de polling aparecen notificaciones nuevas sin leer,
//   se muestra un aviso emergente con vue-toastification.
// ✔ Al abrir un aviso, la vista llama a marcarLeida(id) → PATCH en el backend.
// ─────────────────────────────────────────────────────────────────────────────
import { defineStore } from 'pinia';
import { useToast } from 'vue-toastification';
import { complementariasService } from '@/services/complementariasService';

const INTERVALO_POLLING_MS = 45000; // ~45 s, dentro del rango pedido (30–60 s)

export const useNotificacionesStore = defineStore('notificaciones', {
  state: () => ({
    notificaciones: [],
    cargando: false,
    // 'admin' (campana del panel) o el correo del instructor (su propia vista)
    destinatario: 'admin',
    // Internos del polling
    _timer: null,
    _idsConocidos: new Set(),
    _primeraCarga: true,
  }),

  getters: {
    noLeidas(state) {
      return state.notificaciones.filter((n) => !n.leida);
    },
    totalNoLeidas() {
      return this.noLeidas.length;
    },
  },

  actions: {
    /** Cambia el destinatario de la campana (admin ↔ correo del instructor). */
    configurarDestinatario(destinatario) {
      const nuevo = destinatario || 'admin';
      if (this.destinatario === nuevo) return;
      this.destinatario = nuevo;
      // Reinicio limpio: lo ya visto por el otro destinatario no debe generar toasts
      this.notificaciones = [];
      this._idsConocidos = new Set();
      this._primeraCarga = true;
      if (this._timer) this.cargar();
    },

    /** Trae las notificaciones del destinatario y avisa con un toast si llegaron nuevas. */
    async cargar() {
      this.cargando = true;
      try {
        const lista = await complementariasService.getNotificaciones({ destinatario: this.destinatario });
        // Detectar recién llegadas (no aplica en la primera carga de la sesión)
        if (!this._primeraCarga) {
          const toast = useToast();
          for (const n of lista) {
            if (!n.leida && !this._idsConocidos.has(n.id)) {
              toast.info(n.texto, { timeout: 8000 });
            }
          }
        }
        this._idsConocidos = new Set(lista.map((n) => n.id));
        this._primeraCarga = false;
        this.notificaciones = lista;
      } catch {
        // Silencioso: la campana no debe romper el panel si el backend está caído;
        // el siguiente ciclo de polling reintenta.
      } finally {
        this.cargando = false;
      }
    },

    /** Arranca el polling (idempotente: no crea dos timers). */
    iniciarPolling() {
      if (this._timer) return;
      this.cargar();
      this._timer = setInterval(() => this.cargar(), INTERVALO_POLLING_MS);
    },

    detenerPolling() {
      if (this._timer) {
        clearInterval(this._timer);
        this._timer = null;
      }
    },

    /** Marca como leída en el backend y actualiza la campana al instante. */
    async marcarLeida(id) {
      const notif = this.notificaciones.find((n) => n.id === id);
      if (!notif || notif.leida) return;
      notif.leida = true; // Optimista: el badge baja de inmediato
      try {
        await complementariasService.marcarNotificacionLeida(id);
      } catch {
        notif.leida = false; // Revertir si el backend falló
      }
    },
  },
});

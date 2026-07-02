import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useToast } from 'vue-toastification';

export const useKioskStore = defineStore('kiosk', () => {
  const toast = useToast();
  
  // Estado del kiosko: "ACTIVO", "BLOQUEADO", "MODO_SALIDA"
  const status = ref("ACTIVO");
  const ws = ref(null);
  
  // Variables sincronizadas
  const firmaRequerida = ref(null);
  const horaInicio = ref("--:--");
  const ultimaAsistencia = ref(null);

  const connectWebSocket = (ambiente_id = "402") => {
    if (ws.value) return; // Ya conectado
    
    // Conectarse al backend FastAPI
    ws.value = new WebSocket(`ws://127.0.0.1:8000/api/ws/ambiente/${ambiente_id}`);
    
    ws.value.onopen = () => {
      console.log(`[KioskStore] Conectado a tiempo real para el ambiente ${ambiente_id}`);
    };
    
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.tipo === "CAMBIO_ESTADO") {
          status.value = data.nuevo_estado;
          
          if (data.nuevo_estado === "BLOQUEADO") {
            toast.warning("🔒 El kiosko ha sido bloqueado por el instructor.");
          } else if (data.nuevo_estado === "ACTIVO") {
            toast.success("🔓 El kiosko está abierto para ingresos.");
          } else if (data.nuevo_estado === "MODO_SALIDA") {
            toast.info("🚪 Kiosko en modo salidas.");
          }
        }
        else if (data.tipo === "FORZAR_FIRMA") {
          firmaRequerida.value = {
            id: data.aprendiz_id,
            name: data.nombre_aprendiz,
            timestamp: Date.now()
          };
          toast.info(`✍️ Firma requerida para ${data.nombre_aprendiz}`);
        }
        else if (data.tipo === "SESION_INICIADA") {
          // Convertir ISO a formato local si es necesario, o usar directo
          let h = new Date(data.hora).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
          if (h === "Invalid Date") h = data.hora; // Fallback
          horaInicio.value = h;
          toast.info(`🏫 Sesión de clase iniciada a las ${h}`);
        }
        else if (data.tipo === "ASISTENCIA_REGISTRADA") {
          ultimaAsistencia.value = {
            documento: data.documento,
            nombre: data.nombre,
            accion: data.accion,
            hora: data.hora || new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
            timestamp: Date.now()
          };
          if (data.accion === "INGRESO") {
            toast.success(`✅ Ingreso registrado para el documento ${data.documento}`);
          }
        }
      } catch (e) {
        console.error("Error decodificando mensaje de WS:", e);
      }
    };
    
    ws.value.onclose = () => {
      console.warn("[KioskStore] WebSocket desconectado. Reconectando en 5s...");
      ws.value = null;
      setTimeout(() => connectWebSocket(ambiente_id), 5000);
    };
  };

  const clearFirma = () => {
    firmaRequerida.value = null;
  };

  return {
    status,
    firmaRequerida,
    horaInicio,
    ultimaAsistencia,
    connectWebSocket,
    clearFirma
  };
});

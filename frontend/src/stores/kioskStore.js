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

  // 🟢 CORRECCIÓN: Quitamos el "402" y lo dejamos dinámico
  const connectWebSocket = (ambiente_id = null) => {
    if (ws.value) return; // Ya conectado
    
    // Leemos el ID real desde la memoria si no se pasó por parámetro
    const idReal = ambiente_id || localStorage.getItem('kiosko_ambiente_id') || localStorage.getItem('ambienteActivoId');
    
    if (!idReal) {
      console.warn("⚠️ No se encontró un ID de ambiente configurado. El Kiosko no se puede conectar.");
      return;
    }

    // Conectarse al backend FastAPI
    ws.value = new WebSocket(`ws://127.0.0.1:8000/api/ws/ambiente/${idReal}`);
    
    ws.value.onopen = () => {
      console.log(`[KioskStore] Conectado a tiempo real para el ambiente ${idReal}`);
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
          let h = new Date(data.hora).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
          if (h === "Invalid Date") h = data.hora; 
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
        // 🟢 AQUÍ ESTÁ LA NUEVA REGLA: EL APAGADO AUTOMÁTICO
        else if (data.tipo === "SESION_FINALIZADA") {
          console.log("🛑 Orden de cierre recibida desde el Dashboard. Reiniciando Kiosco...");
          
          toast.info("El instructor ha finalizado la sesión. Bloqueando terminal...");
          
          // Limpiamos SOLO la memoria volátil de la clase (Respetando el ID del ambiente físico)
          localStorage.removeItem('sesionActivaId');
          localStorage.removeItem('isPowerOn');
          localStorage.removeItem('fichaActiva');
          localStorage.removeItem('salidaHabilitada');
          localStorage.removeItem('horaInicio');
          
          // Forzamos un reinicio de la aplicación tras 2.5 segundos
          setTimeout(() => {
            window.location.reload(); 
          }, 2500);
        }
      } catch (e) {
        console.error("Error decodificando mensaje de WS:", e);
      }
    };
    
    ws.value.onclose = () => {
      console.warn("[KioskStore] WebSocket desconectado. Reconectando en 5s...");
      ws.value = null;
      // Reintentamos la conexión usando el ID real que rescatamos al principio
      setTimeout(() => connectWebSocket(idReal), 5000);
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
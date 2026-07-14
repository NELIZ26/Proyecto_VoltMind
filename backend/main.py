# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import fichas, aprendices, sesiones, asistencia, usuarios, ws_kiosko

# ⏰ IMPORTACIÓN DEL PLANIFICADOR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Importaremos la función que se encargará del barrido masivo de los viernes
from services.reportes_service import obtener_rango_semana_actual

app = FastAPI(title="VoltMind API")

# Configurar CORS para el frontend (Vue 3 en localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de rutas existentes
app.include_router(fichas.router)
app.include_router(aprendices.router)
app.include_router(sesiones.router)
app.include_router(asistencia.router)
app.include_router(usuarios.router)
app.include_router(ws_kiosko.router)


# =================================================================
# ⏰ SUBSISTEMA DE TAREAS PROGRAMADAS (CRON JOBS - APSCHEDULER)
# =================================================================

scheduler = AsyncIOScheduler()

# Definición del Cron: Se dispara CADA VIERNES a las 18:00 horas (6:00 PM)
@scheduler.scheduled_job("cron", day_of_week="fri", hour=18, minute=0)
async def tarea_automatica_matriz_semanal():
    """
    Proceso automático en segundo plano que se ejecuta todos los viernes.
    Busca las sesiones de la semana y despacha las planillas oficiales.
    """
    print("⏰ [CRON VOLTMIND] Iniciando generación automática de la Matriz Semanal...")
    try:
        # En el próximo paso crearemos la función lógica de barrido dentro de reportes_service.py
        # para que busque las fichas activas de la semana y les envíe su respectivo PDF.
        pass
    except Exception as e:
        print(f"❌ Error en la ejecución del Cron de asistencia semanal: {e}")


# Evento de ciclo de vida de FastAPI para arrancar el reloj al encender el backend
@app.on_event("startup")
async def iniciar_planificador():
    scheduler.start()
    print("🚀 Sistema IoT VoltMind: Reloj interno (APScheduler) activado con éxito.")
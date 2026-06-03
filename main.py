# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import fichas, aprendices, sesiones

app = FastAPI(title="VoltMind API")

# Configurar CORS para el frontend (Vue 3 en localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fichas.router)
app.include_router(aprendices.router)
app.include_router(sesiones.router)
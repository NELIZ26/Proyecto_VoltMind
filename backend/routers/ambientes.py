from fastapi import APIRouter, HTTPException, Depends
from typing import List

from schemas.ambientes import AmbienteCreate, AmbienteUpdate
from services.ambientes_service import (
    get_all_ambientes,
    create_ambiente,
    update_ambiente,
    delete_ambiente
)

router = APIRouter(prefix="/api/ambientes", tags=["Ambientes"])

@router.get("/")
async def listar_ambientes():
    return await get_all_ambientes()

@router.post("/")
async def crear_ambiente(ambiente: AmbienteCreate):
    return await create_ambiente(ambiente)

@router.put("/{ambiente_id}")
async def editar_ambiente(ambiente_id: str, ambiente: AmbienteUpdate):
    return await update_ambiente(ambiente_id, ambiente)

@router.delete("/{ambiente_id}")
async def borrar_ambiente(ambiente_id: str):
    return await delete_ambiente(ambiente_id)

from schemas.ambientes import SedeCreate
from services.ambientes_service import get_all_sedes, create_sede

@router.get("/sedes/lista")
async def listar_sedes():
    return await get_all_sedes()

@router.post("/sedes/crear")
async def crear_sede(sede: SedeCreate):
    return await create_sede(sede)

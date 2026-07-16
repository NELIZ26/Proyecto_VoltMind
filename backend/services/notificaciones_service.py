# services/notificaciones_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Notificaciones internas de VoltMind (módulo de Fichas Complementarias).
#
# Caso de uso actual: cuando un instructor envía una solicitud de ficha
# complementaria, se crea una notificación para el administrador (dinamizador),
# quien la ve en la campana de la barra superior del panel admin.
#
# Funciona en DOS MODOS automáticos (mismo patrón que complementarias_service):
#   1. DATAVERSE : con credenciales en .env consulta la tabla real.
#   2. DEMO      : sin credenciales persiste en backend/data/notificaciones_demo.json.
#                  El contrato de la API es IDÉNTICO.
#
# ⚠️ La tabla de Dataverse aún NO existe. Plural OData ASUMIDO
# `cr6a3_notificacions`, configurable vía env (TABLA_NOTIFICACIONES).
# Verificar el plural real en Dataverse al crear la tabla.
# ─────────────────────────────────────────────────────────────────────────────
import os
import json
import uuid
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from fastapi import HTTPException

from services.dataverse import (
    cliente_dataverse,
    TENANT_ID,
    CLIENT_ID,
    CLIENT_SECRET,
    DATAVERSE_URL,
)

TABLA_NOTIFICACIONES = os.getenv("TABLA_NOTIFICACIONES", "cr6a3_notificacions")

# Mapeo campo API ↔ columna Dataverse (una sola fuente de verdad).
_CAMPOS_DV = {
    "destinatario": "cr6a3_destinatario",          # rol o correo: "admin", "instructor@sena..."
    "tipo": "cr6a3_tipo",                          # ej: "solicitud_ficha"
    "texto": "cr6a3_texto",                        # mensaje visible en la campana
    "ficha_relacionada": "cr6a3_ficha_relacionada",# id de la solicitud complementaria
    "leida": "cr6a3_leida",                        # booleano
    "fecha": "cr6a3_fecha",                        # ISO 8601 America/Bogota
}
_ID_DV = "cr6a3_notificacionid"

_RUTA_DATA = Path(__file__).resolve().parent.parent / "data"
_RUTA_DEMO = _RUTA_DATA / "notificaciones_demo.json"

# Serializa los ciclos cargar-modificar-guardar del modo demo
_demo_lock = asyncio.Lock()

_ZONA_BOGOTA = ZoneInfo("America/Bogota")


def dataverse_configurado() -> bool:
    """True si el .env tiene todas las credenciales necesarias de Dataverse."""
    return all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, DATAVERSE_URL])


# ─────────────────────────────────────────────────────────────────────────────
# MODO DEMO — Persistencia local en JSON
# ─────────────────────────────────────────────────────────────────────────────
def _cargar_db() -> dict:
    if not _RUTA_DEMO.exists():
        _RUTA_DATA.mkdir(parents=True, exist_ok=True)
        _RUTA_DEMO.write_text(json.dumps({"notificaciones": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(_RUTA_DEMO.read_text(encoding="utf-8"))


def _guardar_db(db: dict) -> None:
    _RUTA_DEMO.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DATAVERSE
# ─────────────────────────────────────────────────────────────────────────────
def _a_cuerpo_dataverse(datos: dict) -> dict:
    return {columna: datos[campo] for campo, columna in _CAMPOS_DV.items() if campo in datos}


def _desde_fila_dataverse(fila: dict) -> dict:
    resultado = {"id": fila.get(_ID_DV)}
    for campo, columna in _CAMPOS_DV.items():
        valor = fila.get(columna)
        if campo == "leida":
            valor = bool(valor)
        else:
            valor = valor or ""
        resultado[campo] = valor
    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# OPERACIONES
# ─────────────────────────────────────────────────────────────────────────────
async def crear_notificacion(
    destinatario: str,
    tipo: str,
    texto: str,
    ficha_relacionada: str = "",
) -> dict:
    """Inserta una notificación nueva (no leída, con fecha de Bogotá)."""
    nueva = {
        "destinatario": destinatario,
        "tipo": tipo,
        "texto": texto,
        "ficha_relacionada": ficha_relacionada,
        "leida": False,
        "fecha": datetime.now(_ZONA_BOGOTA).isoformat(timespec="seconds"),
    }

    if not dataverse_configurado():
        async with _demo_lock:
            db = _cargar_db()
            nueva["id"] = f"notif-{uuid.uuid4().hex[:8]}"
            db["notificaciones"].append(nueva)
            _guardar_db(db)
            return nueva

    # --- MODO DATAVERSE ---
    async with await cliente_dataverse() as client:
        res = await client.post(TABLA_NOTIFICACIONES, json=_a_cuerpo_dataverse(nueva))
        if res.status_code != 204:
            print("ERROR DATAVERSE CREAR NOTIFICACIÓN:", res.text)
            raise HTTPException(status_code=400, detail="No se pudo crear la notificación en Dataverse.")
        entity_url = res.headers.get("OData-EntityId", "")
        nueva["id"] = entity_url.split("(")[-1].replace(")", "") if "(" in entity_url else ""
        return nueva


async def listar_notificaciones(
    destinatario: str | None = None,
    solo_no_leidas: bool = False,
) -> list:
    """Notificaciones ordenadas de la más reciente a la más antigua."""
    if not dataverse_configurado():
        notificaciones = _cargar_db()["notificaciones"]
    else:
        # --- MODO DATAVERSE ---
        async with await cliente_dataverse() as client:
            columnas = ",".join([_ID_DV, *_CAMPOS_DV.values()])
            res = await client.get(f"{TABLA_NOTIFICACIONES}?$select={columnas}")
            if res.status_code != 200:
                print("ERROR DATAVERSE NOTIFICACIONES:", res.text)
                raise HTTPException(
                    status_code=res.status_code,
                    detail="Error al consultar las notificaciones en Dataverse.",
                )
            notificaciones = [_desde_fila_dataverse(f) for f in res.json().get("value", [])]

    # Filtros en memoria: mismo contrato en ambos modos y volumen bajo.
    if destinatario:
        # Insensible a mayúsculas: el destinatario puede ser un correo escrito a mano
        d = destinatario.lower()
        notificaciones = [n for n in notificaciones if (n.get("destinatario") or "").lower() == d]
    if solo_no_leidas:
        notificaciones = [n for n in notificaciones if not n.get("leida")]
    return sorted(notificaciones, key=lambda n: n.get("fecha") or "", reverse=True)


async def marcar_leida(notificacion_id: str) -> dict:
    """Marca una notificación como leída (PATCH al abrir el aviso)."""
    if not dataverse_configurado():
        async with _demo_lock:
            db = _cargar_db()
            for n in db["notificaciones"]:
                if n["id"] == notificacion_id:
                    n["leida"] = True
                    _guardar_db(db)
                    return n
            raise HTTPException(status_code=404, detail="La notificación no existe.")

    # --- MODO DATAVERSE ---
    async with await cliente_dataverse() as client:
        res = await client.patch(
            f"{TABLA_NOTIFICACIONES}({notificacion_id})",
            json={_CAMPOS_DV["leida"]: True},
        )
        if res.status_code != 204:
            raise HTTPException(status_code=400, detail="No se pudo marcar la notificación en Dataverse.")
        return {"id": notificacion_id, "leida": True}

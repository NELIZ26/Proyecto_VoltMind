import asyncio
import os
import sys

# Asegurar que el backend está en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from services.tituladas_service import listar_fichas

async def main():
    try:
        fichas = await listar_fichas()
        print(f"Éxito: {len(fichas)} fichas listadas.")
    except Exception as e:
        print(f"Error al listar fichas: {e}")

if __name__ == "__main__":
    asyncio.run(main())

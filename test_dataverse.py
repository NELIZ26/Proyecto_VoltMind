import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))
from dataverse import consultar_dataverse

async def main():
    try:
        res = await consultar_dataverse("cr6a3_asignacions?$top=1")
        print("Success with cr6a3_asignacions")
    except Exception as e:
        print(f"Failed cr6a3_asignacions: {e}")

    try:
        res = await consultar_dataverse("cr6a3_asignacioneses?$top=1")
        print("Success with cr6a3_asignacioneses")
    except Exception as e:
        print(f"Failed cr6a3_asignacioneses: {e}")
        
    try:
        res = await consultar_dataverse("cr6a3_asignaciones?$top=1")
        print("Success with cr6a3_asignaciones")
    except Exception as e:
        print(f"Failed cr6a3_asignaciones: {e}")

if __name__ == "__main__":
    asyncio.run(main())

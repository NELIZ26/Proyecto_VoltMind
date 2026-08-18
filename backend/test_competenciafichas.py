import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))
from dataverse import consultar_dataverse

async def main():
    try:
        # Ficha provided by user: 8adcbd3c-f997-f111-b8dc-7ced8da870b8
        res = await consultar_dataverse("cr6a3_competenciafichas?$filter=_cr6a3_fichaid_value eq '8adcbd3c-f997-f111-b8dc-7ced8da870b8'")
        print(res.get("value", [])[:1]) # Print the first item
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

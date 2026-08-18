import asyncio
import sys
sys.path.append('C:\\Users\\Ferney\\Desktop\\Proyecto_VoltMind\\backend')
from services.dataverse import consultar_dataverse

async def run():
    try:
        res = await consultar_dataverse('cr6a3_ambiente_formacions?$top=1&$expand=cr6a3_sede')
        if res.get('value'):
            import pprint
            pprint.pprint(res['value'][0].get('cr6a3_sede'))
        else:
            print("No ambientes found.")
    except Exception as e:
        print("Error:", e)

asyncio.run(run())

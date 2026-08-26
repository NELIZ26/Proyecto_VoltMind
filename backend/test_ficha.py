import asyncio
import sys
sys.path.append('C:\\Users\\Ferney\\Desktop\\Proyecto_VoltMind\\backend')
from dotenv import load_dotenv
load_dotenv('C:\\Users\\Ferney\\Desktop\\Proyecto_VoltMind\\backend\\.env')
from services.dataverse import consultar_dataverse
async def test():
    res = await consultar_dataverse('cr6a3_fichas')
    print(res.get('value', [])[0] if res.get('value') else 'Vacio')
asyncio.run(test())
import asyncio
import sys
sys.path.append('C:\\Users\\Ferney\\Desktop\\Proyecto_VoltMind\\backend')
from dotenv import load_dotenv
load_dotenv('C:\\Users\\Ferney\\Desktop\\Proyecto_VoltMind\\backend\\.env')
from services.tituladas_service import calendario_instructor
async def test():
    res = await calendario_instructor(instructor_id='62e41de6-fd94-f111-b8dc-7ced8da870b8')
    print(res)
asyncio.run(test())
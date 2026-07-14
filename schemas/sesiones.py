from typing import Optional
from pydantic import BaseModel

class SesionIniciadaData(BaseModel):
    ficha: str
    email: str
    ambiente_id: Optional[str] = None
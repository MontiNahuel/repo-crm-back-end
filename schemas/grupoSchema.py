from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from schemas.usuarioSchema import UsuarioBasico

class GrupoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class GrupoCreate(GrupoBase):
    pass

class GrupoResponse(GrupoBase):
    id: int
    creado_en: datetime
    miembros: List[UsuarioBasico] = []

    model_config = ConfigDict(from_attributes=True)

class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

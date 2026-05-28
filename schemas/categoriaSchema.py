from pydantic import BaseModel, ConfigDict
from typing import Optional

class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class CategoriaResponse(CategoriaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CategoriaResponseSimple(BaseModel):
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)
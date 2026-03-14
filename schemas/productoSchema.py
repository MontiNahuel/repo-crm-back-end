from pydantic import BaseModel
from typing import Optional

# DTO Base
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int = 0

# DTO para crear (hereda todo del base)
class ProductoCreate(ProductoBase):
    pass

# DTO para actualizar (hacemos que todos los campos sean opcionales)
class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None

# DTO de respuesta (incluye el ID generado por MySQL)
class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True  # Permite leer datos desde SQLAlchemy (reemplaza a orm_mode en Pydantic V2)
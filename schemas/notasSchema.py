from pydantic import BaseModel, field_validator
from typing import Optional

#---------DTO Para Notas de Clientes---------#

# DTO Base
class NotaClienteBase(BaseModel):
    cliente_id: int
    contenido: str

    #La forma PROFESIONAL: Evitar que manden "    " (puros espacios)
    @field_validator('contenido')
    @classmethod # En Pydantic V2 los validadores son classmethods
    def validar_contenido_vacio(cls, value: str):
        texto_limpio = value.strip() # Quita los espacios al principio y al final
        if not texto_limpio:
            raise ValueError("El contenido de la nota no puede estar vacío ni contener solo espacios.")
        return texto_limpio # Devolvemos el texto ya limpio sin espacios extra

# DTO para crear (hereda todo del base)
class NotaClienteCreate(NotaClienteBase):
    pass

class NotaClienteUpdate(NotaClienteBase):
    producto_id: Optional[int] = None
    contenido: Optional[str] = None

# DTO para eliminar (solo necesita el ID)
class NotaClienteDelete(BaseModel):
    cliente_id: int

# DTO de respuesta (incluye el ID generado por MySQL)
class NotaClienteResponse(NotaClienteBase):
    id: int
    class Config:
        from_attributes = True  # Permite leer datos desde SQLAlchemy (reemplaza a orm_mode en Pydantic V2)


#---------DTO Para Notas de Productos---------#

#DTO Base
class ProductoBase(BaseModel):
    producto_id: int
    contenido: str

# DTO para crear (hereda todo del base)
class NotaProductoCreate(ProductoBase):
    pass

class NotaProductoUpdate(ProductoBase):
    producto_id: Optional[int] = None
    contenido: Optional[str] = None

# DTO para eliminar (solo necesita el ID)
class NotaProductoDelete(BaseModel):
    producto_id: int

# DTO de respuesta (incluye el ID generado por MySQL)
class NotaProductoResponse(ProductoBase):
    id: int
    class Config:
        from_attributes = True  # Permite leer datos desde SQLAlchemy (reemplaza a orm_mode en Pydantic V2)


from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from schemas.usuarioSchema import UsuarioBasico

#---------DTO Para Notas de Clientes---------#

# --- BASE ---
# Solo lo que comparten TODOS los flujos (Crear, Leer, etc)
class NotaClienteBase(BaseModel):
    cliente_id: int
    contenido: str
    
    @field_validator('contenido')
    @classmethod
    def validar_contenido_vacio(cls, value: str):
        texto_limpio = value.strip()
        if not texto_limpio:
            raise ValueError("El contenido de la nota no puede estar vacío ni contener solo espacios.")
        return texto_limpio

# --- CREATE ---
# Lo que te manda Vue (Frontend) cuando el vendedor aprieta "Guardar"
class NotaClienteCreate(NotaClienteBase):
    pass 
    # OJO: Vue NO te manda ni la fecha ni el usuario_id. 
    # La fecha la pone la BD sola, y el usuario_id lo deberías sacar del Token de sesión en el endpoint.

# Si tu endpoint necesita validar el objeto completo antes de guardarlo en BD:
class NotaClienteCreateDB(NotaClienteCreate):
    usuario_id: int

# --- UPDATE ---
class NotaClienteUpdate(BaseModel):
    # Rompemos la herencia acá porque no queremos que actualicen el cliente_id.
    # Una nota pertenece a un cliente y punto.
    contenido: Optional[str] = None
    
    # NOTA BRUTAL: Tenías un 'producto_id' acá en tu código. 
    # Si fue un copy-paste, borralo. Si las notas llevan productos, agregalo a NotaClienteBase también.

# --- RESPONSE ---
# Lo que FastAPI le escupe a Vue para dibujar en la pantalla
class NotaClienteResponse(NotaClienteBase):
    id: int
    #usuario_id: int
    autor: UsuarioBasico
    fecha_creacion: datetime # ¡Acá entra la estrella del show!
    
    # Sintaxis moderna y correcta de Pydantic V2 (reemplaza a class Config)
    model_config = ConfigDict(from_attributes=True)


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


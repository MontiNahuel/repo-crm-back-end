from schemas.usuarioSchema import UsuarioBasico
from pydantic import BaseModel, ConfigDict
from typing import Optional
from models.enums import EstadoCliente
from datetime import datetime
from typing import List

# DTO Base
class ClienteBase(BaseModel):
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    estado: EstadoCliente = EstadoCliente.LEAD  # Valor por defecto al crear un cliente nuevo

# DTO para crear (hereda todo del base)
class ClienteCreate(ClienteBase):
    pass

class ClienteCreateDB(ClienteCreate):
    usuario_id: int

# DTO para actualizar (hacemos que todos los campos sean opcionales)
class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

# DTO de respuesta (incluye el ID generado por MySQL)
class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True  # Permite leer datos desde SQLAlchemy (reemplaza a orm_mode en Pydantic V2)

class ClienteResponseWithCount(BaseModel):
    cantidadClientes: int
    clientes: List[ClienteResponse]

class ClienteBasico(BaseModel):
    id: int
    nombre: str

class CambioClienteResponse(BaseModel):
    id: int
    cliente_id: int
    cambio: str
    usuario : UsuarioBasico
    cliente: ClienteBasico
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
    
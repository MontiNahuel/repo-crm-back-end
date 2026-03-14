from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# --- BASE ---
class TareaBase(BaseModel):
    titulo: str
    tipo: str = "personal" # Valor por defecto para el discriminador
    esta_completada: bool = False
    fecha_limite: Optional[datetime] = None

# --- CREATE ---
class TareaCreate(TareaBase):
    pass

class TareaCreateDB(TareaCreate):
    usuario_id: int

class TareaClienteCreate(TareaBase):
    cliente_id: int
    tipo: str = "cliente"

class TareaClienteCreateDB(TareaClienteCreate):
    usuario_id: int

# --- UPDATE (Aquí rompemos la herencia para que todo sea opcional) ---
class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    esta_completada: Optional[bool] = None
    fecha_limite: Optional[datetime] = None
    # No solemos actualizar el usuario_id ni el tipo una vez creada

class TareaClienteUpdate(TareaUpdate):
    cliente_id: Optional[int] = None

# --- READ (Los que usas en response_model) ---
class TareaRead(TareaBase):
    id: int
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes=True)

class TareaClienteRead(TareaRead):
    cliente_id: int
    # Aquí podrías anidar el ClienteBasico si quieres mostrar el nombre en el To-Do
    # cliente: Optional[ClienteBasico] = None 
    
    model_config = ConfigDict(from_attributes=True)
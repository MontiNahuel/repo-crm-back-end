from pydantic import BaseModel, EmailStr, ConfigDict
from models.enums import RolUsuario
from typing import Optional

class UsuarioCreate(BaseModel):
    email: EmailStr # EmailStr valida automáticamente que tenga un @ y un formato de correo
    password: str
    rol: RolUsuario
    nombre: str
    apellido: str

class UsuarioResponse(BaseModel):
    id: int
    email: str
    rol: RolUsuario
    es_activo: bool
    nombre: str
    apellido: str

    class Config:
        from_attributes = True # Permite leer objetos de SQLAlchemy

class UsuarioUpdate(BaseModel):
    is_active: Optional[bool] = None
    rol: Optional[RolUsuario] = None

class UsuarioAdminUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[RolUsuario] = None
    es_activo: Optional[bool] = None
    password: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UsuarioBasico(BaseModel):
    id: int
    email: str
    rol: RolUsuario
    nombre: str
    apellido: str
    
    model_config = ConfigDict(from_attributes=True)
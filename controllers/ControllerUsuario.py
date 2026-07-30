from typing import List
from schemas.usuarioSchema import LoginRequest, TokenResponse, UsuarioCreate, UsuarioResponse, RefreshTokenRequest
from core.security import crear_token_acceso, crear_refresh_token, verificar_refresh_token
from services.usuarioService import UsuarioService
from fastapi import Depends
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from fastapi import HTTPException
from core.dependencias import obtener_usuario_actual

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=UsuarioResponse, status_code=201)
def registrar_usuario(usuario_in: UsuarioCreate, servicio: UsuarioService = Depends()):
    return servicio.crear_usuario(usuario_in)


@router.post("/loginFinal", response_model=TokenResponse, status_code=200)
def loginFinal(credenciales: LoginRequest, servicio: UsuarioService = Depends()):
    usuario = servicio.autenticar_usuario(email = credenciales.email, password = credenciales.password)
    
    datos_token = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol.value
    }

    token_acceso = crear_token_acceso(datos_token)
    refresh_token = crear_refresh_token(datos_token)
    return TokenResponse(access_token=token_acceso, refresh_token=refresh_token, token_type="bearer")


@router.post("/login", response_model=TokenResponse, status_code=200)
def login(credenciales: OAuth2PasswordRequestForm = Depends(), servicio: UsuarioService = Depends()):
    usuario = servicio.autenticar_usuario(email = credenciales.username, password = credenciales.password)
    
    datos_token = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol.value,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido
    }

    token_acceso = crear_token_acceso(datos_token)
    refresh_token = crear_refresh_token(datos_token)
    return TokenResponse(access_token=token_acceso, refresh_token=refresh_token, token_type="bearer")


@router.post("/refresh", response_model=TokenResponse, status_code=200)
def refrescar_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Recibe un refresh_token válido y devuelve un nuevo par de tokens.
    Así el usuario no tiene que volver a loguearse cada 30 minutos.
    """
    # 1. Verificamos que el refresh token sea válido y extraemos el usuario_id
    usuario_id = verificar_refresh_token(body.refresh_token)
    
    # 2. Confirmamos que el usuario siga existiendo y esté activo
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario or not usuario.es_activo:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    
    # 3. Generamos un nuevo par de tokens frescos
    datos_token = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol.value,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido
    }
    
    nuevo_access = crear_token_acceso(datos_token)
    nuevo_refresh = crear_refresh_token(datos_token)
    
    return TokenResponse(access_token=nuevo_access, refresh_token=nuevo_refresh, token_type="bearer")


@router.get("/colaboradores", response_model=List[UsuarioResponse])
def listar_colaboradores(
    busqueda: str = None,
    servicio: UsuarioService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Retorna la lista de colaboradores activos del CRM.
    Permite filtrar opcionalmente por nombre, apellido o email.
    Útil para poblar el buscador de contactos (estilo Microsoft Teams) en el chat.
    """
    return servicio.obtener_directorio_colaboradores(busqueda=busqueda)



from schemas.usuarioSchema import LoginRequest, TokenResponse, UsuarioCreate, UsuarioResponse
from core.security import crear_token_acceso
from services.usuarioService import UsuarioService
from fastapi import Depends
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=UsuarioResponse, status_code=201)
def registrar_usuario(usuario_in: UsuarioCreate, servicio: UsuarioService = Depends()):
    return servicio.crear_usuario(usuario_in)


@router.post("/loginFinal", response_model=TokenResponse, status_code=200)
def loginFinal(credenciales: LoginRequest, servicio: UsuarioService = Depends()):
    usuario = servicio.autenticar_usuario(credenciales)
    
    datos_token = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol.value
    }

    token_acceso = crear_token_acceso(datos_token)
    return TokenResponse(access_token=token_acceso, token_type="bearer")


@router.post("/login", response_model=TokenResponse, status_code=200)
def login(credenciales: OAuth2PasswordRequestForm = Depends(), servicio: UsuarioService = Depends()):
    print("credenciales: ", credenciales)
    usuario = servicio.autenticar_usuario(email = credenciales.username, password = credenciales.password)
    
    datos_token = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol.value
    }

    token_acceso = crear_token_acceso(datos_token)
    return TokenResponse(access_token=token_acceso, token_type="bearer")


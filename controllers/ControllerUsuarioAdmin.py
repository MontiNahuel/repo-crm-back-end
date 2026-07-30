from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from models.usuario import Usuario
from schemas.usuarioSchema import UsuarioResponse, UsuarioAdminUpdate
from services.usuarioService import UsuarioService
from services.grupoService import GrupoService
from core.dependencias import requerir_rol_admin

router = APIRouter(
    prefix="/usuarios",
    tags=["Administración de Usuarios (ADMIN)"]
)

@router.get("/", response_model=List[UsuarioResponse])
def listar_todos_los_usuarios(
    skip: int = 0,
    limit: int = 100,
    servicio: UsuarioService = Depends(),
    _: Usuario = Depends(requerir_rol_admin)
):
    """
    Retorna la lista de todos los usuarios registrados en el sistema de forma paginada.
    Protegido: Solo accesible por usuarios con rol 'ADMIN'.
    """
    return servicio.obtener_todos_los_usuarios(skip=skip, limit=limit)


@router.patch("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    usuario_in: UsuarioAdminUpdate,
    servicio: UsuarioService = Depends(),
    grupo_service: GrupoService = Depends(),
    _: Usuario = Depends(requerir_rol_admin)
):
    """
    Actualiza parcialmente los datos, contraseña, rol o estado del usuario especificado.
    Protegido: Solo accesible por usuarios con rol 'ADMIN'.
    Desvincula automáticamente de grupos si se desactiva el usuario o cambia a un rol no comercial.
    """
    update_data = usuario_in.model_dump(exclude_unset=True)
    
    usuario_actualizado = await servicio.actualizar_usuario_por_admin(
        usuario_id=usuario_id, 
        datos=update_data, 
        grupo_service=grupo_service
    )
    if not usuario_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no encontrado o no se pudo actualizar"
        )
    return usuario_actualizado

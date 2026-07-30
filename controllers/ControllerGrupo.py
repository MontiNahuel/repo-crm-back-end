from fastapi import APIRouter, Depends, Body, status, HTTPException
from typing import List
from schemas.grupoSchema import GrupoCreate, GrupoResponse
from services.grupoService import GrupoService
from core.dependencias import obtener_usuario_actual, requerir_rol_admin, requerir_rol_supervisor_o_admin
from models.usuario import Usuario
from models.enums import RolUsuario

router = APIRouter(
    prefix="/grupos",
    tags=["Grupos de Trabajo"]
)

@router.post("/", response_model=GrupoResponse, status_code=status.HTTP_201_CREATED)
async def crear_grupo_trabajo(
    grupo_in: GrupoCreate,
    servicio: GrupoService = Depends(),
    _: Usuario = Depends(requerir_rol_admin)
):
    """
    Crea un nuevo grupo de trabajo (Team) en MySQL e inicializa
    su sala de chat en MongoDB. (Solo Administradores).
    """
    return await servicio.crear_grupo(grupo_in)

@router.get("/", response_model=List[GrupoResponse])
def listar_grupos_trabajo(
    skip: int = 0,
    limit: int = 100,
    servicio: GrupoService = Depends(),
    _: Usuario = Depends(requerir_rol_admin)
):
    """
    Lista todos los grupos de trabajo creados en el sistema. (Solo Administradores).
    """
    return servicio.obtener_todos_los_grupos(skip=skip, limit=limit)

@router.get("/mi-equipo", response_model=GrupoResponse)
def obtener_mi_equipo(
    servicio: GrupoService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtiene los detalles del grupo de trabajo y miembros del equipo
    al que pertenece el colaborador firmado actualmente.
    """
    if not usuario_actual.grupo_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No perteneces a ningún grupo de trabajo actualmente"
        )
    return servicio.obtener_grupo(usuario_actual.grupo_id)

@router.get("/{grupo_id}", response_model=GrupoResponse)
def obtener_grupo_por_id(
    grupo_id: int,
    servicio: GrupoService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtiene los detalles de un grupo de trabajo por su ID.
    Los miembros solo pueden ver su propio grupo, mientras que los admins ven cualquiera.
    """
    if usuario_actual.rol != RolUsuario.ADMIN and usuario_actual.grupo_id != grupo_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los detalles de este grupo de trabajo"
        )
    return servicio.obtener_grupo(grupo_id)

@router.post("/{grupo_id}/miembros", status_code=status.HTTP_200_OK)
async def asignar_colaborador_a_grupo(
    grupo_id: int,
    usuario_id: int = Body(embed=True),
    servicio: GrupoService = Depends(),
    usuario_actual: Usuario = Depends(requerir_rol_supervisor_o_admin)
):
    """
    Asigna un colaborador a un grupo de trabajo.
    Los administradores pueden asignar a cualquier grupo.
    Los supervisores solo pueden asignar a colaboradores a su propio grupo.
    """
    if usuario_actual.rol == RolUsuario.SUPERVISOR and usuario_actual.grupo_id != grupo_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Como supervisor, solo puedes gestionar miembros de tu propio grupo de trabajo."
        )
    return await servicio.asignar_miembro_a_grupo(grupo_id, usuario_id)

@router.delete("/{grupo_id}/miembros/{usuario_id}", status_code=status.HTTP_200_OK)
async def remover_colaborador_de_grupo(
    grupo_id: int,
    usuario_id: int,
    servicio: GrupoService = Depends(),
    usuario_actual: Usuario = Depends(requerir_rol_supervisor_o_admin)
):
    """
    Remueve un colaborador de un grupo de trabajo.
    Los administradores pueden remover de cualquier grupo.
    Los supervisores solo pueden remover a miembros de su propio grupo.
    """
    if usuario_actual.rol == RolUsuario.SUPERVISOR and usuario_actual.grupo_id != grupo_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Como supervisor, solo puedes gestionar miembros de tu propio grupo de trabajo."
        )
    return await servicio.remover_miembro_de_grupo(grupo_id, usuario_id)

@router.delete("/{grupo_id}", status_code=status.HTTP_200_OK)
async def eliminar_grupo_trabajo(
    grupo_id: int,
    servicio: GrupoService = Depends(),
    _: Usuario = Depends(requerir_rol_admin)
):
    """
    Elimina un grupo de trabajo.
    Sus miembros quedan libres (independientes) y su chat grupal se elimina de MongoDB. (Solo Administradores).
    """
    return await servicio.eliminar_grupo(grupo_id)

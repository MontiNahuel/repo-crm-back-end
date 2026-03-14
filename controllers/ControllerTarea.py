from fastapi import APIRouter, Depends, status
from typing import List, Union
from core.dependencias import obtener_usuario_actual
from models.usuario import Usuario
from schemas.tareaSchema import TareaCreate, TareaClienteCreate, TareaRead, TareaClienteRead, TareaUpdate
from services.tareaService import TareaService

router = APIRouter(prefix="/tareas", tags=["Tareas"])

@router.get("/mis-tareas", response_model=List[Union[TareaClienteRead, TareaRead]])
def listar_mis_tareas(
    skip: int = 0,
    limit: int = 100,
    pendientes_solo: bool = False,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: TareaService = Depends()
):
    return service.get_todo_list_personalizado(usuario_actual.id, skip, limit, pendientes_solo)

@router.post("/personal", response_model=TareaRead)
def crear_tarea_personal(
    tarea_in: TareaCreate,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: TareaService = Depends()
):
    return service.create_tarea_vendedor(usuario_actual.id, tarea_in)

@router.post("/cliente", response_model=TareaClienteRead)
def crear_tarea_cliente(
    tarea_in: TareaClienteCreate,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: TareaService = Depends()
):
    return service.create_tarea_cliente_vendedor(usuario_actual.id, tarea_in)

@router.put("/{tarea_id}/completar", response_model=TareaRead)
def completar_tarea(
    tarea_id: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: TareaService = Depends()
):
    return service.marcar_como_completada(tarea_id, usuario_actual.id)

@router.delete("/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(
    tarea_id: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: TareaService = Depends()
):
    return service.delete_tarea(tarea_id, usuario_actual.id)

@router.patch("/{tarea_id}", response_model=TareaRead)
def actualizar_tarea(
    tarea_id: int,
    tarea_in: TareaUpdate,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: TareaService = Depends()
):
    return service.update_tarea(tarea_id, usuario_actual.id, tarea_in)

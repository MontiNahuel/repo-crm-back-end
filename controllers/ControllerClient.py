from fastapi import APIRouter, Depends, Body
from typing import List
from schemas.clienteSchema import ClienteCreate, ClienteResponse, CambioClienteResponse, ClienteResponseWithCount
from services.clienteService import ClienteService
from core.dependencias import obtener_usuario_actual, requerir_rol_admin
from models.usuario import Usuario
# Definimos el router (El equivalente a @RestController y @RequestMapping)
router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

@router.post("/", response_model=ClienteResponse, status_code=201)
def crear_cliente(cliente_in: ClienteCreate, servicio: ClienteService = Depends(), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    # Usamos nuestro repositorio instanciado para crear el cliente
    nuevo_cliente = servicio.crear_cliente(cliente_in, usuario_id=usuario_actual.id)
    return nuevo_cliente

@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(skip: int = 0, limit: int = 100, servicio: ClienteService = Depends(), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    # Obtenemos todos los clientes con paginación básica
    clientes = servicio.obtener_clientes(skip=skip, limit=limit)
    return clientes

@router.get("/mis-clientes", response_model=ClienteResponseWithCount)
def obtener_clientes_por_usuario(
    skip: int = 0, 
    limit: int = 100, 
    busqueda: str = None, 
    filtroEstado: str = None,
    orden: str = None,
    servicio: ClienteService = Depends(), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
    ):
    clientes = servicio.obtener_clientes_por_usuario(usuario_actual.id, skip=skip, limit=limit, busqueda=busqueda, filtroEstado=filtroEstado, orden=orden)
    return clientes

@router.get("/cambios-clientes", response_model=List[CambioClienteResponse])
def obtener_cambiosClientes(
    skip: int = 0, 
    limit: int = 100, 
    servicio: ClienteService = Depends(), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
    ):
    return servicio.obtener_cambiosClientes(usuario_actual.id, skip=skip, limit=limit)

@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int, servicio: ClienteService = Depends()):
    return servicio.obtener_cliente(cliente_id)

@router.put("/{cliente_id}/estado", response_model=ClienteResponse)
def cambiar_estado_cliente(cliente_id: int, estado: str = Body(embed=True), servicio: ClienteService = Depends(), usuario_admin: Usuario = Depends(requerir_rol_admin)):
    return servicio.cambiar_estado_cliente(cliente_id, estado, usuario_admin.id)

@router.get("/{cliente_id}/historial", response_model=List[CambioClienteResponse])
def ver_historial_cliente(
    cliente_id: int,
    servicio: ClienteService = Depends(),
    _ : Usuario = Depends(obtener_usuario_actual) 
):
    return servicio.obtener_historial_cliente(cliente_id)

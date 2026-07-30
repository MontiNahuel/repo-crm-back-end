from fastapi import APIRouter, Depends, Body, status
from typing import List
from schemas.clienteSchema import ClienteCreate, ClienteResponse, CambioClienteResponse, ClienteResponseWithCount, ClienteUpdate
from services.clienteService import ClienteService
from services.aiService import AiService
from repositories.RepositoryResumenIa import RepositoryResumenIa
from core.dependencias import obtener_usuario_actual, requerir_rol_admin
from models.usuario import Usuario
from models.enums import EstadoCliente

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
    clientes = servicio.obtener_clientes_por_usuario(usuario_actual, skip=skip, limit=limit, busqueda=busqueda, filtroEstado=filtroEstado, orden=orden)
    return clientes

@router.get("/pipeline", response_model=dict[str, List[dict]])
def obtener_pipeline_clientes(
    servicio: ClienteService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Retorna los clientes agrupados por su estado para renderizar un tablero Kanban."""
    return servicio.obtener_pipeline_clientes(usuario_actual)

@router.get("/cambios-clientes", response_model=List[CambioClienteResponse])
def obtener_cambiosClientes(
    skip: int = 0, 
    limit: int = 100, 
    servicio: ClienteService = Depends(), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
    ):
    return servicio.obtener_cambiosClientes(usuario_actual.id, skip=skip, limit=limit)

@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(
    cliente_id: int, 
    servicio: ClienteService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.obtener_cliente(cliente_id)

@router.patch("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_id: int,
    cliente_in: ClienteUpdate,
    servicio: ClienteService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Actualiza nombre, email o teléfono de un cliente."""
    return servicio.actualizar_cliente(cliente_id, cliente_in)

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(
    cliente_id: int,
    servicio: ClienteService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Elimina un cliente y sus datos asociados."""
    servicio.eliminar_cliente(cliente_id)

@router.put("/{cliente_id}/estado", response_model=ClienteResponse)
def cambiar_estado_cliente(cliente_id: int, estado: EstadoCliente = Body(embed=True), servicio: ClienteService = Depends(), usuario_admin: Usuario = Depends(requerir_rol_admin)):
    return servicio.cambiar_estado_cliente(cliente_id, estado, usuario_admin.id)

@router.get("/{cliente_id}/historial", response_model=List[CambioClienteResponse])
def ver_historial_cliente(
    cliente_id: int,
    servicio: ClienteService = Depends(),
    _: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.obtener_historial_cliente(cliente_id)

@router.get("/{cliente_id}/resumen-ia")
async def obtener_resumen_cliente_ia(
    cliente_id: int,
    servicio: ClienteService = Depends(),
    repo_mongo: RepositoryResumenIa = Depends(),
    _: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtiene el último resumen ejecutivo de IA guardado para este cliente en MongoDB.
    Si no existe ninguno, devuelve {"resumen": null}.
    """
    return await servicio.obtener_resumen_ia_guardado(cliente_id, repo_mongo)

@router.post("/{cliente_id}/resumen-ia")
async def generar_y_guardar_resumen_ia(
    cliente_id: int,
    servicio: ClienteService = Depends(),
    ai_servicio: AiService = Depends(),
    repo_mongo: RepositoryResumenIa = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Fuerza la generación de un nuevo resumen ejecutivo utilizando Gemini AI
    y lo almacena permanentemente en MongoDB.
    """
    return await servicio.generar_y_guardar_resumen_ia(cliente_id, usuario_actual, ai_servicio, repo_mongo)

@router.get("/{cliente_id}/resumen-ia/historial")
async def ver_historial_resumenes_ia(
    cliente_id: int,
    servicio: ClienteService = Depends(),
    repo_mongo: RepositoryResumenIa = Depends(),
    _: Usuario = Depends(obtener_usuario_actual)
):
    """
    Retorna la lista histórica de todos los resúmenes ejecutivos guardados
    para este cliente en MongoDB, del más nuevo al más antiguo.
    """
    return await servicio.obtener_historial_resumenes_ia(cliente_id, repo_mongo)

from fastapi import Depends, HTTPException
from models.enums import EstadoCliente
from repositories.RepositoryClient import ClienteRepository
from schemas.clienteSchema import ClienteCreateDB
class ClienteService:
    # 1. Inyectamos el Repositorio (FastAPI se encarga de pasarle la DB por detrás)
    def __init__(self, repo: ClienteRepository = Depends()):
        self.repo = repo

        self.transiciones_permitidas = {
            EstadoCliente.LEAD: [EstadoCliente.ACTIVO, EstadoCliente.PERDIDO],
            EstadoCliente.ACTIVO: [EstadoCliente.INACTIVO, EstadoCliente.PERDIDO],
            EstadoCliente.INACTIVO: [EstadoCliente.ACTIVO, EstadoCliente.PERDIDO],
            EstadoCliente.PERDIDO: [EstadoCliente.LEAD] # Si años después vuelve a consultar
        }

    def obtener_clientes(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip=skip, limit=limit)

    def obtener_cliente(self, cliente_id: int):
        cliente = self.repo.get(id=cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return cliente
    
    def crear_cliente(self, cliente_in, usuario_id: int):
        # Aquí podríamos agregar lógica de negocio, validaciones, etc.
        cliente_para_db = ClienteCreateDB(
            **cliente_in.model_dump(), 
            usuario_id=usuario_id
        )
        return self.repo.create(obj_in=cliente_para_db)
    
    def cambiar_estado_cliente(self, cliente_id: int, nuevo_estado: EstadoCliente, usuario_id: int):
        cliente = self.obtener_cliente(cliente_id)
        estado_actual = cliente.estado
        
        if nuevo_estado not in self.transiciones_permitidas[estado_actual]:
            raise HTTPException(
                status_code=400,
                detail=f"Transición no permitida de {estado_actual} a {nuevo_estado}"
            )
        return self.repo.update_estado_con_auditoria(
            cliente=cliente, 
            nuevo_estado=nuevo_estado, 
            usuario_id=usuario_id
        )
    
    def obtener_historial_cliente(self, cliente_id: int):
        """Obtiene el historial de cambios de un cliente."""
        cliente = self.obtener_cliente(cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return self.repo.obtener_historial(cliente_id)

    def obtener_cambiosClientes(self, usuario_id: int, skip: int = 0, limit: int = 100):
        return self.repo.obtener_cambiosClientes(usuario_id, skip=skip, limit=limit)

    def obtener_clientes_por_usuario(
        self, 
        usuario_id: int, 
        skip: int = 0, 
        limit: int = 100, 
        busqueda: str = None,
        filtroEstado: str = None,
        orden: str = None
        ):
        cantidadClientes, clientes = self.repo.obtener_clientes_por_id_usuario(
            usuario_id, 
            skip=skip, 
            limit=limit, 
            busqueda=busqueda, 
            filtroEstado=filtroEstado, 
            orden=orden
            )
        return {"cantidadClientes": cantidadClientes, "clientes": clientes}
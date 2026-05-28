from fastapi import Depends, HTTPException
from models.enums import EstadoCliente
from repositories.RepositoryClient import ClienteRepository
from schemas.clienteSchema import ClienteCreateDB, ClienteUpdate
from core.notifier import emitir_evento
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
        nuevo_cliente = self.repo.create(obj_in=cliente_para_db)
        
        # Emitimos evento en tiempo real
        emitir_evento("cliente_creado", {
            "id": nuevo_cliente.id,
            "nombre": nuevo_cliente.nombre,
            "estado": nuevo_cliente.estado.value,
            "usuario_id": usuario_id
        })
        
        return nuevo_cliente
    
    def cambiar_estado_cliente(self, cliente_id: int, nuevo_estado: EstadoCliente, usuario_id: int):
        # Aseguramos que sea una instancia del Enum para evitar excepciones de tipo string
        if isinstance(nuevo_estado, str):
            try:
                nuevo_estado = EstadoCliente(nuevo_estado)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estado inválido: {nuevo_estado}"
                )

        cliente = self.obtener_cliente(cliente_id)
        estado_anterior = cliente.estado
        
        if nuevo_estado not in self.transiciones_permitidas[estado_anterior]:
            raise HTTPException(
                status_code=400,
                detail=f"Transición no permitida de {estado_anterior} a {nuevo_estado}"
            )
            
        cliente_actualizado = self.repo.update_estado_con_auditoria(
            cliente=cliente, 
            nuevo_estado=nuevo_estado, 
            usuario_id=usuario_id
        )
        
        # Emitimos evento en tiempo real con datos de auditoría útiles
        emitir_evento("estado_cliente_cambiado", {
            "cliente_id": cliente_id,
            "nombre": cliente.nombre,
            "estado_anterior": estado_anterior.value,
            "nuevo_estado": nuevo_estado.value,
            "usuario_id": usuario_id
        })
        
        return cliente_actualizado
    
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

    def actualizar_cliente(self, cliente_id: int, cliente_in: ClienteUpdate):
        """Actualiza los campos de un cliente existente."""
        self.obtener_cliente(cliente_id)  # Valida que exista (lanza 404)
        update_data = cliente_in.model_dump(exclude_unset=True)
        return self.repo.update(cliente_id, update_data)

    def eliminar_cliente(self, cliente_id: int):
        """Elimina un cliente y todos sus datos asociados."""
        self.obtener_cliente(cliente_id)  # Valida que exista
        return self.repo.delete(cliente_id)

    def obtener_pipeline_clientes(self, usuario_id: int):
        """
        Obtiene los clientes del vendedor agrupados por estado
        para renderizar un Kanban Board visual de forma rápida.
        """
        # Obtenemos los clientes sin paginación para el Kanban completo
        _, clientes = self.repo.obtener_clientes_por_id_usuario(
            usuario_id=usuario_id,
            skip=0,
            limit=1000  # Límite alto para traer el pipeline completo
        )
        
        # Estructuramos el pipeline inicializado en listas vacías
        pipeline = {
            EstadoCliente.LEAD.value: [],
            EstadoCliente.ACTIVO.value: [],
            EstadoCliente.INACTIVO.value: [],
            EstadoCliente.PERDIDO.value: []
        }
        
        for c in clientes:
            estado_str = c.estado.value if hasattr(c.estado, 'value') else c.estado
            if estado_str in pipeline:
                pipeline[estado_str].append({
                    "id": c.id,
                    "nombre": c.nombre,
                    "email": c.email,
                    "telefono": c.telefono,
                    "creado_en": c.creado_en.isoformat() if hasattr(c.creado_en, 'isoformat') else str(c.creado_en)
                })
                
        return pipeline
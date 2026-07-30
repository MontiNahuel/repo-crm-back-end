from fastapi import Depends, HTTPException
from models.enums import EstadoCliente
from repositories.RepositoryClient import ClienteRepository
from schemas.clienteSchema import ClienteCreateDB, ClienteUpdate
from core.notifier import emitir_evento
from models.usuario import Usuario
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
        usuario_actual: Usuario, 
        skip: int = 0, 
        limit: int = 100, 
        busqueda: str = None,
        filtroEstado: str = None,
        orden: str = None
        ):
        cantidadClientes, clientes = self.repo.obtener_clientes_por_visibilidad(
            usuario=usuario_actual, 
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

    def obtener_pipeline_clientes(self, usuario_actual: Usuario):
        """
        Obtiene los clientes del vendedor (o de su grupo) agrupados por estado
        para renderizar un Kanban Board visual de forma rápida.
        """
        # Obtenemos los clientes sin paginación para el Kanban completo aplicando visibilidad
        _, clientes = self.repo.obtener_clientes_por_visibilidad(
            usuario=usuario_actual,
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

    async def obtener_resumen_ia_guardado(self, cliente_id: int, repo_mongo) -> dict:
        """
        Retorna el último resumen ejecutivo de IA guardado en MongoDB para este cliente.
        """
        # Validamos que el cliente exista en SQL
        self.obtener_cliente(cliente_id)
        
        doc = await repo_mongo.obtener_ultimo_resumen(cliente_id)
        if not doc:
            return {"resumen": None}
            
        return {
            "id": doc["id"],
            "cliente_id": doc["cliente_id"],
            "resumen": doc["resumen"],
            "fecha": doc["fecha"],
            "solicitante": doc["solicitante"]
        }

    async def generar_y_guardar_resumen_ia(self, cliente_id: int, usuario_actual, ai_service, repo_mongo) -> dict:
        """
        Fuerza la generación de un nuevo resumen en Gemini y lo almacena en MongoDB
        junto con los datos completos del solicitante denormalizados.
        """
        # 1. Buscamos el cliente (lanza 404 si no existe)
        cliente = self.obtener_cliente(cliente_id)

        # 2. Formateamos las notas de forma segura
        notas_list = []
        for nota in cliente.notas:
            autor_nombre = "Sistema"
            if nota.autor:
                autor_nombre = f"{nota.autor.nombre} {nota.autor.apellido}"
            
            notas_list.append({
                "autor": autor_nombre,
                "contenido": nota.contenido,
                "fecha": nota.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if hasattr(nota.fecha_creacion, "strftime") else str(nota.fecha_creacion)
            })

        # 3. Formateamos las tareas de forma segura
        tareas_list = []
        for tarea in cliente.tareas:
            fecha_limite_str = None
            if tarea.fecha_limite:
                fecha_limite_str = tarea.fecha_limite.strftime("%Y-%m-%d %H:%M:%S") if hasattr(tarea.fecha_limite, "strftime") else str(tarea.fecha_limite)
                
            tareas_list.append({
                "titulo": tarea.titulo,
                "completada": tarea.esta_completada,
                "fecha_limite": fecha_limite_str
            })

        # 4. Formateamos el historial de Kanban
        historial_list = []
        for cambio in cliente.historial_cambios:
            fecha_cambio_str = cambio.fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(cambio.fecha, "strftime") else str(cambio.fecha)
            
            historial_list.append({
                "descripcion": cambio.cambio,
                "fecha": fecha_cambio_str
            })

        # 5. Consolidamos el payload de entrada para la IA
        cliente_data = {
            "nombre": cliente.nombre,
            "email": cliente.email,
            "telefono": cliente.telefono,
            "estado": cliente.estado.value if hasattr(cliente.estado, "value") else str(cliente.estado),
            "notas": notas_list,
            "tareas": tareas_list,
            "historial": historial_list
        }

        # 6. Generamos el prompt y respuesta de Gemini
        resumen_markdown = ai_service.generar_resumen_cliente(cliente_data)
        
        # 7. Preparamos los datos del solicitante denormalizados
        solicitante = {
            "user_id": usuario_actual.id,
            "nombre": usuario_actual.nombre,
            "apellido": usuario_actual.apellido if hasattr(usuario_actual, "apellido") else ""
        }
        
        # 8. Persistimos en MongoDB
        doc = await repo_mongo.guardar_resumen(cliente.id, resumen_markdown, solicitante)
        
        # 9. Emitimos evento en tiempo real para alertar que hay un nuevo resumen disponible
        emitir_evento("resumen_ia_creado", {
            "cliente_id": cliente.id,
            "nombre_cliente": cliente.nombre,
            "solicitante": f"{solicitante['nombre']} {solicitante['apellido']}".strip(),
            "fecha": doc["fecha"].isoformat() if hasattr(doc["fecha"], "isoformat") else str(doc["fecha"])
        })
        
        return {
            "id": doc["id"],
            "cliente_id": cliente.id,
            "nombre": cliente.nombre,
            "resumen": resumen_markdown,
            "fecha": doc["fecha"].isoformat() if hasattr(doc["fecha"], "isoformat") else str(doc["fecha"]),
            "solicitante": doc["solicitante"]
        }

    async def obtener_historial_resumenes_ia(self, cliente_id: int, repo_mongo) -> list:
        """
        Retorna la lista de todos los resúmenes ejecutivos guardados en MongoDB para este cliente.
        """
        # Validamos que el cliente exista en SQL
        self.obtener_cliente(cliente_id)
        
        resumenes = await repo_mongo.obtener_historial_resumenes(cliente_id)
        
        # Limpiamos el campo interno _id para evitar problemas de serialización en FastAPI
        for r in resumenes:
            if "_id" in r:
                del r["_id"]
                
        return resumenes
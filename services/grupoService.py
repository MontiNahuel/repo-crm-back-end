from fastapi import Depends, HTTPException, status
from repositories.RepositoryGrupo import GrupoRepository
from repositories.RepositoryChat import RepositoryChat
from schemas.grupoSchema import GrupoCreate, GrupoUpdate
from models.usuario import Usuario
from core.notifier import emitir_evento

class GrupoService:
    def __init__(
        self,
        repo_grupo: GrupoRepository = Depends(),
        repo_chat: RepositoryChat = Depends()
    ):
        self.repo_grupo = repo_grupo
        self.repo_chat = repo_chat

    async def crear_grupo(self, grupo_in: GrupoCreate) -> dict:
        """
        Crea un nuevo grupo de trabajo en MySQL y automáticamente inicializa
        su correspondiente canal de chat grupal en MongoDB.
        """
        # Validar si el nombre ya existe en MySQL
        existe = self.repo_grupo.obtener_por_nombre(grupo_in.nombre)
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un grupo de trabajo con el nombre '{grupo_in.nombre}'"
            )
            
        # 1. Crear en MySQL
        grupo = self.repo_grupo.create(grupo_in)
        
        # 2. Inicializar el Chat Grupal en MongoDB vinculado por 'grupo_id'
        chat_doc = await self.repo_chat.create_group_conversation(
            name=grupo.nombre,
            participants=[],
            grupo_id=grupo.id
        )
        
        return {
            "id": grupo.id,
            "nombre": grupo.nombre,
            "descripcion": grupo.descripcion,
            "creado_en": grupo.creado_en,
            "chat_conversation_id": chat_doc["id"],
            "miembros": []
        }

    def obtener_grupo(self, grupo_id: int):
        """Obtiene un grupo de trabajo junto con sus miembros cargados."""
        grupo = self.repo_grupo.obtener_con_miembros(grupo_id)
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grupo de trabajo con ID {grupo_id} no encontrado"
            )
        return grupo

    def obtener_todos_los_grupos(self, skip: int = 0, limit: int = 100):
        """Lista todos los grupos de trabajo."""
        return self.repo_grupo.get_all(skip=skip, limit=limit)

    async def asignar_miembro_a_grupo(self, grupo_id: int, usuario_id: int) -> dict:
        """
        Asigna un colaborador a un grupo de trabajo en MySQL y sincroniza
        su participación en el chat grupal de MongoDB.
        """
        # 1. Validamos que el grupo exista
        grupo = self.obtener_grupo(grupo_id)
        
        # 2. Asignamos en MySQL
        usuario = self.repo_grupo.asignar_miembro(grupo_id, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Colaborador con ID {usuario_id} no encontrado"
            )
            
        # 3. Formateamos los datos del usuario para MongoDB
        user_mongo_dict = {
            "user_id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "rol": usuario.rol.value if hasattr(usuario.rol, "value") else str(usuario.rol)
        }
        
        # 4. Sincronizamos en MongoDB (Añadimos al set de participantes de forma atómica)
        await self.repo_chat.add_participant_to_group_conversation(grupo_id, user_mongo_dict)
        
        # 5. Emitir evento por sockets en tiempo real
        emitir_evento("miembro_grupo_asignado", {
            "grupo_id": grupo_id,
            "nombre_grupo": grupo.nombre,
            "usuario_id": usuario.id,
            "nombre_completo": f"{usuario.nombre} {usuario.apellido}".strip()
        })
        
        return {
            "mensaje": f"Colaborador '{usuario.nombre} {usuario.apellido}' asignado al grupo '{grupo.nombre}' con éxito",
            "grupo_id": grupo_id,
            "usuario": user_mongo_dict
        }

    async def remover_miembro_de_grupo(self, grupo_id: int, usuario_id: int) -> dict:
        """
        Remueve a un colaborador de su grupo de trabajo (pone grupo_id en NULL)
        y lo retira del chat de equipo en MongoDB de forma síncrona.
        """
        # 1. Validamos que el grupo exista
        grupo = self.obtener_grupo(grupo_id)
        
        # 2. Removemos en MySQL
        usuario = self.repo_grupo.remover_miembro(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Colaborador con ID {usuario_id} no encontrado"
            )
            
        # 3. Sincronizamos en MongoDB (Retiramos de la lista de participantes de forma atómica)
        await self.repo_chat.remove_participant_from_group_conversation(grupo_id, usuario_id)
        
        # 4. Emitir evento por sockets en tiempo real
        emitir_evento("miembro_grupo_removido", {
            "grupo_id": grupo_id,
            "nombre_grupo": grupo.nombre,
            "usuario_id": usuario_id,
            "nombre_completo": f"{usuario.nombre} {usuario.apellido}".strip()
        })
        
        return {
            "mensaje": f"Colaborador '{usuario.nombre} {usuario.apellido}' removido del grupo '{grupo.nombre}' con éxito",
            "grupo_id": grupo_id,
            "usuario_id": usuario_id
        }

    async def eliminar_grupo(self, grupo_id: int) -> dict:
        """
        Elimina un grupo de trabajo en MySQL (dejando a sus miembros independientes con grupo_id=NULL)
        y remueve la sala de chat y los buckets de mensajes en MongoDB.
        """
        # 1. Buscamos el grupo
        grupo = self.obtener_grupo(grupo_id)
        
        # 2. Eliminamos en MySQL (el ForeignKey ondelete="SET NULL" se encarga de desasociar miembros)
        self.repo_grupo.delete(grupo_id)
        
        # 3. Limpieza total en MongoDB (Evitamos dejar basura huérfana en NoSQL)
        db = self.repo_chat.db
        conv = await db["conversations"].find_one({"type": "group", "grupo_id": grupo_id})
        if conv:
            conv_id = conv["_id"]
            # Borrar la conversación
            await db["conversations"].delete_one({"_id": conv_id})
            # Borrar todos los buckets de mensajes asociados a esa conversación
            await db["chat_message_buckets"].delete_many({"conversation_id": conv_id})
        
        return {
            "mensaje": f"Grupo '{grupo.nombre}' eliminado con éxito. Sus miembros han quedado libres e independientes.",
            "grupo_id": grupo_id
        }

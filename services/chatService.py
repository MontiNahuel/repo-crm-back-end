from sqlalchemy.orm import Session
from models.usuario import Usuario
from repositories.RepositoryChat import RepositoryChat
from fastapi import HTTPException, status

class ChatService:
    def __init__(self):
        self.chat_repo = RepositoryChat()

    async def get_or_create_chat(self, user1_id: int, user2_id: int, db_sql: Session) -> dict:
        """
        Obtiene o crea un chat directo (1 a 1) entre dos colaboradores,
        conectando los datos de MySQL con el esquema de MongoDB.
        """
        user1 = db_sql.query(Usuario).filter(Usuario.id == user1_id).first()
        user2 = db_sql.query(Usuario).filter(Usuario.id == user2_id).first()
        
        if not user1 or not user2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uno o ambos colaboradores no existen en la base de datos."
            )
            
        u1_dict = {
            "user_id": user1.id,
            "nombre": user1.nombre,
            "apellido": user1.apellido,
            "rol": user1.rol.value if hasattr(user1.rol, "value") else str(user1.rol)
        }
        
        u2_dict = {
            "user_id": user2.id,
            "nombre": user2.nombre,
            "apellido": user2.apellido,
            "rol": user2.rol.value if hasattr(user2.rol, "value") else str(user2.rol)
        }
        
        return await self.chat_repo.get_or_create_direct_conversation(u1_dict, u2_dict)

    async def create_group_conversation(self, name: str, creator_id: int, participant_ids: list, db_sql: Session) -> dict:
        """
        Crea una nueva conversación grupal en MongoDB.
        Valida que todos los IDs de colaboradores existan en MySQL y los denormaliza.
        El creador del grupo es añadido automáticamente a la lista.
        """
        # Aseguramos que el creador del grupo esté en la lista sin duplicados
        all_ids = list(set(participant_ids + [creator_id]))
        
        # Buscamos a todos los usuarios en MySQL
        usuarios = db_sql.query(Usuario).filter(Usuario.id.in_(all_ids)).all()
        
        if not usuarios:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontraron colaboradores válidos para conformar el grupo."
            )
            
        participants_list = []
        for u in usuarios:
            participants_list.append({
                "user_id": u.id,
                "nombre": u.nombre,
                "apellido": u.apellido,
                "rol": u.rol.value if hasattr(u.rol, "value") else str(u.rol)
            })
            
        return await self.chat_repo.create_group_conversation(name, participants_list)

    async def save_chat_message(self, conversation_id: str, sender_id: int, content: str, db_sql: Session, msg_type: str = "text") -> dict:
        """
        Valida que el remitente exista en SQL y guarda el mensaje de forma asíncrona
        en el bucket correspondiente de MongoDB, denormalizando el nombre completo.
        """
        sender = db_sql.query(Usuario).filter(Usuario.id == sender_id).first()
        if not sender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El remitente del mensaje no existe en el CRM."
            )
            
        sender_name = f"{sender.nombre} {sender.apellido}"
        
        return await self.chat_repo.save_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            sender_name=sender_name,
            content=content,
            msg_type=msg_type
        )

    async def get_my_conversations(self, user_id: int, limit: int = 50) -> list:
        """
        Obtiene la lista de salas de chat en las que participa el colaborador.
        """
        return await self.chat_repo.get_conversations_for_user(user_id, limit=limit)

    async def get_chat_history(self, conversation_id: str, page: int = 1) -> list:
        """
        Obtiene el historial paginado de mensajes usando el Bucket Pattern.
        """
        return await self.chat_repo.get_message_history(conversation_id, page)

    async def mark_conversation_as_read(self, conversation_id: str, user_id: int) -> str:
        """
        Marca una conversación como leída para un colaborador en base de datos.
        Retorna la fecha en formato ISO string para que sea serializable.
        """
        dt = await self.chat_repo.update_last_read(conversation_id, user_id)
        return dt.isoformat()


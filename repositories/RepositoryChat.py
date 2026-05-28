from datetime import datetime
# pyrefly: ignore [missing-import]
from bson import ObjectId
from typing import List, Optional
from core.mongo_db import get_mongo_db

class RepositoryChat:
    def __init__(self):
        # La DB se obtiene dinámicamente de la conexión asíncrona de motor
        pass

    @property
    def db(self):
        return get_mongo_db()

    async def create_indexes(self):
        """
        Crea los índices críticos en MongoDB para asegurar consultas de alta velocidad.
        Debe ser llamado al arrancar la aplicación.
        """
        db = self.db
        
        # Colección Conversations: Índice para buscar las salas de un usuario
        await db["conversations"].create_index("participants.user_id")
        
        # Colección Chat Message Buckets: Índice compuesto crítico para recuperar historial
        # buscando por conversación y bucket_number de forma descendente (último primero)
        await db["chat_message_buckets"].create_index([
            ("conversation_id", 1),
            ("bucket_number", -1)
        ])

    async def get_or_create_direct_conversation(self, user1: dict, user2: dict) -> dict:
        """
        Busca o crea una conversación directa (1 a 1) entre dos colaboradores.
        'user1' y 'user2' deben ser diccionarios con: { "user_id": int, "nombre": str, "apellido": str, "rol": str }
        """
        db = self.db
        
        # Buscamos si ya existe la conversación directa entre ambos
        query = {
            "type": "direct",
            "participants.user_id": {
                "$all": [user1["user_id"], user2["user_id"]]
            }
        }
        
        conv = await db["conversations"].find_one(query)
        if conv:
            conv["id"] = str(conv["_id"])
            return conv
        
        # Si no existe, la creamos
        new_conv = {
            "participants": [user1, user2],
            "type": "direct",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_message": None,
            "last_read": {}
        }
        
        result = await db["conversations"].insert_one(new_conv)
        new_conv["_id"] = result.inserted_id
        new_conv["id"] = str(result.inserted_id)
        return new_conv

    async def create_group_conversation(self, name: str, participants: List[dict]) -> dict:
        """
        Crea una nueva conversación grupal en MongoDB con múltiples participantes.
        'participants' es una lista de dicts: { "user_id": int, "nombre": str, "apellido": str, "rol": str }
        """
        db = self.db
        new_conv = {
            "name": name,
            "participants": participants,
            "type": "group",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_message": None,
            "last_read": {}
        }
        result = await db["conversations"].insert_one(new_conv)
        new_conv["_id"] = result.inserted_id
        new_conv["id"] = str(result.inserted_id)
        return new_conv

    async def update_last_read(self, conversation_id: str, user_id: int) -> datetime:
        """
        Actualiza el cursor de lectura del usuario al momento actual (UTC).
        Retorna la fecha y hora asignadas.
        """
        db = self.db
        conv_oid = ObjectId(conversation_id)
        now = datetime.utcnow()
        
        await db["conversations"].update_one(
            {"_id": conv_oid},
            {"$set": {f"last_read.{user_id}": now}}
        )
        return now

    async def save_message(self, conversation_id: str, sender_id: int, sender_name: str, content: str, msg_type: str = "text") -> dict:
        """
        Guarda un mensaje en la conversación usando el Bucket Pattern.
        Crea un nuevo bucket si el actual llegó al límite de 50 mensajes.
        """
        db = self.db
        conv_oid = ObjectId(conversation_id)
        
        # 1. Creamos el objeto del mensaje
        msg_doc = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "content": content,
            "timestamp": datetime.utcnow(),
            "type": msg_type
        }
        
        # 2. Buscamos el último bucket activo de esta conversación
        latest_bucket = await db["chat_message_buckets"].find_one(
            {"conversation_id": conv_oid},
            sort=[("bucket_number", -1)]
        )
        
        # 3. Determinamos si añadimos al bucket existente o creamos uno nuevo (Límite: 50 mensajes por bucket)
        if latest_bucket and latest_bucket.get("count", 0) < 50:
            # Añadimos al bucket existente con actualizaciones atómicas de alto rendimiento
            await db["chat_message_buckets"].update_one(
                {"_id": latest_bucket["_id"]},
                {
                    "$push": {"messages": msg_doc},
                    "$inc": {"count": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        else:
            # Calculamos el número de bucket
            next_bucket_num = (latest_bucket["bucket_number"] + 1) if latest_bucket else 1
            
            new_bucket = {
                "conversation_id": conv_oid,
                "bucket_number": next_bucket_num,
                "count": 1,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "messages": [msg_doc]
            }
            await db["chat_message_buckets"].insert_one(new_bucket)
            
        # 4. Actualizamos el 'last_message', 'updated_at' y la marca de agua del emisor
        await db["conversations"].update_one(
            {"_id": conv_oid},
            {
                "$set": {
                    "last_message": msg_doc,
                    "updated_at": datetime.utcnow(),
                    f"last_read.{sender_id}": datetime.utcnow()
                }
            }
        )
        
        return msg_doc

    async def get_conversations_for_user(self, user_id: int, limit: int = 50) -> List[dict]:
        """
        Obtiene todas las conversaciones activas en las que participa un colaborador.
        Filtra chats directos vacíos (donde last_message es null) para optimizar
        el rendimiento y evitar llenar la barra lateral de chats fantasma.
        Las conversaciones grupales se muestran siempre.
        Ordena por fecha de última actividad de manera descendente.
        Aplica un límite físico (por defecto 50) para asegurar alto rendimiento.
        """
        db = self.db
        
        query = {
            "participants.user_id": user_id,
            "$or": [
                {"type": "group"},
                {
                    "type": "direct",
                    "last_message": {"$ne": None}
                }
            ]
        }
        
        cursor = db["conversations"].find(query).sort("updated_at", -1).limit(limit)
        
        conversations = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            conversations.append(doc)
            
        return conversations

    async def get_message_history(self, conversation_id: str, page: int = 1) -> List[dict]:
        """
        Recupera el historial de mensajes de forma paginada usando buckets.
        page=1 devuelve el bucket más reciente (los últimos 50 mensajes).
        page=2 devuelve el anterior (mensajes 51 a 100) y así sucesivamente.
        """
        db = self.db
        conv_oid = ObjectId(conversation_id)
        
        # 1. Buscamos cuál es el número máximo de bucket existente para esta conversación
        latest_bucket = await db["chat_message_buckets"].find_one(
            {"conversation_id": conv_oid},
            sort=[("bucket_number", -1)]
        )
        
        if not latest_bucket:
            return []
            
        max_bucket_number = latest_bucket["bucket_number"]
        
        # 2. Calculamos el bucket deseado
        # Ej: max_bucket_number = 3. page = 1 -> bucket 3. page = 2 -> bucket 2.
        target_bucket_number = max_bucket_number - (page - 1)
        
        if target_bucket_number < 1:
            return []  # No hay historial más antiguo
            
        # 3. Consultamos el bucket objetivo de forma ultra rápida
        bucket = await db["chat_message_buckets"].find_one({
            "conversation_id": conv_oid,
            "bucket_number": target_bucket_number
        })
        
        return bucket["messages"] if bucket else []

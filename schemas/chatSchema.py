from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ParticipanteSchema(BaseModel):
    user_id: int
    nombre: str
    apellido: str
    rol: str

class MessageSchema(BaseModel):
    sender_id: int
    sender_name: str
    content: str
    timestamp: datetime
    type: str = "text"

class MessageCreate(BaseModel):
    content: str
    type: Optional[str] = "text"

class ConversationResponse(BaseModel):
    id: str  # Representación en string del ObjectId de Mongo
    name: Optional[str] = None  # Nombre de la sala, si es grupal
    participants: List[ParticipanteSchema]
    type: str = "direct"  # "direct" o "group"
    created_at: datetime
    updated_at: datetime
    last_message: Optional[MessageSchema] = None
    last_read: Optional[dict] = None  # Mapea user_id (str) -> datetime (last_read_at)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class GroupChatCreate(BaseModel):
    name: str
    participant_ids: List[int]

class MessageBucketResponse(BaseModel):
    id: str
    conversation_id: str
    bucket_number: int
    count: int
    messages: List[MessageSchema]

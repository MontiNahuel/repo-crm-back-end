from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from schemas.chatSchema import ConversationResponse, MessageSchema, GroupChatCreate
from services.chatService import ChatService
from core.dependencias import obtener_usuario_actual
from models.usuario import Usuario

router = APIRouter(
    prefix="/chat",
    tags=["Chat de Colaboradores"]
)

@router.post("/direct", response_model=ConversationResponse, status_code=201)
async def obtener_o_crear_chat_directo(
    other_user_id: int,
    db_sql: Session = Depends(get_db),
    servicio: ChatService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Busca o crea una conversación directa (1 a 1) entre el colaborador autenticado
    y otro colaborador activo en el CRM.
    """
    if usuario_actual.id == other_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes iniciar un chat directo contigo mismo."
        )
    return await servicio.get_or_create_chat(usuario_actual.id, other_user_id, db_sql)

@router.post("/group", response_model=ConversationResponse, status_code=201)
async def crear_chat_grupal(
    payload: GroupChatCreate,
    db_sql: Session = Depends(get_db),
    servicio: ChatService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Crea una nueva sala de chat grupal con múltiples colaboradores.
    Valida la existencia de todos los participantes y los denormaliza para mayor velocidad.
    """
    return await servicio.create_group_conversation(
        name=payload.name,
        creator_id=usuario_actual.id,
        participant_ids=payload.participant_ids,
        db_sql=db_sql
    )

@router.get("/conversations", response_model=List[ConversationResponse])
async def obtener_mis_conversaciones(
    limit: int = Query(50, ge=1, le=100, description="Límite máximo de conversaciones activas a recuperar"),
    servicio: ChatService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Retorna todas las conversaciones (chats) activas en las que participa el colaborador actual.
    Excluye chats directos vacíos para optimizar rendimiento y limita la cantidad total.
    """
    return await servicio.get_my_conversations(usuario_actual.id, limit=limit)

@router.get("/conversations/{conversation_id}/history", response_model=List[MessageSchema])
async def ver_historial_chat(
    conversation_id: str,
    page: int = Query(1, ge=1, description="Número de página del historial (1 carga los 50 mensajes más recientes)"),
    servicio: ChatService = Depends(),
    _: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtiene los mensajes de una conversación de forma paginada.
    Utiliza el Bucket Pattern para retornar bloques de 50 mensajes de forma rápida y escalable.
    """
    return await servicio.get_chat_history(conversation_id, page)

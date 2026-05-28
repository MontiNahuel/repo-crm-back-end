# pyrefly: ignore [missing-import]
import socketio
# pyrefly: ignore [missing-import]
import jwt
import logging
from datetime import datetime
from core.security import SECRET_KEY, ALGORITHM
from database import SessionLocal
from models.usuario import Usuario
from services.chatService import ChatService

logger = logging.getLogger("crm")

# Servidor de Socket.IO en modo ASGI para integrarse con FastAPI
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
chat_service = ChatService()

@sio.event
async def connect(sid, environ, auth=None):
    """
    Se ejecuta cuando un colaborador intenta conectar su WebSocket.
    Valida el token JWT y guarda sus datos en la sesión del socket.
    """
    token = None
    
    # 1. Intentamos leer del objeto auth (enviado en io.connect(url, auth={token: '...'}))
    if auth and isinstance(auth, dict):
        token = auth.get("token")
        
    # 2. Si no viene en auth, intentamos leer desde los headers HTTP
    if not token:
        auth_header = environ.get("HTTP_AUTHORIZATION")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    # 3. Si no hay token, rechazamos la conexión de inmediato por seguridad
    if not token:
        logger.warning(f"🔒 [Socket.IO] Conexión rechazada: Sin token JWT (sid: {sid})")
        return False
        
    try:
        # Decodificamos el token de forma segura
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if not user_id_str:
            return False
            
        user_id = int(user_id_str)
        
        # Validamos en MySQL que el colaborador siga activo en la empresa
        db_sql = SessionLocal()
        try:
            user = db_sql.query(Usuario).filter(Usuario.id == user_id).first()
            if not user or not user.es_activo:
                logger.warning(f"🔒 [Socket.IO] Conexión rechazada: Usuario {user_id} inactivo o inexistente.")
                return False
                
            # Guardamos los datos de sesión para tenerlos disponibles en los eventos siguientes
            session_data = {
                "user_id": user.id,
                "nombre": f"{user.nombre} {user.apellido}",
                "rol": user.rol.value if hasattr(user.rol, "value") else str(user.rol)
            }
            await sio.save_session(sid, session_data)
            logger.info(f"🟢 [Socket.IO] Colaborador conectado: {session_data['nombre']} (sid: {sid})")
        finally:
            db_sql.close()
            
    except jwt.ExpiredSignatureError:
        logger.warning(f"🔒 [Socket.IO] Conexión rechazada: Token expirado (sid: {sid})")
        return False
    except Exception as e:
        logger.warning(f"🔒 [Socket.IO] Conexión rechazada: Error decodificando token: {e}")
        return False
        
    return True

@sio.event
async def disconnect(sid):
    """
    Limpia y registra la salida del colaborador.
    """
    session = await sio.get_session(sid)
    nombre = session.get("nombre", "Desconocido") if session else "Desconocido"
    logger.info(f"🔴 [Socket.IO] Colaborador desconectado: {nombre} (sid: {sid})")

@sio.event
async def join_conversation(sid, data):
    """
    Une al colaborador a la sala (Room) de Socket.IO correspondiente a la conversación.
    Recibe: { "conversation_id": "ID_MONGO" }
    """
    session = await sio.get_session(sid)
    if not session:
        return
        
    conv_id = data.get("conversation_id")
    if not conv_id:
        return
        
    # Unimos al socket a la sala del chat dinámicamente
    await sio.enter_room(sid, conv_id)
    logger.info(f"🚪 [Socket.IO] {session['nombre']} se unió a la sala de chat: {conv_id}")

@sio.event
async def leave_conversation(sid, data):
    """
    Saca al colaborador de la sala de Socket.IO.
    Recibe: { "conversation_id": "ID_MONGO" }
    """
    conv_id = data.get("conversation_id")
    if not conv_id:
        return
    await sio.leave_room(sid, conv_id)
    logger.info(f"🚪 [Socket.IO] Socket {sid} abandonó la sala de chat: {conv_id}")

@sio.event
async def send_message(sid, data):
    """
    Maneja el envío de un mensaje en tiempo real, lo guarda en MongoDB y lo distribuye.
    Recibe: { "conversation_id": "...", "content": "...", "type": "text" }
    """
    session = await sio.get_session(sid)
    if not session:
        logger.error(f"❌ [Socket.IO] Intento de enviar mensaje sin sesión válida (sid: {sid})")
        return
        
    conv_id = data.get("conversation_id")
    content = data.get("content")
    msg_type = data.get("type", "text")
    
    if not conv_id or not content:
        return
        
    db_sql = SessionLocal()
    try:
        # 1. Guardamos el mensaje usando el Bucket Pattern
        saved_msg = await chat_service.save_chat_message(
            conversation_id=conv_id,
            sender_id=session["user_id"],
            content=content,
            db_sql=db_sql,
            msg_type=msg_type
        )
        
        # Convertimos el timestamp datetime a ISO string para que sea serializable en JSON
        if "timestamp" in saved_msg and isinstance(saved_msg["timestamp"], datetime):
            saved_msg["timestamp"] = saved_msg["timestamp"].isoformat()
            
        # Inyectamos el ID de la conversación para que el frontend asocie el mensaje a la ventana activa
        saved_msg["conversation_id"] = conv_id
            
        # 2. Distribuye el mensaje en tiempo real a todas las conexiones en esa sala (incluido el emisor)
        await sio.emit("new_message", saved_msg, room=conv_id)
        logger.info(f"✉️ [Socket.IO] Mensaje enviado en sala '{conv_id}' por {session['nombre']}")
        
    except Exception as e:
        logger.error(f"❌ [Socket.IO] Error procesando mensaje de {session['nombre']}: {e}")
    finally:
        db_sql.close()

@sio.event
async def read_conversation(sid, data):
    """
    Marca una conversación como leída para el colaborador conectado.
    Recibe: { "conversation_id": "ID_MONGO" }
    Emite a la sala: "conversation_read" -> { "conversation_id": "...", "user_id": int, "read_at": "ISO_TIMESTAMP" }
    """
    session = await sio.get_session(sid)
    if not session:
        return
        
    conv_id = data.get("conversation_id")
    if not conv_id:
        return
        
    user_id = session["user_id"]
    try:
        # Marcamos en DB
        read_at_iso = await chat_service.mark_conversation_as_read(conv_id, user_id)
        
        # Notificamos a toda la sala de chat en tiempo real
        await sio.emit("conversation_read", {
            "conversation_id": conv_id,
            "user_id": user_id,
            "read_at": read_at_iso
        }, room=conv_id)
        
        logger.info(f"👁️ [Socket.IO] {session['nombre']} marcó como leída la sala '{conv_id}'")
        
    except Exception as e:
        logger.error(f"❌ [Socket.IO] Error al marcar leída en Socket.IO: {e}")
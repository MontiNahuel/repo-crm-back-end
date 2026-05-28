import os
import logging
# pyrefly: ignore [missing-import]
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

logger = logging.getLogger("crm")

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "crm_colaboradores_chat")

# Variables globales para reutilizar el cliente único de MongoDB (Singleton)
db_client = None
db = None

def get_mongo_db():
    """
    Devuelve la instancia activa de la base de datos de MongoDB.
    Útil para inyectar como dependencia en los controladores o servicios.
    """
    global db
    if db is None:
        raise RuntimeError("🔌 MongoDB no ha sido inicializado. Llama a init_mongo primero.")
    return db

async def init_mongo():
    """
    Inicializa el cliente de MongoDB con un pool de conexiones optimizado
    para un entorno tradicional OLTP (desarrollo local).
    """
    global db_client, db
    try:
        logger.info("🔌 Conectando a MongoDB...")
        db_client = AsyncIOMotorClient(
            MONGO_URL,
            # maxPoolSize: 20 — Límite conservador para desarrollo local que soporta spikes de concurrencia típicos
            maxPoolSize=20,
            # minPoolSize: 2 — Mantiene 2 conexiones precalentadas en el pool para respuestas inmediatas sin desperdiciar RAM
            minPoolSize=2,
            # maxIdleTimeMS: 300000 (5 minutos) — Mantiene las conexiones abiertas durante periodos inactivos normales para evitar conexión/desconexión constante
            maxIdleTimeMS=300000,
            # serverSelectionTimeoutMS: 5000 — Si MongoDB no responde en 5 segundos, falla rápido para evitar congelar el loop de FastAPI
            serverSelectionTimeoutMS=5000,
            # connectTimeoutMS: 5000 — 5 segundos máximo para establecer el handshake TCP/TLS inicial
            connectTimeoutMS=5000
        )
        db = db_client[MONGO_DB_NAME]
        
        # Ping de diagnóstico rápido para verificar el estado de la base de datos
        await db_client.admin.command('ping')
        logger.info(f"✅ Conectado exitosamente a MongoDB en DB: '{MONGO_DB_NAME}'")
    except Exception as e:
        logger.error(f"❌ Error al conectar con MongoDB: {e}")
        raise e

async def close_mongo():
    """
    Cierra de forma segura el pool de conexiones al apagar la aplicación.
    """
    global db_client
    if db_client:
        logger.info("🔌 Cerrando el pool de conexiones de MongoDB...")
        db_client.close()
        logger.info("✅ Pool de conexiones de MongoDB cerrado correctamente.")

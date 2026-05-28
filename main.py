import logging
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
import socketio
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from core.socketManager import sio
from core.error_handlers import registrar_manejadores_de_errores

# ==========================================
# LOGGING — Configuración centralizada
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("crm")

# IMPORTANTE: Debemos importar los modelos antes de llamar a create_all
# para que SQLAlchemy sepa qué tablas debe crear.
from controllers import ControllerNotas, ControllerProducts, ControllerClient, ControllerUsuario, ControllerTarea, ControllerEstadisticas, ControllerCategorias, ControllerChat
from models import categorias, cambiosClientes


# ==========================================
# CREACIÓN DE TABLAS (Equivalente a ddl-auto=update en Spring Boot)
# ==========================================
Base.metadata.create_all(bind=engine)

import asyncio
from contextlib import asynccontextmanager
from core.notifier import set_main_loop
from core.mongo_db import init_mongo, close_mongo

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Capturamos el loop principal para poder emitir eventos Socket.IO desde hilos síncronos
    set_main_loop(asyncio.get_running_loop())
    # Inicialización óptima del pool de MongoDB
    await init_mongo()
    # Creación automática de índices de chat de alta velocidad en MongoDB
    from repositories.RepositoryChat import RepositoryChat
    await RepositoryChat().create_indexes()
    yield
    # Limpieza y cierre seguro del pool al apagar
    await close_mongo()

# ==========================================
# INICIALIZACIÓN DE LA APP
# ==========================================
app = FastAPI(
    title="CRM API",
    description="API RESTful para gestión de clientes, productos, tareas e inventario",
    version="1.0.0",
    lifespan=lifespan,
)

# ==========================================
# ERROR HANDLERS GLOBALES
# ==========================================
registrar_manejadores_de_errores(app)

# ==========================================
# SOCKET.IO
# ==========================================
app_con_socket = socketio.ASGIApp(sio, other_asgi_app=app)

# ==========================================
# ROUTERS
# ==========================================
app.include_router(ControllerProducts.router)
app.include_router(ControllerClient.router)
app.include_router(ControllerNotas.router)
app.include_router(ControllerUsuario.router)
app.include_router(ControllerTarea.router)
app.include_router(ControllerEstadisticas.router)
app.include_router(ControllerCategorias.router)
app.include_router(ControllerChat.router)


# ==========================================
# CORS — Orígenes permitidos
# ==========================================
origenes_permitidos = [
    "http://localhost:5173",   # Vite/Vue en desarrollo
    "http://127.0.0.1:5173",  # IP local alternativa
    "http://localhost:5500",   # VS Code Live Server
    "http://127.0.0.1:5500",   # VS Code Live Server IP
    "null"                     # Permite abrir consola_chat.html localmente con doble-click
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"mensaje": "¡El motor del CRM está encendido y funcionando!"}
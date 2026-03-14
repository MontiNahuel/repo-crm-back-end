import controllers.ControllerTarea
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# IMPORTANTE: Debemos importar los modelos antes de llamar a create_all
# para que SQLAlchemy sepa qué tablas debe crear.

from controllers import ControllerNotas, ControllerProducts, ControllerClient, ControllerUsuario, ControllerTarea, ControllerEstadisticas
from models import cambiosClientes


# ==========================================
# CREACIÓN DE TABLAS (Equivalente a ddl-auto=update en Spring Boot)
# ==========================================
# Esto va a MySQL, revisa si existe la base 'inventario_db' y crea la tabla 'productos'
Base.metadata.create_all(bind=engine)

# ==========================================
# INICIALIZACIÓN DE LA APP
# ==========================================
app = FastAPI(
    title="Gestor de Inventario API",
    description="API robusta para gestión de stock",
    version="1.0.0"
)

# Registramos el controlador de productos
app.include_router(ControllerProducts.router)
# Registramos el controlador de clientes
app.include_router(ControllerClient.router)

app.include_router(ControllerNotas.router)

app.include_router(ControllerUsuario.router)

app.include_router(ControllerTarea.router)

app.include_router(ControllerEstadisticas.router)


origenes_permitidos = [
    "http://localhost:5173", # Este es el puerto mágico por defecto de Vite/Vue
    "http://127.0.0.1:5173", # A veces el navegador usa la IP local
    # "https://midominio.com" # El día de mañana cuando lo subas a internet
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos, # Solo dejamos pasar a nuestra app de Vue
    allow_credentials=True,            # Permite que viajen cookies o tokens de sesión
    allow_methods=["*"],               # Permite todos los verbos: GET, POST, PATCH, DELETE...
    allow_headers=["*"],               # Permite todos los headers (vital para mandar el Authorization: Bearer <token>)
)


@app.get("/")
def root():
    return {"mensaje": "¡El motor del CRM está encendido y funcionando!"}
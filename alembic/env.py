import sys
import os
from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context

# Añadimos la raíz del proyecto al PATH para que Python pueda encontrar los módulos locales
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importamos el motor y la base declarativa configurada del CRM
from database import Base, engine, URL_BASE_DATOS

# IMPORTANTE: Importamos todos los modelos del CRM con sus nombres de clase exactos
# para que SQLAlchemy registre su metadata en Base y Alembic pueda autodetectar cambios.
from models.usuario import Usuario
from models.cliente import Cliente
from models.grupo import Grupo
from models.tarea import Tarea, TareaCliente
from models.notas import NotaCliente, NotaProducto
from models.categorias import Categoria
from models.producto import Producto
from models.inventario import Inventario
from models.cambiosClientes import CambioCliente

# Objeto de configuración de Alembic
config = context.config

# Configuración del logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Asignamos la metadata de nuestros modelos para soportar "autogenerate"
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Ejecuta las migraciones en modo 'offline' (genera scripts SQL sin conectarse)."""
    url = URL_BASE_DATOS
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Ejecuta las migraciones en modo 'online' (conectándose a la base de datos)."""
    # Reutilizamos el motor configurado de database.py para heredar SSL y drivers de forma nativa
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

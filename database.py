import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carga tu archivo .env oculto
load_dotenv()

# La URL de conexión se lee del .env (nunca hardcodeada en el código fuente)
URL_BASE_DATOS = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/inventario_db")

# Auto-corrección para producción: si la URL viene como mysql:// la reescribimos a mysql+pymysql:// para forzar el uso del driver PyMySQL
if URL_BASE_DATOS and URL_BASE_DATOS.startswith("mysql://"):
    URL_BASE_DATOS = URL_BASE_DATOS.replace("mysql://", "mysql+pymysql://", 1)

# Aiven MySQL o Render añaden ?ssl-mode=REQUIRED o sslmode en el URL, lo cual rompe PyMySQL.
# Lo detectamos, lo removemos de la URL para evitar el TypeError, y lo inyectamos de forma nativa en connect_args.
connect_args = {}
if URL_BASE_DATOS and ("ssl-mode" in URL_BASE_DATOS or "sslmode" in URL_BASE_DATOS):
    connect_args["ssl"] = {}  # Activa cifrado SSL nativo en PyMySQL
    if "?" in URL_BASE_DATOS:
        base_url, query_params = URL_BASE_DATOS.split("?", 1)
        # Filtramos los parámetros de ssl-mode
        params = [p for p in query_params.split("&") if not p.startswith("ssl-mode") and not p.startswith("sslmode")]
        if params:
            URL_BASE_DATOS = base_url + "?" + "&".join(params)
        else:
            URL_BASE_DATOS = base_url

# El motor que gestiona las conexiones
engine = create_engine(URL_BASE_DATOS, connect_args=connect_args)

# La fábrica de sesiones para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para nuestros modelos
Base = declarative_base()

# Dependencia para inyectar la sesión en los controladores/servicios
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
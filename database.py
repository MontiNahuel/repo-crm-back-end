import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carga tu archivo .env oculto
load_dotenv()

# La URL de conexión se lee del .env (nunca hardcodeada en el código fuente)
URL_BASE_DATOS = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/inventario_db")

# El motor que gestiona las conexiones
engine = create_engine(URL_BASE_DATOS)

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
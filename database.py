from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cambia 'root' y 'tu_password' por tus credenciales locales de MySQL
# Formato: mysql+driver://usuario:password@host:puerto/nombre_bd
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/inventario_db"

# El motor que gestiona las conexiones
engine = create_engine(SQLALCHEMY_DATABASE_URL)

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
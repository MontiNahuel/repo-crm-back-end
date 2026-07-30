from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from models.enums import RolUsuario


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    apellido = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100))
    rol = Column(SQLEnum(RolUsuario), default=RolUsuario.LEAD_WEB, nullable=False)
    es_activo = Column(Boolean, default=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="SET NULL"), nullable=True)

    clientes = relationship("Cliente", back_populates="creador")
    cambiosClientes = relationship("CambioCliente", back_populates="usuario")
    tareas = relationship("Tarea", back_populates="usuario")
    grupo = relationship("Grupo", back_populates="miembros")

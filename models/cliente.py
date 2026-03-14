from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from models.enums import EstadoCliente # Importamos el Enum
from datetime import datetime

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True)
    telefono = Column(String(20), nullable=True)
    
    estado = Column(SQLEnum(EstadoCliente), default=EstadoCliente.LEAD, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    creado_en = Column(DateTime, default=datetime.now)

    creador = relationship("Usuario", back_populates="clientes")
    historial_cambios = relationship("CambioCliente", back_populates="cliente")
    notas = relationship("NotaCliente", back_populates="cliente", cascade="all, delete-orphan")
    tareas = relationship("TareaCliente", back_populates="cliente")
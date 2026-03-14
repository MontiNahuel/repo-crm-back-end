from database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True)
    tipo = Column(String(20)) # Para discriminar internamente
    titulo = Column(String(100), nullable=False)
    esta_completada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_limite = Column(DateTime(timezone=True), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="tareas")

    __mapper_args__ = {
        "polymorphic_identity": "personal",
        "polymorphic_on": tipo,
    }

class TareaCliente(Tarea):
    __tablename__ = "tareas_clientes"
    id = Column(Integer, ForeignKey("tareas.id"), primary_key=True)
    # Aquí el cliente_id es estrictamente NOT NULL
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente", back_populates="tareas")

    __mapper_args__ = {
        "polymorphic_identity": "cliente",
    }

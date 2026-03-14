from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class CambioCliente(Base):
    __tablename__ = "cambiosClientes"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Ampliamos a 255 para que no te tire error si el texto es largo
    cambio = Column(String(255), nullable=False) 
    
    # server_default le dice a MySQL: "Si no te paso fecha, pon la de ahora mismo"
    fecha = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relaciones bidireccionales
    usuario = relationship("Usuario", back_populates="cambiosClientes")
    cliente = relationship("Cliente", back_populates="historial_cambios") # <-- Agregamos esta
    
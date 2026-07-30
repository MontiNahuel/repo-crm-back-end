from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Grupo(Base):
    __tablename__ = "grupos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Un grupo tiene muchos miembros (usuarios)
    miembros = relationship("Usuario", back_populates="grupo")

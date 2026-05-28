from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    # Relaciones para que FastAPI arme los JOINs automáticamente
    categoria = relationship("Categoria", back_populates="productos")
    
    # LA CLAVE: uselist=False hace que sea una relación 1 a 1 en vez de 1 a N
    inventario = relationship("Inventario", back_populates="producto", uselist=False, cascade="all, delete-orphan")

    # ¡LA LÍNEA QUE FALTA PARA QUE NO EXPLOTE!
    notas = relationship("NotaProducto", back_populates="producto", cascade="all, delete-orphan")
    
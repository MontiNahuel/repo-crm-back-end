from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Inventario(Base):
    __tablename__ = "inventario"
    
    # Es Primary Key y Foreign Key al mismo tiempo
    id_producto = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), primary_key=True)
    stock = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=5)

    # Relación inversa hacia el producto
    producto = relationship("Producto", back_populates="inventario")
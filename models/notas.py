from database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.mixins import NotaMixin



class NotaCliente(Base, NotaMixin):
    __tablename__ = "notas_cliente"
    
    # Solo agregas lo específico de esta relación
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"))
    cliente = relationship("Cliente", back_populates="notas")

class NotaProducto(Base, NotaMixin):
    __tablename__ = "notas_producto"
    
    # Solo agregas lo específico de esta relación
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"))
    producto = relationship("Producto", back_populates="notas")
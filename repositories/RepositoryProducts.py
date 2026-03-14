from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models.producto import Producto
from schemas.productoSchema import ProductoCreate, ProductoUpdate
from repositories.crud_base import CRUDBase

class ProductRepository(CRUDBase[Producto, ProductoCreate, ProductoUpdate]):
    # 1. Inyectamos la BD solo aquí
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(Producto, db)

    # 2. Creamos una función específica para no exponer self.db.commit() al Servicio
    def update_stock(self, producto: Producto, nuevo_stock: int) -> Producto:
        producto.stock = nuevo_stock
        self.db.commit()
        self.db.refresh(producto)
        return producto

# Instanciamos el repositorio para poder inyectarlo luego
producto_repo = ProductRepository(Producto)
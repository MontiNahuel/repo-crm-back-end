from fastapi import Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models.producto import Producto
from models.inventario import Inventario
from schemas.productoSchema import ProductoCreate, ProductoUpdate
from repositories.crud_base import CRUDBase

class ProductRepository(CRUDBase[Producto, ProductoCreate, ProductoUpdate]):
    # 1. Inyectamos la BD solo aquí
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(Producto, db)

    def create(self, obj_in: ProductoCreate) -> Producto:
        data = obj_in.model_dump()
        inventario_data = data.pop("inventario", None)
        
        db_obj = Producto(**data)
        
        # LA MAGIA: Si hay inventario (es un producto físico), lo atamos.
        # Si inventario_data es None (es un servicio), simplemente no hacemos nada.
        if inventario_data is not None:
            db_obj.inventario = Inventario(**inventario_data)
            
        try:
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            self.db.rollback() # Abortamos la transacción si falla
            error_msg = str(e.orig).lower()
            if "sku" in error_msg or "duplicate" in error_msg:
                raise ValueError("Ya existe un producto con este SKU en la base de datos.")
            raise ValueError(f"Error de integridad en la base de datos (revisar categoría u otros datos): {str(e.orig)}")

    def update_stock(self, producto: Producto, nuevo_stock: int) -> Producto:
        # Si por alguna razón el producto no tenía inventario, se lo creamos
        if not producto.inventario:
            producto.inventario = Inventario(stock=nuevo_stock)
            self.db.add(producto.inventario)
        else:
            producto.inventario.stock = nuevo_stock
            
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def count(self) -> int:
        return self.db.query(Producto).count()

    def get_all(self, skip: int = 0, limit: int = 100, filtroEstado: str = None, filtroCategoria: str = None, busqueda: str = None):
        query = self.db.query(Producto).outerjoin(Producto.inventario)
        if filtroCategoria:
            query = query.filter(Producto.categoria.has(nombre=filtroCategoria))
        if busqueda:
            query = query.filter(
                or_(
                    Producto.nombre.ilike(f"%{busqueda}%"),
                    Producto.sku.ilike(f"%{busqueda}%")
                )
            )
        if filtroEstado:
            if filtroEstado == "INACTIVO":
                query = query.filter(Producto.is_active == False)
                
            elif filtroEstado == "BAJO_STOCK":
                # Está activo, PERO su stock perforó el piso
                query = query.filter(
                    Producto.is_active == True,
                    Inventario.stock <= Inventario.stock_minimo
                )
                
            elif filtroEstado == "ACTIVO":
                # Está activo Y (es un servicio OR tiene buen stock)
                query = query.filter(
                    Producto.is_active == True,
                    or_(
                        Inventario.id_producto.is_(None), # Si es nulo, es un servicio (siempre es "ACTIVO")
                        Inventario.stock > Inventario.stock_minimo
                    )
                )
        return query.offset(skip).limit(limit).all()
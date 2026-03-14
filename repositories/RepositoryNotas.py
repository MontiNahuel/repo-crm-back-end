from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models.notas import NotaCliente, NotaProducto
from repositories.crud_base import CRUDBase
from schemas.notasSchema import NotaClienteCreate, NotaProductoCreate, NotaClienteUpdate, NotaProductoUpdate

class NotaClienteRepository(CRUDBase[NotaCliente, NotaClienteCreate, NotaClienteUpdate]):
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(NotaCliente, db)

    def get_all_by_cliente_id(self, cliente_id: int):
        return self.db.query(self.model).filter(self.model.cliente_id == cliente_id).all()

class NotaProductoRepository(CRUDBase[NotaProducto, NotaProductoCreate, NotaProductoUpdate]):
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(NotaProducto, db)

nota_cliente_repo = NotaClienteRepository()
nota_producto_repo = NotaProductoRepository()
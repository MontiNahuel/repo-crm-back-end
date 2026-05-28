from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from repositories.crud_base import CRUDBase
from models.tarea import Tarea, TareaCliente
from schemas.tareaSchema import TareaCreate, TareaClienteCreate, TareaUpdate, TareaClienteUpdate

class TareaRepository(CRUDBase[Tarea, TareaCreate, TareaUpdate]):
    def __init__(self, db: Session = Depends(get_db)):
        # Le pasamos el modelo y la sesión directamente
        super().__init__(Tarea, db)

    # AQUÍ AGREGAMOS EL FILTRO POR USUARIO (Fundamental para el CRM)
    def get_by_user(self, usuario_id: int, skip: int = 0, limit: int = 100, pendientes_solo: bool = False):
        query = self.db.query(self.model).filter(self.model.usuario_id == usuario_id)
        if pendientes_solo:
            query = query.filter(self.model.esta_completada == False)
        query = query.order_by(
            self.model.fecha_limite.is_(None),  # Primero las que TIENEN fecha
            self.model.fecha_limite.asc(),      # Ordenadas de más próxima a más lejana
            self.model.fecha_creacion.desc()    # Si no tienen límite, las más nuevas primero
        )
        return query.offset(skip).limit(limit).all()

class TareaClienteRepository(CRUDBase[TareaCliente, TareaClienteCreate, TareaClienteUpdate]):
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(TareaCliente, db)

    def get_by_cliente(self, cliente_id: int, usuario_actual_id: int, skip: int = 0, limit: int = 100, pendientes_solo: bool = False):
        query = self.db.query(self.model).filter(self.model.cliente_id == cliente_id, self.model.usuario_id == usuario_actual_id)
        if pendientes_solo:
            query = query.filter(self.model.esta_completada == False)
        query = query.order_by(
            self.model.fecha_limite.is_(None),  # Primero las que TIENEN fecha
            self.model.fecha_limite.asc(),      # Ordenadas de más próxima a más lejana
            self.model.fecha_creacion.desc()    # Si no tienen límite, las más nuevas primero
        )
        return query.offset(skip).limit(limit).all()
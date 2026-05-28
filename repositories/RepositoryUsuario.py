from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from schemas.usuarioSchema import UsuarioCreate, UsuarioUpdate
from repositories.crud_base import CRUDBase


class UsuarioRepository(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    # 1. Inyectamos la BD solo aquí
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(Usuario, db)

    def obtener_colaboradores(self, busqueda: str = None, limit: int = 50):
        """
        Retorna la lista de colaboradores activos que coincidan con la búsqueda.
        Si la búsqueda es vacía o tiene menos de 2 caracteres, retorna [] de inmediato para proteger el rendimiento.
        Aplica un límite físico estricto (por defecto 50) para evitar sobrecarga de red y CPU.
        """
        if not busqueda or len(busqueda.strip()) < 2:
            return []

        term = f"%{busqueda.strip()}%"
        return self.db.query(self.model)\
            .filter(self.model.es_activo == True)\
            .filter(
                (self.model.nombre.ilike(term)) |
                (self.model.apellido.ilike(term)) |
                (self.model.email.ilike(term))
            )\
            .limit(limit)\
            .all()


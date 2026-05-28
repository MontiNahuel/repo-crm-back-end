from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models.categorias import Categoria
from schemas.categoriaSchema import CategoriaCreate, CategoriaUpdate
from repositories.crud_base import CRUDBase


class CategoriaRepository(CRUDBase[Categoria, CategoriaCreate, CategoriaUpdate]):
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(Categoria, db)

    def get_by_nombre(self, nombre: str):
        """Busca una categoría por nombre exacto."""
        return self.db.query(self.model).filter(self.model.nombre == nombre).first()

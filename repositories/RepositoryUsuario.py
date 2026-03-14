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

# Instanciamos el repositorio para poder inyectarlo luego
usuario_repo = UsuarioRepository(Usuario)

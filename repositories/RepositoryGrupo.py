from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models.grupo import Grupo
from models.usuario import Usuario
from schemas.grupoSchema import GrupoCreate, GrupoUpdate
from repositories.crud_base import CRUDBase
from typing import Optional

class GrupoRepository(CRUDBase[Grupo, GrupoCreate, GrupoUpdate]):
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(Grupo, db)

    def obtener_por_nombre(self, nombre: str) -> Optional[Grupo]:
        """Busca un grupo por su nombre (para validación de duplicados)."""
        return self.db.query(Grupo).filter(Grupo.nombre == nombre).first()

    def obtener_con_miembros(self, grupo_id: int) -> Optional[Grupo]:
        """Obtiene un grupo cargando de forma ansiosa (joinedload) a sus miembros."""
        return self.db.query(Grupo)\
                       .options(joinedload(Grupo.miembros))\
                       .filter(Grupo.id == grupo_id)\
                       .first()

    def asignar_miembro(self, grupo_id: int, usuario_id: int) -> Optional[Usuario]:
        """Asigna un usuario a un grupo de trabajo (actualiza su grupo_id)."""
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if usuario:
            usuario.grupo_id = grupo_id
            self.db.commit()
            self.db.refresh(usuario)
            return usuario
        return None

    def remover_miembro(self, usuario_id: int) -> Optional[Usuario]:
        """Remueve a un usuario de su grupo actual (pone su grupo_id en NULL)."""
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if usuario:
            usuario.grupo_id = None
            self.db.commit()
            self.db.refresh(usuario)
            return usuario
        return None

from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repositorio base genérico con operaciones CRUD completas.
    Todos los repositorios heredan de acá para no repetir lógica.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        """Obtiene un registro por su ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtiene múltiples registros con paginación."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Crea un nuevo registro a partir de un schema Pydantic."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, update_data: dict) -> Optional[ModelType]:
        """
        Actualiza un registro existente.
        Recibe un dict con los campos a modificar (exclude_unset=True del schema).
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> Optional[ModelType]:
        """Elimina un registro por su ID."""
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj
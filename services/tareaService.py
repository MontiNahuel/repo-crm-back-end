from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from repositories.RepositoryTarea import TareaRepository, TareaClienteRepository
from schemas.tareaSchema import TareaCreate, TareaClienteCreate, TareaUpdate, TareaClienteUpdate, TareaCreateDB, TareaClienteCreateDB

# Suponiendo que tus repositorios están bien tipados
class TareaService:
    def __init__(self, tarea_repo : TareaRepository = Depends(), tarea_cliente_repo : TareaClienteRepository = Depends()):
        self.tarea_repo = tarea_repo
        self.tarea_cliente_repo = tarea_cliente_repo

    # --- VISTA UNIFICADA (Para el Dashboard) ---
    def get_todo_list_personalizado(self, usuario_id: int, skip: int = 0, limit: int = 100, pendientes_solo: bool = False):
        """
        Gracias al polimorfismo, este repo.get_by_user ya trae 
        objetos Tarea y TareaCliente mezclados y ordenados.
        """
        return self.tarea_repo.get_by_user(usuario_id, skip, limit, pendientes_solo)

    # --- LÓGICA DE CREACIÓN ---
    def create_tarea_vendedor(self, usuario_id: int, schema: TareaCreate):
        # Forzamos que el usuario_id sea el del token, no el que venga en el JSON
        tarea_para_db = TareaCreateDB(**schema.model_dump(), usuario_id=usuario_id)
        return self.tarea_repo.create(tarea_para_db)

    def create_tarea_cliente_vendedor(self, usuario_id: int, schema: TareaClienteCreate):
        tarea_para_db = TareaClienteCreateDB(**schema.model_dump(), usuario_id=usuario_id)
        return self.tarea_cliente_repo.create(tarea_para_db)

    # --- ACCIONES GENÉRICAS ---
    def marcar_como_completada(self, tarea_id: int, usuario_id: int):
        # Verificamos primero que la tarea le pertenezca al usuario
        tarea = self.tarea_repo.get(tarea_id)
        if not tarea or tarea.usuario_id != usuario_id:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        value = tarea.esta_completada
        return self.tarea_repo.update(tarea_id, {"esta_completada": not value})
    
    def delete_tarea(self, tarea_id: int, usuario_id: int):
        tarea = self.tarea_repo.get(tarea_id)
        if not tarea or tarea.usuario_id != usuario_id:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return self.tarea_repo.delete(tarea_id)

    def update_tarea(self, tarea_id: int, usuario_id: int, schema: TareaUpdate):
        tarea = self.tarea_repo.get(tarea_id)
        if not tarea or tarea.usuario_id != usuario_id:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return self.tarea_repo.update(tarea_id, schema.model_dump(exclude_unset=True))

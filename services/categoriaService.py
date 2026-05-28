from fastapi import Depends, HTTPException
from repositories.RepositoryCategorias import CategoriaRepository
from schemas.categoriaSchema import CategoriaCreate, CategoriaUpdate


class CategoriaService:
    def __init__(self, repo: CategoriaRepository = Depends()):
        self.repo = repo

    def crear_categoria(self, categoria_in: CategoriaCreate):
        """Crea una categoría nueva. Valida que no exista otra con el mismo nombre."""
        existente = self.repo.get_by_nombre(categoria_in.nombre)
        if existente:
            raise HTTPException(status_code=409, detail=f"Ya existe una categoría con el nombre '{categoria_in.nombre}'")
        return self.repo.create(obj_in=categoria_in)

    def obtener_categorias(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip=skip, limit=limit)

    def obtener_categoria(self, categoria_id: int):
        categoria = self.repo.get(id=categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return categoria

    def actualizar_categoria(self, categoria_id: int, categoria_in: CategoriaUpdate):
        """Actualiza una categoría existente."""
        self.obtener_categoria(categoria_id)  # Valida que exista
        update_data = categoria_in.model_dump(exclude_unset=True)
        return self.repo.update(categoria_id, update_data)

    def eliminar_categoria(self, categoria_id: int):
        """Elimina una categoría. Los productos asociados quedan con id_categoria=NULL."""
        self.obtener_categoria(categoria_id)
        return self.repo.delete(categoria_id)

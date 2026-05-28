from fastapi import APIRouter, Depends, status
from typing import List
from schemas.categoriaSchema import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from services.categoriaService import CategoriaService
from core.dependencias import obtener_usuario_actual
from models.usuario import Usuario

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"]
)

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    categoria_in: CategoriaCreate,
    servicio: CategoriaService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.crear_categoria(categoria_in)

@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(
    skip: int = 0,
    limit: int = 100,
    servicio: CategoriaService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.obtener_categorias(skip=skip, limit=limit)

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(
    categoria_id: int,
    servicio: CategoriaService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.obtener_categoria(categoria_id)

@router.patch("/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria(
    categoria_id: int,
    categoria_in: CategoriaUpdate,
    servicio: CategoriaService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.actualizar_categoria(categoria_id, categoria_in)

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    categoria_id: int,
    servicio: CategoriaService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    servicio.eliminar_categoria(categoria_id)

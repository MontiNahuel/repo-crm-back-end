from fastapi import APIRouter, Depends, status
from typing import List
from schemas.productoSchema import ProductoCreate, ProductoResponse, ProductoUpdate
from services.productService import ProductService
from core.dependencias import obtener_usuario_actual
from models.usuario import Usuario

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(
    producto_in: ProductoCreate, 
    servicio: ProductService = Depends(), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.crear_producto(producto_in)

@router.get("/", response_model=dict[str, int | List[ProductoResponse]])
def listar_productos(
    skip: int = 0, 
    limit: int = 100, 
    filtroEstado: str = None,
    filtroCategoria: str = None,
    busqueda: str = None,
    servicio: ProductService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    productos, cantidadProductos = servicio.obtener_productos(
        skip=skip, limit=limit, filtroEstado=filtroEstado, 
        filtroCategoria=filtroCategoria, busqueda=busqueda
    )
    return {"productos": productos, "cantidadProductos": cantidadProductos}

@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(
    producto_id: int, 
    servicio: ProductService = Depends(), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.obtener_producto(producto_id)

@router.patch("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int,
    producto_in: ProductoUpdate,
    servicio: ProductService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Actualiza parcialmente un producto (solo los campos enviados)."""
    return servicio.actualizar_producto(producto_id, producto_in)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    servicio: ProductService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Elimina un producto por su ID."""
    servicio.eliminar_producto(producto_id)

@router.patch("/{producto_id}/stock", response_model=ProductoResponse)
def ajustar_stock(
    producto_id: int, 
    ajuste: int, 
    servicio: ProductService = Depends(),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return servicio.modificar_stock(producto_id, ajuste)
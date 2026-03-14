from fastapi import APIRouter, Depends
from typing import List
from schemas.productoSchema import ProductoCreate, ProductoResponse
from services.productService import ProductService

# Definimos el router (El equivalente a @RestController y @RequestMapping)
router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

@router.post("/", response_model=ProductoResponse, status_code=201)
def crear_producto(producto_in: ProductoCreate, servicio: ProductService = Depends()):
    # Usamos nuestro repositorio instanciado para crear el producto
    nuevo_producto = servicio.crear_producto(producto_in)
    return nuevo_producto

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(skip: int = 0, limit: int = 100, servicio: ProductService = Depends()):
    # Obtenemos todos los productos con paginación básica
    productos = servicio.obtener_productos(skip=skip, limit=limit)
    return productos

@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, servicio: ProductService = Depends()):
    return servicio.obtener_producto(producto_id)

@router.patch("/{producto_id}/stock", response_model=ProductoResponse)
def ajustar_stock(
    producto_id: int, 
    ajuste: int, 
    servicio: ProductService = Depends() # Inyección limpia
):
    # El Controlador no sabe ni qué es MySQL, ni qué es un Repositorio.
    return servicio.modificar_stock(producto_id, ajuste)
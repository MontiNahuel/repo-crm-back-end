from fastapi import Depends, HTTPException
from repositories.RepositoryProducts import ProductRepository
from schemas.productoSchema import ProductoCreate


class ProductService:
    # 1. Inyectamos el Repositorio (FastAPI se encarga de pasarle la DB por detrás)
    def __init__(self, repo: ProductRepository = Depends()):
        self.repo = repo

    def crear_producto(self, producto_in: ProductoCreate):
        # Lógica de negocio pura
        if producto_in.precio < 0:
            raise HTTPException(status_code=400, detail="El precio no puede ser negativo")
            
        # Delegamos a la capa de datos
        return self.repo.create(obj_in=producto_in)

    def obtener_productos(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip=skip, limit=limit)

    def obtener_producto(self, producto_id: int):
        producto = self.repo.get(id=producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return producto

    def modificar_stock(self, producto_id: int, ajuste: int):
        producto = self.obtener_producto(producto_id)
        nuevo_stock = producto.stock + ajuste
        
        # Regla de negocio de stock
        if nuevo_stock < 0:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente. Actual: {producto.stock}")
        
        # Le pedimos al repositorio que haga el guardado físico
        return self.repo.update_stock(producto, nuevo_stock)
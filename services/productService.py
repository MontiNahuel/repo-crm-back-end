from fastapi import Depends, HTTPException
from repositories.RepositoryProducts import ProductRepository
from schemas.productoSchema import ProductoCreate, ProductoUpdate
from core.notifier import emitir_evento


class ProductService:
    def __init__(self, repo: ProductRepository = Depends()):
        self.repo = repo

    def crear_producto(self, producto_in: ProductoCreate):
        if producto_in.precio < 0:
            raise HTTPException(status_code=400, detail="El precio no puede ser negativo")
            
        try:
            nuevo_producto = self.repo.create(obj_in=producto_in)
            
            # Notificamos la creación en tiempo real
            emitir_evento("producto_creado", {
                "id": nuevo_producto.id,
                "nombre": nuevo_producto.nombre,
                "precio": nuevo_producto.precio,
                "sku": nuevo_producto.sku
            })
            
            return nuevo_producto
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def obtener_productos(self, skip: int = 0, limit: int = 100, filtroEstado: str = None, filtroCategoria: str = None, busqueda: str = None):
        productos = self.repo.get_all(skip=skip, limit=limit, filtroEstado=filtroEstado, filtroCategoria=filtroCategoria, busqueda=busqueda)
        cantidadProductos = self.repo.count()
        return productos, cantidadProductos

    def obtener_producto(self, producto_id: int):
        producto = self.repo.get(id=producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return producto

    def actualizar_producto(self, producto_id: int, producto_in: ProductoUpdate):
        """Actualiza los campos de un producto existente."""
        self.obtener_producto(producto_id)  # Valida que exista (lanza 404 si no)
        
        update_data = producto_in.model_dump(exclude_unset=True)
        if "precio" in update_data and update_data["precio"] is not None and update_data["precio"] < 0:
            raise HTTPException(status_code=400, detail="El precio no puede ser negativo")
        
        return self.repo.update(producto_id, update_data)

    def eliminar_producto(self, producto_id: int):
        """Elimina un producto por su ID."""
        self.obtener_producto(producto_id)  # Valida que exista
        return self.repo.delete(producto_id)

    def modificar_stock(self, producto_id: int, ajuste: int):
        producto = self.obtener_producto(producto_id)
        
        stock_actual = producto.inventario.stock if producto.inventario else 0
        nuevo_stock = stock_actual + ajuste
        
        # Regla de negocio de stock
        if nuevo_stock < 0:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente. Actual: {stock_actual}")
        
        # Le pedimos al repositorio que haga el guardado físico
        producto_actualizado = self.repo.update_stock(producto, nuevo_stock)
        
        # Notificamos el cambio de stock en tiempo real
        emitir_evento("stock_actualizado", {
            "producto_id": producto_id,
            "nombre": producto.nombre,
            "stock_anterior": stock_actual,
            "nuevo_stock": nuevo_stock,
            "ajuste": ajuste
        })
        
        return producto_actualizado
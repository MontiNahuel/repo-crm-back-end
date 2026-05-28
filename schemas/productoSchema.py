from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from schemas.inventarioSchema import InventarioResponse, InventarioBase
from schemas.categoriaSchema import CategoriaResponse

# DTO Base
class ProductoBase(BaseModel):
    sku: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    precio: float
    is_active: bool = True
    id_categoria: Optional[int] = None

# Lo que envía Vue en el POST (Podés mandar los datos de inventario opcionalmente)
class ProductoCreate(ProductoBase):
    inventario: Optional[InventarioBase] = None

# Lo que FastAPI le devuelve a Vue
class ProductoResponse(ProductoBase):
    id: int
    
    # Anidamos los objetos relacionales
    categoria: Optional[CategoriaResponse] = None
    inventario: Optional[InventarioResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

# DTO para actualizar (hacemos que todos los campos sean opcionales)
class ProductoUpdate(BaseModel):
    sku: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    is_active: Optional[bool] = None
    id_categoria: Optional[int] = None
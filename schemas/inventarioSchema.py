from pydantic import BaseModel, ConfigDict

class InventarioBase(BaseModel):
    stock: int = 0
    stock_minimo: int = 5

class InventarioResponse(InventarioBase):
    id_producto: int
    model_config = ConfigDict(from_attributes=True)
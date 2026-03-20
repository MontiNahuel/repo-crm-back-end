from fastapi import Depends, HTTPException
from repositories.RepositoryNotas import NotaClienteRepository, NotaProductoRepository
from sqlalchemy.exc import IntegrityError
from schemas.notasSchema import NotaClienteCreate, NotaClienteCreateDB

from services.clienteService import ClienteService

class NotasService:
    def __init__(
            self, 
            repo_nota_cliente: NotaClienteRepository = Depends(), 
            repo_nota_producto: NotaProductoRepository = Depends(),
            servicio_cliente: ClienteService = Depends()
            ):
        self.repo_nota_cliente = repo_nota_cliente
        self.repo_nota_producto = repo_nota_producto
        self.servicio_cliente = servicio_cliente

    def crear_nota_cliente(self, nota_in: NotaClienteCreate, usuario_id: int):
        self.servicio_cliente.obtener_cliente(cliente_id=nota_in.cliente_id)
        try:
            nota_db = NotaClienteCreateDB(**nota_in.model_dump(), usuario_id=usuario_id)
            return self.repo_nota_cliente.create(obj_in=nota_db)
        except IntegrityError as e:
            self.repo_nota_cliente.db.rollback() 
            raise HTTPException(
                status_code=400, 
                detail="Error de integridad: Verifica que el cliente exista y los datos sean correctos."
            )
        except Exception as e:
            self.repo_nota_cliente.db.rollback()
            print(f"🚨 ERROR CRÍTICO AL CREAR NOTA: {repr(e)}")
            raise HTTPException(status_code=500, detail="Error interno al procesar la nota")

    def eliminar_nota_cliente(self, cliente_id: int):
        nota = self.repo_nota_cliente.get(id=cliente_id)
        if not nota:
            raise HTTPException(status_code=404, detail="Nota de cliente no encontrada")
        return self.repo_nota_cliente.delete(id=cliente_id)
    
#    def obtener_notas(self, skip: int = 0, limit: int = 100):
#        return self.repo_nota_cliente.get_all(skip=skip, limit=limit)
    
    def obtener_notas_cliente(self, cliente_id: int):
        return self.repo_nota_cliente.get_all_by_cliente_id(cliente_id=cliente_id)

    def obtener_notas_propias_cliente(self, cliente_id: int, usuario_id: int):
        return self.repo_nota_cliente.get_all_by_cliente_id_and_usuario_id(cliente_id=cliente_id, usuario_id=usuario_id)

    def crear_nota_producto(self, nota_in):
        # Aquí podrías agregar lógica de negocio específica para notas de producto
        return self.repo_nota_producto.create(obj_in=nota_in)
    
    def eliminar_nota_producto(self, producto_id: int):
        nota = self.repo_nota_producto.get(id=producto_id)
        if not nota:
            raise HTTPException(status_code=404, detail="Nota de producto no encontrada")
        return self.repo_nota_producto.delete(id=producto_id)
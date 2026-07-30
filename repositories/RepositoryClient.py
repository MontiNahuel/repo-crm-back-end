from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models.cliente import Cliente
from schemas.clienteSchema import ClienteCreate, ClienteUpdate
from models.cambiosClientes import CambioCliente
from repositories.crud_base import CRUDBase
from sqlalchemy import desc, func, or_
from models.usuario import Usuario
from models.enums import RolUsuario

class ClienteRepository(CRUDBase[Cliente, ClienteCreate, ClienteUpdate]):
    # 1. Inyectamos la BD solo aquí
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(Cliente, db)

    def update_estado(self, cliente: Cliente, nuevo_estado: str) -> Cliente:
        cliente.estado = nuevo_estado
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    def update_estado_con_auditoria(self, cliente: Cliente, nuevo_estado: str, usuario_id: int) -> Cliente:
        estado_anterior = cliente.estado
        cliente.estado = nuevo_estado
        self.db.add(cliente)
        texto_cambio = f"Cambió el estado de '{estado_anterior}' a '{nuevo_estado}'"
        registro_auditoria = CambioCliente(
            cliente_id=cliente.id,
            usuario_id=usuario_id,
            cambio=texto_cambio
        )
        self.db.add(registro_auditoria)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    def obtener_historial(self, cliente_id: int):
        """Busca todos los cambios de un cliente, del más nuevo al más viejo."""
        return self.db.query(CambioCliente)\
                      .options(joinedload(CambioCliente.usuario))\
                      .filter(CambioCliente.cliente_id == cliente_id)\
                      .order_by(desc(CambioCliente.fecha))\
                      .all()
    
    def count_by_user(self, usuario_id: int):
        return self.db.query(Cliente).filter(Cliente.usuario_id == usuario_id).count()
    
    def obtener_clientes_por_id_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100, busqueda : str = None, filtroEstado: str = None, orden: str = None):
        query = self.db.query(Cliente).filter(Cliente.usuario_id == usuario_id)
        if busqueda:
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(f"%{busqueda}%"),
                    Cliente.email.ilike(f"%{busqueda}%")
                )
            )
        if filtroEstado:
            query = query.filter(Cliente.estado == filtroEstado)
        if orden:
            if orden == "asc":
                query = query.order_by(Cliente.creado_en.asc())
            else:
                query = query.order_by(Cliente.creado_en.desc())
        total = query.count()
        clientes = query.offset(skip).limit(limit).all()
        return total, clientes

    def obtener_clientes_por_visibilidad(
        self,
        usuario: Usuario,
        skip: int = 0,
        limit: int = 100,
        busqueda: str = None,
        filtroEstado: str = None,
        orden: str = None
    ):
        """
        Obtiene los clientes aplicando las reglas de visibilidad del CRM:
        - ADMIN: Ve todos los clientes.
        - VENDEDOR con grupo: Ve clientes de todos los miembros de su grupo de trabajo.
        - VENDEDOR independiente: Ve únicamente sus clientes propios.
        """
        # 1. Si es ADMIN, ve todo
        if usuario.rol == RolUsuario.ADMIN:
            query = self.db.query(Cliente)
        # 2. Si pertenece a un grupo, ve los clientes de su grupo de trabajo
        elif usuario.grupo_id is not None:
            query = self.db.query(Cliente).filter(
                Cliente.usuario_id.in_(
                    self.db.query(Usuario.id).filter(Usuario.grupo_id == usuario.grupo_id)
                )
            )
        # 3. Si es independiente, ve solo los suyos
        else:
            query = self.db.query(Cliente).filter(Cliente.usuario_id == usuario.id)

        # Filtros de búsqueda, estado y orden
        if busqueda:
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(f"%{busqueda}%"),
                    Cliente.email.ilike(f"%{busqueda}%")
                )
            )
        if filtroEstado:
            query = query.filter(Cliente.estado == filtroEstado)
        if orden:
            if orden == "asc":
                query = query.order_by(Cliente.creado_en.asc())
            else:
                query = query.order_by(Cliente.creado_en.desc())

        total = query.count()
        clientes = query.offset(skip).limit(limit).all()
        return total, clientes

    def obtener_cambiosClientes(self, usuario_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(CambioCliente).filter(CambioCliente.usuario_id == usuario_id).order_by(CambioCliente.fecha.desc()).offset(skip).limit(limit).all()

    def get_conteo_por_estado(self, usuario_id: int):
        """
        Devuelve una lista de tuplas: [('lead', 5), ('ganado', 12), ...]
        """
        return self.db.query(
            self.model.estado, 
            func.count(self.model.id)
        ).filter(
            self.model.usuario_id == usuario_id # O usuario_id, según tu modelo
        ).group_by(
            self.model.estado
        ).all()
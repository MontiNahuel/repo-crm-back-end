from fastapi import APIRouter, Depends
from typing import List
from schemas.notasSchema import NotaClienteCreate, NotaClienteResponse, NotaProductoCreate, NotaProductoResponse
from services.notasService import NotasService
from core.dependencias import obtener_usuario_actual
from models.usuario import Usuario

router = APIRouter(
    prefix="/notas",
    tags=["Notas"]
)

@router.post("/", response_model=NotaClienteResponse, status_code=201)
def crear_nota_cliente(nota_in: NotaClienteCreate, servicio: NotasService = Depends(), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    nueva_nota = servicio.crear_nota_cliente(nota_in, usuario_actual.id)
    return nueva_nota

"""
@router.get("/", response_model=List[NotaClienteResponse])
def listar_notas(skip: int = 0, limit: int = 100, servicio: NotasService = Depends()):
    notas = servicio.obtener_notas_cliente(skip=skip, limit=limit)
    return notas
"""

@router.get("/cliente/{cliente_id}", response_model=List[NotaClienteResponse])
def listar_notas_de_un_cliente(cliente_id: int, servicio: NotasService = Depends()):
    notas = servicio.obtener_notas_cliente(cliente_id=cliente_id)
    return notas

@router.get("/propios/cliente/{cliente_id}", response_model=List[NotaClienteResponse])
def listar_notas_propias_de_un_cliente(cliente_id: int, servicio: NotasService = Depends(), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    notas = servicio.obtener_notas_propias_cliente(cliente_id=cliente_id, usuario_id=usuario_actual.id)
    return notas
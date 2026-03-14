from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from core.dependencias import obtener_usuario_actual
from models.usuario import Usuario
from repositories.RepositoryClient import ClienteRepository
from services.estadisticasService import EstadisticasService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Dependencia para inyectar el servicio correctamente armado
def get_estadisticas_service(db: Session = Depends(get_db)):
    cliente_repo = ClienteRepository(db)
    return EstadisticasService(cliente_repo)

@router.get("/kpis")
def obtener_kpis(
    service: EstadisticasService = Depends(get_estadisticas_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # El controlador solo delega la tarea
    return service.calcular_kpis_dashboard(usuario_actual.id)
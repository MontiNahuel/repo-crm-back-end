import logging
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError

logger = logging.getLogger("crm")


def registrar_manejadores_de_errores(app: FastAPI):
    """
    Registra handlers globales de errores en la app de FastAPI.
    Así los controllers no necesitan try/except para cada caso común.
    """

    @app.exception_handler(RequestValidationError)
    async def error_validacion(request: Request, exc: RequestValidationError):
        """Cuando Pydantic rechaza los datos de entrada (422)."""
        errores = []
        for error in exc.errors():
            errores.append({
                "campo": " -> ".join(str(loc) for loc in error["loc"]),
                "mensaje": error["msg"],
            })
        
        logger.warning(f"Validación fallida en {request.method} {request.url.path}: {errores}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Los datos enviados no son válidos",
                    "details": errores,
                }
            },
        )

    @app.exception_handler(IntegrityError)
    async def error_integridad(request: Request, exc: IntegrityError):
        """Cuando la DB rechaza por duplicado, FK inválida, etc. (409)."""
        logger.error(f"Error de integridad en {request.method} {request.url.path}: {exc.orig}")
        
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "code": "INTEGRITY_ERROR",
                    "message": "Conflicto de datos: el registro ya existe o viola una restricción de la base de datos.",
                }
            },
        )

    @app.exception_handler(OperationalError)
    async def error_conexion_db(request: Request, exc: OperationalError):
        """Cuando la DB no responde o la conexión falla (503)."""
        logger.critical(f"Error de conexión a la base de datos: {exc.orig}")
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "DATABASE_UNAVAILABLE",
                    "message": "El servicio de base de datos no está disponible. Intentá de nuevo en unos minutos.",
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def error_http_controlado(request: Request, exc: HTTPException):
        """Mantiene los errores HTTP legítimos (400, 401, 403, 404, etc.) sin alterarlos ni enmascararlos."""
        logger.warning(f"Error HTTP controlado ({exc.status_code}) en {request.method} {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                }
            },
        )

    @app.exception_handler(Exception)
    async def error_generico(request: Request, exc: Exception):
        """Atrapa cualquier error inesperado para que nunca se filtre un traceback al cliente."""
        logger.exception(f"Error inesperado en {request.method} {request.url.path}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Ocurrió un error interno. El equipo ha sido notificado.",
                }
            },
        )

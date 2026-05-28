import asyncio
import logging
from core.socketManager import sio

logger = logging.getLogger("crm")

# Variable global para guardar el loop principal de la aplicación (thread principal de Uvicorn)
_main_loop = None

def set_main_loop(loop: asyncio.AbstractEventLoop):
    """Guarda el event loop principal en el arranque de FastAPI."""
    global _main_loop
    _main_loop = loop
    logger.info("✅ Event loop principal capturado para el Notificador en tiempo real.")

def emitir_evento(evento: str, datos: dict):
    """
    Emite un evento de Socket.IO en tiempo real de forma no bloqueante y 100% segura.
    Funciona tanto si es llamado desde rutas asíncronas como desde hilos síncronos (los thread pools de FastAPI).
    """
    global _main_loop
    if _main_loop is None:
        logger.warning(f"Intento de emitir {evento} antes de capturar el event loop principal.")
        return

    try:
        # run_coroutine_threadsafe envía el coroutine al event loop del thread principal (Uvicorn)
        # de forma totalmente thread-safe y no bloqueante.
        asyncio.run_coroutine_threadsafe(sio.emit(evento, datos), _main_loop)
        logger.info(f"⚡ [Socket.IO] Evento emitido: {evento} -> {datos}")
    except Exception as e:
        logger.error(f"❌ [Socket.IO] Error al emitir evento {evento}: {e}")

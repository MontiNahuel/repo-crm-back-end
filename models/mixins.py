from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_mixin
from datetime import datetime

@declarative_mixin
class NotaMixin:
    """
    Plantilla base para cualquier nota del sistema.
    Ninguna tabla se llama 'NotaMixin', solo hereda estos campos.
    """
    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
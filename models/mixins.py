from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_mixin, declared_attr, relationship
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
    @declared_attr
    def usuario_id(cls):
        return Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    # Opcional pero recomendado: La relación para poder acceder a nota.autor.nombre
    @declared_attr
    def autor(cls):
        return relationship("Usuario") # Asegurate de que tu modelo se llame "Usuario"
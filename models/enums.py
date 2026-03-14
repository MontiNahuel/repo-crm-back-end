from enum import Enum

class EstadoCliente(str, Enum):
    LEAD = "LEAD"           # Prospecto, consultó pero no compró
    ACTIVO = "ACTIVO"       # Cliente regular
    INACTIVO = "INACTIVO"   # Compró en el pasado, pero hace mucho no interactúa
    PERDIDO = "PERDIDO"     # Se fue a la competencia o pidió no ser contactado

class RolUsuario(str, Enum):
    ADMIN = "ADMIN"           # Control total del sistema
    VENDEDOR = "VENDEDOR"     # Puede gestionar clientes y ventas, pero no configuraciones del sistema
    CLIENTE = "CLIENTE"       # Un cliente que ya compró y tiene su propio panel
    LEAD_WEB = "LEAD_WEB"     # Un prospecto/postulante que recién llenó un formulario
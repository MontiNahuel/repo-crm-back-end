from repositories.RepositoryClient import ClienteRepository
from models.enums import EstadoCliente

class EstadisticasService:
    def __init__(self, cliente_repo: ClienteRepository):
        self.cliente_repo = cliente_repo

    def calcular_kpis_dashboard(self, vendedor_id: int) -> dict:
        # 1. Traemos la data cruda de la base de datos
        conteo_crudo = self.cliente_repo.get_conteo_por_estado(vendedor_id)

        # 2. Inicializamos el embudo en 0 para evitar errores si no hay clientes en un estado
        pipeline = {
            EstadoCliente.LEAD.value: 0, 
            EstadoCliente.ACTIVO.value: 0, 
            EstadoCliente.INACTIVO.value: 0, 
            EstadoCliente.PERDIDO.value: 0
        }

        # 3. Mapeamos la respuesta de la base de datos
        for estado, cantidad in conteo_crudo:
            # SQLAlchemy a veces devuelve el Enum y a veces el string puro, esto lo ataja
            estado_str = estado.value if hasattr(estado, 'value') else estado
            if estado_str in pipeline:
                pipeline[estado_str] = cantidad

        # 4. Matemáticas de KPIs adaptadas a tu modelo
        clientes_activos = pipeline[EstadoCliente.ACTIVO.value]
        leads_pendientes = pipeline[EstadoCliente.LEAD.value]
        total_historico = sum(pipeline.values())
        
        # Tasa de Conversión: (Los que compraron alguna vez) / (Los que compraron + Los que perdimos)
        # Excluimos a los LEADs de esta división porque la moneda todavía está en el aire
        historico_compradores = pipeline[EstadoCliente.ACTIVO.value] + pipeline[EstadoCliente.INACTIVO.value]
        casos_cerrados = historico_compradores + pipeline[EstadoCliente.PERDIDO.value]
        
        tasa_conversion = 0.0
        if casos_cerrados > 0:
            tasa_conversion = round((historico_compradores / casos_cerrados) * 100, 1)

        # 5. Devolvemos el JSON estructurado
        return {
            "kpis": {
                "clientes_activos": clientes_activos,
                "leads_pendientes": leads_pendientes,
                "tasa_conversion": tasa_conversion,
                "total_historico": total_historico
            },
            "pipeline": pipeline
        }
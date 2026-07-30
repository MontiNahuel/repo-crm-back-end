from datetime import datetime
from typing import List, Optional
from core.mongo_db import get_mongo_db

class RepositoryResumenIa:
    @property
    def db(self):
        return get_mongo_db()

    async def guardar_resumen(self, cliente_id: int, resumen: str, solicitante: dict) -> dict:
        """
        Guarda un nuevo resumen ejecutivo de IA en MongoDB.
        Denormaliza los datos del solicitante (ID, nombre, apellido) para evitar
        consultas adicionales a MySQL al listar o ver el historial.
        """
        db = self.db
        doc = {
            "cliente_id": cliente_id,
            "resumen": resumen,
            "fecha": datetime.utcnow(),
            "solicitante": {
                "user_id": solicitante["user_id"],
                "nombre": solicitante["nombre"],
                "apellido": solicitante["apellido"]
            }
        }
        result = await db["resumenes_clientes_ia"].insert_one(doc)
        doc["id"] = str(result.inserted_id)
        doc["_id"] = result.inserted_id
        return doc

    async def obtener_ultimo_resumen(self, cliente_id: int) -> Optional[dict]:
        """
        Obtiene el resumen de IA más reciente guardado para un cliente.
        """
        db = self.db
        query = {"cliente_id": cliente_id}
        doc = await db["resumenes_clientes_ia"].find_one(query, sort=[("fecha", -1)])
        if doc:
            doc["id"] = str(doc["_id"])
            if "fecha" in doc and isinstance(doc["fecha"], datetime):
                doc["fecha"] = doc["fecha"].isoformat()
        return doc

    async def obtener_historial_resumenes(self, cliente_id: int) -> List[dict]:
        """
        Obtiene la lista histórica de todos los resúmenes guardados para un cliente,
        del más nuevo al más antiguo.
        """
        db = self.db
        query = {"cliente_id": cliente_id}
        cursor = db["resumenes_clientes_ia"].find(query).sort("fecha", -1)
        
        resumenes = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            if "fecha" in doc and isinstance(doc["fecha"], datetime):
                doc["fecha"] = doc["fecha"].isoformat()
            resumenes.append(doc)
        return resumenes

import os
import json
import time
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import errors # Importamos los errores específicos

class AiService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def extraer_tareas_de_nota(self, texto_nota: str, retries: int = 3) -> list[dict]:
        prompt = f"Analiza esta nota de CRM y extrae tareas: {texto_nota}"
        
        for i in range(retries):
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'titulo': {'type': 'STRING'},
                                    'descripcion': {'type': 'STRING'}
                                },
                                'required': ['titulo', 'descripcion']
                            }
                        }
                    }
                )
                return json.loads(response.text) if response.text else []

            except errors.APIError as e:
                error_str = str(e)
                # Si el error es temporal (429 o 503)
                if "429" in error_str or "503" in error_str or "UNAVAILABLE" in error_str:
                    if i < retries - 1:
                        wait_time = (i + 1) * 5  # Espera 5, 10 segundos...
                        print(f"⚠️ Error temporal de API ({e.code if hasattr(e, 'code') else 'APIError'}). Reintentando en {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("❌ Se agotaron los reintentos de API de Gemini por fallas temporales.")
                else:
                    print(f"❌ Error de API de Gemini: {e}")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                break
        return []

    def generar_resumen_cliente(self, cliente_data: dict, retries: int = 3) -> str:
        """
        Consolida la ficha del cliente y utiliza Gemini 2.5 Flash para generar
        un resumen ejecutivo estructurado en Markdown con plan de acción de ventas.
        """
        detalles_cliente = (
            f"Cliente: {cliente_data['nombre']}\n"
            f"Email: {cliente_data.get('email', 'N/A')}\n"
            f"Teléfono: {cliente_data.get('telefono', 'N/A')}\n"
            f"Estado Actual: {cliente_data['estado']}\n\n"
        )
        
        texto_notas = "--- NOTAS DE SEGUIMIENTO ---\n"
        if cliente_data.get("notas"):
            for idx, nota in enumerate(cliente_data["notas"], 1):
                texto_notas += f"Nota {idx} ({nota['fecha']}) - Escrita por {nota['autor']}:\n{nota['contenido']}\n\n"
        else:
            texto_notas += "No hay notas registradas para este cliente.\n\n"
            
        texto_tareas = "--- TAREAS ASOCIADAS ---\n"
        if cliente_data.get("tareas"):
            for idx, tarea in enumerate(cliente_data["tareas"], 1):
                estado = "Completada" if tarea["completada"] else "Pendiente"
                limite = f", Fecha Límite: {tarea['fecha_limite']}" if tarea.get('fecha_limite') else ""
                texto_tareas += f"Tarea {idx}: {tarea['titulo']} ({estado}{limite})\n"
        else:
            texto_tareas += "No hay tareas asignadas para este cliente.\n\n"
            
        texto_historial = "--- HISTORIAL DE CAMBIOS EN EL KANBAN ---\n"
        if cliente_data.get("historial"):
            for idx, cambio in enumerate(cliente_data["historial"], 1):
                texto_historial += f"Cambio {idx} ({cambio['fecha']}): {cambio['descripcion']}\n"
        else:
            texto_historial += "No hay transiciones de estado registradas.\n\n"

        prompt = (
            "Eres un asistente de inteligencia artificial experto en ventas, análisis de negocios y CRM.\n"
            "Tu tarea es redactar un resumen ejecutivo del cliente para ayudar al vendedor a entender la situación comercial en 10 segundos.\n"
            "Analiza detalladamente el siguiente expediente del cliente:\n\n"
            f"{detalles_cliente}"
            f"{texto_notas}"
            f"{texto_tareas}"
            f"{texto_historial}\n"
            "Por favor, genera un informe estructurado en Markdown con las siguientes secciones obligatorias (usa encabezados de markdown ##):\n"
            "## 📝 Resumen de la Relación\n"
            "Redacta 1 o 2 párrafos concisos analizando la salud de la relación comercial, su madurez y el estado de la comunicación general.\n\n"
            "## 🎯 Puntos Clave Identificados\n"
            "Crea una lista de viñetas cortas con los hallazgos críticos detectados en el historial (intereses particulares, objeciones expresadas, acuerdos alcanzados o motivos de quejas).\n\n"
            "## 🚀 Plan de Acción Sugerido\n"
            "Provee exactamente 3 recomendaciones accionables y muy específicas que el vendedor debería llevar a cabo a continuación para avanzar a este cliente en el pipeline de ventas o reactivarlo.\n\n"
            "Mantén un tono profesional, empático, directo a los negocios y evita rodeos de introducción.\n"
            "Por favor ser lo mas conciso posible, sin metaforas ni relleno. Directo en las ideas. Menos de 200 palabras en total."
        )

        for i in range(retries):
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                return response.text if response.text else "No se pudo generar el resumen ejecutivo por falta de respuesta del modelo."

            except errors.APIError as e:
                error_str = str(e)
                # Si el error es temporal (429 o 503)
                if "429" in error_str or "503" in error_str or "UNAVAILABLE" in error_str:
                    if i < retries - 1:
                        wait_time = (i + 1) * 5  # Espera 5, 10 segundos...
                        print(f"⚠️ Error temporal de API al resumir ({e.code if hasattr(e, 'code') else 'APIError'}). Reintentando en {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("❌ Se agotaron los reintentos de API de Gemini al resumir por fallas temporales.")
                else:
                    print(f"❌ Error de API de Gemini al generar resumen: {e}")
                break
            except Exception as e:
                print(f"❌ Error inesperado en Gemini: {e}")
                break
                
        return "Error al conectar con el servicio de Inteligencia Artificial para generar el resumen."
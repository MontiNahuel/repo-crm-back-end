import os
import json
import time
from google import genai
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

            except errors.ClientError as e:
                # Si el error es 429 (Cuota excedida)
                if "429" in str(e):
                    if i < retries - 1:
                        wait_time = (i + 1) * 10 # Espera 10, 20 segundos...
                        print(f"⚠️ Cuota excedida. Reintentando en {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("❌ Se agotaron los reintentos. Límite de API alcanzado.")
                else:
                    print(f"❌ Error de API: {e}")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                break
        return []
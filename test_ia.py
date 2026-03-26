import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargamos tu .env para leer la clave
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Modelos disponibles para generar texto con tu API Key:")
print("-" * 50)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
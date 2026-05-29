# 1. Imagen base oficial de Python ligera
FROM python:3.11-slim

# 2. Configurar variables de entorno óptimas para producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000

# 3. Establecer el directorio de trabajo
WORKDIR /app

# 4. Copiar e instalar dependencias del requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo el código fuente del proyecto
COPY . .

# 6. Exponer el puerto por defecto (Render lo sobreescribirá dinámicamente)
EXPOSE 10000

# 7. Comando de inicio utilizando el puerto dinámico de Render
CMD ["sh", "-c", "uvicorn main:app_con_socket --host 0.0.0.0 --port ${PORT}"]

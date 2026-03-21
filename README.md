<div align='center'>

# ⚙️ Mi CRM - Backend API

API RESTful de alto rendimiento que alimenta el ecosistema del CRM. Construida de manera asíncrona, maneja la lógica de negocio, la persistencia de datos en bases relacionales, la autenticación segura y los eventos en tiempo real.

## 🛠️ Stack Tecnológico

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/) [![MySQL](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/) [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/) [![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)](https://jwt.io/) [![Socket.io](https://img.shields.io/badge/Socket.io-010101?style=for-the-badge&logo=socket.io&logoColor=white)](https://socket.io/)
  
</div>

## ✨ Características Principales

* **Arquitectura Moderna:** Uso intensivo de tipado estricto con Pydantic para validación automática de datos de entrada y salida.
* **Seguridad:** Autenticación robusta mediante tokens JWT (JSON Web Tokens) y hasheo de contraseñas con bcrypt.
* **Tiempo Real:** Integración con WebSockets (Socket.io) para notificaciones instantáneas de cambios de estado y nuevas tareas.
* **ORM Eficiente:** Consultas a la base de datos gestionadas a través de SQLAlchemy, previniendo inyecciones SQL y facilitando la mantenibilidad.
* **Documentación Automática:** Swagger UI interactivo generado al instante por FastAPI.

## 📂 Estructura del Proyecto

El código está organizado siguiendo el patrón de diseño por dominios, ideal para escalar hacia una arquitectura de microservicios o un ERP:

```text
/
├── app/
│   ├── controllers/  # Enrutadores (Endpoints) separados por módulo (auth, clientes, tareas)
│   ├── core/         # Configuraciones globales, seguridad (JWT) y variables de entorno
│   ├── models/       # Modelos de SQLAlchemy (Tablas de la base de datos)
│   ├── repositories/ # Conexión a la base de datos y configuración del motor (MySQL)
│   ├── schemas/      # Modelos de Pydantic (Validación de datos de entrada/salida)
│   └── services/     # Lógica de negocio (Consultas CRUD complejas)
├── database.py       # Conexión principal a MySQL y configuración de SQLAlchemy
├── main.py           # Punto de entrada de la aplicación y configuración de FastAPI
└── requirements.txt  # Dependencias del proyecto
```

## 🚀 Instalación y Uso Local

Pasos para levantar el repositorio en entorno local:
1. Clonar el repositorio y entrar a la carpeta

```bash
git clone [https://github.com/MontiNahuel/repo-crm-back-end.git](https://github.com/MontiNahuel/repo-crm-back-end.git)
cd repo-crm-back-end
```

2. Crear y activar el entorno virtual
   
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. Levantar el servidor

```bash
uvicorn main:app_con_socket --reload
```

La API estará corriendo en http://localhost:8000.
Puedes acceder a la documentación interactiva (Swagger) en http://localhost:8000/docs.

---

⌨️ Desarrollado por **[Nahuel Monti](https://montinahuel.github.io/portafilioV6/)** - *Full Stack Developer*

[LinkedIn](https://www.linkedin.com/in/monti-nahuel/) • [GitHub](https://github.com/MontiNahuel) • [Email](mailto:montinahuel@gmail.com)

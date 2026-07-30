# 🌉 Especificación y Contrato de la API CRM

Este documento sirve como puente para conectar el Frontend (Vue/React) con el Backend (FastAPI + Socket.IO).

---

## 🔑 1. Autenticación (JWT + Refresh Token Flow)

Todos los endpoints protegidos requieren el envío del token de acceso en las cabeceras HTTP:
`Authorization: Bearer <access_token>`

### 🚪 Iniciar Sesión (OAuth2 Form)
*   **Ruta:** `POST /usuarios/login`
*   **Content-Type:** `application/x-www-form-urlencoded`
*   **Parámetros (Body):**
    *   `username`: (Email del usuario)
    *   `password`: (Contraseña)
*   **Respuesta Exitosa (200 OK):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1...",
      "refresh_token": "eyJhbGciOiJIUzI1...",
      "token_type": "bearer"
    }
    ```

### 🚪 Iniciar Sesión (JSON alternativo)
*   **Ruta:** `POST /usuarios/loginFinal`
*   **Content-Type:** `application/json`
*   **Body:**
    ```json
    {
      "email": "usuario@correo.com",
      "password": "mi_contraseña"
    }
    ```
*   **Respuesta Exitosa (200 OK):** Mismo formato que el endpoint anterior.

### 🔄 Refrescar Token (Silencioso)
Se utiliza para obtener un nuevo token de acceso cuando el actual (30 min de duración) expira, sin obligar al usuario a iniciar sesión nuevamente.
*   **Ruta:** `POST /usuarios/refresh`
*   **Content-Type:** `application/json`
*   **Body:**
    ```json
    {
      "refresh_token": "token_largo_de_7_dias_aqui"
    }
    ```
*   **Respuesta Exitosa (200 OK):**
    ```json
    {
      "access_token": "nuevo_access_token",
      "refresh_token": "nuevo_refresh_token",
      "token_type": "bearer"
    }
    ```

### 👥 Buscar Colaboradores / Directorio (Buscador estilo Teams)
Permite buscar y obtener la lista de colaboradores activos del sistema para el inicio de chats directos o la creación de grupos de manera altamente escalable.
*   **Ruta:** `GET /usuarios/colaboradores`
*   **Query Params (Opcionales):**
    *   `busqueda`: string (Filtra por nombre, apellido o email)
*   **Reglas de Rendimiento (Escalabilidad de Varios Miles de Usuarios):**
    > [!IMPORTANT]
    > * **Mínimo de caracteres:** Si el parámetro `busqueda` no se envía, está vacío o tiene **menos de 2 caracteres**, el backend responderá con una lista vacía `[]` de inmediato sin consultar la base de datos (ahorro total de recursos).
    > * **Límite físico:** Los resultados de la base de datos están capados a un máximo estricto de **50 registros** (`limit=50`).
    > * **Debounce Sugerido:** Se recomienda implementar un antirebote (Debounce) de **300ms** en el input del frontend para evitar múltiples llamadas sucesivas mientras el usuario tipea.
*   **Respuesta Exitosa (200 OK):**
    ```json
    [
      {
        "id": 2,
        "email": "matias@correo.com",
        "rol": "VENDEDOR",
        "es_activo": true,
        "nombre": "Matias",
        "apellido": "Calabrese"
      }
    ]
    ```

---

## 📊 2. Clientes & Tablero Kanban (Protegidos)

> [!IMPORTANT]
> **Políticas de Visibilidad y Permisos (TBAC - Team Based Access Control):**
> La respuesta de los endpoints de lectura (`/mis-clientes` y `/pipeline`) varía dinámicamente según el rol y grupo del usuario autenticado:
> *   **`RolUsuario.ADMIN`**: Tiene acceso absoluto. Retorna todos los clientes del sistema.
> *   **`RolUsuario.SUPERVISOR` o `VENDEDOR` con Grupo**: Retorna los clientes propios del usuario **más los clientes asignados a cualquier otro miembro de su mismo grupo de trabajo** (visibilidad colaborativa).
> *   **`RolUsuario.VENDEDOR` independiente**: Retorna **únicamente** los clientes creados por o asignados a su propio `usuario_id` (acceso aislado).

### 📋 Listar Clientes (Con filtros y visibilidad dinámica)
*   **Ruta:** `GET /clientes/mis-clientes`
*   **Query Params (Opcionales):**
    *   `skip`: int (Paginación, defecto 0)
    *   `limit`: int (Paginación, defecto 100)
    *   `busqueda`: string (Busca por nombre/email de cliente)
    *   `filtroEstado`: string (`LEAD`, `ACTIVO`, `INACTIVO`, `PERDIDO`)
    *   `orden`: string (`asc` / `desc` para ordenar por fecha de creación)
*   **Respuesta (200 OK):**
    ```json
    {
      "cantidadClientes": 15,
      "clientes": [
        {
          "id": 4,
          "nombre": "Juan Pérez",
          "email": "juan@correo.com",
          "telefono": "+54 9 11 1234-5678",
          "estado": "LEAD"
        }
      ]
    }
    ```

### 🗂️ Pipeline Kanban (Visibilidad dinámica)
Devuelve todos los clientes del vendedor o de su equipo agrupados por estado para renderizar un tablero Kanban colaborativo.
*   **Ruta:** `GET /clientes/pipeline`
*   **Respuesta (200 OK):**
    ```json
    {
      "LEAD": [
        {
          "id": 1,
          "nombre": "Esteban Quito",
          "email": "esteban@correo.com",
          "telefono": "123456",
          "creado_en": "2026-05-20T09:12:30"
        }
      ],
      "ACTIVO": [],
      "INACTIVO": [],
      "PERDIDO": []
    }
    ```

### ➕ Crear Cliente
*   **Ruta:** `POST /clientes/`
*   **Body:**
    ```json
    {
      "nombre": "María López",
      "email": "maria@correo.com",
      "telefono": "987654321",
      "estado": "LEAD"
    }
    ```

### ✏️ Editar Cliente
*   **Ruta:** `PATCH /clientes/{cliente_id}`
*   **Body (Parcial):**
    ```json
    {
      "nombre": "María López Actualizado",
      "telefono": "555-5555"
    }
    ```

### 🗑️ Eliminar Cliente
*   **Ruta:** `DELETE /clientes/{cliente_id}`
*   **Respuesta:** `204 No Content`

### 🔄 Cambiar Estado de Cliente (Requiere rol ADMIN)
*   **Ruta:** `PUT /clientes/{cliente_id}/estado`
*   **Body (embed):**
    ```json
    {
      "estado": "ACTIVO"
    }
    ```

### 🤖 2.1 Resúmenes Ejecutivos de IA (MongoDB Caching & Gemini Flow)
Gestiona resúmenes comerciales automáticos del cliente basados en su historial, notas y tareas con Gemini 2.5 Flash.

#### 1. Obtener Resumen Guardado (Lectura Instantánea con Caché)
Intenta leer el último resumen guardado en MongoDB. Si no existe ningún resumen previo, dispara el modelo de IA para crearlo, lo persiste y lo retorna de inmediato.
*   **Ruta:** `GET /clientes/{cliente_id}/resumen-ia`
*   **Respuesta Exitosa (200 OK):**
    ```json
    {
      "cliente_id": 4,
      "resumen": "### Resumen Ejecutivo de IA\nEl cliente Juan Pérez se encuentra en estado LEAD...",
      "generado_en": "2026-06-01T19:40:00.000Z",
      "solicitado_por": {
        "user_id": 1,
        "nombre": "Nahuel",
        "apellido": "Monti"
      }
    }
    ```

#### 2. Forzar Regeneración de Resumen (POST)
Ignora la caché y re-ejecuta a Gemini para que construya un nuevo resumen fresco en base a la información actualizada (nuevas notas, cambios de Kanban, etc.) y lo guarde cronológicamente.
*   **Ruta:** `POST /clientes/{cliente_id}/resumen-ia`
*   **Respuesta Exitosa (200 OK):** Mismo formato que el endpoint anterior.

#### 3. Cargar Historial de Resúmenes (Línea de Tiempo)
Obtiene todos los resúmenes de IA históricos generados para este cliente en orden cronológico descendente. Ideal para pintar una línea de tiempo del progreso del cliente.
*   **Ruta:** `GET /clientes/{cliente_id}/resumen-ia/historial`
*   **Respuesta Exitosa (200 OK):**
    ```json
    [
      {
        "resumen": "### Resumen de Progreso\nEl cliente avanzó a estado LEAD...",
        "generado_en": "2026-06-01T19:40:00Z",
        "solicitado_por": {
          "user_id": 1,
          "nombre": "Nahuel",
          "apellido": "Monti"
        }
      },
      {
        "resumen": "### Resumen Inicial\nCliente registrado en frío...",
        "generado_en": "2026-05-28T10:15:00Z",
        "solicitado_por": {
          "user_id": 2,
          "nombre": "Matias",
          "apellido": "Calabrese"
        }
      }
    ]
    ```

---

## 📦 3. Productos & Categorías (Protegidos)

### ➕ Crear Producto
*   **Ruta:** `POST /productos/`
*   **Body:**
    ```json
    {
      "nombre": "Producto Increíble",
      "descripcion": "Descripción del producto",
      "precio": 1500.50,
      "sku": "PROD-12345",
      "id_categoria": 1,
      "inventario": {
        "stock": 50,
        "stock_minimo": 5
      }
    }
    ```

### ✏️ Editar Producto
*   **Ruta:** `PATCH /productos/{producto_id}`
*   **Body (Parcial):** Cualquier combinación de los campos anteriores.

### 🗑️ Eliminar Producto
*   **Ruta:** `DELETE /productos/{producto_id}`
*   **Respuesta:** `204 No Content`

### ⚙️ Ajustar Stock (Inventario)
*   **Ruta:** `PATCH /productos/{producto_id}/stock`
*   **Query Params:** `ajuste` (int, ej: `5` para sumar stock, `-2` para restar stock)
*   **Respuesta (200 OK):** Detalle del producto con su stock actualizado.

### 🗄️ Categorías
*   `GET /categorias/` -> Retorna listado de categorías.
*   `POST /categorias/` -> Crea una categoría `{"nombre": "...", "descripcion": "..."}`.
*   `PATCH /categorias/{categoria_id}` -> Modifica categoría.
*   `DELETE /categorias/{categoria_id}` -> Elimina categoría (204 No Content).

---

## 📡 4. Eventos en Tiempo Real (Socket.IO)

El servidor de Socket.IO está integrado en el mismo puerto que FastAPI (`http://localhost:8001`).

### Eventos que el Frontend debe escuchar para actualizar la UI automáticamente:

1.  **`cliente_creado`**
    *   **Cuándo ocurre:** Al registrar un cliente nuevo.
    *   **Payload:**
        ```json
        {
          "id": 5,
          "nombre": "María López",
          "estado": "LEAD",
          "usuario_id": 2
        }
        ```

2.  **`estado_cliente_cambiado`**
    *   **Cuándo ocurre:** Al mover un cliente en el Kanban o cambiar su estado.
    *   **Payload:**
        ```json
        {
          "cliente_id": 4,
          "nombre": "Juan Pérez",
          "estado_anterior": "LEAD",
          "nuevo_estado": "ACTIVO",
          "usuario_id": 1
        }
        ```

3.  **`producto_creado`**
    *   **Cuándo ocurre:** Al registrar un nuevo ítem en stock.
    *   **Payload:**
        ```json
        {
          "id": 10,
          "nombre": "Producto Nuevo",
          "precio": 450.00,
          "sku": "NEW-99"
        }
        ```

4.  **`stock_actualizado`**
    *   **Cuándo ocurre:** Al comprar o vender productos (ajuste de stock).
    *   **Payload:**
        ```json
        {
          "producto_id": 10,
          "nombre": "Producto Nuevo",
          "stock_anterior": 50,
          "nuevo_stock": 45,
          "ajuste": -5
        }
        ```

---

## 💬 5. Chat entre Colaboradores (NoSQL MongoDB + Socket.IO)

El sistema de mensajería utiliza una **persistencia políglota**:
*   **MySQL (SQL):** Valida la identidad y roles de los colaboradores.
*   **MongoDB (NoSQL):** Almacena las salas de chat y los buckets de mensajes (Bucket Pattern de hasta 50 mensajes para optimizar lectura y evitar límites de tamaño de documento de 16MB).
*   **Socket.IO:** Gestiona la conexión persistente bidireccional y la comunicación al instante.

---

### 🔑 A. Autenticación y Conexión WebSocket
Para conectar el cliente Socket.IO del frontend al backend, se debe proveer el Token JWT de acceso en el objeto de autenticación del handshake.

*   **URL de Conexión:** `http://localhost:8000` (o url del backend)
*   **Ejemplo de conexión en Frontend (Javascript):**
    ```javascript
    const socket = io("http://localhost:8000", {
      transports: ["websocket"],
      auth: {
        token: "TU_ACCESS_TOKEN_JWT" // (Sin el prefijo 'Bearer ')
      }
    });
    ```
> [!IMPORTANT]
> Si el token es inválido o no se envía, el backend rechazará la conexión inmediatamente por motivos de seguridad.

> [!CAUTION]
> **⚠️ BUG CRÍTICO DE SESIÓN CRUZADA (Solución en Frontend):**
> Si un colaborador cierra sesión y otro inicia sesión en la misma pestaña del navegador, el socket seguirá conectado físicamente utilizando el token y la sesión del usuario anterior en el servidor.
> **El Frontend tiene la obligación absoluta de:**
> 1. **Al hacer Logout:** Ejecutar de inmediato `socket.disconnect()` para matar físicamente la conexión y limpiar el socket.
> 2. **Al hacer Login:** Tras guardar el nuevo token, instanciar un nuevo cliente de socket pasando el nuevo token en la propiedad `auth.token`, y llamar explícitamente a `socket.connect()`.
> *Si no se desconecta físicamente el socket en el logout, el backend seguirá asumiendo que todos los eventos corresponden al usuario que inició sesión primero.*

---

### 🔌 B. Eventos Socket.IO (Tiempo Real)

#### 1. Unirse a una Sala de Chat (`join_conversation`)
Al abrir o hacer clic en un chat específico en la interfaz, el frontend debe indicarle al backend que se una al canal de esa conversación para empezar a escuchar sus mensajes en vivo.
*   **Evento (Cliente -> Servidor):** `join_conversation`
*   **Payload:**
    ```json
    {
      "conversation_id": "6a156265d8fa2808a69ad2da" // ID de MongoDB del chat
    }
    ```

#### 2. Salir de una Sala de Chat (`leave_conversation`)
Al cerrar la pestaña de chat o cambiar a otra conversación, el frontend debe desuscribirse de la sala actual para no recibir eventos en segundo plano innecesariamente.
*   **Evento (Cliente -> Servidor):** `leave_conversation`
*   **Payload:**
    ```json
    {
      "conversation_id": "6a156265d8fa2808a69ad2da"
    }
    ```

#### 3. Enviar Mensaje (`send_message`)
Envía un mensaje de texto a la conversación activa. El backend se encarga de persistirlo en MongoDB de forma asíncrona y distribuirlo a los demás participantes.
*   **Evento (Cliente -> Servidor):** `send_message`
*   **Payload:**
    ```json
    {
      "conversation_id": "6a156265d8fa2808a69ad2da",
      "content": "Hola Matias, ¿cómo vas con el reporte de stock?",
      "type": "text" // Por defecto 'text' (ampliable a 'image', 'file')
    }
    ```

#### 4. Recibir Mensaje en Vivo (`new_message`)
El backend emite este evento a todas las conexiones que estén unidas a la sala correspondiente. El frontend debe escuchar este evento para pintar el mensaje nuevo en pantalla al instante.
*   **Evento (Servidor -> Cliente):** `new_message`
*   **Payload:**
    ```json
    {
      "sender_id": 1,
      "sender_name": "Nahuel Monti",
      "content": "Hola Matias, ¿cómo vas con el reporte de stock?",
      "timestamp": "2026-05-26T19:12:01.000Z", // Formato ISO estricto UTC
      "type": "text",
      "conversation_id": "6a156265d8fa2808a69ad2da"
    }
    ```

#### 5. Confirmar Lectura / Marcar Visto (`read_conversation`)
Informa al backend que el colaborador ha abierto el chat o que ha recibido un mensaje entrante con la ventana activa. El backend actualiza su cursor temporal en MongoDB y lo difunde a la sala.
*   **Evento (Cliente -> Servidor):** `read_conversation`
*   **Payload:**
    ```json
    {
      "conversation_id": "6a156265d8fa2808a69ad2da"
    }
    ```

#### 6. Notificar Visto en Vivo (`conversation_read`)
El backend difunde este evento a todos los integrantes de la sala al registrarse una lectura. Permite cambiar al instante el color de los ticks de visto a azul en el frontend.
*   **Evento (Servidor -> Cliente):** `conversation_read`
*   **Payload:**
    ```json
    {
      "conversation_id": "6a156265d8fa2808a69ad2da",
      "user_id": 2, // ID del colaborador en MySQL que leyó la sala
      "read_at": "2026-05-26T19:56:00.000Z" // Timestamp ISO UTC de lectura
    }
    ```

---

### 🌐 C. Endpoints REST (HTTP) de Soporte

Todos estos endpoints requieren cabecera `Authorization: Bearer <access_token>`.

#### 1. Crear / Obtener Chat Directo 1-a-1
Busca si ya existe una sala de chat directa creada entre el usuario autenticado y otro colaborador. Si no existe, la crea dinámicamente.
*   **Ruta:** `POST /chat/direct`
*   **Query Params:**
    *   `other_user_id`: int (ID del otro colaborador en MySQL)
*   **Respuesta Exitosa (200 OK):**
    ```json
    {
      "id": "6a156265d8fa2808a69ad2da",
      "is_group": false,
      "created_at": "2026-05-26T06:05:00Z",
      "participants": [
        { "user_id": 1, "nombre": "Nahuel Monti", "rol": "ADMIN" },
        { "user_id": 2, "nombre": "Matias Calabrese", "rol": "VENDEDOR" }
      ],
      "last_message": null,
      "last_read": {}
    }
    ```

#### 2. Crear Sala de Chat Grupal
Crea una nueva sala de chat grupal con múltiples colaboradores. El creador del grupo se añade de manera automática a la lista de participantes.
*   **Ruta:** `POST /chat/group`
*   **Content-Type:** `application/json`
*   **Body:**
    ```json
    {
      "name": "Equipo de Ventas 🚀",
      "participant_ids": [2, 3]
    }
    ```
*   **Respuesta Exitosa (201 Created):**
    ```json
    {
      "id": "6a156265d8fa2808a69ad2db",
      "name": "Equipo de Ventas 🚀",
      "type": "group",
      "created_at": "2026-05-26T16:47:00Z",
      "participants": [
        { "user_id": 1, "nombre": "Nahuel Monti", "rol": "ADMIN" },
        { "user_id": 2, "nombre": "Matias Calabrese", "rol": "VENDEDOR" },
        { "user_id": 3, "nombre": "Facundo Gomez", "rol": "VENDEDOR" }
      ],
      "last_message": null,
      "last_read": {}
    }
    ```

#### 3. Listar Mis Conversaciones Activas
Obtiene un listado de todas las salas de chat (tanto 1-a-1 como grupales) en las que participa el colaborador autenticado. Útil para rellenar la barra lateral del chat.
> [!NOTE]
> **Optimización de Rendimiento (Chats Fantasma):**
> Para optimizar red y CPU, este listado filtra y **excluye** los chats directos (1-a-1) vacíos (`last_message: null`). Solo aparecerán en la barra lateral una vez que se envíe el primer mensaje. Los chats grupales se muestran siempre desde su creación.
*   **Ruta:** `GET /chat/conversations`
*   **Query Params (Opcionales):**
    *   `limit`: int (Defecto 50, rango de 1 a 100. Límite máximo de chats activos a retornar)
*   **Respuesta Exitosa (200 OK):**
    ```json
    [
      {
        "id": "6a156265d8fa2808a69ad2da",
        "is_group": false,
        "created_at": "2026-05-26T06:05:00Z",
        "participants": [
          { "user_id": 1, "nombre": "Nahuel Monti", "rol": "ADMIN" },
          { "user_id": 2, "nombre": "Matias Calabrese", "rol": "VENDEDOR" }
        ],
        "last_message": {
          "sender_id": 1,
          "sender_name": "Nahuel Monti",
          "content": "Hola Matias, ¿cómo vas con el reporte de stock?",
          "timestamp": "2026-05-26T19:12:01.000Z",
          "type": "text"
        },
        "last_read": {
          "1": "2026-05-26T19:12:01.000Z",
          "2": "2026-05-26T19:10:00.000Z"
        }
      }
    ]
    ```

#### 4. Obtener Historial de Mensajes (Paginado)
Carga los mensajes históricos de una conversación específica. Implementa el **Bucket Pattern**: cada página (`page=1`, `page=2`, etc.) representa un bucket completo de hasta 50 mensajes de MongoDB de forma cronológica descendente.
*   **Ruta:** `GET /chat/conversations/{conversation_id}/history`
*   **Query Params (Opcionales):**
    *   `page`: int (Defecto 1. `page=1` trae los últimos 50 mensajes, `page=2` del 51 al 100, etc.)
*   **Respuesta Exitosa (200 OK):**
    ```json
    [
      {
        "sender_id": 2,
        "sender_name": "Matias Calabrese",
        "content": "Buenas! Ya los cargué en el sistema.",
        "timestamp": "2026-05-26T19:15:00.000Z",
        "type": "text"
      },
      {
        "sender_id": 1,
        "sender_name": "Nahuel Monti",
        "content": "Hola Matias, ¿cómo vas con el reporte?",
        "timestamp": "2026-05-26T19:12:01.000Z",
        "type": "text"
      }
    ]
    ```
> [!TIP]
> **Diseño de UI Frontend sugerido para Historial:**
> Carga la página 1 al abrir el chat. Si el array de respuesta contiene **exactamente 50 elementos**, significa que hay más páginas disponibles. En ese caso, muestra un botón *"Cargar más"* arriba del chat, y al hacerle clic carga la página `2`, concatenando los mensajes viejos al inicio del panel.


---

## 👥 6. Grupos de Trabajo (Teams) & Jerarquía de Roles (Protegidos)

El módulo de Equipos organiza a los vendedores en células comerciales utilizando una arquitectura híbrida sincronizada en caliente con MongoDB para el chat de grupo.

### 👤 A. Registro de Colaboradores con Roles
Registra a un nuevo colaborador de la empresa.
*   **Ruta:** `POST /usuarios/register`
*   **Body:**
    ```json
    {
      "nombre": "Carlos",
      "apellido": "Monti",
      "email": "carlos@correo.com",
      "password": "contraseña_segura",
      "rol": "SUPERVISOR" // Valores permitidos: 'ADMIN', 'SUPERVISOR', 'VENDEDOR', 'CLIENTE', 'LEAD_WEB'
    }
    ```
*   **Respuesta Exitosa (201 Created):**
    ```json
    {
      "id": 4,
      "email": "carlos@correo.com",
      "rol": "SUPERVISOR",
      "es_activo": true,
      "nombre": "Carlos",
      "apellido": "Monti"
    }
    ```

---

### 🛡️ B. Endpoints de Grupos de Trabajo (`/grupos`)

#### 1. Crear Grupo de Trabajo (Solo ADMIN)
Crea un grupo de ventas en MySQL y le inicializa automáticamente una sala de chat grupal en MongoDB vinculada por `grupo_id`.
*   **Ruta:** `POST /grupos/`
*   **Body:**
    ```json
    {
      "nombre": "Ventas Latam",
      "descripcion": "Equipo comercial de LATAM"
    }
    ```
*   **Respuesta Exitosa (201 Created):**
    ```json
    {
      "id": 1,
      "nombre": "Ventas Latam",
      "descripcion": "Equipo comercial de LATAM",
      "creado_en": "2026-06-01T19:40:00Z",
      "chat_conversation_id": "6a156265d8fa2808a69ad2db",
      "miembros": []
    }
    ```

#### 2. Listar Todos los Grupos (Solo ADMIN)
Obtiene todos los grupos creados junto con la lista de sus miembros cargados en MySQL.
*   **Ruta:** `GET /grupos/`
*   **Respuesta Exitosa (200 OK):** Lista de objetos con el mismo formato que el response de creación.

#### 3. Obtener Mi Equipo (Público para usuarios firmados)
Retorna la ficha del equipo y la lista de todos los compañeros de trabajo del usuario autenticado de forma instantánea.
*   **Ruta:** `GET /grupos/mi-equipo`
*   **Respuesta Exitosa (200 OK):** Ficha de su grupo de ventas.
*   **Error (404 Not Found):** `{"detail": "No perteneces a ningún grupo de trabajo actualmente"}` si el usuario no tiene `grupo_id`.

#### 4. Obtener Grupo por ID (ADMIN o Miembros del mismo Grupo)
Retorna la información del grupo especificado.
*   **Restricción de Seguridad (Vendedores):** Un vendedor común tiene estrictamente prohibido espiar grupos ajenos. Si intenta consultar un ID que no es el suyo, el backend arrojará un error `403 Forbidden`. Los administradores pueden ver cualquiera.
*   **Ruta:** `GET /grupos/{grupo_id}`
*   **Respuesta Exitosa (200 OK):** Ficha detallada del grupo.

#### 5. Asignar Colaborador al Grupo (ADMIN o SUPERVISOR del Grupo)
Asocia a un usuario a un grupo de trabajo en MySQL, lo inyecta de forma atómica en los participantes del chat grupal en MongoDB y gatilla una notificación Socket.IO instantánea.
*   **Restricción de Seguridad (Supervisores):** Un `SUPERVISOR` únicamente puede asignar colaboradores a su **propio** grupo. Intentar asignar a un grupo ajeno lanzará un `403 Forbidden`.
*   **Ruta:** `POST /grupos/{grupo_id}/miembros`
*   **Body (embed):**
    ```json
    {
      "usuario_id": 4
    }
    ```
*   **Respuesta Exitosa (200 OK):**
    ```json
    {
      "mensaje": "Colaborador 'Carlos Monti' asignado al grupo 'Ventas Latam' con éxito",
      "grupo_id": 1,
      "usuario": {
        "user_id": 4,
        "nombre": "Carlos",
        "apellido": "Monti",
        "rol": "SUPERVISOR"
      }
    }
    ```

#### 6. Remover Colaborador del Grupo (ADMIN o SUPERVISOR del Grupo)
Desasocia a un colaborador de su grupo (colocando su `grupo_id` a `null` en MySQL) y lo remueve atómicamente de la lista de integrantes del chat de MongoDB, emitiendo una notificación push de Sockets.
*   **Restricción de Seguridad (Supervisores):** Un `SUPERVISOR` solo puede remover miembros de **su propio** grupo de trabajo.
*   **Ruta:** `DELETE /grupos/{grupo_id}/miembros/{usuario_id}`
*   **Respuesta Exitosa (200 OK):**
    ```json
    {
      "mensaje": "Colaborador 'Carlos Monti' removido del grupo 'Ventas Latam' con éxito",
      "grupo_id": 1,
      "usuario_id": 4
    }
    ```

#### 7. Eliminar Grupo de Trabajo (Solo ADMIN)
Elimina físicamente el grupo en MySQL (los miembros quedan independientes con `grupo_id=null`) y gatilla un pipeline de limpieza en MongoDB borrando la conversación y todos sus buckets de mensajes huérfanos.
*   **Ruta:** `DELETE /grupos/{grupo_id}`
*   **Respuesta Exitosa (200 OK):**
    ```json
    {
      "mensaje": "Grupo 'Ventas Latam' eliminado con éxito. Sus miembros han quedado libres e independientes.",
      "grupo_id": 1
    }
    ```

---

### 👤 C. Gestión Integral y Administración de Usuarios (Solo ADMIN)

#### 1. Listar Todos los Usuarios Registrados
Retorna el listado completo de usuarios registrados en el sistema de manera paginada.
*   **Ruta:** `GET /usuarios/`
*   **Query Params (Opcionales):**
    *   `skip`: int (Paginación, defecto 0)
    *   `limit`: int (Paginación, defecto 100)
*   **Respuesta Exitosa (200 OK):**
    ```json
    [
      {
        "id": 1,
        "email": "montinahuel@gmail.com",
        "rol": "ADMIN",
        "es_activo": true,
        "nombre": "Nahuel",
        "apellido": "Monti"
      },
      {
        "id": 2,
        "email": "matias@correo.com",
        "rol": "VENDEDOR",
        "es_activo": true,
        "nombre": "Matias",
        "apellido": "Calabrese"
      }
    ]
    ```

#### 2. Modificar Parcialmente un Usuario (PATCH)
Permite a un Administrador editar cualquier atributo de un colaborador, incluyendo el hasheo automático de contraseña, cambios de roles o estado activo.
*   **Ruta:** `PATCH /usuarios/{usuario_id}`
*   **Content-Type:** `application/json`
*   **Body (Parcial / Opcional):**
    ```json
    {
      "nombre": "Matias Modificado",
      "rol": "SUPERVISOR",
      "es_activo": true,
      "password": "nueva_password_hasheable"
    }
    ```
*   **Automatización de Negocio (Desvinculación en Caliente):**
    > [!IMPORTANT]
    > Si un Administrador cambia el rol de un colaborador a uno no comercial (ej: `CLIENTE` o `LEAD_WEB`) o desactiva su cuenta (`es_activo: false`), el backend **removerá automáticamente en caliente** al usuario de su correspondiente grupo de trabajo en MySQL y lo desasociará de los participantes del chat grupal en MongoDB.
*   **Respuesta Exitosa (200 OK):**
    ```json
    {
      "id": 2,
      "email": "matias@correo.com",
      "rol": "SUPERVISOR",
      "es_activo": true,
      "nombre": "Matias Modificado",
      "apellido": "Calabrese"
    }
    ```


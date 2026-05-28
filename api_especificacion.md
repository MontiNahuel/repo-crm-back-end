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

### 📋 Listar Clientes Propios (Con filtros)
*   **Ruta:** `GET /clientes/mis-clientes`
*   **Query Params (Opcionales):**
    *   `skip`: int (Paginación, defecto 0)
    *   `limit`: int (Paginación, defecto 100)
    *   `busqueda`: string (Busca por nombre/email)
    *   `filtroEstado`: string (`LEAD`, `ACTIVO`, `INACTIVO`, `PERDIDO`)
    *   `orden`: string (`asc` / `desc`)
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

### 🗂️ Pipeline Kanban
Devuelve todos los clientes del vendedor agrupados por estado para renderizar un tablero Kanban visual de inmediato.
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


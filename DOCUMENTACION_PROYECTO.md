```markdown
# DOCUMENTACIÓN DEL PROYECTO: Mi Librería Inteligente

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales (PDF y EPUB), facilitando la subida, organización por categorías y autores, búsqueda, lectura y descarga. Además, integra capacidades avanzadas de inteligencia artificial (IA) para analizar el contenido de los libros, extraer metadatos automáticamente y ofrecer una interfaz de conversación (RAG - Retrieval Augmented Generation) para interactuar directamente con el contenido de los libros mediante un modelo de lenguaje. También incluye herramientas prácticas como un conversor de EPUB a PDF.

La aplicación sigue una arquitectura de microservicios o monolito modular, con un frontend desarrollado en React y un potente backend en FastAPI, complementado con una base de datos SQLite para la persistencia de datos y ChromaDB para el almacenamiento de vectores semánticos en el contexto del RAG.

**Características Clave:**

*   **Gestión de Libros:** Sube, organiza y elimina libros PDF y EPUB.
*   **Análisis Inteligente:** Utiliza IA (Google Gemini) para extraer automáticamente el título, autor y categoría de los libros subidos.
*   **Búsqueda y Filtrado:** Busca libros por título, autor o categoría.
*   **Lectura y Descarga:** Lee libros EPUB directamente en el navegador y descarga PDFs o EPUBs.
*   **Conversión de Formato:** Herramienta para convertir archivos EPUB a PDF.
*   **Conversación con IA (RAG):** Permite a los usuarios hacer preguntas sobre el contenido de libros específicos y recibir respuestas generadas por IA, basadas en el texto del libro.
*   **Control de Acceso (CORS):** Configuración flexible para permitir el acceso desde diferentes orígenes de frontend.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales: `backend/` para la lógica del servidor y la API, y `frontend/src` para la interfaz de usuario.

```
.
├── backend/
│   ├── alembic/                      # Herramienta de migraciones de base de datos (SQLAlchemy Alembic)
│   │   └── versions/                 # Scripts de migración de la base de datos
│   ├── tests/                        # Pruebas unitarias para el backend
│   ├── tests_curated/                # Pruebas adicionales o curadas
│   ├── crud.py                       # Operaciones CRUD para la base de datos
│   ├── database.py                   # Configuración de la base de datos SQLAlchemy
│   ├── main.py                       # Aplicación FastAPI principal y definición de endpoints
│   ├── models.py                     # Definición de modelos de base de datos SQLAlchemy
│   ├── rag.py                        # Lógica de Retrieval Augmented Generation (RAG) e integración con ChromaDB/Gemini
│   ├── schemas.py                    # Esquemas de datos Pydantic para la API
│   └── utils.py                      # Funciones de utilidad (ej. configuración de la API de Gemini)
│
├── frontend/src/
│   ├── App.js                        # Componente principal de React y enrutamiento
│   ├── CategoriesView.js             # Vista para mostrar y gestionar categorías
│   ├── config.js                     # Configuración de la URL de la API
│   ├── ErrorBoundary.js              # Componente de React para manejo de errores en la UI
│   ├── Header.js                     # Componente del encabezado y navegación
│   ├── LibraryView.js                # Vista principal de la biblioteca (listado, búsqueda, eliminación)
│   ├── RagView.js                    # Vista para interactuar con el sistema RAG
│   ├── ReaderView.js                 # Vista para la lectura de libros EPUB
│   ├── ToolsView.js                  # Vista para herramientas adicionales (ej. conversión EPUB a PDF)
│   ├── UploadView.js                 # Vista para subir nuevos libros
│   ├── App.css                       # Estilos globales de la aplicación
│   ├── CategoriesView.css            # Estilos para la vista de categorías
│   ├── Header.css                    # Estilos para el encabezado
│   ├── index.css                     # Estilos base
│   ├── LibraryView.css               # Estilos para la vista de la biblioteca
│   ├── RagView.css                   # Estilos para la vista RAG
│   ├── ReaderView.css                # Estilos para la vista de lectura
│   ├── ToolsView.css                 # Estilos para la vista de herramientas
│   ├── UploadView.css                # Estilos para la vista de subida
│   └── reportWebVitals.js            # Utilidad para reportar métricas web
│
├── .env.example                      # Archivo de ejemplo para variables de entorno
├── library.db                        # Base de datos SQLite (generada por la app)
├── rag_index/                        # Directorio para el índice de ChromaDB (generado por la app)
└── README.md                         # Archivo README del proyecto
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend está construido con FastAPI, SQLAlchemy para la base de datos, Pydantic para la validación de datos, ChromaDB para el almacenamiento de embeddings y Google Gemini para las funcionalidades de IA.

### `backend/schemas.py`

Define los modelos de datos (Pydantic) para la validación de peticiones y la serialización de respuestas de la API.

*   **`BookBase(BaseModel)`**: Esquema base para los datos de un libro, utilizado para la creación.
    *   `title` (str): Título del libro.
    *   `author` (str): Autor del libro.
    *   `category` (str): Categoría a la que pertenece el libro.
    *   `cover_image_url` (str | None): URL opcional de la portada del libro.
    *   `file_path` (str): Ruta de archivo local donde se almacena el libro.
*   **`Book(BookBase)`**: Esquema completo de un libro, incluyendo el ID de la base de datos.
    *   `id` (int): Identificador único del libro en la base de datos.
    *   `Config.from_attributes = True`: Permite mapear directamente desde modelos ORM.
*   **`ConversionResponse(BaseModel)`**: Esquema para la respuesta de la conversión de archivos.
    *   `download_url` (str): URL para descargar el archivo convertido.
*   **`RagUploadResponse(BaseModel)`**: Esquema para la respuesta de subida de un libro para RAG.
    *   `book_id` (str): ID único asignado al libro para el sistema RAG.
    *   `message` (str): Mensaje de estado.
*   **`RagQuery(BaseModel)`**: Esquema para la consulta al sistema RAG.
    *   `query` (str): La pregunta del usuario.
    *   `book_id` (str): El ID del libro sobre el que se pregunta.
    *   `mode` (str | None): Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`).
*   **`RagQueryResponse(BaseModel)`**: Esquema para la respuesta del sistema RAG.
    *   `response` (str): La respuesta generada por la IA.

### `backend/models.py`

Define el modelo ORM (SQLAlchemy) para la tabla `books` en la base de datos.

*   **`Book(Base)`**: Representa la tabla `books`.
    *   `__tablename__ = "books"`: Nombre de la tabla en la base de datos.
    *   `__table_args__ = {'extend_existing': True}`: Permite redefinir la tabla en caso de hot-reloads (útil en desarrollo/pruebas).
    *   `id` (Column, Integer, primary_key=True, index=True): ID único del libro.
    *   `title` (Column, String, index=True): Título del libro.
    *   `author` (Column, String, index=True): Autor del libro.
    *   `category` (Column, String, index=True): Categoría del libro.
    *   `cover_image_url` (Column, String, nullable=True): URL de la portada. Puede ser nulo.
    *   `file_path` (Column, String, unique=True): Ruta única al archivo original del libro en el sistema de ficheros.

### `backend/database.py`

Configura la conexión a la base de datos SQLite y la sesión de SQLAlchemy.

*   `_base_dir`, `_db_path`: Calcula la ruta absoluta al archivo de la base de datos (`library.db`) en la raíz del proyecto.
*   `SQLALCHEMY_DATABASE_URL`: URL de conexión a la base de datos SQLite.
*   `engine`: Objeto `Engine` de SQLAlchemy, que gestiona la conexión a la DB. `connect_args={"check_same_thread": False}` es necesario para SQLite con múltiples hilos en FastAPI.
*   `SessionLocal`: Una factoría de sesiones que creará nuevas sesiones de base de datos.
*   `Base`: La clase base declarativa para los modelos ORM de SQLAlchemy.

### `backend/crud.py`

Contiene funciones para realizar operaciones de creación, lectura, actualización y eliminación (CRUD) en la base de datos de libros.

*   **`get_book_by_path(db: Session, file_path: str)`**:
    *   Obtiene un libro por su ruta de archivo única.
    *   **Parámetros**: `db` (sesión de DB), `file_path` (str).
    *   **Retorna**: El objeto `Book` si se encuentra, `None` en caso contrario.
*   **`get_book_by_title(db: Session, title: str)`**:
    *   Obtiene un libro por su título exacto.
    *   **Parámetros**: `db` (sesión de DB), `title` (str).
    *   **Retorna**: El objeto `Book` si se encuentra, `None` en caso contrario.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**:
    *   Busca libros cuyo título contenga la cadena proporcionada (case-insensitive) y soporta paginación.
    *   **Parámetros**: `db` (sesión de DB), `title` (str), `skip` (int), `limit` (int).
    *   **Retorna**: Una lista de objetos `Book`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**:
    *   Obtiene una lista de libros, con opciones de filtrado por categoría, autor, o una búsqueda general (título, autor, categoría). Los resultados se ordenan por ID descendente.
    *   **Parámetros**: `db` (sesión de DB), `category` (str | None), `search` (str | None), `author` (str | None).
    *   **Retorna**: Una lista de objetos `Book`.
*   **`get_categories(db: Session)`**:
    *   Obtiene una lista de todas las categorías de libros únicas, ordenadas alfabéticamente.
    *   **Parámetros**: `db` (sesión de DB).
    *   **Retorna**: `list[str]`.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**:
    *   Crea un nuevo libro en la base de datos.
    *   **Parámetros**: `db` (sesión de DB), `title` (str), `author` (str), `category` (str), `cover_image_url` (str), `file_path` (str).
    *   **Retorna**: El objeto `Book` recién creado.
*   **`delete_book(db: Session, book_id: int)`**:
    *   Elimina un libro de la base de datos por su ID, y también elimina los archivos asociados (libro y portada) del disco.
    *   **Parámetros**: `db` (sesión de DB), `book_id` (int).
    *   **Retorna**: El objeto `Book` eliminado si se encontró, `None` en caso contrario.
*   **`delete_books_by_category(db: Session, category: str)`**:
    *   Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados del disco.
    *   **Parámetros**: `db` (sesión de DB), `category` (str).
    *   **Retorna**: El número de libros eliminados.
*   **`get_books_count(db: Session)`**:
    *   Obtiene el número total de libros en la base de datos.
    *   **Parámetros**: `db` (sesión de DB).
    *   **Retorna**: `int`.

### `backend/utils.py`

Contiene funciones de utilidad, principalmente para la configuración de la API de Google Generative AI.

*   **`configure_genai()`**:
    *   Carga las variables de entorno desde un archivo `.env`.
    *   Busca la clave API (`GOOGLE_API_KEY` o `GEMINI_API_KEY`) y configura el SDK de Google Generative AI.
    *   **Eleva**: `ValueError` si no se encuentra ninguna clave API.

### `backend/rag.py`

Implementa la lógica del sistema de Retrieval Augmented Generation (RAG) utilizando ChromaDB para el almacenamiento de vectores y Google Gemini para la generación de embeddings y respuestas.

*   `_initialized`, `_collection`, `_ai_enabled`: Variables internas para gestionar la inicialización perezosa y el estado de la IA.
*   `EMBEDDING_MODEL`, `GENERATION_MODEL`: Modelos de Gemini configurables via variables de entorno, con valores por defecto.
*   **`_ensure_init()`**:
    *   Inicializa las variables de entorno, configura la API de Gemini (si `DISABLE_AI` no está activado) y se conecta a ChromaDB. Crea la colección `book_rag_collection` si no existe.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**:
    *   Genera un embedding (representación vectorial) para el texto dado usando el modelo de embedding de Gemini.
    *   Si `DISABLE_AI` está activo, devuelve un embedding dummy.
    *   **Parámetros**: `text` (str), `task_type` (str).
    *   **Retorna**: `list[float]` (el embedding).
*   **`extract_text_from_pdf(file_path: str)`**:
    *   Extrae texto de un archivo PDF usando `PyPDF2`.
    *   **Parámetros**: `file_path` (str).
    *   **Retorna**: `str` (el texto extraído).
*   **`extract_text_from_epub(file_path: str)`**:
    *   Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup` para procesar HTML.
    *   **Parámetros**: `file_path` (str).
    *   **Retorna**: `str` (el texto extraído).
*   **`extract_text(file_path: str)`**:
    *   Función unificada para extraer texto de archivos PDF o EPUB.
    *   **Parámetros**: `file_path` (str).
    *   **Eleva**: `ValueError` para tipos de archivo no soportados.
    *   **Retorna**: `str` (el texto extraído).
*   **`chunk_text(text: str, max_tokens: int = 1000)`**:
    *   Divide un texto largo en trozos más pequeños (chunks) basados en un número máximo de tokens, utilizando `tiktoken` para la tokenización.
    *   **Parámetros**: `text` (str), `max_tokens` (int).
    *   **Retorna**: `list[str]` (lista de chunks).
*   **`_has_index_for_book(book_id: str)`**:
    *   Comprueba si ya existen vectores indexados para un `book_id` dado en ChromaDB.
    *   **Parámetros**: `book_id` (str).
    *   **Retorna**: `bool`.
*   **`delete_book_from_rag(book_id: str)`**:
    *   Elimina todos los vectores asociados a un `book_id` de ChromaDB.
    *   **Parámetros**: `book_id` (str).
*   **`get_index_count(book_id: str)`**:
    *   Devuelve el número de vectores almacenados para un `book_id` en ChromaDB.
    *   **Parámetros**: `book_id` (str).
    *   **Retorna**: `int`.
*   **`has_index(book_id: str)`**:
    *   Función pública para verificar si un libro tiene índice RAG.
    *   **Parámetros**: `book_id` (str).
    *   **Retorna**: `bool`.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)` (async)**:
    *   Extrae texto de un libro, lo divide en chunks, genera embeddings para cada chunk y los almacena en ChromaDB.
    *   Si `force_reindex` es `True`, elimina los índices existentes antes de reindexar.
    *   **Parámetros**: `file_path` (str), `book_id` (str), `force_reindex` (bool).
    *   **Eleva**: `ValueError` si el tipo de archivo no es compatible o no se puede extraer texto.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**:
    *   Estima el número total de tokens y chunks para un archivo dado.
    *   **Parámetros**: `file_path` (str), `max_tokens` (int).
    *   **Retorna**: `dict` con `tokens` y `chunks`.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**:
    *   Estima el número total de tokens y chunks para una lista de archivos.
    *   **Parámetros**: `file_paths` (list[str]), `max_tokens` (int).
    *   **Retorna**: `dict` con `tokens`, `chunks` y `files` contados.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)` (async)**:
    *   Consulta el sistema RAG con una pregunta, recupera chunks relevantes del libro especificado y utiliza Gemini para generar una respuesta basada en el contexto recuperado, los metadatos del libro y el contexto de la biblioteca.
    *   `mode` controla cómo la IA integra el conocimiento del libro con el conocimiento general.
    *   **Parámetros**: `query` (str), `book_id` (str), `mode` (str), `metadata` (dict | None), `library` (dict | None).
    *   **Retorna**: `str` (la respuesta generada).

### `backend/main.py`

La aplicación principal de FastAPI, que define todos los endpoints de la API, la lógica de negocio y las integraciones con los módulos `crud`, `models`, `database` y `rag`.

*   **Configuración Inicial:**
    *   Define directorios estáticos para portadas (`STATIC_COVERS_DIR_FS`), archivos temporales (`TEMP_BOOKS_DIR_FS`), y libros subidos (`BOOKS_DIR_FS`).
    *   Configura middleware CORS para permitir peticiones desde el frontend, con orígenes configurables vía variables de entorno.
    *   Inicializa la base de datos de SQLAlchemy.
*   **`analyze_with_gemini(text: str)` (async)**:
    *   Usa el modelo de lenguaje de Gemini para analizar un texto extraído de un libro y detectar su título, autor y categoría.
    *   **Parámetros**: `text` (str).
    *   **Retorna**: `dict` con `title`, `author`, `category`.
*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str)`**:
    *   Extrae texto de las primeras páginas de un PDF y busca una imagen de portada.
    *   **Parámetros**: `file_path` (str), `covers_dir_fs` (str), `covers_url_prefix` (str).
    *   **Retorna**: `dict` con `text` y `cover_image_url`.
*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str)`**:
    *   Extrae texto de un EPUB y busca una imagen de portada, con lógica mejorada para encontrar portadas.
    *   **Parámetros**: `file_path` (str), `covers_dir_fs` (str), `covers_url_prefix` (str).
    *   **Retorna**: `dict` con `text` y `cover_image_url`.
*   **`get_db()`**:
    *   Función de dependencia para FastAPI que proporciona una sesión de base de datos a los endpoints.
*   **Endpoints de la API:**
    *   **`POST /upload-book/`**: Sube un archivo de libro (PDF o EPUB), lo procesa con Gemini para extraer metadatos, guarda el libro y su portada, y lo añade a la base de datos.
        *   **Entrada**: `UploadFile` (el archivo del libro).
        *   **Salida**: `schemas.Book`.
        *   **Eleva**: `HTTPException` (409 si el libro ya existe, 400 si el tipo de archivo no es soportado, 422 si la IA no puede analizar el libro).
    *   **`GET /books/`**: Obtiene una lista de libros, con opciones de filtrado por categoría, búsqueda general o autor.
        *   **Parámetros de consulta**: `category` (str), `search` (str), `author` (str).
        *   **Salida**: `List[schemas.Book]`.
    *   **`GET /books/count`**: Obtiene el número total de libros en la biblioteca.
        *   **Salida**: `int`.
    *   **`GET /books/search/`**: Busca libros por título parcial, con paginación.
        *   **Parámetros de consulta**: `title` (str), `skip` (int), `limit` (int).
        *   **Salida**: `List[schemas.Book]`.
    *   **`GET /categories/`**: Obtiene una lista de todas las categorías únicas de libros.
        *   **Salida**: `List[str]`.
    *   **`DELETE /books/{book_id}`**: Elimina un libro por su ID, junto con sus archivos asociados y los índices RAG.
        *   **Parámetros de ruta**: `book_id` (int).
        *   **Salida**: `{"message": str}`.
        *   **Eleva**: `HTTPException` (404 si el libro no existe).
    *   **`DELETE /categories/{category_name}`**: Elimina todos los libros de una categoría específica, sus archivos y sus índices RAG.
        *   **Parámetros de ruta**: `category_name` (str).
        *   **Salida**: `{"message": str}`.
        *   **Eleva**: `HTTPException` (404 si la categoría no existe o está vacía).
    *   **`GET /books/download/{book_id}`**: Permite descargar (o abrir en navegador) un libro por su ID.
        *   **Parámetros de ruta**: `book_id` (int).
        *   **Salida**: `FileResponse`.
        *   **Eleva**: `HTTPException` (404 si el libro o archivo no existen).
    *   **`POST /tools/convert-epub-to-pdf` (async)**: Convierte un archivo EPUB subido a PDF.
        *   **Entrada**: `UploadFile` (el archivo EPUB).
        *   **Salida**: `schemas.ConversionResponse`.
        *   **Eleva**: `HTTPException` (400 si no es EPUB, 500 si falla la conversión).
    *   **`POST /rag/upload-book/` (async)**: Sube un archivo y lo procesa para RAG, devolviendo un `book_id` para futuras consultas RAG.
        *   **Entrada**: `UploadFile` (el archivo del libro).
        *   **Salida**: `schemas.RagUploadResponse`.
        *   **Eleva**: `HTTPException` (500 si falla el procesamiento RAG).
    *   **`POST /rag/query/` (async)**: Realiza una consulta al sistema RAG sobre un libro específico.
        *   **Entrada**: `schemas.RagQuery`.
        *   **Salida**: `schemas.RagQueryResponse`.
        *   **Eleva**: `HTTPException` (500 si falla la consulta RAG).
    *   **`POST /rag/index/{book_id}` (async)**: Indexa un libro existente en la base de datos para RAG. Permite forzar la reindexación.
        *   **Parámetros de ruta**: `book_id` (int).
        *   **Parámetros de consulta**: `force` (bool).
        *   **Salida**: `{"message": str, "book_id": str, "force": bool}`.
        *   **Eleva**: `HTTPException` (404 si el libro o archivo no existen, 500 si falla el indexado).
    *   **`GET /rag/status/{book_id}`**: Devuelve el estado de indexación RAG para un libro.
        *   **Parámetros de ruta**: `book_id` (int).
        *   **Salida**: `{"book_id": str, "indexed": bool, "vector_count": int}`.
        *   **Eleva**: `HTTPException` (500 si falla la consulta de estado).
    *   **`POST /rag/reindex/category/{category_name}` (async)**: (Re)indexa todos los libros de una categoría para RAG.
        *   **Parámetros de ruta**: `category_name` (str).
        *   **Parámetros de consulta**: `force` (bool).
        *   **Salida**: `{"category": str, "processed": int, "failed": list, "force": bool}`.
        *   **Eleva**: `HTTPException` (404 si la categoría no existe o está vacía).
    *   **`POST /rag/reindex/all` (async)**: (Re)indexa todos los libros de la biblioteca para RAG.
        *   **Parámetros de consulta**: `force` (bool).
        *   **Salida**: `{"processed": int, "failed": list, "total": int, "force": bool}`.
    *   **`GET /rag/estimate/book/{book_id}`**: Estima tokens/chunks y coste potencial para un libro en RAG.
        *   **Parámetros de ruta**: `book_id` (int).
        *   **Parámetros de consulta**: `per1k` (float), `max_tokens` (int).
        *   **Salida**: `{"book_id": str, "tokens": int, "chunks": int, "per1k": float, "estimated_cost": float | None}`.
        *   **Eleva**: `HTTPException` (404 si el libro no existe, 500 si falla la estimación).
    *   **`GET /rag/estimate/category/{category_name}`**: Estima tokens/chunks y coste potencial para todos los libros de una categoría en RAG.
        *   **Parámetros de ruta**: `category_name` (str).
        *   **Parámetros de consulta**: `per1k` (float), `max_tokens` (int).
        *   **Salida**: `{"category": str, "tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float | None}`.
        *   **Eleva**: `HTTPException` (404 si la categoría no existe o está vacía, 500 si falla la estimación).
    *   **`GET /rag/estimate/all`**: Estima tokens/chunks y coste potencial para todos los libros de la biblioteca en RAG.
        *   **Parámetros de consulta**: `per1k` (float), `max_tokens` (int).
        *   **Salida**: `{"tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float | None}`.
        *   **Eleva**: `HTTPException` (500 si falla la estimación).

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

Script de migración de Alembic que define la estructura inicial de la tabla `books`. Contiene funciones `upgrade()` y `downgrade()` para aplicar y revertir los cambios en la base de datos.

### `backend/__init__.py`

Un archivo `__init__.py` vacío, que marca el directorio `backend` como un paquete Python.

## 4. Análisis Detallado del Frontend (React)

El frontend utiliza React con `react-router-dom` para el enrutamiento y `react-reader` para la lectura de EPUBs.

### `frontend/src/App.js`

El componente raíz de la aplicación React.

*   **Propósito:** Configura el enrutamiento de la aplicación utilizando `react-router-dom` y renderiza el `Header` y las diferentes vistas (páginas) de la aplicación.
*   **Estado (State) / Propiedades (Props):** No gestiona estado propio ni recibe props directamente.
*   **Efectos Secundarios (Effects):** Ninguno directamente en este componente.
*   **Interacciones del Usuario:** Gestiona la navegación entre las diferentes rutas/vistas.
*   **Comunicación con el Backend:** Indirectamente, a través de los componentes de vista que se renderizan.

### `frontend/src/Header.js`

El componente del encabezado de la aplicación, que incluye el título, el contador de libros y la navegación.

*   **Propósito:** Proporcionar una barra de navegación consistente y mostrar un contador en tiempo real del número de libros en la biblioteca.
*   **Estado (State):**
    *   `menuOpen` (boolean): Controla la visibilidad del menú de navegación en dispositivos móviles.
    *   `bookCount` (number): El número total de libros obtenidos del backend.
    *   `errorMessage` (string | null): Mensaje de error si la carga del contador falla.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect`: Al montarse el componente, realiza una llamada a la API (`/books/count`) para obtener el número de libros. También configura un intervalo para refrescar este contador cada 10 minutos.
*   **Interacciones del Usuario:**
    *   Clic en el botón de hamburguesa para abrir/cerrar el menú en móvil.
    *   Clic en los enlaces de navegación (`NavLink`) para cambiar de vista.
*   **Comunicación con el Backend:** Realiza una petición `GET` a `/books/count`.

### `frontend/src/LibraryView.js`

La vista principal de la biblioteca, donde se listan los libros, se permite buscar, filtrar y realizar acciones sobre ellos.

*   **Propósito:** Mostrar los libros de la biblioteca en una cuadrícula, permitir buscar, filtrar por autor/categoría y ofrecer opciones de descarga/lectura/eliminación.
*   **Estado (State):**
    *   `books` (array): La lista de libros cargados desde la API.
    *   `searchTerm` (string): El término de búsqueda introducido por el usuario.
    *   `debouncedSearchTerm` (string): Versión del `searchTerm` con debounce para evitar llamadas excesivas a la API.
    *   `error` (string): Mensaje de error si la carga o eliminación de libros falla.
    *   `loading` (boolean): Indica si la lista de libros se está cargando.
    *   `isMobile` (boolean): Detecta si el dispositivo es móvil para mostrar el botón de descarga condicionalmente.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect` (para `debouncedSearchTerm` y `searchParams`): Llama a `fetchBooks` cuando cambian el término de búsqueda o los parámetros de URL (categoría, autor).
    *   `useEffect` (para `isMobile`): Detecta el tamaño de la ventana para determinar si es un dispositivo móvil.
*   **Funciones / Lógica:**
    *   `useDebounce`: Custom hook para retrasar la ejecución de una función hasta que un valor no haya cambiado por un período determinado.
    *   `BookCover`: Componente para mostrar la portada del libro, con un fallback a una imagen genérica.
    *   `handleAuthorClick(author)`: Establece el filtro por autor.
    *   `handleCategoryClick(category)`: Establece el filtro por categoría.
    *   `fetchBooks()`: Realiza la llamada `GET` a `/books/` con los parámetros de búsqueda/filtrado.
    *   `handleDeleteBook(bookId)`: Llama a la API `DELETE /books/{book_id}` y actualiza la lista de libros.
*   **Interacciones del Usuario:**
    *   Introduce texto en la barra de búsqueda.
    *   Clic en el nombre del autor o la categoría para filtrar.
    *   Clic en el botón "Eliminar" (×) para borrar un libro.
    *   Clic en "Abrir PDF" / "Descargar PDF" / "Leer EPUB" para interactuar con el archivo del libro.
*   **Comunicación con el Backend:**
    *   `GET /books/`: Carga y busca libros.
    *   `DELETE /books/{book_id}`: Elimina libros.
    *   `GET /books/download/{book.id}`: Descarga o abre libros.

### `frontend/src/UploadView.js`

Permite a los usuarios subir uno o varios archivos de libros (PDF/EPUB) a la biblioteca.

*   **Propósito:** Facilitar la subida de nuevos libros al sistema, mostrando el progreso y el estado del procesamiento de cada archivo.
*   **Estado (State):**
    *   `filesToUpload` (array de objetos): Cada objeto representa un archivo con `file` (el objeto `File`), `status` (`'pending'`, `'uploading'`, `'success'`, `'error'`) y `message`.
    *   `isUploading` (boolean): Indica si hay archivos en proceso de subida.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):** Ninguno directamente.
*   **Funciones / Lógica:**
    *   `handleFileChange(event)`: Añade los archivos seleccionados por el input a `filesToUpload`.
    *   `handleDrop(event)` / `handleDragOver(event)`: Gestionan la funcionalidad de arrastrar y soltar archivos.
    *   `updateFileStatus(index, status, message)`: Actualiza el estado y mensaje de un archivo específico en `filesToUpload`.
    *   `handleUpload()`: Itera sobre `filesToUpload`, sube cada archivo usando `POST /upload-book/`, y actualiza su estado.
*   **Interacciones del Usuario:**
    *   Selecciona archivos usando el botón o arrastra y suelta.
    *   Clic en "Subir Archivo(s)" para iniciar el proceso.
    *   Clic en "Ir a la Biblioteca" cuando todas las subidas han finalizado.
*   **Comunicación con el Backend:**
    *   `POST /upload-book/`: Sube el archivo del libro para su procesamiento.

### `frontend/src/ReaderView.js`

Vista dedicada a la lectura de archivos EPUB directamente en el navegador.

*   **Propósito:** Proporcionar una interfaz de lectura para libros en formato EPUB.
*   **Estado (State):**
    *   `location` (string | null): Ubicación actual del lector dentro del EPUB (CFI).
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB.
    *   `isLoading` (boolean): Indica si el EPUB se está cargando.
    *   `error` (string): Mensaje de error si la carga del EPUB falla.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect` (para `bookId`): Al montarse o cambiar el `bookId` de los parámetros de URL, realiza una llamada `GET` a `/books/download/{bookId}` para obtener los datos binarios del EPUB.
*   **Interacciones del Usuario:** Navega por el EPUB usando la interfaz del lector.
*   **Comunicación con el Backend:**
    *   `GET /books/download/{bookId}`: Descarga el archivo EPUB como un ArrayBuffer.

### `frontend/src/ToolsView.js`

Una vista que agrupa diferentes herramientas de utilidad para la biblioteca. Actualmente, solo incluye un convertidor de EPUB a PDF.

*   **Propósito:** Ofrecer herramientas adicionales a los usuarios.
*   **Componentes Internos:**
    *   **`EpubToPdfConverter`**:
        *   **Estado (State):** `selectedFile`, `message`, `isLoading`.
        *   **Funciones / Lógica:**
            *   `handleFileChange`: Establece el archivo EPUB seleccionado.
            *   `handleDrop` / `handleDragOver`: Implementa la funcionalidad de arrastrar y soltar para archivos.
            *   `handleConvert`: Llama a `POST /tools/convert-epub-to-pdf` para enviar el archivo EPUB y, si la conversión es exitosa, inicia la descarga del PDF resultante.
        *   **Interacciones del Usuario:** Selecciona/arrastra un archivo EPUB, hace clic en "Convertir a PDF".
        *   **Comunicación con el Backend:** `POST /tools/convert-epub-to-pdf`.
*   **Estado (State) / Propiedades (Props) / Efectos Secundarios (Effects) de `ToolsView`:** Mínimos, actúa como contenedor.
*   **Comunicación con el Backend:** A través de sus componentes hijos.

### `frontend/src/RagView.js`

La interfaz para interactuar con el sistema de Conversación Inteligente (RAG).

*   **Propósito:** Permitir al usuario seleccionar un libro de su biblioteca, indexarlo para RAG si es necesario, y luego hacer preguntas sobre su contenido para recibir respuestas generadas por IA.
*   **Estado (State):**
    *   `message` (string): Mensajes informativos para el usuario.
    *   `isLoading` (boolean): Indica si la IA está generando una respuesta.
    *   `bookId` (string | null): El ID del libro actualmente seleccionado para el chat RAG.
    *   `chatHistory` (array de objetos): Historial de mensajes de la conversación (usuario y Gemini).
    *   `currentQuery` (string): La pregunta actual del usuario.
    *   `libraryBooks` (array): Lista de todos los libros en la biblioteca.
    *   `selectedLibraryId` (string): El ID del libro seleccionado en el buscador de la biblioteca.
    *   `libStatus` (object): Estado de indexación RAG del libro seleccionado (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy` (boolean): Bloquea las acciones de indexación/reindexación.
    *   `refreshing` (boolean): Indica si se está refrescando el estado RAG.
    *   `searchTerm` (string): Término de búsqueda para libros de la biblioteca.
    *   `searching` (boolean): Indica si se está buscando en la biblioteca.
    *   `searchResults` (array): Resultados de la búsqueda de libros.
    *   `resultsOpen` (boolean): Controla la visibilidad de los resultados de búsqueda.
    *   `mode` (string): El modo de respuesta de la IA ('strict', 'balanced', 'open').
    *   `selectedBook` (object | null): El objeto Book completo del libro seleccionado.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect` (auto-scroll): Desplaza automáticamente al final del chat cuando se actualiza el historial o el estado de carga.
    *   `useEffect` (carga de libros): Al montarse, carga la lista completa de libros de la biblioteca.
    *   `useEffect` (búsqueda de libros): Realiza una búsqueda "debounced" de libros cuando `searchTerm` cambia.
    *   `useEffect` (estado RAG): Cuando `selectedLibraryId` cambia, comprueba automáticamente el estado de indexación RAG del libro.
*   **Funciones / Lógica:**
    *   `currentBook` (useMemo): Calcula el libro actualmente conversado.
    *   `focusChatInput`: Intenta enfocar el input del chat.
    *   `handleQuerySubmit(event)`: Envía la pregunta del usuario a la API `POST /rag/query/` y actualiza el historial del chat.
    *   `checkLibraryStatus(silent)`: Llama a `GET /rag/status/{book_id}` para verificar si un libro está indexado.
    *   `indexLibraryBook(force)`: Llama a `POST /rag/index/{book_id}` para indexar un libro.
*   **Interacciones del Usuario:**
    *   Busca libros por título/autor/categoría.
    *   Selecciona un libro de los resultados de búsqueda.
    *   Clica en "Comprobar RAG", "Indexar" o "Reindexar".
    *   Elige un "Modo de respuesta" para la IA.
    *   Escribe preguntas en el área de texto y las envía para chatear con la IA.
*   **Comunicación con el Backend:**
    *   `GET /books/`: Carga la lista de libros de la biblioteca.
    *   `GET /books/?search=...`: Busca libros en la biblioteca.
    *   `GET /rag/status/{book_id}`: Obtiene el estado de indexación RAG de un libro.
    *   `POST /rag/index/{book_id}`: Indexa un libro para RAG.
    *   `POST /rag/query/`: Envía la consulta a la IA para obtener una respuesta.

### `frontend/src/config.js`

Archivo simple para gestionar la URL base de la API.

*   **Propósito:** Centralizar la configuración de la URL del backend, facilitando el despliegue en diferentes entornos.
*   `API_URL`: Exporta la URL, obteniéndola de la variable de entorno `REACT_APP_API_URL` o usando `http://localhost:8001` como fallback.

### `frontend/src/CategoriesView.js`

Muestra una lista de todas las categorías de libros disponibles como enlaces navegables.

*   **Propósito:** Proporcionar una vista para explorar la biblioteca por categorías.
*   **Estado (State):**
    *   `categories` (array de strings): La lista de categorías únicas obtenidas del backend.
    *   `error` (string): Mensaje de error si la carga de categorías falla.
    *   `loading` (boolean): Indica si las categorías se están cargando.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect`: Al montarse, realiza una llamada a la API (`/categories/`) para obtener la lista de categorías.
*   **Interacciones del Usuario:** Clic en una tarjeta de categoría para navegar a la `LibraryView` filtrada por esa categoría.
*   **Comunicación con el Backend:**
    *   `GET /categories/`: Obtiene la lista de categorías.

### `frontend/src/ErrorBoundary.js`

Un componente React de "Error Boundary" para capturar y mostrar errores en la interfaz de usuario.

*   **Propósito:** Mejorar la resiliencia de la aplicación, capturando errores de JavaScript en el árbol de componentes y mostrando una interfaz de usuario alternativa en lugar de bloquear toda la aplicación.
*   **Estado (State):**
    *   `hasError` (boolean): Indica si un error ha sido capturado.
    *   `error` (Error | null): El objeto de error capturado.
*   **Métodos de Ciclo de Vida:**
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para indicar que se ha producido un error.
    *   `componentDidCatch(error, info)`: Registra el error en la consola.
*   **Retorno:** Si `hasError` es `true`, renderiza un mensaje de error; de lo contrario, renderiza los componentes hijos.

### `frontend/src/index.js`

El punto de entrada principal para el renderizado de la aplicación React.

*   **Propósito:** Montar el componente `App` en el elemento DOM con ID `root`.
*   **Lógica:** Utiliza `ReactDOM.createRoot` para el renderizado concurrente y `React.StrictMode` para activar comprobaciones adicionales en desarrollo. También incluye `reportWebVitals` para medir el rendimiento.

## 5. Flujo de Datos y API

El flujo de datos en "Mi Librería Inteligente" es bidireccional entre el frontend de React y el backend de FastAPI. La comunicación se realiza mediante peticiones HTTP a los endpoints de la API RESTful.

### Ejemplo de Flujo de Datos: Subida de un Libro

1.  **Frontend (`UploadView.js`):**
    *   El usuario selecciona un archivo (PDF o EPUB) o lo arrastra a la zona de subida.
    *   `handleFileChange` o `handleDrop` actualiza el estado `filesToUpload` con el archivo y un estado `'pending'`.
    *   El usuario hace clic en "Subir Archivo(s)".
    *   `handleUpload` inicia el proceso: para cada archivo, establece el estado a `'uploading'`.
    *   Crea un objeto `FormData` y añade el archivo bajo la clave `book_file`.
    *   Realiza una petición `POST` a `/upload-book/` con el `FormData`.

2.  **Backend (`main.py` - Endpoint `/upload-book/`):**
    *   FastAPI recibe el `UploadFile`.
    *   Verifica si un libro con la misma `file_path` ya existe usando `crud.get_book_by_path`. Si existe, devuelve un error 409.
    *   Guarda el archivo en el directorio `backend/books/`.
    *   Determina el tipo de archivo (PDF/EPUB) y llama a `process_pdf` o `process_epub` para extraer el texto inicial y la portada.
    *   Llama a `analyze_with_gemini` con el texto extraído para obtener el título, autor y categoría.
    *   Implementa una "Puerta de Calidad": si Gemini no puede determinar el título y autor, se borra el archivo y se devuelve un error 422.
    *   Si el análisis es exitoso, llama a `crud.create_book` para añadir el libro a la base de datos (SQLite).
    *   El libro recién creado (objeto `schemas.Book`) es devuelto al frontend.

3.  **Frontend (`UploadView.js`):**
    *   Recibe la respuesta del backend.
    *   Si es `OK` (`200`): Actualiza el estado del archivo a `'success'` con el título del libro.
    *   Si hay un error: Actualiza el estado del archivo a `'error'` con el mensaje de error del backend.
    *   Una vez que todos los archivos se han procesado, el usuario puede navegar a la `LibraryView`.

### Principales Endpoints de la API

| Método | Ruta                                  | Descripción                                                                 | Petición (Body)                                                                                             | Respuesta                                                                  |
| :----- | :------------------------------------ | :-------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| `POST` | `/upload-book/`                       | Sube y procesa un libro (PDF/EPUB) con IA, añadiéndolo a la biblioteca.     | `multipart/form-data` con `book_file`                                                                       | `schemas.Book`                                                             |
| `GET`  | `/books/`                             | Obtiene libros con filtros opcionales (`category`, `search`, `author`).     | (Query params)                                                                                              | `List[schemas.Book]`                                                       |
| `GET`  | `/books/count`                        | Obtiene el número total de libros.                                          | -                                                                                                           | `int`                                                                      |
| `GET`  | `/books/search/`                      | Busca libros por título parcial.                                            | (Query param `title`, `skip`, `limit`)                                                                      | `List[schemas.Book]`                                                       |
| `GET`  | `/categories/`                        | Obtiene una lista de todas las categorías únicas.                           | -                                                                                                           | `List[str]`                                                                |
| `DELETE`| `/books/{book_id}`                    | Elimina un libro y sus archivos.                                            | -                                                                                                           | `{"message": str}`                                                         |
| `DELETE`| `/categories/{category_name}`         | Elimina todos los libros de una categoría y sus archivos.                   | -                                                                                                           | `{"message": str}`                                                         |
| `GET`  | `/books/download/{book_id}`           | Descarga o visualiza un libro.                                              | -                                                                                                           | `FileResponse`                                                             |
| `POST` | `/tools/convert-epub-to-pdf`          | Convierte un archivo EPUB a PDF.                                            | `multipart/form-data` con `file`                                                                            | `schemas.ConversionResponse`                                               |
| `POST` | `/rag/index/{book_id}`                | Indexa un libro existente para RAG.                                         | (Query param `force`)                                                                                       | `{"message": str, "book_id": str, "force": bool}`                          |
| `GET`  | `/rag/status/{book_id}`               | Obtiene el estado de indexación RAG de un libro.                            | -                                                                                                           | `{"book_id": str, "indexed": bool, "vector_count": int}`                   |
| `POST` | `/rag/query/`                         | Realiza una consulta RAG sobre un libro.                                    | `schemas.RagQuery`                                                                                          | `schemas.RagQueryResponse`                                                 |
| `POST` | `/rag/reindex/category/{category_name}`| (Re)indexa todos los libros de una categoría.                              | (Query param `force`)                                                                                       | `{"category": str, "processed": int, "failed": list, "force": bool}`       |
| `POST` | `/rag/reindex/all`                    | (Re)indexa todos los libros de la biblioteca.                               | (Query param `force`)                                                                                       | `{"processed": int, "failed": list, "total": int, "force": bool}`          |
| `GET`  | `/rag/estimate/book/{book_id}`        | Estima tokens/chunks y coste para el indexado RAG de un libro.              | (Query params `per1k`, `max_tokens`)                                                                        | `{"book_id": str, "tokens": int, "chunks": int, "per1k": float, "estimated_cost": float | None}` |
| `GET`  | `/rag/estimate/category/{category_name}`| Estima tokens/chunks y coste para el indexado RAG de una categoría.         | (Query params `per1k`, `max_tokens`)                                                                        | `{"category": str, "tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float | None}` |
| `GET`  | `/rag/estimate/all`                   | Estima tokens/chunks y coste para el indexado RAG de toda la biblioteca.    | (Query params `per1k`, `max_tokens`)                                                                        | `{"tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float | None}` |
```
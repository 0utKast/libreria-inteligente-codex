# Documentación Técnica: Mi Librería Inteligente

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web full-stack diseñada para gestionar una colección personal de libros digitales, ofreciendo funcionalidades avanzadas de catalogación y un sistema de preguntas y respuestas impulsado por inteligencia artificial (RAG - Retrieval Augmented Generation).

La aplicación permite a los usuarios subir libros en formatos PDF y EPUB. Utiliza capacidades de IA para analizar automáticamente el contenido de los libros, extraer metadatos como el título, autor y categoría, y generar portadas. Los libros se almacenan de forma organizada y pueden ser explorados, buscados y descargados. Además, incorpora una herramienta para convertir archivos EPUB a PDF.

La característica más destacada es su módulo de IA conversacional. Una vez que un libro es "indexado", los usuarios pueden chatear con una IA sobre su contenido, obteniendo respuestas directamente extraídas o inferidas del texto del libro, con opciones de modos de respuesta (estricto, equilibrado, abierto) para controlar la integración con el conocimiento general de la IA.

### Arquitectura General

El proyecto sigue una arquitectura cliente-servidor con los siguientes componentes principales:

*   **Frontend (React.js):** Una interfaz de usuario moderna y reactiva que permite a los usuarios interactuar con la librería. Gestiona la carga de archivos, la visualización de libros, la navegación por categorías, la interfaz de chat con IA y la herramienta de conversión.
*   **Backend (FastAPI con Python):** Una API RESTful de alto rendimiento que maneja toda la lógica de negocio. Se encarga de la gestión de archivos, la interacción con la base de datos, el procesamiento de documentos (extracción de texto y portadas), la integración con los modelos de IA de Google Gemini, y la lógica RAG.
*   **Base de Datos (SQLite):** Una base de datos ligera y basada en archivos (`library.db`) que almacena los metadatos de los libros (título, autor, categoría, URL de portada, ruta de archivo).
*   **Motor de RAG (ChromaDB):** Una base de datos vectorial embebida (`rag_index/`) utilizada para almacenar los "embeddings" (representaciones numéricas) de los fragmentos de texto de los libros. Esto permite una búsqueda semántica eficiente de información relevante durante las consultas de IA.
*   **Modelos de IA (Google Gemini):** Se utilizan dos tipos de modelos Gemini:
    *   **Generación de Contenido:** Para analizar libros y extraer metadatos (`gemini-2.5-flash` o `GEMINI_MODEL_MAIN`). También se usa para generar respuestas en el módulo RAG (`gemini-2.5-flash` o `GEMINI_GENERATION_MODEL`).
    *   **Embeddings:** Para crear representaciones vectoriales del texto (`text-embedding-004` o `GEMINI_EMBEDDING_MODEL`) que ChromaDB utiliza para la búsqueda de similitud.
*   **Almacenamiento de Archivos:** Los libros originales (PDF/EPUB) y las portadas extraídas se almacenan en el sistema de archivos del servidor.
*   **Conversión EPUB a PDF:** Utiliza librerías como `PyPDF2`, `ebooklib`, `BeautifulSoup`, y `WeasyPrint` para el procesamiento y conversión de documentos.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales: `backend/` para la lógica del servidor y `frontend/` para la interfaz de usuario.

```
.
├── backend/
│   ├── alembic/                    # Migraciones de base de datos SQLAlchemy (Alembic)
│   │   ├── versions/               # Scripts de migración específicos
│   │   └── env.py
│   ├── books/                      # Almacena los archivos de libros originales subidos
│   ├── static/                     # Archivos estáticos servidos por FastAPI
│   │   └── covers/                 # Almacena las imágenes de portada extraídas
│   ├── temp_books/                 # Almacena archivos temporales (e.g., PDFs convertidos de EPUB, libros para RAG temporal)
│   ├── tests/                      # Archivos de pruebas unitarias para el backend
│   ├── tests_curated/              # Pruebas adicionales o "curadas"
│   ├── crud.py                     # Operaciones CRUD para la base de datos de libros
│   ├── database.py                 # Configuración de la base de datos SQLAlchemy
│   ├── main.py                     # Aplicación FastAPI principal y endpoints de la API
│   ├── models.py                   # Definiciones de modelos de base de datos (SQLAlchemy ORM)
│   ├── __init__.py                 # Marca el directorio 'backend' como un paquete Python
│   ├── rag.py                      # Lógica de Retrieval Augmented Generation (RAG)
│   ├── schemas.py                  # Modelos Pydantic para validación de datos de la API
│   └── utils.py                    # Funciones de utilidad generales (e.g., configuración de IA)
├── frontend/
│   ├── public/                     # Archivos públicos para el frontend (HTML, etc.)
│   ├── src/                        # Código fuente de la aplicación React
│   │   ├── App.css
│   │   ├── App.js                  # Componente principal de la aplicación React
│   │   ├── CategoriesView.css
│   │   ├── CategoriesView.js       # Vista para mostrar y navegar por categorías
│   │   ├── config.js               # Configuración de la URL del API
│   │   ├── ErrorBoundary.js        # Componente para manejo de errores en React
│   │   ├── Header.css
│   │   ├── Header.js               # Componente de encabezado y navegación
│   │   ├── index.css
│   │   ├── index.js                # Punto de entrada de la aplicación React
│   │   ├── LibraryView.css
│   │   ├── LibraryView.js          # Vista principal de la librería de libros
│   │   ├── RagView.css
│   │   ├── RagView.js              # Vista para la conversación inteligente con libros (RAG)
│   │   ├── ReaderView.css
│   │   ├── ReaderView.js           # Vista para leer libros EPUB
│   │   ├── ToolsView.css
│   │   └── ToolsView.js            # Vista que contiene herramientas (e.g., convertidor EPUB a PDF)
│   ├── package.json                # Dependencias y scripts del frontend
│   └── README.md
├── library.db                      # Archivo de base de datos SQLite (se genera aquí)
├── rag_index/                      # Almacena los índices vectoriales de ChromaDB
└── .env                            # Variables de entorno (no incluido en el repo, pero usado)
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/schemas.py`

Define los modelos de datos para la validación de solicitudes (request) y respuestas (response) de la API utilizando Pydantic.

*   **`class BookBase(BaseModel)`**:
    *   **Propósito**: Esquema base para los datos de un libro, utilizado principalmente para la creación.
    *   **Campos**:
        *   `title` (str): Título del libro.
        *   `author` (str): Autor del libro.
        *   `category` (str): Categoría a la que pertenece el libro.
        *   `cover_image_url` (str | None): URL opcional de la portada del libro.
        *   `file_path` (str): Ruta absoluta al archivo del libro en el sistema.
*   **`class Book(BookBase)`**:
    *   **Propósito**: Extiende `BookBase` para incluir el `id` del libro, utilizado para representar libros recuperados de la base de datos.
    *   **Campos**:
        *   `id` (int): Identificador único del libro en la base de datos.
    *   **Config**: `from_attributes = True` permite mapear directamente desde modelos ORM.
*   **`class ConversionResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta de la API de conversión de EPUB a PDF.
    *   **Campos**:
        *   `download_url` (str): URL donde se puede descargar el archivo PDF convertido temporalmente.
*   **`class RagUploadResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta al subir un libro para procesamiento RAG.
    *   **Campos**:
        *   `book_id` (str): ID único (UUID) asignado al libro para el contexto RAG.
        *   `message` (str): Mensaje de confirmación.
*   **`class RagQuery(BaseModel)`**:
    *   **Propósito**: Esquema para la solicitud de consulta al módulo RAG.
    *   **Campos**:
        *   `query` (str): La pregunta del usuario.
        *   `book_id` (str): El ID del libro sobre el que se consulta (corresponde al ID de BD).
        *   `mode` (str | None): Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`). Por defecto es `None` (se manejará en el backend).
*   **`class RagQueryResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta de una consulta RAG.
    *   **Campos**:
        *   `response` (str): La respuesta generada por la IA.

### `backend/crud.py`

Contiene funciones para interactuar con la base de datos de libros, encapsulando las operaciones CRUD (Crear, Leer, Actualizar, Borrar).

*   **`get_book_by_path(db: Session, file_path: str)`**:
    *   **Lógica**: Busca un libro por su ruta de archivo única.
    *   **Parámetros**: `db` (Session), `file_path` (str).
    *   **Retorno**: `models.Book` o `None`.
*   **`get_book_by_title(db: Session, title: str)`**:
    *   **Lógica**: Busca un libro por su título exacto.
    *   **Parámetros**: `db` (Session), `title` (str).
    *   **Retorno**: `models.Book` o `None`.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**:
    *   **Lógica**: Busca libros con títulos que contienen una subcadena (case-insensitive) y soporta paginación.
    *   **Parámetros**: `db` (Session), `title` (str), `skip` (int), `limit` (int).
    *   **Retorno**: `list[models.Book]`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**:
    *   **Lógica**: Recupera una lista de libros, permitiendo filtrar por categoría, autor (parcial, case-insensitive) o una búsqueda general (título, autor, categoría). Ordena por ID descendente.
    *   **Parámetros**: `db` (Session), `category` (str | None), `search` (str | None), `author` (str | None).
    *   **Retorno**: `list[models.Book]`.
*   **`get_categories(db: Session)`**:
    *   **Lógica**: Obtiene una lista de todas las categorías únicas de libros existentes en la base de datos, ordenadas alfabéticamente.
    *   **Parámetros**: `db` (Session).
    *   **Retorno**: `list[str]`.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**:
    *   **Lógica**: Crea una nueva entrada de libro en la base de datos, añade el objeto, lo guarda y lo refresca para obtener el ID.
    *   **Parámetros**: `db` (Session), `title` (str), `author` (str), `category` (str), `cover_image_url` (str), `file_path` (str).
    *   **Retorno**: `models.Book`.
*   **`delete_book(db: Session, book_id: int)`**:
    *   **Lógica**: Elimina un libro por su ID. También se encarga de eliminar los archivos asociados (libro y portada) del sistema de archivos.
    *   **Parámetros**: `db` (Session), `book_id` (int).
    *   **Retorno**: `models.Book` si se encontró y eliminó, `None` en caso contrario.
*   **`delete_books_by_category(db: Session, category: str)`**:
    *   **Lógica**: Elimina todos los libros que pertenecen a una categoría específica, junto con sus archivos asociados.
    *   **Parámetros**: `db` (Session), `category` (str).
    *   **Retorno**: `int` (número de libros eliminados).
*   **`get_books_count(db: Session)`**:
    *   **Lógica**: Devuelve el número total de libros en la base de datos.
    *   **Parámetros**: `db` (Session).
    *   **Retorno**: `int`.

### `backend/database.py`

Configura la conexión a la base de datos SQLite y define los componentes necesarios para SQLAlchemy.

*   **`_base_dir`, `_db_path`**: Rutas para construir la ubicación de la base de datos SQLite. `library.db` se ubicará en la raíz del proyecto.
*   **`SQLALCHEMY_DATABASE_URL`**: Cadena de conexión a la base de datos SQLite. `connect_args={"check_same_thread": False}` es necesario para SQLite con FastAPI/Uvicorn.
*   **`engine`**: El motor de SQLAlchemy que gestiona la conexión a la base de datos.
*   **`SessionLocal`**: Una clase de sesión que se utiliza para crear instancias de sesión de base de datos (`db`).
*   **`Base`**: La clase base declarativa de SQLAlchemy a partir de la cual se heredarán los modelos ORM.

### `backend/utils.py`

Contiene funciones de utilidad diversas. Actualmente, solo una función para configurar la API de Gemini.

*   **`configure_genai()`**:
    *   **Lógica**: Carga las variables de entorno (`.env`) y configura la API de Google Generative AI (Gemini) utilizando `GOOGLE_API_KEY` o `GEMINI_API_KEY`. Lanza un `ValueError` si no se encuentra ninguna clave.
    *   **Parámetros**: Ninguno.
    *   **Retorno**: Ninguno.

### `backend/models.py`

Define el modelo ORM (Object-Relational Mapping) para los libros en la base de datos, utilizando SQLAlchemy.

*   **`class Book(Base)`**:
    *   **`__tablename__ = "books"`**: Nombre de la tabla en la base de datos.
    *   **`__table_args__ = {'extend_existing': True}`**: Permite redefinir la tabla si ya existe (útil en algunos contextos, como pruebas).
    *   **Columnas**:
        *   `id` (Integer, primary_key=True, index=True): Clave primaria autoincremental.
        *   `title` (String, index=True): Título del libro.
        *   `author` (String, index=True): Autor del libro.
        *   `category` (String, index=True): Categoría del libro.
        *   `cover_image_url` (String, nullable=True): URL a la imagen de portada.
        *   `file_path` (String, unique=True): Ruta al archivo original del libro.

### `backend/rag.py`

Implementa la lógica central del sistema Retrieval Augmented Generation (RAG).

*   **Variables Globales y Configuración**:
    *   `_initialized`, `_collection`, `_ai_enabled`: Controlan la inicialización del módulo.
    *   `EMBEDDING_MODEL`, `GENERATION_MODEL`: Modelos de Gemini utilizados, configurables por variables de entorno.
*   **`_ensure_init()`**:
    *   **Lógica**: Función interna para asegurar que las variables de entorno se han cargado, la API de Gemini está configurada (a menos que `DISABLE_AI` esté activado), y el cliente de ChromaDB está inicializado y conectado a la colección `book_rag_collection`.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**:
    *   **Lógica**: Genera un embedding vectorial para el texto dado utilizando el modelo Gemini configurado. Si la IA está deshabilitada, devuelve un embedding dummy.
    *   **Parámetros**: `text` (str), `task_type` (str).
    *   **Retorno**: `list[float]` (el vector embedding).
*   **`extract_text_from_pdf(file_path: str)`**:
    *   **Lógica**: Extrae texto de un archivo PDF página por página usando `PyPDF2`.
    *   **Parámetros**: `file_path` (str).
    *   **Retorno**: `str` (texto extraído).
*   **`extract_text_from_epub(file_path: str)`**:
    *   **Lógica**: Extrae texto de un archivo EPUB iterando sobre sus ítems de documento y usando `BeautifulSoup` para limpiar el HTML.
    *   **Parámetros**: `file_path` (str).
    *   **Retorno**: `str` (texto extraído).
*   **`extract_text(file_path: str)`**:
    *   **Lógica**: Función unificada que llama al extractor de texto adecuado según la extensión del archivo.
    *   **Parámetros**: `file_path` (str).
    *   **Retorno**: `str` (texto extraído).
    *   **Excepciones**: `ValueError` para tipos de archivo no soportados.
*   **`chunk_text(text: str, max_tokens: int = 1000)`**:
    *   **Lógica**: Divide un texto largo en fragmentos más pequeños, asegurando que cada fragmento no exceda `max_tokens`. Utiliza `tiktoken` para el conteo de tokens.
    *   **Parámetros**: `text` (str), `max_tokens` (int).
    *   **Retorno**: `list[str]` (lista de fragmentos de texto).
*   **`_has_index_for_book(book_id: str)`**:
    *   **Lógica**: Comprueba si ya existen vectores indexados para un `book_id` dado en ChromaDB.
    *   **Parámetros**: `book_id` (str).
    *   **Retorno**: `bool`.
*   **`delete_book_from_rag(book_id: str)`**:
    *   **Lógica**: Elimina todos los vectores asociados a un `book_id` de ChromaDB.
    *   **Parámetros**: `book_id` (str).
    *   **Retorno**: Ninguno.
*   **`get_index_count(book_id: str)`**:
    *   **Lógica**: Devuelve el número de vectores almacenados para un `book_id`.
    *   **Parámetros**: `book_id` (str).
    *   **Retorno**: `int`.
*   **`has_index(book_id: str)`**:
    *   **Lógica**: Wrapper público para `get_index_count` para verificar si un libro tiene índice.
    *   **Parámetros**: `book_id` (str).
    *   **Retorno**: `bool`.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**:
    *   **Lógica**: Procesa un libro completo para el sistema RAG. Extrae el texto, lo divide en fragmentos, genera embeddings para cada fragmento y los almacena en ChromaDB junto con los metadatos (`book_id`, `chunk_index`). Puede forzar la reindexación.
    *   **Parámetros**: `file_path` (str), `book_id` (str), `force_reindex` (bool).
    *   **Retorno**: Ninguno.
    *   **Excepciones**: `ValueError` si el tipo de archivo no es soportado o no se puede extraer/fragmentar texto.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**:
    *   **Lógica**: Estima el número total de tokens y chunks para un archivo dado. Útil para predecir costos de indexación.
    *   **Parámetros**: `file_path` (str), `max_tokens` (int).
    *   **Retorno**: `dict` con `tokens` y `chunks`.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**:
    *   **Lógica**: Estima tokens y chunks para una lista de archivos.
    *   **Parámetros**: `file_paths` (list[str]), `max_tokens` (int).
    *   **Retorno**: `dict` con `tokens`, `chunks` y `files`.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**:
    *   **Lógica**: Realiza una consulta al sistema RAG. Genera un embedding para la consulta, recupera los fragmentos más relevantes de ChromaDB para el `book_id` dado, construye un prompt con el contexto y los metadatos/información de la biblioteca, y utiliza el modelo de generación Gemini para producir una respuesta. El comportamiento de la respuesta se ajusta según el `mode`.
    *   **Parámetros**: `query` (str), `book_id` (str), `mode` (str), `metadata` (dict | None), `library` (dict | None).
    *   **Retorno**: `str` (la respuesta generada por la IA).

### `backend/main.py`

Es el archivo principal de la aplicación FastAPI. Contiene la configuración de la API, la lógica de procesamiento de archivos, la integración con Gemini y todos los endpoints de la API.

*   **Configuración Inicial**:
    *   Carga variables de entorno.
    *   Configura la API de Gemini (si `AI_ENABLED` es `True`).
    *   Crea las tablas de la base de datos si no existen (`models.Base.metadata.create_all`).
    *   Define y crea directorios para archivos estáticos (`static/`, `static/covers/`), libros (`books/`) y temporales (`temp_books/`).
    *   Monta directorios estáticos para servir archivos.
    *   Configura `CORSMiddleware` para permitir solicitudes desde el frontend (con opciones flexibles para desarrollo en redes privadas).
*   **`get_db()`**:
    *   **Propósito**: Función de dependencia de FastAPI para obtener una sesión de base de datos SQLAlchemy. Asegura que la sesión se cierre correctamente después de su uso.
    *   **Parámetros**: Ninguno.
    *   **Retorno**: Un generador que produce una `Session` de SQLAlchemy.
*   **`analyze_with_gemini(text: str)`**:
    *   **Propósito**: Envía un fragmento de texto a un modelo Gemini para extraer el título, autor y categoría de un libro.
    *   **Parámetros**: `text` (str, las primeras páginas del libro).
    *   **Retorno**: `dict` con las claves `title`, `author`, `category`. Devuelve valores por defecto "Error de IA" en caso de fallo o "Desconocido" si no puede determinar un valor.
*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str)`**:
    *   **Propósito**: Extrae el texto de las primeras páginas de un PDF y busca una posible imagen de portada, guardándola si se encuentra.
    *   **Parámetros**: `file_path` (str), `covers_dir_fs` (str, ruta al directorio de portadas), `covers_url_prefix` (str, prefijo URL para las portadas).
    *   **Retorno**: `dict` con `text` (texto extraído) y `cover_image_url` (URL de la portada o `None`).
*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str)`**:
    *   **Propósito**: Extrae el texto de las primeras páginas de un EPUB y busca una imagen de portada, con lógica de fallback si no se encuentra la oficial.
    *   **Parámetros**: `file_path` (str), `covers_dir_fs` (str, ruta al directorio de portadas), `covers_url_prefix` (str, prefijo URL para las portadas).
    *   **Retorno**: `dict` con `text` (texto extraído) y `cover_image_url` (URL de la portada o `None`).
    *   **Excepciones**: `HTTPException` si no se puede extraer suficiente texto.
*   **Endpoints de la API**:
    *   `POST /upload-book/`: Sube un nuevo libro (PDF/EPUB). Procesa el archivo, analiza con Gemini y lo guarda en la base de datos. (`schemas.Book`)
    *   `GET /books/`: Recupera una lista de libros, con opciones de filtrado por `category`, `search` y `author`. (`List[schemas.Book]`)
    *   `GET /books/count`: Devuelve el número total de libros en la base de datos. (`int`)
    *   `GET /books/search/`: Busca libros por título parcial con paginación. (`List[schemas.Book]`)
    *   `GET /categories/`: Obtiene una lista de todas las categorías únicas. (`List[str]`)
    *   `DELETE /books/{book_id}`: Elimina un libro específico por su ID, incluyendo archivos asociados y el índice RAG.
    *   `DELETE /categories/{category_name}`: Elimina todos los libros de una categoría, incluyendo archivos asociados e índices RAG.
    *   `GET /books/download/{book_id}`: Permite descargar o abrir un libro existente.
    *   `POST /tools/convert-epub-to-pdf`: Convierte un archivo EPUB subido a PDF y devuelve una URL temporal de descarga. (`schemas.ConversionResponse`)
    *   `POST /rag/upload-book/`: Sube un libro (PDF/EPUB) para indexar en RAG (temporalmente). Devuelve un `book_id` para la interacción RAG. (`schemas.RagUploadResponse`)
    *   `POST /rag/query/`: Envía una consulta a la IA sobre un libro indexado en RAG. (`schemas.RagQueryResponse`)
    *   `POST /rag/index/{book_id}`: Indexa un libro existente en la base de datos para el sistema RAG.
    *   `GET /rag/status/{book_id}`: Devuelve el estado de indexación RAG para un libro.
    *   `POST /rag/reindex/category/{category_name}`: (Re)indexa todos los libros de una categoría específica en RAG.
    *   `POST /rag/reindex/all`: (Re)indexa todos los libros de la biblioteca en RAG.
    *   `GET /rag/estimate/book/{book_id}`: Estima el número de tokens y chunks para un libro.
    *   `GET /rag/estimate/category/{category_name}`: Estima tokens y chunks para todos los libros de una categoría.
    *   `GET /rag/estimate/all`: Estima tokens y chunks para todos los libros de la biblioteca.

### `backend/__init__.py`

*   **Propósito**: Un archivo vacío que simplemente marca el directorio `backend` como un paquete Python, permitiendo la importación de sus módulos.

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

*   **Propósito**: Script de migración de la base de datos generado por Alembic. Define cómo crear y eliminar la tabla `books`.
*   **`upgrade()`**:
    *   **Lógica**: Crea la tabla `books` con columnas `id`, `title`, `author`, `category`, `cover_image_url`, `file_path`. Establece `id` como clave primaria y `file_path` como única. Crea índices en `id`, `title`, `author` y `category` para mejorar el rendimiento de las consultas.
*   **`downgrade()`**:
    *   **Lógica**: Elimina la tabla `books` y sus índices asociados.

### `backend/tests/`

Este directorio contiene varias pruebas unitarias y de integración para el backend, asegurando la calidad y el comportamiento esperado de las diferentes partes del sistema.

*   **Propósito**: Verificar la funcionalidad de módulos individuales (`crud.py`, `models.py`, `schemas.py`, `utils.py`, `rag.py`) y los endpoints de la API (`main.py`). Utilizan `unittest.mock` y `pytest` para simular dependencias externas y la base de datos, lo que permite pruebas aisladas y deterministas. También incluye pruebas para el proceso de generación automática de tests.

## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

*   **Propósito**: Es el componente raíz de la aplicación React. Configura el enrutamiento de la aplicación (`react-router-dom`) y define la estructura general del diseño.
*   **Estado (State)**: Ninguno directamente.
*   **Props**: Ninguna.
*   **Efectos Secundarios (Effects)**: Ninguno directamente.
*   **Interacciones y Comunicación con Backend**: Se limita a montar los componentes de vista que a su vez interactúan con el backend.

### `frontend/src/Header.js`

*   **Propósito**: Componente de navegación global que incluye el título de la aplicación, un contador de libros y enlaces a las diferentes vistas.
*   **Estado (State)**:
    *   `menuOpen` (boolean): Controla la visibilidad del menú de navegación en pantallas pequeñas.
    *   `bookCount` (number): Número total de libros en la biblioteca.
    *   `errorMessage` (string | null): Mensaje de error si falla la carga del contador de libros.
*   **Props**: Ninguna.
*   **Efectos Secundarios (Effects)**:
    *   `useEffect` al montar el componente: Realiza una llamada a la API (`${API_URL}/books/count`) para obtener el número de libros. También configura un intervalo para refrescar el contador periódicamente (cada 10 minutos).
*   **Interacciones y Comunicación con Backend**: Realiza solicitudes `GET` al endpoint `/books/count`.

### `frontend/src/ToolsView.js`

*   **Propósito**: Contiene varias herramientas de utilidad para la librería. Actualmente, solo el `EpubToPdfConverter`.
*   **Estado (State)**: Ninguno directamente.
*   **Props**: Ninguna.
*   **Efectos Secundarios (Effects)**: Ninguno directamente.
*   **Interacciones y Comunicación con Backend**: Ninguno directamente, delega en los componentes de herramientas hijos.

#### `EpubToPdfConverter` (dentro de `ToolsView.js`)

*   **Propósito**: Permite al usuario subir un archivo EPUB y convertirlo a PDF a través del backend.
*   **Estado (State)**:
    *   `selectedFile` (File | null): El archivo EPUB seleccionado por el usuario.
    *   `message` (string): Mensaje de estado para el usuario (éxito, error, progreso).
    *   `isLoading` (boolean): Indica si la conversión está en progreso.
*   **Props**: Ninguna.
*   **Efectos Secundarios (Effects)**: Ninguno directamente.
*   **Interacciones y Comunicación con Backend**:
    *   `handleConvert` (función): Envía el archivo seleccionado mediante una solicitud `POST` a `${API_URL}/tools/convert-epub-to-pdf`. Si la conversión es exitosa, el backend devuelve una URL de descarga, que se utiliza para iniciar la descarga en el navegador.

### `frontend/src/UploadView.js`

*   **Propósito**: Proporciona una interfaz para que los usuarios suban uno o varios archivos de libros (PDF o EPUB) al sistema.
*   **Estado (State)**:
    *   `filesToUpload` (Array de objetos `{ file: File, status: string, message: string }`): Lista de archivos seleccionados con su estado de carga.
    *   `isUploading` (boolean): Indica si hay archivos en proceso de subida.
*   **Props**: Ninguna.
*   **Efectos Secundarios (Effects)**: Ninguno directamente.
*   **Interacciones y Comunicación con Backend**:
    *   `handleUpload` (función): Itera sobre `filesToUpload`, enviando cada archivo individualmente a `${API_URL}/upload-book/` mediante una solicitud `POST` con `FormData`. Actualiza el estado de cada archivo (pendiente, subiendo, éxito, error) según la respuesta del backend.
    *   Navega a la vista principal (`/`) si todos los archivos han terminado de procesarse.

### `frontend/src/ReaderView.js`

*   **Propósito**: Permite a los usuarios leer libros en formato EPUB directamente en el navegador utilizando la librería `react-reader`.
*   **Estado (State)**:
    *   `location` (string | null): La posición actual de lectura en el EPUB (EPUB CFI).
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB.
    *   `isLoading` (boolean): Indica si el libro se está cargando.
    *   `error` (string): Mensaje de error si la carga falla.
*   **Props**:
    *   `bookId` (string): ID del libro a leer, obtenido de los parámetros de la URL (`useParams`).
*   **Efectos Secundarios (Effects)**:
    *   `useEffect` al cambiar `bookId`: Realiza una solicitud `GET` a `${API_URL}/books/download/${bookId}` para obtener los datos binarios del EPUB. Los datos se cargan como `ArrayBuffer` para ser pasados a `react-reader`.
*   **Interacciones y Comunicación con Backend**: Realiza solicitudes `GET` al endpoint `/books/download/{bookId}`.

### `frontend/src/ErrorBoundary.js`

*   **Propósito**: Un componente estándar de React que captura errores JavaScript en cualquier parte de su árbol de componentes hijo, los registra y muestra una interfaz de usuario de fallback en lugar de dejar que la aplicación se bloquee por completo.
*   **Estado (State)**:
    *   `hasError` (boolean): Indica si se ha detectado un error.
    *   `error` (Error | null): El objeto de error capturado.
*   **Props**:
    *   `children`: Los componentes que envuelve el `ErrorBoundary`.
*   **Efectos Secundarios (Effects)**:
    *   `componentDidCatch`: Un método de ciclo de vida que se utiliza para registrar información del error.
*   **Interacciones y Comunicación con Backend**: Ninguna.

### `frontend/src/RagView.js`

*   **Propósito**: Proporciona una interfaz para interactuar con la IA conversacional (RAG) sobre el contenido de los libros. Permite seleccionar un libro de la biblioteca, indexarlo y luego chatear.
*   **Estado (State)**:
    *   `message` (string): Mensajes de estado para el usuario.
    *   `isLoading` (boolean): Indica si la IA está generando una respuesta.
    *   `bookId` (string | null): El ID del libro actualmente seleccionado para el chat RAG (una vez indexado).
    *   `chatHistory` (Array de objetos `{ sender: 'user' | 'gemini', text: string }`): Historial de la conversación.
    *   `currentQuery` (string): La consulta actual escrita por el usuario.
    *   `libraryBooks` (Array): Lista de todos los libros en la biblioteca.
    *   `selectedLibraryId` (string): El ID del libro seleccionado en la interfaz de usuario para el RAG.
    *   `libStatus` (objeto): Contiene el estado de indexación RAG del libro seleccionado (cargando, indexado, conteo de vectores, error).
    *   `actionsBusy` (boolean): Bloquea las acciones de indexación/reindexación para evitar múltiples ejecuciones.
    *   `refreshing` (boolean): Indica si se está refrescando el estado RAG.
    *   `searchTerm` (string): Término de búsqueda para libros de la biblioteca.
    *   `searching` (boolean): Indica si la búsqueda de libros está activa.
    *   `searchResults` (Array): Resultados de la búsqueda de libros.
    *   `resultsOpen` (boolean): Controla la visibilidad de los resultados de búsqueda.
    *   `mode` (string): El modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`).
    *   `selectedBook` (object | null): Objeto completo del libro seleccionado.
*   **Props**: Ninguna.
*   **Efectos Secundarios (Effects)**:
    *   `useEffect` para `chatHistory`, `isLoading`: Auto-scroll al final del chat.
    *   `useEffect` al montar: Carga `libraryBooks` de la API.
    *   `useEffect` para `searchTerm`: Implementa un debounce para la búsqueda de libros en la biblioteca.
    *   `useEffect` para `selectedLibraryId`: Llama a `checkLibraryStatus` para obtener el estado RAG del libro seleccionado.
*   **Interacciones y Comunicación con Backend**:
    *   `handleQuerySubmit` (función): Envía la `currentQuery` y el `bookId` a `${API_URL}/rag/query/` mediante `POST`. Actualiza `chatHistory` con la pregunta del usuario y la respuesta de Gemini.
    *   `checkLibraryStatus` (función): Obtiene el estado de indexación RAG de un libro desde `${API_URL}/rag/status/${bookId}`.
    *   `indexLibraryBook` (función): Llama a `${API_URL}/rag/index/${bookId}` mediante `POST` para indexar o reindexar un libro.
    *   Realiza solicitudes `GET` a `/books/` para poblar la lista de libros de la biblioteca.

### `frontend/src/LibraryView.js`

*   **Propósito**: La vista principal que muestra la colección de libros, permitiendo buscar, filtrar por categoría o autor, y gestionar los libros (abrir/descargar, eliminar).
*   **Estado (State)**:
    *   `books` (Array): Lista de objetos de libros recuperados de la API.
    *   `searchTerm` (string): El texto introducido en la barra de búsqueda.
    *   `debouncedSearchTerm` (string): Versión con "debounce" de `searchTerm` para evitar demasiadas llamadas a la API.
    *   `error` (string): Mensaje de error si la carga de libros falla.
    *   `loading` (boolean): Indica si los libros se están cargando.
    *   `isMobile` (boolean): Detecta si la pantalla es móvil para adaptar la UI.
*   **Props**: Ninguna.
*   **Efectos Secundarios (Effects)**:
    *   `useDebounce` (custom hook): Retrasa la actualización de `debouncedSearchTerm` para optimizar las llamadas a la API de búsqueda.
    *   `useEffect` al montar y al cambiar `debouncedSearchTerm` o `searchParams`: Llama a `fetchBooks` para obtener libros según los filtros y la búsqueda.
    *   `useEffect` para `resize`: Detecta el tamaño de la ventana para `isMobile`.
*   **Interacciones y Comunicación con Backend**:
    *   `fetchBooks` (función): Realiza una solicitud `GET` a `${API_URL}/books/` con parámetros de consulta (`category`, `author`, `search`).
    *   `handleDeleteBook` (función): Envía una solicitud `DELETE` a `${API_URL}/books/${bookId}` para eliminar un libro.
    *   Los enlaces de descarga/lectura apuntan a `${API_URL}/books/download/${book.id}` o a la ruta `/leer/:bookId` para EPUBs.

### `frontend/src/config.js`

*   **Propósito**: Define la URL base del backend de la API.
*   **Contenido**: `const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';`
*   **Nota**: Permite configurar la URL de la API mediante una variable de entorno `REACT_APP_API_URL`, útil para entornos de producción o desarrollo. Por defecto, usa `http://localhost:8001`.

### `frontend/src/CategoriesView.js`

*   **Propósito**: Muestra una lista de todas las categorías de libros disponibles en la biblioteca.
*   **Estado (State)**:
    *   `categories` (Array): Lista de cadenas de categorías.
    *   `error` (string): Mensaje de error si la carga falla.
    *   `loading` (boolean): Indica si las categorías se están cargando.
*   **Props**: Ninguna.
*   **Efectos Secundarios (Effects)**:
    *   `useEffect` al montar el componente: Realiza una solicitud `GET` a `${API_URL}/categories/` para obtener la lista de categorías.
*   **Interacciones y Comunicación con Backend**: Realiza solicitudes `GET` al endpoint `/categories/`.

### `frontend/src/index.js`

*   **Propósito**: El punto de entrada principal de la aplicación React. Renderiza el componente `App` en el elemento DOM con `id="root"`.
*   **Contenido**: Configuración estándar de un proyecto React. Incluye `React.StrictMode` para desarrollo y `reportWebVitals` para medir el rendimiento.

## 5. Flujo de Datos y API

### Flujo de Carga de Libros

1.  **Frontend (UploadView)**: El usuario selecciona un archivo (PDF o EPUB) y hace clic en "Subir".
2.  **Frontend a Backend**: `UploadView` envía una solicitud `POST` a `/upload-book/` con el archivo como `FormData`.
3.  **Backend (main.py)**:
    *   Guarda el archivo en el directorio `backend/books/`.
    *   Detecta el tipo de archivo (PDF/EPUB) y lo procesa (`process_pdf` o `process_epub`) para extraer texto de las primeras páginas y, si es posible, una imagen de portada. La portada se guarda en `backend/static/covers/`.
    *   Envía el texto extraído a la función `analyze_with_gemini` para que la IA determine el título, autor y categoría.
    *   Si la IA logra identificar el libro, `main.py` llama a `crud.create_book`.
4.  **Backend (crud.py)**: `create_book` guarda los metadatos del libro (título, autor, categoría, URL de portada, ruta de archivo) en la base de datos SQLite (`library.db`).
5.  **Backend a Frontend**: El backend responde con los detalles del libro recién creado, que `UploadView` muestra al usuario.
6.  **Frontend**: Tras el éxito, el usuario puede navegar a `LibraryView` para ver el libro.

### Flujo de Navegación y Búsqueda de Libros

1.  **Frontend (LibraryView)**: El usuario navega a la vista de librería, introduce un término de búsqueda, o hace clic en un autor/categoría para filtrar.
2.  **Frontend a Backend**: `LibraryView` envía una solicitud `GET` a `/books/` (o `/books/search/` para búsqueda avanzada) con los parámetros de filtro/búsqueda correspondientes.
3.  **Backend (main.py)**: El endpoint `/books/` invoca a `crud.get_books` (o `crud.get_books_by_partial_title` para `/books/search/`).
4.  **Backend (crud.py)**: `get_books` (o `get_books_by_partial_title`) consulta la base de datos `library.db` para obtener los libros que coinciden con los criterios.
5.  **Backend a Frontend**: El backend devuelve una lista de objetos de libro (según `schemas.Book`).
6.  **Frontend**: `LibraryView` renderiza la lista de libros, mostrando sus portadas y metadatos.

### Flujo de Conversión EPUB a PDF

1.  **Frontend (ToolsView -> EpubToPdfConverter)**: El usuario selecciona un archivo EPUB y hace clic en "Convertir".
2.  **Frontend a Backend**: `EpubToPdfConverter` envía una solicitud `POST` a `/tools/convert-epub-to-pdf` con el archivo EPUB.
3.  **Backend (main.py)**:
    *   Recibe el archivo EPUB.
    *   Descomprime el EPUB en un directorio temporal.
    *   Utiliza `BeautifulSoup` y `WeasyPrint` para procesar el contenido HTML y CSS del EPUB y renderizarlo como PDF.
    *   Guarda el PDF resultante en el directorio temporal `backend/temp_books/`.
4.  **Backend a Frontend**: El backend responde con una `download_url` que apunta al PDF temporal.
5.  **Frontend**: `EpubToPdfConverter` crea un enlace invisible y simula un clic para iniciar la descarga del PDF convertido.

### Flujo de Chat RAG con la IA

1.  **Frontend (RagView)**:
    *   El usuario busca y selecciona un libro de la biblioteca.
    *   `RagView` comprueba el estado RAG del libro (`GET /rag/status/{book_id}`).
    *   Si el libro no está indexado, el usuario hace clic en "Indexar antes de charlar" (`POST /rag/index/{book_id}`).
    *   Una vez indexado, el usuario introduce una pregunta en el chat.
2.  **Frontend a Backend**: `RagView` envía una solicitud `POST` a `/rag/query/` con la pregunta (`query`) y el `book_id`.
3.  **Backend (main.py)**: El endpoint `/rag/query/` recupera metadatos adicionales del libro desde la BD y llama a `rag.query_rag`.
4.  **Backend (rag.py)**:
    *   Genera un embedding de la `query` del usuario.
    *   Utiliza este embedding para buscar los fragmentos de texto más relevantes en ChromaDB (índice vectorial) que pertenecen al `book_id` dado.
    *   Construye un prompt para Gemini, incluyendo la pregunta, los fragmentos relevantes (contexto del libro) y los metadatos del libro.
    *   Envía el prompt al modelo de generación Gemini para obtener una respuesta. El `mode` de la consulta influye en cómo Gemini usa el contexto del libro y su conocimiento general.
5.  **Backend a Frontend**: El backend responde con la `response` generada por la IA.
6.  **Frontend**: `RagView` añade la pregunta del usuario y la respuesta de la IA al historial del chat.

### Resumen de Endpoints de la API

| Método | Ruta                     | Descripción                                                                                              | Entrada (Body/Query)                                     | Salida                   |
| :----- | :----------------------- | :------------------------------------------------------------------------------------------------------- | :------------------------------------------------------- | :----------------------- |
| `POST` | `/upload-book/`          | Sube y procesa un nuevo libro (PDF/EPUB), lo analiza con IA y lo guarda en la biblioteca.                | `book_file`: `UploadFile`                                | `schemas.Book`           |
| `GET`  | `/books/`                | Obtiene una lista de libros, con opciones de filtrado por categoría, búsqueda general y autor.           | `category`, `search`, `author` (query params)            | `List[schemas.Book]`     |
| `GET`  | `/books/count`           | Obtiene el número total de libros en la base de datos.                                                  | N/A                                                      | `int`                    |
| `GET`  | `/books/search/`         | Busca libros por un título parcial (case-insensitive) con paginación.                                    | `title`, `skip`, `limit` (query params)                  | `List[schemas.Book]`     |
| `GET`  | `/categories/`           | Obtiene una lista de todas las categorías de libros únicas.                                              | N/A                                                      | `List[str]`              |
| `DELETE` | `/books/{book_id}`       | Elimina un libro específico por su ID, incluyendo sus archivos y el índice RAG asociado.                 | `book_id` (path param)                                   | `{"message": str}`       |
| `DELETE` | `/categories/{category_name}` | Elimina todos los libros de una categoría específica, incluyendo archivos e índices RAG.                 | `category_name` (path param)                             | `{"message": str}`       |
| `GET`  | `/books/download/{book_id}` | Permite descargar o abrir el archivo de un libro por su ID.                                              | `book_id` (path param)                                   | `FileResponse`           |
| `POST` | `/tools/convert-epub-to-pdf` | Convierte un archivo EPUB subido a PDF.                                                                  | `file`: `UploadFile`                                     | `schemas.ConversionResponse` |
| `POST` | `/rag/upload-book/`      | Sube un libro para ser procesado e indexado en el sistema RAG. Retorna un ID temporal para el RAG.     | `file`: `UploadFile`                                     | `schemas.RagUploadResponse` |
| `POST` | `/rag/query/`            | Realiza una consulta a la IA sobre el contenido de un libro indexado en RAG.                             | `schemas.RagQuery` (query, book\_id, mode)             | `schemas.RagQueryResponse` |
| `POST` | `/rag/index/{book_id}`   | Indexa un libro ya existente en la base de datos para el sistema RAG.                                    | `book_id` (path param), `force` (query param)            | `{"message": str, ...}`  |
| `GET`  | `/rag/status/{book_id}`  | Devuelve el estado de indexación RAG de un libro (si está indexado y número de vectores).                | `book_id` (path param)                                   | `{"book_id": str, "indexed": bool, "vector_count": int}` |
| `POST` | `/rag/reindex/category/{category_name}` | (Re)indexa todos los libros de una categoría específica en RAG.                                  | `category_name` (path param), `force` (query param)      | `{"processed": int, "failed": list, ...}` |
| `POST` | `/rag/reindex/all`       | (Re)indexa todos los libros de la biblioteca en RAG.                                                    | `force` (query param)                                    | `{"processed": int, "failed": list, ...}` |
| `GET`  | `/rag/estimate/book/{book_id}` | Estima tokens y chunks para un libro, con coste opcional.                                                | `book_id` (path param), `per1k`, `max_tokens` (query params) | `{"book_id": str, "tokens": int, "chunks": int, "estimated_cost": float | None}` |
| `GET`  | `/rag/estimate/category/{category_name}` | Estima tokens y chunks para todos los libros de una categoría, con coste opcional.                     | `category_name` (path param), `per1k`, `max_tokens` (query params) | `{"category": str, "tokens": int, "chunks": int, "files": int, "estimated_cost": float | None}` |
| `GET`  | `/rag/estimate/all`      | Estima tokens y chunks para todos los libros de la biblioteca, con coste opcional.                       | `per1k`, `max_tokens` (query params)                     | `{"tokens": int, "chunks": int, "files": int, "estimated_cost": float | None}` |
```markdown
# Documentación del Proyecto: Mi Librería Inteligente

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web full-stack diseñada para gestionar y interactuar con una biblioteca personal de libros digitales. Permite a los usuarios subir, organizar, leer y consultar sus libros de una manera innovadora, integrando capacidades de inteligencia artificial para enriquecer la experiencia de usuario.

**Características principales:**

*   **Gestión de Biblioteca:** Sube libros en formato PDF y EPUB. La IA extrae automáticamente el título, autor y categoría.
*   **Organización:** Visualiza libros por categorías, busca por título o autor.
*   **Lectura:** Lector integrado para archivos EPUB y descarga directa para PDF.
*   **Herramientas:** Conversor de EPUB a PDF.
*   **RAG (Retrieval-Augmented Generation):** Un potente sistema que permite conversar con el contenido de los libros utilizando modelos de lenguaje avanzados. Los libros se indexan, y la IA puede responder preguntas específicas basándose en el texto del libro, complementando con conocimiento general según el modo de consulta.

**Arquitectura General:**

El proyecto sigue una arquitectura cliente-servidor, dividida en dos componentes principales:

*   **Frontend (Cliente):** Desarrollado con **React**, proporciona la interfaz de usuario interactiva para la gestión de la biblioteca, la subida de libros, la lectura y la interacción con el sistema RAG. Se comunica con el backend a través de la API REST.
*   **Backend (Servidor):** Implementado con **FastAPI** (Python), es el cerebro de la aplicación. Gestiona la lógica de negocio, la interacción con la base de datos, el almacenamiento de archivos, el procesamiento de documentos (PDF/EPUB), la integración con la API de Gemini (Google AI) para análisis de texto y RAG, y la gestión de la base de datos vectorial ChromaDB.
    *   **Base de Datos Relacional:** **SQLite** se utiliza para almacenar los metadatos de los libros (título, autor, categoría, rutas de archivo, etc.) a través de **SQLAlchemy ORM**.
    *   **Base de Datos Vectorial:** **ChromaDB** se emplea para el almacenamiento y la recuperación de incrustaciones (embeddings) de texto, esenciales para la funcionalidad RAG.
    *   **Modelos de Lenguaje (LLMs):** Se utiliza la API de **Google Gemini** para el análisis inicial de los libros (extracción de metadatos) y para generar respuestas en el módulo RAG.

## 2. Estructura del Proyecto

La estructura del proyecto se organiza en dos directorios principales, `backend` y `frontend`, reflejando la arquitectura full-stack.

```
.
├── backend/
│   ├── alembic/                      # Herramienta de migraciones de base de datos (SQLAlchemy Alembic)
│   │   ├── versions/                 # Scripts de migración de la base de datos
│   │   └── ...
│   ├── books/                        # Almacena los archivos de libros subidos (PDFs, EPUBs)
│   ├── static/                       # Contenido estático servido por FastAPI
│   │   └── covers/                   # Portadas de libros generadas o extraídas
│   ├── temp_books/                   # Archivos temporales (ej. PDFs convertidos de EPUBs, archivos RAG)
│   ├── tests/                        # Pruebas unitarias y de integración para el backend
│   ├── tests_curated/                # Pruebas unitarias curadas para el backend
│   ├── __init__.py                   # Paquete Python
│   ├── crud.py                       # Operaciones CRUD para la base de datos
│   ├── database.py                   # Configuración de la conexión a la base de datos
│   ├── main.py                       # Aplicación FastAPI principal y endpoints de la API
│   ├── models.py                     # Definición de modelos de la base de datos (SQLAlchemy ORM)
│   ├── rag.py                        # Lógica para Retrieval-Augmented Generation (RAG)
│   ├── schemas.py                    # Esquemas de datos Pydantic para validación de API
│   └── utils.py                      # Utilidades y configuración de la IA
├── frontend/
│   ├── public/                       # Archivos estáticos públicos (index.html, etc.)
│   ├── src/                          # Código fuente de la aplicación React
│   │   ├── App.css                   # Estilos generales de la aplicación
│   │   ├── App.js                    # Componente principal de React y enrutamiento
│   │   ├── CategoriesView.css        # Estilos para la vista de categorías
│   │   ├── CategoriesView.js         # Componente para mostrar y navegar por categorías
│   │   ├── ErrorBoundary.js          # Componente para manejo de errores en React
│   │   ├── Header.css                # Estilos del encabezado
│   │   ├── Header.js                 # Componente del encabezado de la aplicación
│   │   ├── LibraryView.css           # Estilos para la vista de la biblioteca
│   │   ├── LibraryView.js            # Componente para mostrar y gestionar libros
│   │   ├── RagView.css               # Estilos para la vista de conversación con IA
│   │   ├── RagView.js                # Componente para interactuar con el sistema RAG
│   │   ├── ReaderView.css            # Estilos del lector de libros
│   │   ├── ReaderView.js             # Componente para el lector de EPUBs
│   │   ├── ToolsView.css             # Estilos para la vista de herramientas
│   │   ├── ToolsView.js              # Componente para herramientas (ej. conversor EPUB a PDF)
│   │   ├── UploadView.css            # Estilos para la vista de subida
│   │   ├── UploadView.js             # Componente para subir libros
│   │   ├── config.js                 # Configuración de la URL del API
│   │   ├── index.css                 # Estilos globales
│   │   ├── index.js                  # Punto de entrada de la aplicación React
│   │   └── reportWebVitals.js        # Utilidad para medir el rendimiento web
│   ├── .env.example                  # Ejemplo de variables de entorno para frontend
│   ├── package.json                  # Definiciones y scripts del proyecto Node.js
│   └── ...
├── .env.example                      # Ejemplo de variables de entorno para backend
├── library.db                        # Base de datos SQLite (generada al ejecutar)
└── README.md                         # Archivo README principal
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend de FastAPI es el núcleo de la lógica de negocio y la interacción con los datos.

### `backend/schemas.py`

Define los modelos Pydantic para la validación de datos de entrada y salida de la API.

*   **`BookBase(BaseModel)`**: Esquema base para los datos de un libro.
    *   `title: str`: Título del libro.
    *   `author: str`: Autor del libro.
    *   `category: str`: Categoría a la que pertenece el libro.
    *   `cover_image_url: str | None = None`: URL opcional de la portada del libro.
    *   `file_path: str`: Ruta física del archivo del libro en el servidor.
*   **`Book(BookBase)`**: Extiende `BookBase` añadiendo el ID de la base de datos.
    *   `id: int`: Identificador único del libro en la base de datos.
    *   `class Config: from_attributes = True`: Permite mapear directamente desde modelos SQLAlchemy.
*   **`ConversionResponse(BaseModel)`**: Respuesta para la conversión de EPUB a PDF.
    *   `download_url: str`: URL para descargar el PDF convertido.
*   **`RagUploadResponse(BaseModel)`**: Respuesta al subir un libro para el proceso RAG.
    *   `book_id: str`: ID único asignado al libro en el sistema RAG.
    *   `message: str`: Mensaje de estado.
*   **`RagQuery(BaseModel)`**: Esquema para una consulta al sistema RAG.
    *   `query: str`: La pregunta del usuario.
    *   `book_id: str`: El ID del libro al que se refiere la consulta.
    *   `mode: str | None = None`: Modo de la consulta (`'strict'`, `'balanced'`, `'open'`).
*   **`RagQueryResponse(BaseModel)`**: Respuesta del sistema RAG.
    *   `response: str`: La respuesta generada por la IA.

### `backend/models.py`

Define el modelo de datos `Book` utilizando SQLAlchemy ORM, mapeando a la tabla `books` en la base de datos.

*   **`class Book(Base)`**: Representa un libro en la base de datos.
    *   `__tablename__ = "books"`: Nombre de la tabla.
    *   `__table_args__ = {'extend_existing': True}`: Permite redefinir la tabla en caso de hot reload, útil para desarrollo.
    *   `id = Column(Integer, primary_key=True, index=True)`: Clave primaria autoincremental.
    *   `title = Column(String, index=True)`: Título del libro, indexado para búsquedas.
    *   `author = Column(String, index=True)`: Autor del libro, indexado para búsquedas.
    *   `category = Column(String, index=True)`: Categoría del libro, indexada para búsquedas.
    *   `cover_image_url = Column(String, nullable=True)`: URL a la portada, opcional.
    *   `file_path = Column(String, unique=True)`: Ruta absoluta al archivo del libro, única.

### `backend/database.py`

Configura la conexión a la base de datos SQLite y el motor de SQLAlchemy.

*   `_base_dir = Path(__file__).resolve().parent`: Directorio base del backend.
*   `_db_path = (_base_dir.parent / "library.db").resolve()`: Ruta al archivo `library.db` en la raíz del proyecto.
*   `SQLALCHEMY_DATABASE_URL = f"sqlite:///{_db_path.as_posix()}"`: URL de conexión para SQLite. `check_same_thread=False` es necesario para SQLite con FastAPI en un entorno de múltiples hilos.
*   `engine = create_engine(...)`: Motor de la base de datos.
*   `SessionLocal = sessionmaker(...)`: Clase para crear sesiones de base de datos.
*   `Base = declarative_base()`: Clase base para los modelos declarativos de SQLAlchemy.

### `backend/crud.py`

Contiene funciones para realizar operaciones CRUD (Crear, Leer, Actualizar, Borrar) en la tabla `books`.

*   **`get_book_by_path(db: Session, file_path: str)`**:
    *   **Propósito:** Obtiene un libro por su ruta de archivo única.
    *   **Parámetros:** `db` (sesión de DB), `file_path` (ruta del archivo).
    *   **Retorna:** `models.Book` o `None`.
*   **`get_book_by_title(db: Session, title: str)`**:
    *   **Propósito:** Obtiene un libro por su título exacto.
    *   **Parámetros:** `db`, `title`.
    *   **Retorna:** `models.Book` o `None`.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**:
    *   **Propósito:** Busca libros por un título parcial (insensible a mayúsculas/minúsculas).
    *   **Parámetros:** `db`, `title` (cadena parcial), `skip` (para paginación), `limit` (para paginación).
    *   **Retorna:** `list[models.Book]`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**:
    *   **Propósito:** Obtiene una lista de libros, con opciones de filtrado.
    *   **Parámetros:** `db`, `category` (filtrar por categoría exacta), `search` (búsqueda general en título, autor, categoría), `author` (búsqueda parcial de autor).
    *   **Retorna:** `list[models.Book]`, ordenados por ID descendente.
*   **`get_categories(db: Session) -> list[str]`**:
    *   **Propósito:** Obtiene una lista de todas las categorías de libros únicas.
    *   **Parámetros:** `db`.
    *   **Retorna:** `list[str]`.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**:
    *   **Propósito:** Crea un nuevo libro en la base de datos.
    *   **Parámetros:** `db`, `title`, `author`, `category`, `cover_image_url`, `file_path`.
    *   **Retorna:** El objeto `models.Book` recién creado.
*   **`delete_book(db: Session, book_id: int)`**:
    *   **Propósito:** Elimina un libro por su ID, incluyendo sus archivos asociados (libro y portada).
    *   **Parámetros:** `db`, `book_id`.
    *   **Retorna:** El objeto `models.Book` eliminado o `None` si no se encontró.
*   **`delete_books_by_category(db: Session, category: str)`**:
    *   **Propósito:** Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados.
    *   **Parámetros:** `db`, `category`.
    *   **Retorna:** El número de libros eliminados.
*   **`get_books_count(db: Session) -> int`**:
    *   **Propósito:** Obtiene el número total de libros en la base de datos.
    *   **Parámetros:** `db`.
    *   **Retorna:** `int`.

### `backend/utils.py`

Contiene funciones de utilidad, principalmente para la configuración de las API de IA.

*   **`configure_genai()`**:
    *   **Propósito:** Configura el SDK de Google Generative AI (Gemini) cargando la clave API desde las variables de entorno (`GOOGLE_API_KEY` o `GEMINI_API_KEY`).
    *   **Parámetros:** Ninguno.
    *   **Retorna:** Ninguno.
    *   **Lógica:** Carga `.env`, busca la clave, configura `genai`. Lanza `ValueError` si no se encuentra la clave.

### `backend/rag.py`

Implementa la lógica del sistema Retrieval-Augmented Generation (RAG).

*   **Variables Globales / Configuración:**
    *   `_initialized`, `_collection`, `_ai_enabled`: Control de estado y cliente ChromaDB.
    *   `EMBEDDING_MODEL`, `GENERATION_MODEL`: Nombres de modelos de Gemini configurables via `os.getenv`.
*   **`_ensure_init()`**:
    *   **Propósito:** Inicializa lazily el cliente `chromadb` y `genai.configure` si no se ha hecho ya.
    *   **Lógica:** Carga `.env`, comprueba `DISABLE_AI`. Configura `genai` si hay API key y la IA no está deshabilitada. Inicializa `chromadb.PersistentClient` y obtiene la colección `book_rag_collection`.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**:
    *   **Propósito:** Genera un embedding vectorial para un texto dado usando el modelo de embedding de Gemini.
    *   **Parámetros:** `text` (texto a embedder), `task_type` (tipo de tarea para Gemini, ej. "RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY").
    *   **Retorna:** `list[float]` (el vector embedding). Devuelve un embedding dummy si la IA está deshabilitada.
*   **`extract_text_from_pdf(file_path: str)`**:
    *   **Propósito:** Extrae texto de un archivo PDF usando `PyPDF2`.
    *   **Parámetros:** `file_path`.
    *   **Retorna:** `str` (texto extraído).
*   **`extract_text_from_epub(file_path: str)`**:
    *   **Propósito:** Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`.
    *   **Parámetros:** `file_path`.
    *   **Retorna:** `str` (texto extraído).
*   **`extract_text(file_path: str)`**:
    *   **Propósito:** Función unificada para extraer texto de PDF o EPUB.
    *   **Parámetros:** `file_path`.
    *   **Retorna:** `str`. Lanza `ValueError` para tipos de archivo no soportados.
*   **`chunk_text(text: str, max_tokens: int = 1000)`**:
    *   **Propósito:** Divide un texto largo en fragmentos más pequeños basados en el recuento de tokens (usando `tiktoken` como aproximación).
    *   **Parámetros:** `text`, `max_tokens` (tamaño máximo de token por fragmento).
    *   **Retorna:** `list[str]` (lista de fragmentos de texto).
*   **`_has_index_for_book(book_id: str)`**:
    *   **Propósito:** Comprueba si ya existen vectores indexados para un `book_id` dado en ChromaDB.
    *   **Parámetros:** `book_id`.
    *   **Retorna:** `bool`.
*   **`delete_book_from_rag(book_id: str)`**:
    *   **Propósito:** Elimina todos los vectores asociados a un `book_id` de ChromaDB.
    *   **Parámetros:** `book_id`.
    *   **Retorna:** Ninguno.
*   **`get_index_count(book_id: str)`**:
    *   **Propósito:** Devuelve el número de vectores almacenados para un `book_id` específico.
    *   **Parámetros:** `book_id`.
    *   **Retorna:** `int`.
*   **`has_index(book_id: str)`**:
    *   **Propósito:** Helper público para `get_index_count`.
    *   **Parámetros:** `book_id`.
    *   **Retorna:** `bool`.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**:
    *   **Propósito:** Extrae texto, lo divide en fragmentos, genera embeddings y los almacena en ChromaDB.
    *   **Parámetros:** `file_path` (ruta al archivo del libro), `book_id` (ID del libro para RAG), `force_reindex` (si es `True`, borra el índice existente y lo vuelve a crear).
    *   **Lógica:** Si no se fuerza la reindexación y el libro ya está indexado, se salta el proceso. Extrae texto, lo chunk-ea, genera embeddings para cada chunk y los añade a ChromaDB con metadatos.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**:
    *   **Propósito:** Estima el número de tokens y chunks para un archivo dado, útil para calcular costes.
    *   **Parámetros:** `file_path`, `max_tokens`.
    *   **Retorna:** `dict` con `tokens` y `chunks`.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**:
    *   **Propósito:** Estima tokens y chunks para una lista de archivos.
    *   **Parámetros:** `file_paths`, `max_tokens`.
    *   **Retorna:** `dict` con `tokens`, `chunks`, `files` (contados).
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**:
    *   **Propósito:** Consulta el sistema RAG para obtener respuestas basadas en el contenido del libro.
    *   **Parámetros:** `query` (pregunta del usuario), `book_id` (ID del libro), `mode` (estrategia de respuesta: `strict`, `balanced`, `open`), `metadata` (metadatos del libro para enriquecer el prompt), `library` (contexto de la biblioteca, ej. otros libros del autor).
    *   **Lógica:** Genera embedding de la consulta, busca los chunks más relevantes en ChromaDB, construye un prompt con contexto y metadatos, y llama al modelo de generación de Gemini para obtener la respuesta.

### `backend/main.py`

Archivo principal de la aplicación FastAPI. Contiene los endpoints de la API, la lógica de inicialización y las funciones auxiliares para el procesamiento de archivos.

*   **Configuración Inicial:**
    *   Carga variables de entorno.
    *   Configura la API de Google Gemini (si `AI_ENABLED` es `True`).
    *   Crea las tablas de la base de datos si no existen (`models.Base.metadata.create_all`).
    *   Define y crea directorios para libros, portadas y archivos temporales.
    *   Configura `CORSMiddleware` para manejar peticiones de diferentes orígenes.
*   **Funciones de IA y Procesamiento:**
    *   **`analyze_with_gemini(text: str) -> dict`**:
        *   **Propósito:** Analiza texto (generalmente las primeras páginas de un libro) usando Gemini para extraer título, autor y categoría.
        *   **Parámetros:** `text` (contenido textual del libro).
        *   **Retorna:** `dict` con `title`, `author`, `category`. Devuelve valores por defecto "Error de IA" en caso de fallo.
    *   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
        *   **Propósito:** Extrae texto de las primeras páginas de un PDF y busca una posible imagen de portada.
        *   **Parámetros:** `file_path`, `covers_dir_fs` (directorio de portadas en el sistema de archivos), `covers_url_prefix` (prefijo URL para las portadas).
        *   **Retorna:** `dict` con `text` y `cover_image_url` (si se encontró).
    *   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
        *   **Propósito:** Extrae texto de las primeras páginas de un EPUB y busca una posible imagen de portada (con varios fallbacks).
        *   **Parámetros:** `file_path`, `covers_dir_fs`, `covers_url_prefix`.
        *   **Retorna:** `dict` con `text` y `cover_image_url` (si se encontró). Lanza `HTTPException` si no se extrae suficiente texto.
*   **Dependencia `get_db()`**:
    *   Proporciona una sesión de base de datos SQLAlchemy por petición.
*   **Endpoints de la API:**
    *   **`POST /upload-book/`**: Sube un nuevo archivo de libro (PDF o EPUB), lo procesa con IA para extraer metadatos y lo guarda en la base de datos.
    *   **`GET /books/`**: Obtiene una lista de libros, con opciones de filtrado por categoría, búsqueda general y autor.
    *   **`GET /books/count`**: Retorna el número total de libros.
    *   **`GET /books/search/`**: Busca libros por título parcial (con paginación).
    *   **`GET /categories/`**: Retorna una lista de todas las categorías únicas.
    *   **`DELETE /books/{book_id}`**: Elimina un libro específico por su ID, incluyendo archivos asociados y el índice RAG.
    *   **`DELETE /categories/{category_name}`**: Elimina todos los libros de una categoría, incluyendo archivos e índices RAG.
    *   **`GET /books/download/{book_id}`**: Permite descargar o abrir un libro por su ID.
    *   **`POST /tools/convert-epub-to-pdf`**: Convierte un archivo EPUB subido a PDF y retorna una URL de descarga temporal.
    *   **`POST /rag/upload-book/`**: Sube un libro (PDF/EPUB) directamente para indexarlo en el sistema RAG (genera un `book_id` temporal).
    *   **`POST /rag/query/`**: Consulta el sistema RAG con una pregunta para un libro específico.
    *   **`POST /rag/index/{book_id}`**: Indexa un libro ya existente en la biblioteca para RAG.
    *   **`GET /rag/status/{book_id}`**: Verifica si un libro tiene índice RAG y cuántos vectores tiene.
    *   **`POST /rag/reindex/category/{category_name}`**: (Re)indexa todos los libros de una categoría.
    *   **`POST /rag/reindex/all`**: (Re)indexa todos los libros de la biblioteca.
    *   **`GET /rag/estimate/book/{book_id}`**: Estima tokens/chunks y coste potencial para indexar un libro.
    *   **`GET /rag/estimate/category/{category_name}`**: Estima tokens/chunks y coste potencial para indexar una categoría.
    *   **`GET /rag/estimate/all`**: Estima tokens/chunks y coste potencial para indexar toda la biblioteca.

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

Script de migración de Alembic para crear la tabla `books`.

*   **`upgrade()`**: Crea la tabla `books` con las columnas `id`, `title`, `author`, `category`, `cover_image_url`, `file_path`. Establece `id` como clave primaria y añade índices a `id`, `title`, `author`, `category`. `file_path` tiene una restricción de unicidad.
*   **`downgrade()`**: Elimina la tabla `books` y sus índices.

### `backend/__init__.py`

Archivo vacío que marca el directorio `backend` como un paquete Python.

## 4. Análisis Detallado del Frontend (React)

El frontend de React proporciona la interfaz de usuario, gestionando la interacción y la visualización de datos.

### `frontend/src/App.js`

El componente raíz de la aplicación React.

*   **Propósito:** Configura el enrutamiento de la aplicación utilizando `react-router-dom` y la estructura general del layout con el `Header` y el contenido principal.
*   **Estado/Props:** No tiene estado local ni props.
*   **Efectos Secundarios:** No tiene efectos secundarios directos; delega la lógica a los componentes de vista.
*   **Interacciones:** Define las rutas de navegación para las diferentes vistas de la aplicación.

### `frontend/src/Header.js`

El encabezado de la aplicación, incluye la navegación y un contador de libros.

*   **Propósito:** Proporciona un menú de navegación global y muestra el número total de libros en la biblioteca.
*   **Estado:**
    *   `menuOpen (boolean)`: Controla la visibilidad del menú hamburguesa en dispositivos móviles.
    *   `bookCount (number)`: Almacena el número de libros obtenido del backend.
    *   `errorMessage (string)`: Mensaje de error si falla la carga del contador.
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useEffect`: Realiza una petición `GET` a `/books/count` al montar el componente y cada 10 minutos para actualizar el contador de libros.
*   **Interacciones:**
    *   `handleLinkClick`: Cierra el menú móvil cuando se hace clic en un enlace.
    *   Botón de menú hamburguesa: Alterna el estado `menuOpen`.
    *   `NavLink`s: Permiten la navegación entre las diferentes vistas.

### `frontend/src/LibraryView.js`

Muestra una lista de libros, permitiendo buscar, filtrar y realizar acciones sobre ellos.

*   **Propósito:** Es la vista principal de la biblioteca. Permite a los usuarios explorar, buscar, filtrar, descargar/leer y eliminar libros.
*   **Estado:**
    *   `books (array)`: Lista de libros a mostrar.
    *   `searchTerm (string)`: Término de búsqueda introducido por el usuario.
    *   `debouncedSearchTerm (string)`: Versión con "debounce" de `searchTerm` para evitar peticiones excesivas.
    *   `error (string)`: Mensaje de error.
    *   `loading (boolean)`: Indica si los libros están cargando.
    *   `isMobile (boolean)`: Detecta si la pantalla es de móvil para adaptar la UI (ej. botón de descarga de PDF).
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useDebounce`: Custom hook para retrasar la ejecución de la búsqueda.
    *   `useEffect` (detección móvil): Escucha cambios en el tamaño de la ventana para `isMobile`.
    *   `useEffect` (carga de libros): Llama a `fetchBooks` cuando `debouncedSearchTerm` o `searchParams` cambian.
*   **Interacciones:**
    *   `handleAuthorClick(author)`: Filtra libros por autor al hacer clic en el nombre del autor.
    *   `handleCategoryClick(category)`: Filtra libros por categoría al hacer clic en la categoría.
    *   `handleDeleteBook(bookId)`: Elimina un libro del backend y de la vista local.
    *   `BookCover` (componente interno): Muestra la portada del libro o un fallback genérico.
    *   Enlaces/botones: Para descargar PDFs, leer EPUBs o navegar al lector.

### `frontend/src/UploadView.js`

Permite a los usuarios subir uno o varios libros al sistema.

*   **Propósito:** Sube archivos de libros (PDF/EPUB) al backend para su procesamiento y adición a la biblioteca.
*   **Estado:**
    *   `filesToUpload (array)`: Lista de objetos de archivo con su estado (`pending`, `uploading`, `success`, `error`) y mensaje.
    *   `isUploading (boolean)`: Indica si hay archivos en proceso de subida.
*   **Props:** Ninguna.
*   **Efectos Secundarios:** Ninguno directo.
*   **Interacciones:**
    *   `handleFileChange`: Actualiza `filesToUpload` cuando se seleccionan archivos.
    *   `handleDrop`, `handleDragOver`: Implementa la funcionalidad de arrastrar y soltar archivos.
    *   `handleUpload`: Itera sobre `filesToUpload`, sube cada archivo al endpoint `/upload-book/` y actualiza su estado.
    *   Botón "Ir a la Biblioteca": Navega a la vista principal una vez que todos los archivos han terminado de procesarse.

### `frontend/src/CategoriesView.js`

Muestra todas las categorías únicas de libros disponibles en la biblioteca.

*   **Propósito:** Permite a los usuarios ver y navegar por las categorías de libros. Cada categoría es un enlace que filtra la vista de la biblioteca.
*   **Estado:**
    *   `categories (array)`: Lista de nombres de categorías.
    *   `error (string)`: Mensaje de error.
    *   `loading (boolean)`: Indica si las categorías están cargando.
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useEffect`: Realiza una petición `GET` a `/categories/` al montar el componente para obtener la lista de categorías.
*   **Interacciones:**
    *   `Link`s: Cada categoría es un enlace a la `LibraryView` con el parámetro de búsqueda `category`.

### `frontend/src/ToolsView.js`

Proporciona herramientas adicionales, como la conversión de EPUB a PDF.

*   **Propósito:** Aloja diversas herramientas para la gestión de libros. Actualmente, incluye un conversor de EPUB a PDF.
*   **Estado (EpubToPdfConverter):**
    *   `selectedFile (File)`: El archivo EPUB seleccionado para convertir.
    *   `message (string)`: Mensaje de estado al usuario (errores, éxito, progreso).
    *   `isLoading (boolean)`: Indica si la conversión está en curso.
*   **Props:** Ninguna.
*   **Efectos Secundarios:** Ninguno.
*   **Interacciones:**
    *   `handleFileChange`: Actualiza `selectedFile`.
    *   `handleDrop`, `handleDragOver`: Permite arrastrar y soltar archivos.
    *   `handleConvert`: Envía el archivo EPUB al endpoint `/tools/convert-epub-to-pdf`, maneja la respuesta y dispara la descarga del PDF resultante.

### `frontend/src/ReaderView.js`

Componente para leer libros en formato EPUB directamente en el navegador.

*   **Propósito:** Muestra el contenido de un libro EPUB utilizando la librería `react-reader`.
*   **Estado:**
    *   `location (string)`: La ubicación actual de lectura en formato EPUB CFI.
    *   `epubData (ArrayBuffer)`: Los datos binarios del archivo EPUB.
    *   `isLoading (boolean)`: Indica si el libro está cargando.
    *   `error (string)`: Mensaje de error si el libro no se puede cargar.
*   **Props:** `bookId` (obtenido de los parámetros de la URL).
*   **Efectos Secundarios:**
    *   `useEffect`: Realiza una petición `GET` a `/books/download/{bookId}` al montar el componente para obtener el contenido del EPUB como `ArrayBuffer`.
*   **Interacciones:**
    *   `locationChanged`: Actualiza el estado `location` cuando el usuario navega por el libro.

### `frontend/src/RagView.js`

Permite a los usuarios interactuar con un libro específico a través de un chat con IA.

*   **Propósito:** Facilita la conversación con los libros de la biblioteca utilizando el sistema RAG del backend. Los usuarios pueden seleccionar un libro, indexarlo (si no lo está) y hacer preguntas sobre su contenido.
*   **Estado:**
    *   `message (string)`: Mensajes informativos o de error para el usuario.
    *   `isLoading (boolean)`: Indica si se está esperando una respuesta de la IA.
    *   `bookId (string)`: El ID del libro con el que se está chateando actualmente en RAG.
    *   `chatHistory (array)`: Historial de la conversación (usuario y respuestas de Gemini).
    *   `currentQuery (string)`: La pregunta actual del usuario.
    *   `libraryBooks (array)`: Lista completa de libros de la biblioteca para la selección.
    *   `selectedLibraryId (string)`: El ID del libro seleccionado de la biblioteca para RAG.
    *   `libStatus (object)`: Estado del indexado RAG del libro seleccionado (loading, indexed, vector_count, error).
    *   `actionsBusy (boolean)`: Bloquea acciones de indexado/reindexado.
    *   `refreshing (boolean)`: Indica si se está refrescando el estado RAG.
    *   `searchTerm (string)`: Término para buscar libros en la biblioteca.
    *   `searching (boolean)`: Indica si se está realizando una búsqueda de libros.
    *   `searchResults (array)`: Resultados de la búsqueda de libros.
    *   `resultsOpen (boolean)`: Controla la visibilidad de los resultados de búsqueda.
    *   `mode (string)`: Modo de respuesta de la IA (`strict`, `balanced`, `open`).
    *   `selectedBook (object)`: Objeto completo del libro actualmente seleccionado.
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useEffect` (scroll chat): Desplaza automáticamente el chat al final cuando se añaden mensajes.
    *   `useEffect` (carga libros): Carga la lista de `libraryBooks` al montar.
    *   `useEffect` (búsqueda con debounce): Implementa la búsqueda de libros con un retardo para optimizar peticiones.
    *   `useEffect` (estado RAG): Comprueba el estado RAG del `selectedLibraryId` cuando este cambia.
*   **Interacciones:**
    *   `handleQuerySubmit`: Envía la `currentQuery` al endpoint `/rag/query/` y actualiza el `chatHistory`.
    *   `checkLibraryStatus`: Llama a `/rag/status/{book_id}` para obtener el estado de indexado de un libro.
    *   `indexLibraryBook`: Llama a `/rag/index/{book_id}` para indexar o reindexar un libro.
    *   Selección de libro: Actualiza `selectedLibraryId` y `selectedBook`, disparando la verificación del estado RAG.
    *   Cambio de modo: Actualiza el `mode` de la consulta RAG.

### `frontend/src/ErrorBoundary.js`

Un componente de React para capturar errores en sus componentes hijos.

*   **Propósito:** Proporciona una interfaz de usuario de respaldo cuando ocurre un error en cualquier componente React anidado, evitando que toda la aplicación se bloquee.
*   **Estado:**
    *   `hasError (boolean)`: `True` si se ha detectado un error.
    *   `error (Error)`: El objeto de error capturado.
*   **Props:** `children` (los componentes que envuelve).
*   **Efectos Secundarios:**
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para mostrar la UI de error.
    *   `componentDidCatch(error, info)`: Registra el error en la consola.

### `frontend/src/config.js`

Archivo de configuración para la URL base del API.

*   **Propósito:** Proporciona la URL del backend, permitiendo que sea configurable mediante una variable de entorno (`REACT_APP_API_URL`) para diferentes entornos (desarrollo, producción).
*   **Exporta:** `API_URL` (string).

### `frontend/src/index.js`

El punto de entrada principal de la aplicación React.

*   **Propósito:** Renderiza el componente `App` en el elemento DOM con ID 'root'. También inicializa `reportWebVitals` para métricas de rendimiento.
*   **Lógica:** Envuelve `App` en `React.StrictMode` para ayudar a detectar problemas potenciales.

## 5. Flujo de Datos y API

El flujo de datos en "Mi Librería Inteligente" se centra en la interacción entre el frontend de React y el backend de FastAPI, con la base de datos relacional (SQLite) y la base de datos vectorial (ChromaDB) como almacenes de persistencia.

### Flujo de Subida de un Libro

1.  **Frontend (UploadView):** El usuario selecciona uno o más archivos (PDF/EPUB) a través del input de archivo o arrastrando y soltando.
2.  **Frontend (UploadView):** Para cada archivo, crea un `FormData` y realiza una petición `POST` al endpoint `/upload-book/` del backend, enviando el archivo.
3.  **Backend (main.py - `upload_book`):**
    *   Recibe el `UploadFile` y guarda el archivo en el directorio `backend/books/`.
    *   Comprueba si un libro con la misma `file_path` ya existe en la DB (`crud.get_book_by_path`). Si es así, lanza un error HTTP 409.
    *   Detecta la extensión del archivo (`.pdf` o `.epub`) y llama a la función de procesamiento correspondiente (`process_pdf` o `process_epub`). Estas funciones extraen el texto inicial y buscan una imagen de portada, guardándola en `backend/static/covers/`.
    *   Llama a `analyze_with_gemini` para que la IA extraiga el título, autor y categoría del texto extraído.
    *   Realiza una "puerta de calidad": si la IA no puede identificar el título y el autor, el archivo subido se elimina y se retorna un error HTTP 422.
    *   Si el análisis es exitoso, llama a `crud.create_book` para guardar los metadatos del libro (título, autor, categoría, URL de portada, ruta de archivo) en la base de datos SQLite.
4.  **Backend (main.py):** Retorna el objeto `schemas.Book` del libro creado.
5.  **Frontend (UploadView):** Recibe la respuesta, actualiza el estado (`status`, `message`) del archivo en la UI, informando al usuario del éxito o fracaso. Una vez que todos los archivos han sido procesados, se ofrece al usuario la opción de ir a `LibraryView`.

### Flujo de Búsqueda y Visualización de Libros

1.  **Frontend (LibraryView):**
    *   Al cargar la vista, o cuando el usuario escribe en la barra de búsqueda (`searchTerm`), o hace clic en un autor/categoría, se actualizan los parámetros de la URL (`searchParams`).
    *   Un `useEffect` con `debouncedSearchTerm` o `searchParams` dispara la función `fetchBooks`.
2.  **Frontend (LibraryView - `fetchBooks`):** Construye una URL de API con los parámetros de consulta (`category`, `author`, `search`) y realiza una petición `GET` a `/books/`.
3.  **Backend (main.py - `read_books`):**
    *   Recibe los parámetros de consulta.
    *   Llama a `crud.get_books` con los filtros apropiados.
4.  **Backend (crud.py - `get_books`):**
    *   Construye una consulta SQLAlchemy a la tabla `books` aplicando los filtros.
    *   Ejecuta la consulta y retorna una lista de objetos `models.Book`.
5.  **Backend (main.py):** Convierte la lista de `models.Book` a `schemas.Book` y la retorna.
6.  **Frontend (LibraryView):** Recibe la lista de libros, la almacena en el estado `books` y renderiza la cuadrícula de libros en la UI.

### Flujo del Sistema RAG (Conversación con IA)

El sistema RAG tiene dos fases principales: indexación y consulta.

#### Fase de Indexación:

1.  **Frontend (RagView):** El usuario selecciona un libro de la biblioteca (o sube un archivo temporal para RAG) y hace clic en "Indexar antes de charlar" o "Reindexar".
2.  **Frontend (RagView):** Realiza una petición `POST` a `/rag/index/{book_id}` (para libros existentes) o `/rag/upload-book/` (para archivos temporales de RAG).
3.  **Backend (main.py - `index_existing_book_for_rag` o `upload_book_for_rag`):**
    *   En el caso de un libro existente, recupera la `file_path` de la DB.
    *   Llama a `rag.process_book_for_rag` con la `file_path` y el `book_id` (que es el ID de la base de datos del libro, convertido a string). Si se fuerza la reindexación, se envía el parámetro `force_reindex=True`.
4.  **Backend (rag.py - `process_book_for_rag`):**
    *   Si `force_reindex` es `True` o el libro no está indexado, borra cualquier índice RAG existente para ese `book_id` (`rag.delete_book_from_rag`).
    *   Extrae el texto completo del libro (`extract_text_from_pdf` o `extract_text_from_epub`).
    *   Divide el texto en `chunks` (fragmentos) más pequeños (`chunk_text`).
    *   Para cada `chunk`, genera un `embedding` vectorial utilizando `get_embedding` (llamando a la API de Gemini).
    *   Almacena el `embedding` y el `chunk` asociado en la base de datos vectorial ChromaDB, junto con metadatos (`book_id`, `chunk_index`).
5.  **Backend (main.py):** Retorna un mensaje de éxito.
6.  **Frontend (RagView):** Recibe la confirmación, actualiza el estado `libStatus` a `indexed: true`, y permite al usuario iniciar una conversación.

#### Fase de Consulta:

1.  **Frontend (RagView):** El usuario escribe una pregunta en el input del chat y la envía.
2.  **Frontend (RagView):** Añade la pregunta al `chatHistory` y realiza una petición `POST` al endpoint `/rag/query/` con la pregunta (`query`), el `book_id` del libro seleccionado y el `mode` de respuesta.
3.  **Backend (main.py - `query_rag_endpoint`):**
    *   Recupera el objeto `models.Book` de la DB para obtener metadatos (título, autor, categoría) y, opcionalmente, otros libros del mismo autor de la biblioteca.
    *   Llama a `rag.query_rag` con la `query`, `book_id`, `mode` y los metadatos/contexto de la biblioteca.
4.  **Backend (rag.py - `query_rag`):**
    *   Genera un `embedding` de la `query` del usuario.
    *   Consulta ChromaDB para encontrar los 5 `chunks` de texto más relevantes del libro asociado al `book_id` que son semánticamente similares a la pregunta.
    *   Construye un `prompt` para el modelo de Gemini, incluyendo la `query`, los `relevant_chunks` como contexto del libro, los `metadata` del libro y el `library_ctx`, y las instrucciones específicas del `mode` de consulta.
    *   Envía el `prompt` al modelo de generación de Gemini (`genai.GenerativeModel.generate_content`).
    *   Retorna la respuesta textual generada por Gemini.
5.  **Backend (main.py):** Retorna la respuesta de la IA en un objeto `schemas.RagQueryResponse`.
6.  **Frontend (RagView):** Recibe la respuesta de la IA, la añade al `chatHistory` y la muestra en la UI.

### Flujo de Conversión de EPUB a PDF

1.  **Frontend (ToolsView):** El usuario selecciona un archivo EPUB.
2.  **Frontend (ToolsView):** Realiza una petición `POST` al endpoint `/tools/convert-epub-to-pdf`, enviando el archivo EPUB en un `FormData`.
3.  **Backend (main.py - `convert_epub_to_pdf`):**
    *   Recibe el archivo EPUB.
    *   Utiliza librerías como `zipfile`, `BeautifulSoup`, `weasyprint` (HTML a PDF) para:
        *   Extraer el contenido del EPUB a un directorio temporal.
        *   Analizar el manifiesto `.opf` para identificar la estructura del libro, archivos CSS y la portada.
        *   Generar una página HTML para la portada (si existe).
        *   Cargar los archivos CSS.
        *   Leer los capítulos HTML en el orden de lectura (spine).
        *   Renderizar todo el contenido HTML (incluyendo portada y capítulos) a PDF usando `weasyprint`.
    *   Guarda el PDF generado en el directorio `backend/temp_books/` con un nombre de archivo `uuid` único.
    *   Retorna una `schemas.ConversionResponse` con la `download_url` al PDF temporal.
4.  **Frontend (ToolsView):**
    *   Recibe la `download_url`.
    *   Crea un enlace `<a>` dinámicamente, establece su `href` a la `download_url` (prefixed with `API_URL`), y simula un clic para iniciar la descarga en una nueva pestaña.
    *   Muestra un mensaje de éxito al usuario.

### Principales Endpoints de la API

| Método | URL                                     | Descripción                                                                 | Pydantic Schema (Request/Response)           |
| :----- | :-------------------------------------- | :-------------------------------------------------------------------------- | :------------------------------------------- |
| `POST` | `/upload-book/`                         | Sube un nuevo libro (PDF/EPUB), lo analiza con IA y lo añade a la biblioteca. | `UploadFile` / `schemas.Book`                  |
| `GET`  | `/books/`                               | Obtiene una lista de libros, con filtros opcionales (categoría, búsqueda, autor). | `None` / `List[schemas.Book]`                  |
| `GET`  | `/books/count`                          | Obtiene el número total de libros.                                          | `None` / `int`                                 |
| `GET`  | `/books/search/?title={title}`          | Busca libros por título parcial.                                            | `None` / `List[schemas.Book]`                  |
| `GET`  | `/categories/`                          | Obtiene una lista de todas las categorías únicas.                           | `None` / `List[str]`                           |
| `DELETE` | `/books/{book_id}`                      | Elimina un libro por ID, incluyendo sus archivos y el índice RAG.           | `None` / `dict({"message": str})`              |
| `DELETE` | `/categories/{category_name}`           | Elimina una categoría y todos sus libros asociados.                         | `None` / `dict({"message": str})`              |
| `GET`  | `/books/download/{book_id}`             | Descarga o abre el archivo de un libro por ID.                              | `None` / `FileResponse`                        |
| `POST` | `/tools/convert-epub-to-pdf`            | Convierte un archivo EPUB a PDF.                                            | `UploadFile` / `schemas.ConversionResponse`    |
| `POST` | `/rag/upload-book/`                     | Sube un libro temporalmente para indexarlo en RAG.                          | `UploadFile` / `schemas.RagUploadResponse`     |
| `POST` | `/rag/query/`                           | Consulta el sistema RAG con una pregunta para un libro específico.          | `schemas.RagQuery` / `schemas.RagQueryResponse` |
| `POST` | `/rag/index/{book_id}?force={bool}`     | Indexa un libro existente en la biblioteca para RAG.                        | `None` / `dict`                                |
| `GET`  | `/rag/status/{book_id}`                 | Obtiene el estado de indexación RAG para un libro.                          | `None` / `dict({"book_id": str, "indexed": bool, "vector_count": int})` |
| `POST` | `/rag/reindex/category/{category_name}` | (Re)indexa todos los libros de una categoría.                               | `None` / `dict`                                |
| `POST` | `/rag/reindex/all`                      | (Re)indexa todos los libros de la biblioteca.                               | `None` / `dict`                                |
| `GET`  | `/rag/estimate/book/{book_id}`          | Estima tokens/chunks y coste potencial para un libro en RAG.                | `None` / `dict`                                |
| `GET`  | `/rag/estimate/category/{category_name}`| Estima tokens/chunks y coste potencial para una categoría en RAG.           | `None` / `dict`                                |
| `GET`  | `/rag/estimate/all`                     | Estima tokens/chunks y coste potencial para toda la biblioteca en RAG.      | `None` / `dict`                                |
```
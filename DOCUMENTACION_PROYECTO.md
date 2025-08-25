```markdown
# Documentación Técnica: Mi Librería Inteligente

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web diseñada para gestionar, explorar y interactuar con una colección personal de libros digitales. La aplicación permite a los usuarios subir libros en formato PDF y EPUB, los cuales son automáticamente analizados por inteligencia artificial para extraer metadatos como el título, autor y categoría. Los libros se organizan en una biblioteca, donde los usuarios pueden buscar, filtrar por categoría o autor, y leerlos directamente en el navegador o descargarlos.

Una característica destacada es la funcionalidad de Recuperación Aumentada por Generación (RAG), que permite a los usuarios interactuar con el contenido de los libros a través de un chat impulsado por IA. Además, se incluye una herramienta para convertir libros EPUB a PDF.

**Arquitectura General:**

*   **Frontend:** Desarrollado con **React**, proporciona la interfaz de usuario interactiva y se comunica con el backend a través de solicitudes HTTP.
*   **Backend:** Implementado con **FastAPI** (Python), expone una API RESTful para la gestión de libros, el procesamiento de archivos, la conversión y la interacción con IA.
*   **Base de Datos:** Utiliza **SQLite** como base de datos ligera para almacenar los metadatos de los libros. SQLAlchemy se usa como ORM.
*   **Inteligencia Artificial (IA):** Integra la API de **Google Gemini** para:
    *   Análisis inicial de libros (extracción de título, autor, categoría).
    *   Generación de respuestas en el sistema RAG.
*   **RAG (Retrieval Augmented Generation):**
    *   Almacena vectores de incrustación de texto en **ChromaDB** (una base de datos vectorial local).
    *   Utiliza **tiktoken** para la tokenización y fragmentación de texto.
    *   Las incrustaciones se generan con el modelo `text-embedding-004` de Gemini.
    *   Las respuestas generativas utilizan el modelo `gemini-2.5-flash`.
*   **Procesamiento de Archivos:**
    *   **PyPDF2** para extracción de texto de PDFs.
    *   **ebooklib** y **BeautifulSoup** para extracción de texto y portada de EPUBs.
    *   **fitz** (PyMuPDF) para extracción de texto y portadas de PDFs.
    *   **WeasyPrint** para la conversión de EPUB a PDF.
*   **Contenedorización/Despliegue:** Aunque no se proporciona el `Dockerfile` o `docker-compose.yml`, la estructura es apta para despliegue en contenedores. La configuración de orígenes (CORS) es flexible para entornos de desarrollo y producción.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales: `backend/` para la lógica del servidor y `frontend/` para la aplicación web de React.

```
.
├── backend/
│   ├── alembic/                      # Herramienta de migración de base de datos SQLAlchemy
│   │   ├── versions/                 # Archivos de migración de esquema de BD
│   │   └── env.py                    # Entorno de configuración de Alembic
│   ├── __init__.py                   # Paquete Python backend
│   ├── crud.py                       # Operaciones CRUD para la base de datos
│   ├── database.py                   # Configuración de la conexión a la base de datos
│   ├── main.py                       # Aplicación principal FastAPI y puntos finales API
│   ├── models.py                     # Modelos de base de datos SQLAlchemy
│   ├── rag.py                        # Lógica para Retrieval Augmented Generation (RAG)
│   ├── schemas.py                    # Esquemas de datos Pydantic para la API
│   ├── utils.py                      # Funciones de utilidad (ej. configuración de GenAI)
│   ├── static/                       # Archivos estáticos servidos por FastAPI
│   │   └── covers/                   # Portadas de libros extraídas
│   ├── books/                        # Almacenamiento de archivos de libros subidos
│   ├── temp_books/                   # Archivos temporales (ej. PDFs convertidos, archivos RAG)
│   └── tests/                        # Pruebas unitarias para el backend
│       ├── test_api_curated.py
│       ├── test_ci_smoke.py
│       ├── test_crud.py
│       ├── test_generate_tests.py
│       ├── test_main.py
│       ├── test_models.py
│       ├── test_rag.py
│       ├── test_schemas.py
│       ├── test_test_api_curated.py
│       ├── test_test_rag_curated.py
│       ├── test_test_schemas_curated.py
│       └── test_test_utils_curated.py
│   └── tests_curated/                # Pruebas unitarias curadas adicionales para el backend
│       ├── test_api_curated.py
│       ├── test_crud_curated.py
│       ├── test_main_async_curated.py
│       ├── test_rag_curated.py
│       ├── test_schemas_curated.py
│       └── test_utils_curated.py
├── frontend/
│   ├── public/                       # Archivos públicos para la aplicación React
│   ├── src/                          # Código fuente de la aplicación React
│   │   ├── App.css                   # Estilos globales de la aplicación
│   │   ├── App.js                    # Componente principal de la aplicación React
│   │   ├── CategoriesView.css        # Estilos para CategoriesView
│   │   ├── CategoriesView.js         # Vista para mostrar y navegar categorías
│   │   ├── config.js                 # Configuración de la URL de la API
│   │   ├── ErrorBoundary.js          # Componente para el manejo de errores de React
│   │   ├── Header.css                # Estilos para el Header
│   │   ├── Header.js                 # Componente del encabezado y navegación
│   │   ├── index.css                 # Estilos CSS globales
│   │   ├── index.js                  # Punto de entrada de la aplicación React
│   │   ├── LibraryView.css           # Estilos para LibraryView
│   │   ├── LibraryView.js            # Vista principal de la biblioteca
│   │   ├── RagView.css               # Estilos para RagView
│   │   ├── RagView.js                # Vista para la interacción RAG con libros
│   │   ├── ReaderView.css            # Estilos para ReaderView
│   │   ├── ReaderView.js             # Vista para leer libros EPUB
│   │   ├── reportWebVitals.js        # Utilitario para medir el rendimiento web
│   │   ├── ToolsView.css             # Estilos para ToolsView
│   │   └── ToolsView.js              # Vista para herramientas de la biblioteca (ej. conversor EPUB a PDF)
│   │   ├── UploadView.css            # Estilos para UploadView
│   │   └── UploadView.js             # Vista para subir nuevos libros
│   ├── .env                          # Variables de entorno para React
│   └── package.json                  # Definiciones y scripts del proyecto npm
├── library.db                        # Archivo de base de datos SQLite (generado)
└── .env                              # Variables de entorno para el backend
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend de la aplicación está construido con FastAPI y Python, y se encarga de la lógica de negocio, la interacción con la base de datos, el procesamiento de archivos y la integración con modelos de IA.

### `backend/schemas.py`

Define los modelos de datos para la API utilizando Pydantic. Estos esquemas garantizan la validación de los datos de entrada y la serialización de los datos de salida.

*   **`BookBase(BaseModel)`**:
    *   **Propósito**: Esquema base para los datos de un libro, utilizado en la creación o representación sin ID.
    *   **Atributos**:
        *   `title` (str): Título del libro.
        *   `author` (str): Autor del libro.
        *   `category` (str): Categoría del libro.
        *   `cover_image_url` (str | None): URL de la imagen de portada (opcional).
        *   `file_path` (str): Ruta de archivo del libro en el servidor.
*   **`Book(BookBase)`**:
    *   **Propósito**: Extiende `BookBase` para incluir el ID del libro, usado típicamente en respuestas de la API.
    *   **Atributos**:
        *   `id` (int): Identificador único del libro.
    *   **`Config`**: `from_attributes = True` permite mapear desde atributos de ORM a campos de Pydantic.
*   **`ConversionResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta de la conversión de EPUB a PDF.
    *   **Atributos**:
        *   `download_url` (str): URL donde se puede descargar el PDF resultante.
*   **`RagUploadResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta después de subir un libro para procesamiento RAG.
    *   **Atributos**:
        *   `book_id` (str): ID temporal o definitivo del libro en el contexto RAG.
        *   `message` (str): Mensaje de confirmación.
*   **`RagQuery(BaseModel)`**:
    *   **Propósito**: Esquema para la consulta al sistema RAG.
    *   **Atributos**:
        *   `query` (str): La pregunta del usuario.
        *   `book_id` (str): El ID del libro al que se refiere la consulta.
        *   `mode` (str | None): Modo de respuesta de la IA ('strict', 'balanced', 'open').
*   **`RagQueryResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta de la consulta RAG.
    *   **Atributos**:
        *   `response` (str): La respuesta generada por la IA.

### `backend/crud.py`

Contiene funciones de "Create, Read, Update, Delete" (CRUD) para interactuar con la base de datos de libros, utilizando SQLAlchemy.

*   **`get_book_by_path(db: Session, file_path: str)`**:
    *   **Propósito**: Busca un libro por su ruta de archivo única.
    *   **Parámetros**: `db` (sesión de DB), `file_path` (ruta del archivo).
    *   **Retorno**: Objeto `models.Book` si se encuentra, `None` en caso contrario.
*   **`get_book_by_title(db: Session, title: str)`**:
    *   **Propósito**: Busca un libro por su título exacto.
    *   **Parámetros**: `db`, `title`.
    *   **Retorno**: Objeto `models.Book` si se encuentra, `None` en caso contrario.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**:
    *   **Propósito**: Busca libros por un título parcial (case-insensitive) con paginación.
    *   **Parámetros**: `db`, `title`, `skip` (elementos a omitir), `limit` (máximo de elementos).
    *   **Retorno**: Lista de objetos `models.Book`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**:
    *   **Propósito**: Obtiene una lista de libros, con opciones de filtrado por categoría, búsqueda general (título, autor, categoría) y autor. Ordena por ID descendente.
    *   **Parámetros**: `db`, `category` (opcional), `search` (opcional, término general), `author` (opcional).
    *   **Retorno**: Lista de objetos `models.Book`.
*   **`get_categories(db: Session)`**:
    *   **Propósito**: Obtiene una lista de todas las categorías de libros únicas, ordenadas alfabéticamente.
    *   **Parámetros**: `db`.
    *   **Retorno**: `list[str]`.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**:
    *   **Propósito**: Crea un nuevo libro en la base de datos.
    *   **Parámetros**: `db`, `title`, `author`, `category`, `cover_image_url`, `file_path`.
    *   **Retorno**: El objeto `models.Book` recién creado.
*   **`delete_book(db: Session, book_id: int)`**:
    *   **Propósito**: Elimina un libro de la base de datos por su ID, incluyendo sus archivos asociados (libro y portada) del sistema de archivos.
    *   **Parámetros**: `db`, `book_id`.
    *   **Retorno**: El objeto `models.Book` eliminado si se encontró, `None` en caso contrario.
*   **`delete_books_by_category(db: Session, category: str)`**:
    *   **Propósito**: Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados del sistema de archivos.
    *   **Parámetros**: `db`, `category`.
    *   **Retorno**: `int` (número de libros eliminados).
*   **`get_books_count(db: Session)`**:
    *   **Propósito**: Obtiene el número total de libros en la base de datos.
    *   **Parámetros**: `db`.
    *   **Retorno**: `int`.

### `backend/database.py`

Configura la conexión a la base de datos y la sesión de SQLAlchemy.

*   **`_base_dir`, `_db_path`**: Variables internas para construir la ruta absoluta al archivo `library.db` en la raíz del proyecto.
*   **`SQLALCHEMY_DATABASE_URL`**: Cadena de conexión para SQLite.
*   **`engine`**: Objeto `Engine` de SQLAlchemy que gestiona la conexión a la base de datos. Configurado para SQLite (`check_same_thread=False`).
*   **`SessionLocal`**: Constructor de sesiones de base de datos.
*   **`Base`**: Clase base declarativa para los modelos ORM.

### `backend/utils.py`

Contiene funciones de utilidad generales.

*   **`configure_genai()`**:
    *   **Propósito**: Carga las variables de entorno (`.env`) y configura la clave API para Google Generative AI (Gemini).
    *   **Lógica**: Busca `GOOGLE_API_KEY` o `GEMINI_API_KEY`. Si no se encuentra ninguna, lanza un `ValueError`.

### `backend/models.py`

Define los modelos ORM (Object-Relational Mapping) para la base de datos, mapeando clases de Python a tablas de SQLite.

*   **`Book(Base)`**:
    *   **Propósito**: Representa la tabla `books` en la base de datos.
    *   **`__tablename__ = "books"`**: Nombre de la tabla.
    *   **`__table_args__ = {'extend_existing': True}`**: Permite redefinir la tabla en caso de hot-reloading (útil en desarrollo/pruebas).
    *   **Columnas**:
        *   `id` (Integer): Clave primaria, autoincrementable, indexada.
        *   `title` (String): Título del libro, indexado.
        *   `author` (String): Autor del libro, indexado.
        *   `category` (String): Categoría del libro, indexada.
        *   `cover_image_url` (String, nullable=True): URL de la imagen de portada.
        *   `file_path` (String, unique=True): Ruta del archivo original del libro en el sistema, única.

### `backend/rag.py`

Contiene la lógica de Retrieval Augmented Generation (RAG) para permitir interacciones de IA con el contenido de los libros.

*   **Variables Globales (Lazy Initialization)**: `_initialized`, `_collection`, `_ai_enabled`.
*   **`EMBEDDING_MODEL`**, **`GENERATION_MODEL`**: Modelos de Gemini configurables via variables de entorno.
*   **`_ensure_init()`**:
    *   **Propósito**: Inicializa perezosamente la configuración de GenAI y el cliente ChromaDB (persistente en el disco).
    *   **Lógica**: Carga `.env`, configura `genai` si `DISABLE_AI` no está activado, y obtiene/crea la colección `book_rag_collection` en ChromaDB.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**:
    *   **Propósito**: Genera un vector de incrustación (embedding) para un texto dado.
    *   **Parámetros**: `text`, `task_type` (tipo de tarea para el modelo de incrustación).
    *   **Retorno**: `list[float]` (el vector de incrustación). Devuelve un vector dummy si la IA está deshabilitada.
*   **`extract_text_from_pdf(file_path: str)`**:
    *   **Propósito**: Extrae texto de un archivo PDF usando `PyPDF2`.
    *   **Parámetros**: `file_path`.
    *   **Retorno**: `str` (el texto extraído).
*   **`extract_text_from_epub(file_path: str)`**:
    *   **Propósito**: Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`.
    *   **Parámetros**: `file_path`.
    *   **Retorno**: `str` (el texto extraído).
*   **`extract_text(file_path: str)`**:
    *   **Propósito**: Función unificada para extraer texto de tipos de archivo soportados.
    *   **Parámetros**: `file_path`.
    *   **Retorno**: `str`. Lanza `ValueError` si el tipo no es soportado.
*   **`chunk_text(text: str, max_tokens: int = 1000)`**:
    *   **Propósito**: Divide un texto largo en fragmentos más pequeños basados en un recuento máximo de tokens, usando `tiktoken`.
    *   **Parámetros**: `text`, `max_tokens`.
    *   **Retorno**: `list[str]` (lista de fragmentos de texto).
*   **`_has_index_for_book(book_id: str)`**:
    *   **Propósito**: Comprueba si un libro tiene vectores almacenados en ChromaDB.
    *   **Parámetros**: `book_id`.
    *   **Retorno**: `bool`.
*   **`delete_book_from_rag(book_id: str)`**:
    *   **Propósito**: Elimina todos los vectores asociados a un `book_id` de ChromaDB.
    *   **Parámetros**: `book_id`.
*   **`get_index_count(book_id: str)`**:
    *   **Propósito**: Devuelve el número de vectores almacenados para un `book_id` en ChromaDB.
    *   **Parámetros**: `book_id`.
    *   **Retorno**: `int`.
*   **`has_index(book_id: str)`**:
    *   **Propósito**: Helper público para verificar la existencia de índices.
    *   **Parámetros**: `book_id`.
    *   **Retorno**: `bool`.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**:
    *   **Propósito**: Función principal para procesar un libro: extrae texto, lo fragmenta, genera incrustaciones y lo almacena en ChromaDB.
    *   **Parámetros**: `file_path`, `book_id`, `force_reindex` (si es `True`, borra y vuelve a indexar).
    *   **Lógica**: Salta si ya está indexado y `force_reindex` es `False`.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**:
    *   **Propósito**: Estima el número de tokens y fragmentos para un archivo.
    *   **Parámetros**: `file_path`, `max_tokens`.
    *   **Retorno**: `dict` con `tokens` y `chunks`.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**:
    *   **Propósito**: Estima el número de tokens y fragmentos para una lista de archivos.
    *   **Parámetros**: `file_paths`, `max_tokens`.
    *   **Retorno**: `dict` con `tokens`, `chunks` y `files`.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**:
    *   **Propósito**: Realiza una consulta al sistema RAG, recuperando fragmentos relevantes y usando Gemini para generar una respuesta.
    *   **Parámetros**:
        *   `query`: La pregunta del usuario.
        *   `book_id`: ID del libro.
        *   `mode`: Estrategia de respuesta de la IA ('strict', 'balanced', 'open').
        *   `metadata`: Metadatos opcionales del libro (título, autor, categoría) para enriquecer el prompt.
        *   `library`: Contexto opcional de la biblioteca (ej. otras obras del mismo autor).
    *   **Retorno**: `str` (la respuesta de la IA).

### `backend/main.py`

Es el punto de entrada de la aplicación FastAPI, donde se definen todos los endpoints de la API, la configuración de la aplicación y la lógica de alto nivel.

*   **Configuración Inicial**:
    *   Carga variables de entorno (`.env`).
    *   Configura la clave API de Gemini.
    *   Crea las tablas de la base de datos si no existen (`models.Base.metadata.create_all`).
    *   Define rutas absolutas para directorios de archivos (`STATIC_DIR_FS`, `BOOKS_DIR_FS`, `TEMP_BOOKS_DIR_FS`, `STATIC_COVERS_DIR_FS`).
    *   Monta directorios estáticos para servir portadas y archivos temporales.
    *   Configura CORS para permitir solicitudes desde el frontend.
*   **`analyze_with_gemini(text: str)` (async)**:
    *   **Propósito**: Utiliza Google Gemini para analizar texto de un libro e identificar su título, autor y categoría.
    *   **Parámetros**: `text` (texto extraído del libro).
    *   **Retorno**: `dict` con `title`, `author`, `category`. Gestiona errores de IA.
*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str)`**:
    *   **Propósito**: Extrae texto de las primeras páginas de un PDF y busca una imagen de portada.
    *   **Parámetros**: `file_path`, `covers_dir_fs` (directorio para guardar portadas), `covers_url_prefix` (prefijo URL para las portadas).
    *   **Retorno**: `dict` con `text` y `cover_image_url` (si se encuentra).
*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str)`**:
    *   **Propósito**: Extrae texto de un EPUB y busca una imagen de portada (con varios métodos de fallback).
    *   **Parámetros**: `file_path`, `covers_dir_fs`, `covers_url_prefix`.
    *   **Retorno**: `dict` con `text` y `cover_image_url` (si se encuentra).
*   **`get_db()`**:
    *   **Propósito**: Función de dependencia para obtener una sesión de base de datos.
    *   **Uso**: Inyectada en los endpoints de la API.
*   **Endpoints de la API**:
    *   **`POST /upload-book/`**:
        *   Sube un archivo de libro (PDF/EPUB), lo guarda, lo procesa con `process_pdf/epub`, lo analiza con `analyze_with_gemini`, y lo guarda en la base de datos usando `crud.create_book`. Incluye validación de calidad de IA.
        *   **Request**: `UploadFile`
        *   **Response**: `schemas.Book`
    *   **`GET /books/`**:
        *   Obtiene una lista de libros. Permite filtrar por `category`, `search` (general), y `author`.
        *   **Query Params**: `category`, `search`, `author`.
        *   **Response**: `List[schemas.Book]`
    *   **`GET /books/count`**:
        *   Devuelve el número total de libros en la biblioteca.
        *   **Response**: `int`
    *   **`GET /books/search/`**:
        *   Busca libros por título parcial con paginación.
        *   **Query Params**: `title`, `skip`, `limit`.
        *   **Response**: `List[schemas.Book]`
    *   **`GET /categories/`**:
        *   Devuelve una lista de todas las categorías de libros únicas.
        *   **Response**: `List[str]`
    *   **`DELETE /books/{book_id}`**:
        *   Elimina un libro por su ID de la base de datos y sus archivos asociados, incluyendo la limpieza de su índice RAG.
        *   **Path Params**: `book_id` (int).
        *   **Response**: `dict` con mensaje.
    *   **`DELETE /categories/{category_name}`**:
        *   Elimina todos los libros de una categoría específica, sus archivos y sus índices RAG.
        *   **Path Params**: `category_name` (str).
        *   **Response**: `dict` con mensaje.
    *   **`GET /books/download/{book_id}`**:
        *   Permite descargar o abrir un archivo de libro.
        *   **Path Params**: `book_id` (int).
        *   **Response**: `FileResponse` (PDF o EPUB).
    *   **`POST /tools/convert-epub-to-pdf`**:
        *   Convierte un archivo EPUB subido a PDF y lo guarda temporalmente.
        *   **Request**: `UploadFile` (EPUB).
        *   **Response**: `schemas.ConversionResponse` (URL de descarga del PDF).
    *   **`POST /rag/upload-book/`**:
        *   Sube un archivo temporalmente y lo procesa para RAG. Devuelve un ID para referencia futura.
        *   **Request**: `UploadFile`.
        *   **Response**: `schemas.RagUploadResponse`.
    *   **`POST /rag/query/`**:
        *   Consulta el sistema RAG para un libro específico.
        *   **Request**: `schemas.RagQuery`.
        *   **Response**: `schemas.RagQueryResponse`.
    *   **`POST /rag/index/{book_id}`**:
        *   Indexa un libro existente en la base de datos para el sistema RAG.
        *   **Path Params**: `book_id` (int).
        *   **Query Params**: `force` (bool, para reindexar).
        *   **Response**: `dict` con mensaje.
    *   **`GET /rag/status/{book_id}`**:
        *   Devuelve el estado del índice RAG para un libro (si está indexado, número de vectores).
        *   **Path Params**: `book_id` (int).
        *   **Response**: `dict` con `book_id`, `indexed`, `vector_count`.
    *   **`POST /rag/reindex/category/{category_name}`**:
        *   (Re)indexa todos los libros de una categoría específica en RAG.
        *   **Path Params**: `category_name` (str).
        *   **Query Params**: `force` (bool).
        *   **Response**: `dict` con resultados del procesamiento.
    *   **`POST /rag/reindex/all`**:
        *   (Re)indexa todos los libros de la biblioteca en RAG.
        *   **Query Params**: `force` (bool).
        *   **Response**: `dict` con resultados del procesamiento.
    *   **`GET /rag/estimate/book/{book_id}`**, **`category/{category_name}`**, **`all`**:
        *   Estima el número de tokens y fragmentos para el procesamiento RAG de un libro, categoría o toda la biblioteca. Opcionalmente, calcula un coste basado en un precio por 1000 tokens.
        *   **Path Params**: `book_id` (int) o `category_name` (str).
        *   **Query Params**: `per1k` (float, coste por 1000 tokens), `max_tokens` (int, tamaño de fragmento).
        *   **Response**: `dict` con estimaciones y coste.

### `backend/__init__.py`

Un archivo `__init__.py` vacío, que simplemente marca el directorio `backend` como un paquete Python. El `__all__ = []` no tiene un impacto significativo en la forma en que se importan los módulos dentro del paquete en este proyecto, ya que se usan importaciones explícitas.

## 4. Análisis Detallado del Frontend (React)

El frontend está construido con React y utiliza `react-router-dom` para la navegación. La interfaz es moderna y reactiva, interactuando con el backend a través de la API REST.

### `frontend/src/App.js`

*   **Propósito**: Componente raíz de la aplicación React. Configura el enrutamiento y la estructura general de la interfaz.
*   **Estado**: No gestiona estado propio.
*   **Props**: No recibe props.
*   **Efectos Secundarios**: No tiene efectos secundarios directos.
*   **Interacciones**: Define las rutas de la aplicación para navegar entre las diferentes vistas (`/`, `/upload`, `/etiquetas`, `/herramientas`, `/rag`, `/leer/:bookId`).
*   **Componentes Hijos**: `Header`, `LibraryView`, `UploadView`, `CategoriesView`, `ToolsView`, `ReaderView`, `RagView`.

### `frontend/src/Header.js`

*   **Propósito**: Barra de navegación superior de la aplicación, incluye el título, un contador de libros y enlaces a las diferentes secciones.
*   **Estado**:
    *   `menuOpen` (boolean): Controla la visibilidad del menú de navegación en dispositivos móviles.
    *   `bookCount` (number): Número total de libros en la biblioteca.
    *   `errorMessage` (string | null): Mensaje de error si falla la carga del contador.
*   **Props**: No recibe props.
*   **Efectos Secundarios**:
    *   `useEffect`: Al montar el componente, realiza una llamada a `GET /books/count` para obtener el número total de libros y lo actualiza cada 10 minutos (600000 ms).
*   **Interacciones del Usuario**:
    *   Botón de hamburguesa: Abre/cierra el menú en móviles.
    *   Enlaces de navegación: Redirigen a las diferentes vistas de la aplicación.
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/books/count`: Para obtener el número total de libros.

### `frontend/src/LibraryView.js`

*   **Propósito**: Vista principal que muestra la lista de libros disponibles en la biblioteca. Permite buscar, filtrar y realizar acciones sobre los libros.
*   **Estado**:
    *   `books` (array): Lista de objetos libro obtenidos del backend.
    *   `searchParams` (URLSearchParams): Objeto para gestionar los parámetros de la URL (ej. `?category=Ficción`).
    *   `searchTerm` (string): Valor actual del input de búsqueda.
    *   `debouncedSearchTerm` (string): Versión "debounced" del `searchTerm` para evitar llamadas API excesivas.
    *   `error` (string): Mensaje de error si falla la carga o eliminación de libros.
    *   `loading` (boolean): Indica si la lista de libros está cargando.
    *   `isMobile` (boolean): Detecta si el dispositivo es móvil para adaptar la interfaz (ej. botones de descarga).
*   **Props**: No recibe props.
*   **Efectos Secundarios**:
    *   `useEffect` (detección móvil): Escucha cambios en el tamaño de la ventana para actualizar `isMobile`.
    *   `useEffect` (fetch libros): Llama a `fetchBooks` cuando cambia `debouncedSearchTerm` o `searchParams`.
*   **Hooks Personalizados**:
    *   `useDebounce(value, delay)`: Retrasa la actualización de un valor, útil para búsquedas.
*   **Componentes Internos**:
    *   `BookCover({ src, alt, title })`: Componente que muestra la portada de un libro, con un fallback a una portada genérica si la imagen no carga o no existe.
*   **Interacciones del Usuario**:
    *   Input de búsqueda: Permite buscar libros por título, autor o categoría.
    *   Clic en Autor/Categoría: Filtra la vista por el autor o categoría seleccionados.
    *   Botón "×": Elimina un libro de la biblioteca (con confirmación).
    *   Botón "Abrir PDF": Abre el PDF en una nueva pestaña (para PDFs).
    *   Botón "Leer EPUB": Navega a la vista `ReaderView` para EPUBs.
    *   Botón "Descargar PDF/EPUB": (visible en móvil) Descarga el archivo del libro.
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/books/?...`: Para obtener libros filtrados o buscados.
    *   `DELETE ${API_URL}/books/{bookId}`: Para eliminar un libro.
    *   `GET ${API_URL}/books/download/{bookId}`: Para descargar o abrir un libro.

### `frontend/src/UploadView.js`

*   **Propósito**: Interfaz para subir nuevos archivos de libros a la biblioteca. Permite subir uno o varios archivos simultáneamente con seguimiento de estado.
*   **Estado**:
    *   `filesToUpload` (array de objetos): Cada objeto contiene `file` (el objeto `File` nativo), `status` ('pending', 'uploading', 'success', 'error') y `message` (información del proceso).
    *   `isUploading` (boolean): Indica si hay archivos en proceso de subida.
*   **Props**: No recibe props.
*   **Efectos Secundarios**: No tiene efectos secundarios directos.
*   **Interacciones del Usuario**:
    *   Input de archivo: Permite seleccionar uno o varios archivos (PDF o EPUB).
    *   Zona de arrastrar y soltar (`drop-zone`): Permite añadir archivos mediante drag-and-drop.
    *   Botón "Subir Archivo(s)": Inicia el proceso de subida para todos los archivos pendientes.
    *   Botón "Ir a la Biblioteca": Aparece cuando todos los archivos han sido procesados.
*   **Comunicación con el Backend**:
    *   `POST ${API_URL}/upload-book/`: Sube cada archivo individualmente para su procesamiento.

### `frontend/src/ToolsView.js`

*   **Propósito**: Contenedor para diversas herramientas de utilidad de la biblioteca. Actualmente aloja el `EpubToPdfConverter`.
*   **Estado**: No gestiona estado propio, funciona como un envoltorio para las herramientas.
*   **Props**: No recibe props.
*   **Efectos Secundarios**: No tiene efectos secundarios directos.
*   **Componentes Hijos**: `EpubToPdfConverter`.

#### `EpubToPdfConverter` (interno a `ToolsView.js`)

*   **Propósito**: Permite a los usuarios subir un archivo EPUB y convertirlo a PDF.
*   **Estado**:
    *   `selectedFile` (object | null): El archivo EPUB seleccionado para la conversión.
    *   `message` (string): Mensajes de estado o error para el usuario.
    *   `isLoading` (boolean): Indica si el proceso de conversión está en curso.
*   **Props**: No recibe props.
*   **Efectos Secundarios**: No tiene efectos secundarios directos.
*   **Interacciones del Usuario**:
    *   Input de archivo: Seleccionar un archivo EPUB.
    *   Zona de arrastrar y soltar: Añadir archivo EPUB.
    *   Botón "Convertir a PDF": Inicia la conversión. Una vez completada, inicia la descarga del PDF.
*   **Comunicación con el Backend**:
    *   `POST ${API_URL}/tools/convert-epub-to-pdf`: Envía el archivo EPUB para su conversión y recibe la URL del PDF resultante.

### `frontend/src/ReaderView.js`

*   **Propósito**: Vista dedicada a la lectura de libros en formato EPUB utilizando la librería `react-reader`.
*   **Estado**:
    *   `location` (string | null): CFI (Canonical Fragment Identifier) del EPUB, que guarda la posición actual de lectura.
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB, necesarios para `react-reader`.
    *   `isLoading` (boolean): Indica si el libro está cargando.
    *   `error` (string): Mensaje de error si falla la carga del libro.
*   **Props**: No recibe props.
*   **Efectos Secundarios**:
    *   `useEffect`: Al montar el componente (o cuando cambia `bookId`), realiza una solicitud a `GET /books/download/{bookId}` para obtener los datos binarios del EPUB.
*   **Interacciones del Usuario**:
    *   `react-reader` gestiona las interacciones de paginación y navegación dentro del EPUB.
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/books/download/{bookId}`: Descarga el archivo EPUB.

### `frontend/src/RagView.js`

*   **Propósito**: Interfaz de chat que permite a los usuarios hacer preguntas sobre el contenido de un libro de su biblioteca, utilizando el sistema RAG.
*   **Estado**:
    *   `message` (string): Mensajes informativos o de error para el usuario.
    *   `isLoading` (boolean): Indica si la IA está generando una respuesta.
    *   `bookId` (string | null): El ID del libro actualmente seleccionado para el chat.
    *   `chatHistory` (array de objetos): Almacena los mensajes del usuario y las respuestas de la IA.
    *   `currentQuery` (string): La pregunta actual que el usuario está escribiendo.
    *   `libraryBooks` (array): Lista de libros disponibles en la biblioteca para seleccionar.
    *   `selectedLibraryId` (string): ID del libro seleccionado en la lista desplegable/búsqueda.
    *   `libStatus` (object): Información sobre el estado RAG del libro seleccionado (cargando, indexado, conteo de vectores, error).
    *   `actionsBusy` (boolean): Bloquea las acciones de indexado/reindexado mientras están en curso.
    *   `refreshing` (boolean): Indica si se está refrescando el estado RAG.
    *   `searchTerm` (string): Término de búsqueda para filtrar libros de la biblioteca.
    *   `searching` (boolean): Indica si la búsqueda de libros está en curso.
    *   `searchResults` (array): Resultados de la búsqueda de libros.
    *   `resultsOpen` (boolean): Controla la visibilidad de los resultados de búsqueda.
    *   `mode` (string): Modo de respuesta de la IA ('strict', 'balanced', 'open').
    *   `selectedBook` (object | null): Objeto completo del libro seleccionado.
*   **Props**: No recibe props.
*   **Referencias (Refs)**:
    *   `inputRef`: Referencia al `textarea` de la consulta del chat para enfocarlo.
    *   `chatHistoryRef`: Referencia al contenedor del historial de chat para desplazamiento automático.
*   **Efectos Secundarios**:
    *   `useEffect` (cargar libros): Al montar, carga la lista de todos los libros de la biblioteca.
    *   `useEffect` (búsqueda de libros): Realiza una búsqueda "debounced" de libros a medida que el usuario escribe en `searchTerm`.
    *   `useEffect` (scroll del chat): Desplaza automáticamente el historial de chat al final cuando se añaden nuevos mensajes o la IA está cargando.
    *   `useEffect` (estado RAG): Cuando `selectedLibraryId` cambia, llama a `checkLibraryStatus` para actualizar la información de indexado.
*   **Interacciones del Usuario**:
    *   Input de búsqueda: Busca libros en la biblioteca para seleccionar uno.
    *   Selección de libro: Elige un libro de los resultados de búsqueda.
    *   Botones "Comprobar RAG", "Indexar", "Reindexar", "Chatear": Gestionan el estado de indexado del libro y el inicio del chat.
    *   Selección de `mode`: Elige la preferencia de respuesta de la IA.
    *   Textarea de consulta: Escribe preguntas sobre el libro.
    *   Botón "Enviar": Envía la pregunta a la IA.
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/books/`: Para obtener la lista de libros y los resultados de búsqueda.
    *   `GET ${API_URL}/rag/status/{bookId}`: Para verificar si un libro ya está indexado en RAG.
    *   `POST ${API_URL}/rag/index/{bookId}`: Para indexar (o reindexar) un libro en RAG.
    *   `POST ${API_URL}/rag/query/`: Para enviar una consulta al sistema RAG y obtener una respuesta.

### `frontend/src/CategoriesView.js`

*   **Propósito**: Muestra una lista de todas las categorías de libros únicas, permitiendo a los usuarios navegar a la vista de biblioteca filtrada por una categoría específica.
*   **Estado**:
    *   `categories` (array): Lista de cadenas de categorías únicas.
    *   `error` (string): Mensaje de error si falla la carga de categorías.
    *   `loading` (boolean): Indica si la lista de categorías está cargando.
*   **Props**: No recibe props.
*   **Efectos Secundarios**:
    *   `useEffect`: Al montar, realiza una llamada a `GET /categories/` para obtener las categorías disponibles.
*   **Interacciones del Usuario**:
    *   Clic en una tarjeta de categoría: Navega a `/` (LibraryView) con el parámetro de búsqueda `?category=...`.
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/categories/`: Para obtener la lista de categorías.

### `frontend/src/config.js`

*   **Propósito**: Archivo de configuración simple para definir la URL base del backend API.
*   **Lógica**: Utiliza la variable de entorno `REACT_APP_API_URL` si está definida, de lo contrario, usa `http://localhost:8001` como valor por defecto.

### `frontend/src/ErrorBoundary.js`

*   **Propósito**: Componente React de "Boundary Error" para capturar errores de JavaScript en su árbol de componentes hijo. Proporciona una interfaz de usuario de respaldo en caso de errores, mejorando la robustez de la aplicación.
*   **Estado**:
    *   `hasError` (boolean): Indica si se ha capturado un error.
    *   `error` (Error | null): El objeto de error capturado.
*   **Métodos del Ciclo de Vida**:
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para indicar que se ha producido un error.
    *   `componentDidCatch(error, info)`: Registra el error en la consola para depuración.
*   **Renderizado**: Si `hasError` es `true`, muestra un mensaje de error con la información del error; de lo contrario, renderiza los componentes hijos.

## 5. Flujo de Datos y API

Esta sección describe cómo los datos fluyen a través de la aplicación y resume los principales endpoints de la API del backend.

### Flujos de Datos Clave

1.  **Subida de un Libro:**
    *   **Frontend (`UploadView`)**: El usuario selecciona uno o varios archivos (PDF/EPUB).
    *   **Comunicación**: Cada archivo se envía individualmente al endpoint `POST /upload-book/` del backend.
    *   **Backend (`main.py`)**:
        *   Recibe el archivo y lo guarda en el directorio `backend/books/`.
        *   Detecta el tipo de archivo y utiliza `process_pdf()` o `process_epub()` para extraer el texto inicial y, si es posible, una imagen de portada.
        *   Llama a `analyze_with_gemini()` con el texto extraído para obtener automáticamente el título, autor y categoría.
        *   Si la IA no puede identificar el título/autor, se rechaza la subida.
        *   Si tiene éxito, `crud.create_book()` almacena los metadatos del libro (título, autor, categoría, URL de portada, ruta de archivo) en la base de datos SQLite.
    *   **Resultado**: El libro está disponible en la biblioteca, con sus metadatos y portada.

2.  **Navegación y Filtrado de Libros:**
    *   **Frontend (`LibraryView`)**: El componente realiza una solicitud `GET /books/` al montar o cuando los parámetros de búsqueda/filtro cambian (por `searchTerm`, `category` o `author`).
    *   **Backend (`main.py`)**:
        *   El endpoint `GET /books/` invoca a `crud.get_books()` con los filtros proporcionados.
        *   `crud.get_books()` consulta la base de datos SQLite para obtener los libros que coinciden.
    *   **Resultado**: `LibraryView` muestra la lista de libros con sus metadatos y portadas, permitiendo al usuario abrirlos o eliminarlos.

3.  **Conversación con la IA sobre un Libro (RAG):**
    *   **Frontend (`RagView`)**:
        1.  **Selección/Búsqueda de Libro**: El usuario busca y selecciona un libro de la biblioteca (usando `GET /books/`).
        2.  **Verificación RAG**: `RagView` comprueba el estado RAG del libro con `GET /rag/status/{book_id}`.
        3.  **Indexado (si es necesario)**: Si el libro no está indexado, el usuario lo inicia (o fuerza la reindexación) con `POST /rag/index/{book_id}`.
            *   **Backend (`main.py`)**: Recibe la solicitud y llama a `rag.process_book_for_rag()`.
            *   **Backend (`rag.py`)**: Extrae el texto del libro, lo fragmenta, genera incrustaciones con Gemini y las almacena en ChromaDB.
        4.  **Consulta Chat**: El usuario escribe una pregunta y la envía a `POST /rag/query/`.
    *   **Backend (`main.py`)**:
        *   El endpoint `POST /rag/query/` invoca a `rag.query_rag()`.
    *   **Backend (`rag.py`)**:
        *   Genera una incrustación para la pregunta del usuario.
        *   Busca los fragmentos de texto más relevantes en ChromaDB para el `book_id` dado.
        *   Construye un prompt para Gemini, incluyendo la pregunta, los fragmentos relevantes y metadatos del libro/biblioteca (según el `mode` de consulta).
        *   `genai.GenerativeModel` genera la respuesta.
    *   **Resultado**: `RagView` muestra la respuesta de la IA en el historial del chat.

4.  **Conversión de EPUB a PDF:**
    *   **Frontend (`ToolsView` -> `EpubToPdfConverter`)**: El usuario sube un archivo EPUB.
    *   **Comunicación**: El archivo se envía a `POST /tools/convert-epub-to-pdf`.
    *   **Backend (`main.py`)**:
        *   Recibe el archivo EPUB.
        *   Utiliza librerías como `zipfile`, `BeautifulSoup` y `WeasyPrint` para extraer el contenido del EPUB y renderizarlo como PDF.
        *   El PDF resultante se guarda temporalmente en el directorio `backend/temp_books/`.
        *   Devuelve una URL de descarga a través del endpoint montado en `/temp_books/`.
    *   **Resultado**: El frontend recibe una URL, la cual se utiliza para iniciar la descarga automática del PDF convertido en el navegador.

### Resumen de Endpoints de la API del Backend

| Método | Ruta                                  | Descripción                                                                                               | Esquema Request                      | Esquema Response                     |
| :----- | :------------------------------------ | :-------------------------------------------------------------------------------------------------------- | :----------------------------------- | :----------------------------------- |
| `POST` | `/upload-book/`                       | Sube y procesa un nuevo libro (PDF/EPUB) con IA.                                                          | `UploadFile`                         | `schemas.Book`                       |
| `GET`  | `/books/`                             | Obtiene una lista de libros. Admite filtros por `category`, `search`, `author`.                           | (Query Params)                       | `List[schemas.Book]`                 |
| `GET`  | `/books/count`                        | Devuelve el número total de libros.                                                                       | (None)                               | `int`                                |
| `GET`  | `/books/search/`                      | Busca libros por título parcial. Admite `skip`, `limit` para paginación.                                  | (Query Params)                       | `List[schemas.Book]`                 |
| `GET`  | `/categories/`                        | Obtiene una lista de todas las categorías únicas.                                                         | (None)                               | `List[str]`                          |
| `DELETE`|`/books/{book_id}`                     | Elimina un libro específico y sus archivos asociados, incluyendo el índice RAG.                            | (None)                               | `dict` (mensaje)                     |
| `DELETE`|`/categories/{category_name}`          | Elimina todos los libros de una categoría y sus archivos/índices RAG.                                     | (None)                               | `dict` (mensaje)                     |
| `GET`  | `/books/download/{book_id}`           | Permite descargar o ver un archivo de libro.                                                              | (None)                               | `FileResponse`                       |
| `POST` | `/tools/convert-epub-to-pdf`          | Convierte un archivo EPUB subido a PDF.                                                                   | `UploadFile`                         | `schemas.ConversionResponse`         |
| `POST` | `/rag/upload-book/`                   | Sube un libro (temporalmente) y lo procesa para RAG.                                                      | `UploadFile`                         | `schemas.RagUploadResponse`          |
| `POST` | `/rag/query/`                         | Realiza una consulta RAG sobre el contenido de un libro.                                                  | `schemas.RagQuery`                   | `schemas.RagQueryResponse`           |
| `POST` | `/rag/index/{book_id}`                | Indexa un libro existente en la base de datos para RAG. Admite `force` para reindexar.                     | (None)                               | `dict` (mensaje)                     |
| `GET`  | `/rag/status/{book_id}`               | Devuelve el estado de indexación RAG para un libro.                                                       | (None)                               | `dict` (estado RAG)                  |
| `POST` | `/rag/reindex/category/{category_name}`| (Re)indexa todos los libros de una categoría en RAG.                                                      | (None)                               | `dict` (resultados)                  |
| `POST` | `/rag/reindex/all`                    | (Re)indexa todos los libros de la biblioteca en RAG.                                                      | (None)                               | `dict` (resultados)                  |
| `GET`  | `/rag/estimate/book/{book_id}`        | Estima tokens/chunks y coste de RAG para un libro.                                                        | (Query Params)                       | `dict` (estimación)                  |
| `GET`  | `/rag/estimate/category/{category_name}`| Estima tokens/chunks y coste de RAG para una categoría.                                                   | (Query Params)                       | `dict` (estimación)                  |
| `GET`  | `/rag/estimate/all`                   | Estima tokens/chunks y coste de RAG para toda la biblioteca.                                              | (Query Params)                       | `dict` (estimación)                  |
```
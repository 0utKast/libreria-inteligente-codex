# Documentación del Proyecto: Mi Librería Inteligente

Este documento describe la arquitectura, la implementación y el flujo de trabajo del proyecto "Mi Librería Inteligente", una aplicación web para la gestión de bibliotecas digitales personales con capacidades de IA.

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales. Los usuarios pueden subir archivos de libros (PDF y EPUB), y la aplicación utiliza Inteligencia Artificial (IA) para extraer automáticamente metadatos como el título, el autor y la categoría. Además de las funcionalidades básicas de una biblioteca (visualización, búsqueda, filtrado y eliminación de libros), la aplicación incorpora herramientas avanzadas como la conversión de EPUB a PDF y un sistema de Conversación Aumentada por Recuperación (RAG) que permite a los usuarios interactuar con el contenido de sus libros mediante un chatbot basado en IA.

### Arquitectura General

La aplicación sigue una arquitectura cliente-servidor, dividida en dos componentes principales:

*   **Frontend**: Una aplicación web interactiva desarrollada con **React.js**. Se encarga de la interfaz de usuario, la gestión del estado y la comunicación con el backend a través de peticiones HTTP.
*   **Backend**: Un servidor de API RESTful construido con **FastAPI** (Python). Gestiona la lógica de negocio, la interacción con la base de datos, el procesamiento de archivos, la integración con servicios de IA y la persistencia de datos.

### Tecnologías Clave:

*   **Backend**:
    *   Python 3.x
    *   FastAPI: Framework web de alto rendimiento.
    *   SQLAlchemy: ORM (Object Relational Mapper) para la interacción con la base de datos.
    *   SQLite: Base de datos ligera utilizada para la persistencia de los metadatos de los libros.
    *   Alembic: Herramienta de migración de bases de datos para SQLAlchemy.
    *   Google Generative AI (Gemini): Utilizada para la extracción inteligente de metadatos de libros y como modelo de generación para el sistema RAG.
    *   ChromaDB: Base de datos vectorial utilizada para almacenar los embeddings (representaciones vectoriales) del contenido de los libros para el sistema RAG.
    *   PyPDF2, ebooklib, BeautifulSoup, fitz (PyMuPDF): Bibliotecas para la extracción de texto y portadas de archivos PDF y EPUB.
    *   WeasyPrint: Utilizado para la conversión de EPUB a PDF.
    *   `python-dotenv`: Para la gestión de variables de entorno.
*   **Frontend**:
    *   React.js: Biblioteca de JavaScript para construir interfaces de usuario.
    *   React Router DOM: Para la gestión del enrutamiento en el cliente.
    *   `react-reader`: Componente para la visualización de libros EPUB.
    *   `react-error-boundary`: Para la gestión robusta de errores en la interfaz de usuario.
    *   CSS: Para el estilo de la aplicación.
*   **Almacenamiento**:
    *   Los archivos de libros originales y las imágenes de portada extraídas se almacenan en el sistema de archivos del servidor.
    *   Los índices vectoriales para RAG se persisten en disco utilizando ChromaDB.

## 2. Estructura del Proyecto

La estructura del proyecto está organizada de la siguiente manera:

```
.
├── backend/
│   ├── alembic/                      # Gestión de migraciones de la base de datos (Alembic)
│   │   └── versions/                 # Scripts de migración de la base de datos
│   ├── books/                        # Directorio para almacenar los archivos de libros subidos
│   ├── static/                       # Archivos estáticos servidos por FastAPI
│   │   └── covers/                   # Imágenes de portada de los libros
│   ├── temp_books/                   # Archivos temporales (ej: PDFs convertidos)
│   ├── tests/                        # Pruebas unitarias e de integración del backend
│   ├── tests_curated/                # Pruebas de backend seleccionadas o curadas
│   ├── __init__.py                   # Archivo de inicialización del paquete Python
│   ├── crud.py                       # Operaciones CRUD para la base de datos
│   ├── database.py                   # Configuración de la base de datos SQLAlchemy
│   ├── main.py                       # Aplicación FastAPI principal y definición de endpoints
│   ├── models.py                     # Definiciones de modelos de la base de datos (SQLAlchemy)
│   ├── rag.py                        # Lógica del sistema de Conversación Aumentada por Recuperación (RAG)
│   ├── schemas.py                    # Modelos Pydantic para validación de datos (API)
│   └── utils.py                      # Funciones de utilidad (ej: configuración de la IA)
├── frontend/
│   ├── public/                       # Archivos estáticos públicos para React
│   ├── src/                          # Código fuente de la aplicación React
│   │   ├── App.css                   # Estilos globales de la aplicación
│   │   ├── App.js                    # Componente raíz de React
│   │   ├── CategoriesView.css        # Estilos para CategoriesView
│   │   ├── CategoriesView.js         # Componente para la vista de categorías
│   │   ├── ErrorBoundary.js          # Componente para manejo de errores de UI
│   │   ├── Header.css                # Estilos para el Header
│   │   ├── Header.js                 # Componente de encabezado
│   │   ├── LibraryView.css           # Estilos para LibraryView
│   │   ├── LibraryView.js            # Componente para la vista de la biblioteca principal
│   │   ├── RagView.css               # Estilos para RagView
│   │   ├── RagView.js                # Componente para la vista de chat con IA (RAG)
│   │   ├── ReaderView.css            # Estilos para ReaderView
│   │   ├── ReaderView.js             # Componente para la vista de lectura de libros
│   │   ├── ToolsView.css             # Estilos para ToolsView
│   │   ├── ToolsView.js              # Componente para la vista de herramientas
│   │   ├── UploadView.css            # Estilos para UploadView
│   │   ├── UploadView.js             # Componente para la vista de carga de libros
│   │   ├── config.js                 # Configuración del frontend (ej: URL de la API)
│   │   ├── index.css                 # Estilos CSS base
│   │   └── index.js                  # Punto de entrada de la aplicación React
│   └── package.json                  # Definiciones y scripts del proyecto Frontend (npm/yarn)
├── .env                              # Variables de entorno (no versionado)
├── library.db                        # Base de datos SQLite (generada)
├── rag_index/                        # Directorio persistente de ChromaDB para el índice RAG
└── README.md                         # Documentación general del proyecto (este archivo)
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend es el núcleo de la lógica de negocio, manejo de datos y orquestación de la IA.

### `backend/schemas.py`

*   **Propósito**: Define los modelos de datos para la validación de entrada y la serialización de salida en la API utilizando `Pydantic`. Estos esquemas aseguran que los datos intercambiados entre el frontend y el backend sean consistentes y válidos.

*   **Clases Principales**:
    *   `BookBase(BaseModel)`
        *   **Descripción**: Esquema base para los datos de un libro, utilizado para la creación o actualización de libros donde el `id` aún no está presente.
        *   **Campos**:
            *   `title` (str): Título del libro.
            *   `author` (str): Autor del libro.
            *   `category` (str): Categoría a la que pertenece el libro.
            *   `cover_image_url` (str | None): URL o ruta a la imagen de portada del libro (opcional).
            *   `file_path` (str): Ruta absoluta en el servidor al archivo del libro original.
    *   `Book(BookBase)`
        *   **Descripción**: Esquema completo de un libro, que extiende `BookBase` añadiendo el identificador único. Se utiliza para representar libros ya existentes en la base de datos.
        *   **Campos**:
            *   `id` (int): Identificador único del libro en la base de datos.
        *   **Configuración**: `Config.from_attributes = True` permite la compatibilidad con modelos ORM de SQLAlchemy.
    *   `ConversionResponse(BaseModel)`
        *   **Descripción**: Esquema de respuesta para el endpoint de conversión de EPUB a PDF.
        *   **Campos**:
            *   `download_url` (str): URL donde se puede descargar el archivo PDF convertido.
    *   `RagUploadResponse(BaseModel)`
        *   **Descripción**: Esquema de respuesta para la carga de un libro para el procesamiento RAG.
        *   **Campos**:
            *   `book_id` (str): El ID asignado al libro para su uso en el sistema RAG.
            *   `message` (str): Un mensaje de estado sobre la operación.
    *   `RagQuery(BaseModel)`
        *   **Descripción**: Esquema para las peticiones de consulta al sistema RAG.
        *   **Campos**:
            *   `query` (str): La pregunta del usuario.
            *   `book_id` (str): El ID del libro sobre el que se realiza la consulta.
            *   `mode` (str | None): Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`). `'balanced'` es el predeterminado si no se especifica.
    *   `RagQueryResponse(BaseModel)`
        *   **Descripción**: Esquema de respuesta para las consultas al sistema RAG.
        *   **Campos**:
            *   `response` (str): La respuesta generada por la IA.

### `backend/crud.py`

*   **Propósito**: Módulo de operaciones C.R.U.D (Crear, Leer, Actualizar, Eliminar) para los libros en la base de datos. Abstrae la lógica de interacción con SQLAlchemy y maneja la eliminación de archivos asociados.

*   **Funciones Principales**:
    *   `get_book_by_path(db: Session, file_path: str)`
        *   **Lógica**: Busca un libro en la base de datos por su ruta de archivo única.
        *   **Parámetros**: `db` (sesión de SQLAlchemy), `file_path` (ruta del archivo).
        *   **Retorno**: Instancia de `models.Book` si se encuentra, `None` en caso contrario.
    *   `get_book_by_title(db: Session, title: str)`
        *   **Lógica**: Busca un libro por su título exacto.
        *   **Parámetros**: `db`, `title`.
        *   **Retorno**: Instancia de `models.Book` o `None`.
    *   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`
        *   **Lógica**: Busca libros donde el título contiene una subcadena (sin distinción entre mayúsculas y minúsculas), con paginación.
        *   **Parámetros**: `db`, `title`, `skip` (elementos a omitir), `limit` (número máximo de resultados).
        *   **Retorno**: Lista de instancias de `models.Book`.
    *   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`
        *   **Lógica**: Obtiene una lista de libros, permitiendo filtrar por categoría, autor, y una búsqueda general que coincide en título, autor o categoría. Los resultados se ordenan por ID de forma descendente.
        *   **Parámetros**: `db`, `category` (opcional), `search` (opcional), `author` (opcional).
        *   **Retorno**: Lista de instancias de `models.Book`.
    *   `get_categories(db: Session) -> list[str]`
        *   **Lógica**: Obtiene todas las categorías únicas de los libros existentes en la base de datos, ordenadas alfabéticamente.
        *   **Parámetros**: `db`.
        *   **Retorno**: Lista de cadenas (nombres de categoría).
    *   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`
        *   **Lógica**: Crea un nuevo registro de libro en la base de datos con los datos proporcionados.
        *   **Parámetros**: `db`, `title`, `author`, `category`, `cover_image_url`, `file_path`.
        *   **Retorno**: La instancia `models.Book` del libro recién creado.
    *   `delete_book(db: Session, book_id: int)`
        *   **Lógica**: Elimina un libro por su ID. Incluye la eliminación de los archivos físicos del libro y su portada asociada del sistema de archivos.
        *   **Parámetros**: `db`, `book_id`.
        *   **Retorno**: La instancia `models.Book` del libro eliminado si se encontró, `None` en caso contrario.
    *   `delete_books_by_category(db: Session, category: str)`
        *   **Lógica**: Elimina todos los libros que pertenecen a una categoría específica, junto con sus archivos asociados.
        *   **Parámetros**: `db`, `category`.
        *   **Retorno**: El número de libros eliminados.
    *   `get_books_count(db: Session) -> int`
        *   **Lógica**: Retorna el número total de libros en la base de datos.
        *   **Parámetros**: `db`.
        *   **Retorno**: Un entero.

### `backend/database.py`

*   **Propósito**: Configura la conexión a la base de datos utilizando SQLAlchemy. Se utiliza SQLite para la simplicidad y la portabilidad.

*   **Variables y Clases**:
    *   `SQLALCHEMY_DATABASE_URL`: Define la cadena de conexión a la base de datos. Apunta a un archivo `library.db` en la raíz del proyecto. `connect_args={"check_same_thread": False}` es necesario para SQLite con FastAPI.
    *   `engine`: La instancia del motor de SQLAlchemy, que gestiona la conexión a la base de datos.
    *   `SessionLocal`: Un constructor de sesiones de SQLAlchemy que se utiliza para crear objetos de sesión de base de datos. Está configurado para no auto-commit y no auto-flush.
    *   `Base`: La base declarativa de SQLAlchemy, de la que heredan los modelos de la base de datos.

### `backend/utils.py`

*   **Propósito**: Contiene funciones de utilidad genéricas. Actualmente, su función principal es configurar la API de Google Generative AI.

*   **Funciones Principales**:
    *   `configure_genai()`
        *   **Lógica**: Carga las variables de entorno desde el archivo `.env`. Busca `GOOGLE_API_KEY` o `GEMINI_API_KEY` para configurar el cliente de Google Generative AI.
        *   **Parámetros**: Ninguno.
        *   **Retorno**: Ninguno.
        *   **Lanza**: `ValueError` si no se encuentra ninguna de las claves de API.

### `backend/models.py`

*   **Propósito**: Define el modelo de la base de datos para los libros utilizando SQLAlchemy ORM. Este modelo se mapea directamente a la tabla `books` en la base de datos.

*   **Clases Principales**:
    *   `Book(Base)`
        *   **Descripción**: Representa un libro en la base de datos.
        *   `__tablename__ = "books"`: Especifica el nombre de la tabla en la base de datos.
        *   `__table_args__ = {'extend_existing': True}`: Permite la redefinición de la tabla, útil en entornos de prueba.
        *   **Columnas**:
            *   `id` (Integer, Primary Key, Index): Identificador único del libro.
            *   `title` (String, Index): Título del libro.
            *   `author` (String, Index): Autor del libro.
            *   `category` (String, Index): Categoría del libro.
            *   `cover_image_url` (String, Nullable): URL o ruta a la imagen de portada. Puede ser nulo.
            *   `file_path` (String, Unique): Ruta absoluta al archivo del libro. Debe ser única.

### `backend/rag.py`

*   **Propósito**: Implementa el sistema de Conversación Aumentada por Recuperación (RAG). Se encarga de la extracción de texto, la división en fragmentos (chunking), la generación de embeddings, el almacenamiento en una base de datos vectorial (ChromaDB) y la consulta a modelos de lenguaje grandes (LLMs) con contexto recuperado.

*   **Variables y Configuración**:
    *   `EMBEDDING_MODEL`: Modelo de Gemini para embeddings (configurable por `GEMINI_EMBEDDING_MODEL` en `.env`).
    *   `GENERATION_MODEL`: Modelo de Gemini para generación de texto (configurable por `GEMINI_GENERATION_MODEL` en `.env`).
    *   `_initialized`, `_collection`, `_ai_enabled`: Variables de estado internas para asegurar la inicialización única y la disponibilidad de la IA.

*   **Funciones Principales**:
    *   `_ensure_init()`
        *   **Lógica**: Inicializa las dependencias de ChromaDB y Google Generative AI si aún no se han inicializado. Carga variables de entorno y configura el API Key de Gemini. Si `DISABLE_AI` es "1", la IA se deshabilita.
    *   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`
        *   **Lógica**: Genera un vector de embeddings para un texto dado utilizando el modelo de embeddings de Gemini. Si la IA está deshabilitada, devuelve un embedding "dummy" para pruebas.
        *   **Parámetros**: `text` (el texto a embeber), `task_type` (tipo de tarea para el embedding, ej. `RETRIEVAL_DOCUMENT` o `RETRIEVAL_QUERY`).
        *   **Retorno**: Lista de flotantes (el vector de embedding).
    *   `extract_text_from_pdf(file_path: str)`
        *   **Lógica**: Abre un archivo PDF y extrae todo el texto de sus páginas utilizando `PyPDF2`.
        *   **Parámetros**: `file_path` (ruta al archivo PDF).
        *   **Retorno**: Cadena de texto con el contenido extraído.
    *   `extract_text_from_epub(file_path: str)`
        *   **Lógica**: Abre un archivo EPUB, extrae el contenido HTML de cada capítulo y lo convierte a texto plano utilizando `ebooklib` y `BeautifulSoup`.
        *   **Parámetros**: `file_path` (ruta al archivo EPUB).
        *   **Retorno**: Cadena de texto con el contenido extraído.
    *   `extract_text(file_path: str)`
        *   **Lógica**: Función unificada que detecta el tipo de archivo (`.pdf` o `.epub`) y llama a la función de extracción correspondiente.
        *   **Parámetros**: `file_path`.
        *   **Retorno**: Cadena de texto.
        *   **Lanza**: `ValueError` si el tipo de archivo no es soportado.
    *   `chunk_text(text: str, max_tokens: int = 1000)`
        *   **Lógica**: Divide un texto largo en fragmentos más pequeños (chunks) basándose en un número máximo de tokens por chunk. Utiliza `tiktoken` para una estimación de tokens.
        *   **Parámetros**: `text`, `max_tokens` (tamaño máximo de tokens por chunk).
        *   **Retorno**: Lista de cadenas (los chunks de texto).
    *   `_has_index_for_book(book_id: str)`
        *   **Lógica**: Comprueba si ya existen vectores asociados a un `book_id` dado en la colección de ChromaDB.
        *   **Parámetros**: `book_id`.
        *   **Retorno**: `True` si existen, `False` en caso contrario.
    *   `delete_book_from_rag(book_id: str)`
        *   **Lógica**: Elimina todos los vectores y metadatos asociados a un `book_id` de ChromaDB.
        *   **Parámetros**: `book_id`.
    *   `get_index_count(book_id: str)`
        *   **Lógica**: Retorna el número de vectores almacenados para un `book_id` específico.
        *   **Parámetros**: `book_id`.
        *   **Retorno**: Un entero.
    *   `has_index(book_id: str)`
        *   **Lógica**: Función pública para verificar si un libro está indexado en RAG.
        *   **Parámetros**: `book_id`.
        *   **Retorno**: `True` si está indexado, `False` en caso contrario.
    *   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`
        *   **Lógica**: Procesa un archivo de libro para el sistema RAG. Extrae el texto, lo divide en chunks, genera embeddings para cada chunk y los almacena en ChromaDB junto con metadatos (`book_id`, `chunk_index`). Si `force_reindex` es `True`, elimina cualquier índice existente primero.
        *   **Parámetros**: `file_path`, `book_id`, `force_reindex` (booleano, por defecto `False`).
        *   **Lanza**: `ValueError` si el tipo de archivo no es soportado o no se puede extraer texto.
    *   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`
        *   **Lógica**: Estima el número total de tokens y chunks que se generarían para un archivo dado si se indexara para RAG, usando el mismo chunking logic.
        *   **Parámetros**: `file_path`, `max_tokens`.
        *   **Retorno**: Diccionario con `tokens` y `chunks`.
    *   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`
        *   **Lógica**: Calcula la estimación agregada de tokens y chunks para una lista de archivos.
        *   **Parámetros**: `file_paths`, `max_tokens`.
        *   **Retorno**: Diccionario con `tokens`, `chunks` y `files` (archivos procesados exitosamente).
    *   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`
        *   **Lógica**: Ejecuta una consulta RAG. Genera un embedding de la consulta, recupera los fragmentos de texto más relevantes del libro (desde ChromaDB), construye un prompt contextualizado con los fragmentos, metadatos del libro (título, autor, categoría) y un contexto opcional de la biblioteca (ej. otros libros del mismo autor), y envía este prompt al modelo de generación de Gemini para obtener una respuesta.
        *   **Parámetros**: `query` (la pregunta del usuario), `book_id` (ID del libro), `mode` (estilo de respuesta: `strict`, `balanced`, `open`), `metadata` (diccionario opcional con metadatos del libro), `library` (diccionario opcional con contexto de la biblioteca).
        *   **Retorno**: La respuesta generada por la IA como una cadena de texto.

### `backend/main.py`

*   **Propósito**: Es el archivo principal de la aplicación FastAPI. Configura la aplicación, las rutas (endpoints), el middleware CORS, y orquesta la interacción entre los diferentes módulos (CRUD, RAG, procesamiento de archivos, IA).

*   **Configuración Inicial**:
    *   `FastAPI()`: Instancia de la aplicación FastAPI.
    *   `base_dir`, `STATIC_DIR_FS`, `STATIC_COVERS_DIR_FS`, `TEMP_BOOKS_DIR_FS`, `BOOKS_DIR_FS`: Definición de rutas absolutas para directorios de archivos.
    *   `AI_ENABLED`: Variable booleana que indica si la funcionalidad de IA está activa (basado en la presencia de `GOOGLE_API_KEY` o `GEMINI_API_KEY`).
    *   `genai.configure()`: Configura el cliente de Google Generative AI si `AI_ENABLED` es `True`.
    *   `models.Base.metadata.create_all(bind=database.engine)`: Crea todas las tablas de la base de datos definidas en `models.py` si no existen.
    *   Montaje de directorios estáticos: `/static` para portadas, `/temp_books` para archivos temporales.
    *   `CORSMiddleware`: Configuración de CORS para permitir peticiones desde el frontend. Permite orígenes configurables vía `ALLOW_ORIGINS` y un regex `ALLOW_ORIGIN_REGEX` para redes privadas.

*   **Funciones de Ayuda**:
    *   `analyze_with_gemini(text: str) -> dict`
        *   **Lógica**: Envía las primeras 4000 caracteres de un texto a un modelo de Gemini (configurable con `GEMINI_MODEL_MAIN`) con un prompt específico para extraer título, autor y categoría en formato JSON.
        *   **Retorno**: Diccionario con `title`, `author`, `category` o valores de "Error de IA" en caso de fallo.
    *   `process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`
        *   **Lógica**: Abre un PDF, extrae texto de las primeras 5 páginas y busca imágenes que puedan ser la portada, guardándolas.
        *   **Retorno**: Diccionario con el texto extraído y la URL de la portada.
    *   `process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`
        *   **Lógica**: Abre un EPUB, extrae texto de sus capítulos y busca la imagen de portada (primero metadatos, luego por nombre de archivo), guardándola.
        *   **Retorno**: Diccionario con el texto extraído y la URL de la portada.
        *   **Lanza**: `HTTPException` si no se puede extraer suficiente texto.
    *   `get_db()`
        *   **Lógica**: Función generadora de dependencia para obtener una sesión de base de datos de SQLAlchemy. Asegura que la sesión se cierre correctamente después de su uso.

*   **Endpoints de la API**:
    *   `POST /upload-book/` (`response_model=schemas.Book`)
        *   **Funcionalidad**: Sube un archivo de libro (PDF/EPUB), lo guarda, lo procesa para extraer metadatos (usando `analyze_with_gemini`), y crea un nuevo registro en la base de datos. Si la IA no puede identificar el título y el autor, rechaza el libro.
        *   **Dependencias**: `get_db`, `schemas.BookBase`, `UploadFile`.
    *   `GET /books/` (`response_model=List[schemas.Book]`)
        *   **Funcionalidad**: Obtiene una lista de libros, con opciones de filtrado por `category`, `search` (búsqueda general) y `author`.
        *   **Dependencias**: `get_db`, `crud.get_books`.
    *   `GET /books/count` (`response_model=int`)
        *   **Funcionalidad**: Retorna el número total de libros en la biblioteca.
        *   **Dependencias**: `get_db`, `crud.get_books_count`.
    *   `GET /books/search/` (`response_model=List[schemas.Book]`)
        *   **Funcionalidad**: Busca libros por un título parcial, con opciones de paginación (`skip`, `limit`).
        *   **Dependencias**: `get_db`, `crud.get_books_by_partial_title`.
    *   `GET /categories/` (`response_model=List[str]`)
        *   **Funcionalidad**: Obtiene una lista de todas las categorías de libros únicas.
        *   **Dependencias**: `get_db`, `crud.get_categories`.
    *   `DELETE /books/{book_id}`
        *   **Funcionalidad**: Elimina un libro específico por su ID. También se encarga de eliminar sus archivos asociados y cualquier índice RAG.
        *   **Dependencias**: `get_db`, `crud.delete_book`, `rag.delete_book_from_rag`.
    *   `DELETE /categories/{category_name}`
        *   **Funcionalidad**: Elimina todos los libros de una categoría específica, incluyendo sus archivos y sus índices RAG.
        *   **Dependencias**: `get_db`, `crud.delete_books_by_category`, `rag.delete_book_from_rag`.
    *   `GET /books/download/{book_id}`
        *   **Funcionalidad**: Permite la descarga de un archivo de libro. Para PDF, se sirve `inline`; para EPUB, como `attachment`.
        *   **Dependencias**: `get_db`, `FileResponse`.
    *   `POST /tools/convert-epub-to-pdf` (`response_model=schemas.ConversionResponse`)
        *   **Funcionalidad**: Convierte un archivo EPUB subido a PDF. Utiliza `weasyprint` internamente para realizar la conversión. Guarda el PDF resultante en un directorio temporal y devuelve una URL de descarga.
    *   `POST /rag/upload-book/` (`response_model=schemas.RagUploadResponse`)
        *   **Funcionalidad**: Sube un archivo y lo procesa directamente para el sistema RAG, asignándole un `book_id` UUID.
        *   **Dependencias**: `rag.process_book_for_rag`.
    *   `POST /rag/query/` (`response_model=schemas.RagQueryResponse`)
        *   **Funcionalidad**: Envía una consulta al sistema RAG para obtener una respuesta basada en el contenido de un libro. Se recuperan metadatos y contexto de la biblioteca para enriquecer el prompt.
        *   **Dependencias**: `get_db`, `schemas.RagQuery`, `rag.query_rag`.
    *   `POST /rag/index/{book_id}`
        *   **Funcionalidad**: Indexa un libro ya existente en la base de datos para el sistema RAG.
        *   **Dependencias**: `get_db`, `rag.process_book_for_rag`.
    *   `GET /rag/status/{book_id}`
        *   **Funcionalidad**: Proporciona información sobre el estado de indexación RAG de un libro (si está indexado y cuántos vectores tiene).
        *   **Dependencias**: `rag.get_index_count`.
    *   `POST /rag/reindex/category/{category_name}`
        *   **Funcionalidad**: Reindexa todos los libros de una categoría específica en RAG.
        *   **Dependencias**: `get_db`, `rag.process_book_for_rag`.
    *   `POST /rag/reindex/all`
        *   **Funcionalidad**: Reindexa todos los libros de la biblioteca en RAG.
        *   **Dependencias**: `get_db`, `rag.process_book_for_rag`.
    *   `GET /rag/estimate/book/{book_id}`
        *   **Funcionalidad**: Estima el número de tokens y chunks para un libro específico que se indexaría en RAG, con una estimación de coste opcional.
        *   **Dependencias**: `get_db`, `rag.estimate_embeddings_for_file`.
    *   `GET /rag/estimate/category/{category_name}`
        *   **Funcionalidad**: Estima el número total de tokens y chunks para todos los libros en una categoría.
        *   **Dependencias**: `get_db`, `rag.estimate_embeddings_for_files`.
    *   `GET /rag/estimate/all`
        *   **Funcionalidad**: Estima el número total de tokens y chunks para todos los libros en la biblioteca.
        *   **Dependencias**: `get_db`, `rag.estimate_embeddings_for_files`.

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

*   **Propósito**: Script de migración de la base de datos generado por Alembic para crear la tabla `books`.
*   **`upgrade()`**: Contiene el código SQLAlchemy para crear la tabla `books` con sus columnas (`id`, `title`, `author`, `category`, `cover_image_url`, `file_path`), establecer `id` como clave primaria, `file_path` como único, y crear índices en `id`, `title`, `author` y `category` para optimizar las búsquedas.
*   **`downgrade()`**: Contiene el código para revertir la migración, eliminando la tabla `books` y sus índices.

### `backend/__init__.py`

*   **Propósito**: Este archivo marca el directorio `backend` como un paquete Python. Actualmente, está vacío, lo que significa que no hay importaciones o configuraciones a nivel de paquete que se ejecuten automáticamente cuando se importa `backend`.

## 4. Análisis Detallado del Frontend (React)

El frontend proporciona la interfaz de usuario y gestiona la interacción del usuario con la aplicación.

### `frontend/src/App.js`

*   **Propósito**: Es el componente raíz de la aplicación React. Configura el enrutamiento utilizando `react-router-dom` y define las diferentes vistas disponibles para el usuario.
*   **Estado**: No gestiona estado propio significativo.
*   **Propiedades**: No recibe propiedades.
*   **Efectos Secundarios**: No tiene efectos directos, pero orquesta los efectos de sus componentes hijos.
*   **Interacciones del Usuario**: El enrutador maneja la navegación a diferentes rutas de la aplicación.
*   **Comunicación con el Backend**: Indirecta, a través de los componentes de vista que renderiza.

### `frontend/src/Header.js`

*   **Propósito**: Renderiza la barra de navegación superior de la aplicación. Muestra el título, un contador de libros y enlaces de navegación.
*   **Estado**:
    *   `menuOpen` (boolean): Controla la visibilidad del menú de navegación en dispositivos móviles.
    *   `bookCount` (number): El número total de libros en la biblioteca, obtenido del backend.
    *   `errorMessage` (string): Mensaje de error si falla la carga del contador de libros.
*   **Propiedades**: Ninguna.
*   **Efectos Secundarios**:
    *   `useEffect`: Fetches el contador de libros del backend (`/books/count`) al montar el componente y cada 10 minutos para mantenerlo actualizado.
*   **Interacciones del Usuario**:
    *   Botón de "hamburguesa" para alternar el menú en móviles.
    *   `NavLink`s para navegar a las diferentes vistas de la aplicación.
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/books/count`: Para obtener el número total de libros.

### `frontend/src/LibraryView.js`

*   **Propósito**: La vista principal de la biblioteca que muestra una lista de libros, permitiendo la búsqueda, el filtrado por autor/categoría y la eliminación/lectura de libros.
*   **Estado**:
    *   `books` (array): Lista de objetos libro a mostrar.
    *   `searchParams` (URLSearchParams): Parámetros de la URL utilizados para filtrar la lista de libros.
    *   `searchTerm` (string): El texto actual en la barra de búsqueda.
    *   `debouncedSearchTerm` (string): Versión "debounced" de `searchTerm` para evitar llamadas excesivas a la API.
    *   `error` (string): Mensaje de error si falla la carga de libros.
    *   `loading` (boolean): Indica si los libros están cargando.
    *   `isMobile` (boolean): Detecta si la pantalla es de un dispositivo móvil para adaptar la UI (ej., botón de descarga).
*   **Propiedades**: Ninguna.
*   **Efectos Secundarios**:
    *   `useEffect`: Llama a `fetchBooks` cuando cambian `debouncedSearchTerm` o `searchParams`.
    *   `useEffect`: Monitorea el tamaño de la ventana para actualizar `isMobile`.
    *   `useDebounce`: Hook personalizado para aplicar un retardo a la búsqueda.
*   **Interacciones del Usuario**:
    *   Barra de búsqueda para filtrar libros por título, autor o categoría.
    *   Clic en el nombre de un autor o categoría para filtrar la vista.
    *   Botón "Abrir PDF" para archivos PDF, o "Leer EPUB" para archivos EPUB.
    *   Botones "Descargar PDF/EPUB" para dispositivos móviles.
    *   Botón "×" para eliminar un libro individual.
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/books/`: Para obtener la lista de libros, con parámetros de consulta para filtrado (`category`, `search`, `author`).
    *   `DELETE ${API_URL}/books/{bookId}`: Para eliminar un libro.
    *   `GET ${API_URL}/books/download/{bookId}`: Para descargar o abrir un archivo de libro.

### `frontend/src/UploadView.js`

*   **Propósito**: Permite a los usuarios subir uno o varios archivos de libros (PDF o EPUB) a la biblioteca.
*   **Estado**:
    *   `filesToUpload` (array de objetos): Cada objeto contiene el `File` original, su `status` (`pending`, `uploading`, `success`, `error`) y un `message` asociado.
    *   `isUploading` (boolean): Indica si hay archivos en proceso de subida.
*   **Propiedades**: Ninguna.
*   **Efectos Secundarios**: Ninguno.
*   **Interacciones del Usuario**:
    *   Selección de archivos mediante input (`<input type="file" multiple>`).
    *   Arrastrar y soltar archivos en la zona designada.
    *   Botón "Subir Archivo(s)" para iniciar el proceso de carga y análisis.
    *   Botón "Ir a la Biblioteca" que aparece una vez que todas las cargas han finalizado.
*   **Comunicación con el Backend**:
    *   `POST ${API_URL}/upload-book/`: Envía cada archivo de libro al backend para su procesamiento y almacenamiento.

### `frontend/src/ToolsView.js`

*   **Propósito**: Ofrece herramientas adicionales para la gestión de la biblioteca, actualmente incluyendo un convertidor de EPUB a PDF.
*   **Estado (dentro de `EpubToPdfConverter`)**:
    *   `selectedFile` (File | null): El archivo EPUB seleccionado para la conversión.
    *   `message` (string): Mensajes de estado o error para el usuario.
    *   `isLoading` (boolean): Indica si el proceso de conversión está en curso.
*   **Propiedades**: Ninguna.
*   **Efectos Secundarios**: Ninguno.
*   **Interacciones del Usuario**:
    *   Selección de archivo EPUB.
    *   Arrastrar y soltar archivos EPUB.
    *   Botón "Convertir a PDF" para iniciar el proceso.
*   **Comunicación con el Backend**:
    *   `POST ${API_URL}/tools/convert-epub-to-pdf`: Envía el archivo EPUB al backend para su conversión. La respuesta incluye una URL de descarga para el PDF resultante.

### `frontend/src/ReaderView.js`

*   **Propósito**: Proporciona una interfaz de lectura para libros en formato EPUB directamente en el navegador.
*   **Estado**:
    *   `location` (string | null): La ubicación actual de lectura en el EPUB (CFI).
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB.
    *   `isLoading` (boolean): Indica si el EPUB se está cargando.
    *   `error` (string): Mensaje de error si no se puede cargar el libro.
*   **Propiedades**: Recibe `bookId` de los parámetros de la URL (`useParams`).
*   **Efectos Secundarios**:
    *   `useEffect`: Carga los datos binarios del EPUB desde el backend (`/books/download/{bookId}`) cuando el componente se monta o `bookId` cambia.
*   **Interacciones del Usuario**:
    *   Navegación dentro del libro EPUB (proporcionada por `react-reader`).
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/books/download/{bookId}`: Obtiene el archivo EPUB como un `ArrayBuffer`.

### `frontend/src/RagView.js`

*   **Propósito**: Permite a los usuarios interactuar con el contenido de un libro a través de un chatbot inteligente impulsado por el sistema RAG.
*   **Estado**:
    *   `message` (string): Mensajes informativos o de error para el usuario.
    *   `isLoading` (boolean): Indica si se está esperando una respuesta de la IA.
    *   `bookId` (string | null): El ID del libro actualmente seleccionado para la conversación RAG.
    *   `chatHistory` (array de objetos): Historial de mensajes de usuario y respuestas de la IA.
    *   `currentQuery` (string): El texto de la consulta actual del usuario.
    *   `libraryBooks` (array): Lista de todos los libros de la biblioteca.
    *   `selectedLibraryId` (string): El ID del libro seleccionado de la lista de la biblioteca para RAG.
    *   `libStatus` (objeto): `{ loading, indexed, vector_count, error }` - estado de indexación RAG del libro seleccionado.
    *   `actionsBusy` (boolean): Bloquea botones durante operaciones intensivas (indexación).
    *   `refreshing` (boolean): Indica un refresco del estado RAG sin bloquear otras acciones.
    *   `searchTerm` (string): Término de búsqueda para encontrar libros en la biblioteca.
    *   `searching` (boolean): Indica si la búsqueda está activa.
    *   `searchResults` (array): Resultados de la búsqueda de libros.
    *   `resultsOpen` (boolean): Controla la visibilidad de los resultados de búsqueda.
    *   `mode` (string): Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`).
    *   `selectedBook` (object | null): Detalles del libro seleccionado manualmente.
*   **Propiedades**: Ninguna.
*   **Efectos Secundarios**:
    *   `useEffect`: Carga la lista completa de libros de la biblioteca al montar el componente.
    *   `useEffect`: Implementa un "debounce" para la barra de búsqueda de libros, filtrando los resultados.
    *   `useEffect`: Cuando `selectedLibraryId` cambia, llama a `checkLibraryStatus` para actualizar el estado RAG.
    *   `useEffect`: Desplaza automáticamente el historial del chat al final cuando se añaden nuevos mensajes o mientras la IA está generando una respuesta.
*   **Interacciones del Usuario**:
    *   Campo de búsqueda para encontrar y seleccionar un libro de la biblioteca.
    *   Botones para "Comprobar RAG", "Indexar antes de charlar", "Reindexar" un libro.
    *   Botón "Chatear" para iniciar la conversación una vez que el libro está indexado.
    *   Selección del "Modo de respuesta" de la IA (Solo libro, Equilibrado, Abierto).
    *   Área de texto para escribir preguntas y botón "Enviar".
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/books/`: Para cargar la lista de libros de la biblioteca.
    *   `GET ${API_URL}/books/?search=...`: Para buscar libros en la biblioteca.
    *   `GET ${API_URL}/rag/status/{bookId}`: Para verificar el estado de indexación RAG de un libro.
    *   `POST ${API_URL}/rag/index/{bookId}`: Para iniciar la indexación RAG de un libro existente.
    *   `POST ${API_URL}/rag/query/`: Para enviar una consulta al sistema RAG y recibir una respuesta.

### `frontend/src/CategoriesView.js`

*   **Propósito**: Muestra una lista de todas las categorías únicas de libros disponibles en la biblioteca. Cada categoría es un enlace que filtra la vista de la biblioteca por esa categoría.
*   **Estado**:
    *   `categories` (array de strings): Lista de nombres de categorías únicas.
    *   `error` (string): Mensaje de error si falla la carga de categorías.
    *   `loading` (boolean): Indica si las categorías están cargando.
*   **Propiedades**: Ninguna.
*   **Efectos Secundarios**:
    *   `useEffect`: Carga las categorías del backend (`/categories/`) al montar el componente.
*   **Interacciones del Usuario**:
    *   Clic en una categoría para navegar a `LibraryView` y filtrar por esa categoría.
*   **Comunicación con el Backend**:
    *   `GET ${API_URL}/categories/`: Para obtener la lista de categorías únicas.

### `frontend/src/config.js`

*   **Propósito**: Proporciona una forma centralizada de definir la URL base del backend de la API, haciéndola configurable a través de variables de entorno.
*   **Variable**:
    *   `API_URL` (string): La URL del backend. Por defecto es `http://localhost:8001`, pero se puede sobrescribir usando la variable de entorno `REACT_APP_API_URL`.

### `frontend/src/index.js`

*   **Propósito**: El punto de entrada principal para la aplicación React. Renderiza el componente `App` en el elemento DOM con ID `root`.
*   **Estado**: Ninguno.
*   **Propiedades**: Ninguna.
*   **Efectos Secundarios**: Ninguno.
*   **Interacciones del Usuario**: Ninguna directa, inicializa la aplicación.
*   **Comunicación con el Backend**: Ninguna directa.

### `frontend/src/ErrorBoundary.js`

*   **Propósito**: Un componente React Error Boundary genérico. Captura errores de JavaScript en sus componentes hijos y muestra una interfaz de usuario alternativa en lugar de que la aplicación falle por completo.
*   **Estado**:
    *   `hasError` (boolean): `true` si se ha capturado un error.
    *   `error` (Error | null): El objeto de error capturado.
*   **Métodos**:
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para indicar que ha ocurrido un error.
    *   `componentDidCatch(error, info)`: Registra el error y la información de la pila.
    *   `render()`: Renderiza el contenido normal si no hay error, o una UI de fallback con el mensaje de error si `hasError` es `true`.

## 5. Flujo de Datos y API

### Flujo de Carga de un Libro

1.  **Frontend (Componente `UploadView`)**:
    *   El usuario selecciona uno o varios archivos (PDF o EPUB) a través del input de archivo o arrastrando y soltando.
    *   Para cada archivo, se crea un objeto `FormData` y se envía una petición `POST` al endpoint `/upload-book/` del backend.
2.  **Backend (Endpoint `POST /upload-book/` en `main.py`)**:
    *   **Recepción**: FastAPI recibe el `UploadFile` que contiene el archivo del libro.
    *   **Guardado Temporal**: El archivo se guarda en la carpeta `backend/books/`.
    *   **Procesamiento de Archivo**: Se detecta la extensión (`.pdf` o `.epub`).
        *   Si es PDF, se llama a `process_pdf()`: extrae texto de las primeras páginas y busca una imagen para la portada, guardándola en `backend/static/covers/`.
        *   Si es EPUB, se llama a `process_epub()`: extrae texto de los capítulos y busca la portada, guardándola de manera similar.
    *   **Análisis con IA**: El texto extraído se envía a `analyze_with_gemini()` (que utiliza la API de Google Gemini) para inferir el título, autor y categoría del libro.
    *   **Control de Calidad**: Si la IA no puede determinar un título y autor válidos, el archivo se elimina y se devuelve un error 422 al frontend.
    *   **Guardado en BD**: Si el análisis es exitoso, los metadatos (título, autor, categoría, URL de la portada, ruta del archivo) se persisten en la base de datos SQLite mediante `crud.create_book()`.
    *   **Respuesta**: Se devuelve un objeto `schemas.Book` al frontend.
3.  **Frontend (`UploadView`)**:
    *   Actualiza el estado de cada archivo en la UI, mostrando si la subida y el procesamiento fueron `success` o `error` y el mensaje correspondiente.
    *   Una vez que todos los archivos se han procesado, el usuario puede navegar a la `LibraryView`.

### Flujo de Conversación RAG (IA)

1.  **Frontend (Componente `RagView`)**:
    *   El usuario busca y selecciona un libro existente de la biblioteca.
    *   Al seleccionar un libro, se envía una petición `GET` a `/rag/status/{bookId}` para verificar si el libro ya tiene un índice RAG.
    *   Si el libro no está indexado, el usuario puede hacer clic en "Indexar antes de charlar" (o "Reindexar"). Esto envía una petición `POST` a `/rag/index/{bookId}`.
    *   Una vez que el `libStatus.indexed` es `true`, el usuario introduce una pregunta en el área de texto del chat.
2.  **Envío de Consulta al Backend (`RagView`)**:
    *   Cuando el usuario envía una consulta, se añade al `chatHistory` local como mensaje del `user`.
    *   Se envía una petición `POST` a `/rag/query/` con la `query`, `book_id` y el `mode` de respuesta seleccionados.
3.  **Backend (Endpoint `POST /rag/query/` en `main.py`)**:
    *   **Recepción**: FastAPI recibe los datos de la consulta (`schemas.RagQuery`).
    *   **Contexto Adicional**: Se recuperan los metadatos del libro (`crud.get_book_by_id`) y se construye un contexto adicional de la biblioteca (ej., otros libros del mismo autor) si el `mode` no es `strict`.
    *   **Consulta RAG**: Se llama a la función `rag.query_rag()` con la consulta, el `book_id`, el `mode` y los contextos recuperados.
        *   **Dentro de `rag.py` (`query_rag` function)**:
            *   Se genera un vector de embedding para la consulta del usuario.
            *   Se consulta la base de datos vectorial ChromaDB (`_collection.query()`) para recuperar los 5 fragmentos de texto más relevantes del libro asociado (`book_id`).
            *   Se construye un prompt para el modelo de lenguaje de Gemini, incluyendo:
                *   Instrucciones de `guidance` según el `mode`.
                *   Los `relevant_chunks` (contexto del libro).
                *   `metadata` del libro.
                *   `library_ctx` (otras obras del autor, si aplica).
                *   La `query` original.
            *   Este prompt se envía al modelo de generación de Gemini (`genai.GenerativeModel`) para obtener una respuesta.
            *   La respuesta de Gemini se retorna al endpoint de FastAPI.
    *   **Respuesta**: El endpoint de FastAPI devuelve la respuesta de la IA (`schemas.RagQueryResponse`) al frontend.
4.  **Frontend (`RagView`)**:
    *   La respuesta de la IA se añade al `chatHistory` como mensaje de `gemini`.
    *   El chat se desplaza automáticamente para mostrar los últimos mensajes.

### Endpoints Principales de la API

La API del backend expone los siguientes endpoints principales:

#### Gestión de Libros
*   `POST /upload-book/`
    *   **Descripción**: Sube un archivo de libro (PDF/EPUB) para ser procesado, analizado por IA y añadido a la biblioteca.
    *   **Entrada**: `UploadFile` (archivo de libro).
    *   **Salida**: `schemas.Book` (detalles del libro creado).
*   `GET /books/`
    *   **Descripción**: Recupera una lista de libros de la biblioteca.
    *   **Parámetros de Consulta (Opcionales)**: `category` (str), `search` (str, busca en título/autor/categoría), `author` (str).
    *   **Salida**: `List[schemas.Book]`.
*   `GET /books/count`
    *   **Descripción**: Obtiene el número total de libros en la biblioteca.
    *   **Salida**: `int`.
*   `GET /books/search/?title={title}`
    *   **Descripción**: Busca libros por un título parcial (insensible a mayúsculas/minúsculas).
    *   **Parámetros de Consulta**: `title` (str), `skip` (int), `limit` (int).
    *   **Salida**: `List[schemas.Book]`.
*   `DELETE /books/{book_id}`
    *   **Descripción**: Elimina un libro por su ID, incluyendo sus archivos y su índice RAG.
    *   **Parámetros de Ruta**: `book_id` (int).
    *   **Salida**: `{ "message": "Libro '...' eliminado con éxito." }`.
*   `GET /books/download/{book_id}`
    *   **Descripción**: Descarga el archivo de un libro. PDF se abre `inline`, EPUB como `attachment`.
    *   **Parámetros de Ruta**: `book_id` (int).
    *   **Salida**: `FileResponse` (archivo binario).

#### Gestión de Categorías
*   `GET /categories/`
    *   **Descripción**: Obtiene una lista de todas las categorías de libros únicas presentes en la biblioteca.
    *   **Salida**: `List[str]`.
*   `DELETE /categories/{category_name}`
    *   **Descripción**: Elimina todos los libros de una categoría específica, incluyendo sus archivos y sus índices RAG.
    *   **Parámetros de Ruta**: `category_name` (str).
    *   **Salida**: `{ "message": "Categoría '...' y sus X libros han sido eliminados." }`.

#### Herramientas
*   `POST /tools/convert-epub-to-pdf`
    *   **Descripción**: Convierte un archivo EPUB subido a PDF.
    *   **Entrada**: `UploadFile` (archivo EPUB).
    *   **Salida**: `schemas.ConversionResponse` (contiene `download_url` al PDF temporal).

#### RAG (Retrieval Augmented Generation)
*   `POST /rag/upload-book/`
    *   **Descripción**: Sube un libro y lo procesa específicamente para el sistema RAG (funcionalidad de legado o auxiliar).
    *   **Entrada**: `UploadFile` (archivo de libro).
    *   **Salida**: `schemas.RagUploadResponse`.
*   `POST /rag/query/`
    *   **Descripción**: Envía una consulta a la IA sobre el contenido de un libro indexado en RAG.
    *   **Entrada**: `schemas.RagQuery` (contiene la consulta, ID del libro y modo).
    *   **Salida**: `schemas.RagQueryResponse` (contiene la respuesta de la IA).
*   `POST /rag/index/{book_id}`
    *   **Descripción**: Indexa un libro existente en la base de datos en el sistema RAG.
    *   **Parámetros de Ruta**: `book_id` (int).
    *   **Parámetros de Consulta (Opcionales)**: `force` (bool, para forzar reindexación).
    *   **Salida**: `{ "message": "Libro indexado en RAG", "book_id": "...", "force": "..." }`.
*   `GET /rag/status/{book_id}`
    *   **Descripción**: Obtiene el estado de indexación RAG para un libro dado (si está indexado y número de vectores).
    *   **Parámetros de Ruta**: `book_id` (int).
    *   **Salida**: `{ "book_id": "...", "indexed": bool, "vector_count": int }`.
*   `POST /rag/reindex/category/{category_name}`
    *   **Descripción**: (Re)indexa todos los libros de una categoría específica en RAG.
    *   **Parámetros de Ruta**: `category_name` (str).
    *   **Parámetros de Consulta (Opcionales)**: `force` (bool, por defecto `True`).
    *   **Salida**: `{ "category": "...", "processed": int, "failed": List[dict], "force": bool }`.
*   `POST /rag/reindex/all`
    *   **Descripción**: (Re)indexa todos los libros de la biblioteca en RAG.
    *   **Parámetros de Consulta (Opcionales)**: `force` (bool, por defecto `True`).
    *   **Salida**: `{ "processed": int, "failed": List[dict], "total": int, "force": bool }`.
*   `GET /rag/estimate/book/{book_id}`
    *   **Descripción**: Estima el número de tokens y chunks para un libro en el proceso de indexación RAG, con un coste estimado opcional.
    *   **Parámetros de Ruta**: `book_id` (int).
    *   **Parámetros de Consulta (Opcionales)**: `per1k` (float, coste por 1000 tokens), `max_tokens` (int).
    *   **Salida**: `{ "book_id": "...", "tokens": int, "chunks": int, "per1k": float, "estimated_cost": float }`.
*   `GET /rag/estimate/category/{category_name}`
    *   **Descripción**: Estima el número total de tokens y chunks para todos los libros de una categoría específica.
    *   **Parámetros de Ruta**: `category_name` (str).
    *   **Parámetros de Consulta (Opcionales)**: `per1k` (float), `max_tokens` (int).
    *   **Salida**: `{ "category": "...", "tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float }`.
*   `GET /rag/estimate/all`
    *   **Descripción**: Estima el número total de tokens y chunks para todos los libros de la biblioteca.
    *   **Parámetros de Consulta (Opcionales)**: `per1k` (float), `max_tokens` (int).
    *   **Salida**: `{ "tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float }`.
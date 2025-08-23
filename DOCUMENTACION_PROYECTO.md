# Documentación del Proyecto: Mi Librería Inteligente

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web diseñada para gestionar una biblioteca personal de libros digitales, ofreciendo funcionalidades avanzadas impulsadas por inteligencia artificial. Su objetivo es simplificar la organización, el consumo y la interacción con colecciones de libros en formatos como PDF y EPUB.

**Características principales:**

*   **Gestión de Biblioteca:** Permite subir, listar, buscar, filtrar y eliminar libros.
*   **Análisis Inteligente de Libros:** Utiliza modelos de IA (Google Gemini) para extraer automáticamente metadatos clave como el título, autor y categoría de los libros subidos.
*   **Conversión de Formatos:** Ofrece una herramienta para convertir archivos EPUB a PDF.
*   **Asistente RAG (Retrieval Augmented Generation):** Permite a los usuarios interactuar con el contenido de los libros mediante un sistema conversacional de IA. Los libros son indexados en una base de datos vectorial (ChromaDB) y las consultas del usuario son respondidas basándose en la información recuperada del libro, complementada con conocimiento general si se configura así.
*   **Interfaz de Lector:** Incluye un lector integrado para archivos EPUB.

**Arquitectura General:**

La aplicación sigue una arquitectura cliente-servidor con los siguientes componentes principales:

*   **Frontend (React):** Una aplicación web de una sola página (SPA) que proporciona la interfaz de usuario. Se encarga de la interacción con el usuario, la visualización de datos y el envío de peticiones al backend.
*   **Backend (FastAPI - Python):** Una API RESTful que actúa como el cerebro de la aplicación. Gestiona la lógica de negocio, la interacción con la base de datos, el procesamiento de archivos, la integración con los modelos de IA y la lógica del sistema RAG.
*   **Base de Datos (SQLite):** Una base de datos ligera utilizada por el backend para almacenar los metadatos de los libros (título, autor, categoría, rutas de archivo, etc.).
*   **Almacenamiento de Archivos:** Los archivos de libros (PDF, EPUB) y sus portadas extraídas se almacenan directamente en el sistema de archivos del servidor.
*   **Base de Datos Vectorial (ChromaDB):** Utilizada por el módulo RAG para almacenar los embeddings (representaciones vectoriales) de los fragmentos de texto de los libros, permitiendo una búsqueda semántica eficiente.
*   **Modelos de IA (Google Gemini):** Integrados en el backend para el análisis de metadatos de libros y la generación de respuestas en el sistema RAG.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales, `backend` y `frontend`, junto con archivos de configuración a nivel de raíz:

```
.
├── backend/                  # Contiene todo el código Python para el servidor API.
│   ├── alembic/              # Herramienta de migración de bases de datos para SQLAlchemy.
│   │   └── versions/         # Scripts de migración de la base de datos.
│   ├── crud.py               # Funciones para las operaciones CRUD (Create, Read, Update, Delete) de la base de datos.
│   ├── database.py           # Configuración de la conexión a la base de datos y la sesión.
│   ├── main.py               # La aplicación FastAPI principal, define los endpoints de la API.
│   ├── models.py             # Definiciones de los modelos de la base de datos (tablas).
│   ├── rag.py                # Lógica para el sistema de Recuperación Aumentada por Generación (RAG).
│   ├── schemas.py            # Modelos Pydantic para la validación y serialización de datos.
│   ├── tests/                # Directorio para pruebas unitarias y de integración del backend.
│   ├── tests_curated/        # Pruebas adicionales o "curadas" del backend.
│   └── utils.py              # Funciones de utilidad generales, como la configuración de la API de IA.
├── frontend/                 # Contiene el código de la aplicación web React.
│   ├── public/               # Archivos estáticos servidos directamente por el navegador.
│   ├── src/                  # Código fuente de la aplicación React.
│   │   ├── App.js            # Componente raíz de la aplicación y enrutamiento.
│   │   ├── App.css           # Estilos globales de la aplicación.
│   │   ├── CategoriesView.js # Componente para la vista de categorías/etiquetas.
│   │   ├── CategoriesView.css# Estilos para la vista de categorías.
│   │   ├── config.js         # Archivo de configuración para la URL del API.
│   │   ├── ErrorBoundary.js  # Componente para manejo de errores en React.
│   │   ├── Header.js         # Componente del encabezado de la aplicación.
│   │   ├── Header.css        # Estilos para el encabezado.
│   │   ├── index.js          # Punto de entrada de la aplicación React.
│   │   ├── index.css         # Estilos base de la aplicación.
│   │   ├── LibraryView.js    # Componente para la vista principal de la biblioteca.
│   │   ├── LibraryView.css   # Estilos para la vista de la biblioteca.
│   │   ├── RagView.js        # Componente para la vista del asistente RAG.
│   │   ├── RagView.css       # Estilos para la vista RAG.
│   │   ├── ReaderView.js     # Componente para el lector de libros EPUB.
│   │   ├── ReaderView.css    # Estilos para el lector.
│   │   ├── ToolsView.js      # Componente para la vista de herramientas.
│   │   ├── ToolsView.css     # Estilos para la vista de herramientas.
│   │   ├── UploadView.js     # Componente para la vista de subida de libros.
│   │   └── UploadView.css    # Estilos para la vista de subida.
│   └── .env                  # Variables de entorno para el frontend (ej. REACT_APP_API_URL).
├── .env                      # Variables de entorno para el backend (ej. GOOGLE_API_KEY, GEMINI_API_KEY).
├── library.db                # Archivo de la base de datos SQLite (creado en tiempo de ejecución).
├── rag_index/                # Directorio para los índices de ChromaDB (creado en tiempo de ejecución).
└── README.md                 # Información general del proyecto (este archivo).
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend está construido con FastAPI y Python, utilizando SQLAlchemy para la ORM y ChromaDB con Google Gemini para las funcionalidades de IA.

### `backend/schemas.py`

Define los modelos de datos de Pydantic utilizados para la validación de entrada y serialización de salida en la API.

*   **`class BookBase(BaseModel)`**
    *   **Propósito:** Esquema base para los atributos de un libro.
    *   **Parámetros:**
        *   `title: str`: Título del libro.
        *   `author: str`: Autor del libro.
        *   `category: str`: Categoría a la que pertenece el libro.
        *   `cover_image_url: str | None = None`: URL de la imagen de portada del libro (opcional).
        *   `file_path: str`: Ruta física del archivo del libro en el sistema de almacenamiento.

*   **`class Book(BookBase)`**
    *   **Propósito:** Extiende `BookBase` añadiendo el identificador único del libro, utilizado para las respuestas de la API que incluyen el ID.
    *   **Parámetros:**
        *   `id: int`: Identificador único del libro en la base de datos.
    *   **Configuración:** `from_attributes = True` indica a Pydantic que debe mapear los atributos de los objetos de SQLAlchemy.

*   **`class ConversionResponse(BaseModel)`**
    *   **Propósito:** Esquema para la respuesta de una operación de conversión de archivos.
    *   **Parámetros:**
        *   `download_url: str`: URL donde se puede descargar el archivo convertido.

*   **`class RagUploadResponse(BaseModel)`**
    *   **Propósito:** Esquema para la respuesta de la subida o procesamiento de un libro para el sistema RAG.
    *   **Parámetros:**
        *   `book_id: str`: El identificador del libro en el contexto RAG (puede ser un UUID o el ID de la DB).
        *   `message: str`: Mensaje de estado de la operación.

*   **`class RagQuery(BaseModel)`**
    *   **Propósito:** Esquema para la entrada de una consulta al sistema RAG.
    *   **Parámetros:**
        *   `query: str`: La pregunta del usuario.
        *   `book_id: str`: El identificador del libro sobre el que se hace la pregunta.
        *   `mode: str | None = None`: Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`). Por defecto es `None`, implicando un valor predeterminado en la lógica del RAG.

*   **`class RagQueryResponse(BaseModel)`**
    *   **Propósito:** Esquema para la respuesta de una consulta al sistema RAG.
    *   **Parámetros:**
        *   `response: str`: La respuesta generada por la IA.

### `backend/models.py`

Define los modelos de la base de datos utilizando SQLAlchemy.

*   **`class Book(Base)`**
    *   **Propósito:** Representa la tabla `books` en la base de datos.
    *   **`__tablename__ = "books"`**: Nombre de la tabla.
    *   **`__table_args__ = {'extend_existing': True}`**: Permite redefinir la tabla, útil en ciertos contextos de desarrollo/pruebas.
    *   **Columnas:**
        *   `id = Column(Integer, primary_key=True, index=True)`: Clave primaria, autoincremental, indexada.
        *   `title = Column(String, index=True)`: Título del libro, indexado.
        *   `author = Column(String, index=True)`: Autor del libro, indexado.
        *   `category = Column(String, index=True)`: Categoría del libro, indexada.
        *   `cover_image_url = Column(String, nullable=True)`: URL de la imagen de portada, puede ser nula.
        *   `file_path = Column(String, unique=True)`: Ruta al archivo original del libro, debe ser única.

### `backend/database.py`

Configura la base de datos SQLAlchemy y proporciona las herramientas para interactuar con ella.

*   **`_base_dir`**: Calcula la ruta absoluta del directorio base del backend.
*   **`_db_path`**: Define la ruta absoluta al archivo `library.db` en la raíz del proyecto.
*   **`SQLALCHEMY_DATABASE_URL`**: Cadena de conexión a la base de datos SQLite. `sqlite:///` seguido de la ruta absoluta.
*   **`engine`**: Objeto `create_engine` de SQLAlchemy que representa la conexión a la base de datos. `connect_args={"check_same_thread": False}` es necesario para SQLite con FastAPI.
*   **`SessionLocal`**: Un constructor de sesiones de base de datos. Las instancias de `SessionLocal` son sesiones de base de datos individuales. `autocommit=False` y `autoflush=False` son configuraciones estándar.
*   **`Base`**: Clase base declarativa para los modelos de SQLAlchemy, de la cual heredarán todos los modelos (`models.py`).

### `backend/crud.py`

Proporciona funciones para realizar operaciones comunes de la base de datos (CRUD) en los objetos `Book`.

*   **`get_book_by_path(db: Session, file_path: str)`**
    *   **Propósito:** Obtiene un libro de la base de datos usando su ruta de archivo.
    *   **Parámetros:**
        *   `db: Session`: Sesión de base de datos.
        *   `file_path: str`: Ruta del archivo del libro.
    *   **Retorna:** Un objeto `models.Book` o `None` si no se encuentra.

*   **`get_book_by_title(db: Session, title: str)`**
    *   **Propósito:** Obtiene un libro por su título exacto (case-sensitive).
    *   **Parámetros:**
        *   `db: Session`.
        *   `title: str`.
    *   **Retorna:** Un objeto `models.Book` o `None`.

*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**
    *   **Propósito:** Busca libros por un título parcial (case-insensitive) con paginación.
    *   **Parámetros:**
        *   `db: Session`.
        *   `title: str`: Título parcial a buscar.
        *   `skip: int`: Número de registros a omitir (offset).
        *   `limit: int`: Número máximo de registros a devolver.
    *   **Retorna:** Una lista de objetos `models.Book`.

*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**
    *   **Propósito:** Obtiene una lista de libros, permitiendo filtrar por categoría, autor o un término de búsqueda general (que aplica a título, autor y categoría).
    *   **Parámetros:**
        *   `db: Session`.
        *   `category: str | None`: Filtrar por categoría.
        *   `search: str | None`: Término de búsqueda general.
        *   `author: str | None`: Filtrar por autor.
    *   **Retorna:** Una lista de objetos `models.Book`, ordenados por ID descendente.

*   **`get_categories(db: Session) -> list[str]`**
    *   **Propósito:** Obtiene una lista de todas las categorías únicas de los libros en la base de datos.
    *   **Parámetros:** `db: Session`.
    *   **Retorna:** Una lista de cadenas (nombres de categorías).

*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**
    *   **Propósito:** Crea un nuevo registro de libro en la base de datos.
    *   **Parámetros:** Recibe todos los atributos necesarios para crear un `models.Book`.
    *   **Retorna:** El objeto `models.Book` recién creado, con su `id` asignado.

*   **`delete_book(db: Session, book_id: int)`**
    *   **Propósito:** Elimina un libro específico de la base de datos y sus archivos asociados (libro y portada).
    *   **Parámetros:**
        *   `db: Session`.
        *   `book_id: int`: ID del libro a eliminar.
    *   **Retorna:** El objeto `models.Book` eliminado o `None` si no se encuentra.

*   **`delete_books_by_category(db: Session, category: str)`**
    *   **Propósito:** Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados.
    *   **Parámetros:**
        *   `db: Session`.
        *   `category: str`: Categoría de libros a eliminar.
    *   **Retorna:** El número de libros eliminados.

*   **`get_books_count(db: Session) -> int`**
    *   **Propósito:** Obtiene el número total de libros registrados en la base de datos.
    *   **Parámetros:** `db: Session`.
    *   **Retorna:** Un entero con el conteo.

### `backend/utils.py`

Contiene funciones de utilidad para la configuración global de la aplicación.

*   **`configure_genai()`**
    *   **Propósito:** Carga las variables de entorno y configura la API de Google Generative AI (Gemini) utilizando una clave API (ya sea `GOOGLE_API_KEY` o `GEMINI_API_KEY`).
    *   **Lógica:** Busca la clave en las variables de entorno. Si no la encuentra, lanza un `ValueError`. Si la encuentra, inicializa `genai.configure()`.
    *   **Retorna:** Nada.
    *   **Excepciones:** `ValueError` si no se encuentra la clave API.

### `backend/rag.py`

Implementa la lógica del sistema Retrieval Augmented Generation (RAG) para interactuar con los libros usando IA.

*   **`_ensure_init()`**
    *   **Propósito:** Inicializa las dependencias clave (carga `.env`, configura `genai`, inicializa `chromadb.PersistentClient`) una sola vez.
    *   **Lógica:** Verifica un flag `_initialized`. Si es `False`, carga las variables de entorno, configura `genai` si hay una API Key y la IA no está deshabilitada, y establece ChromaDB para persistencia en `./rag_index`.

*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**
    *   **Propósito:** Genera un embedding (representación vectorial) para un texto dado utilizando el modelo de embedding de Gemini.
    *   **Parámetros:**
        *   `text: str`: El texto para el cual generar el embedding.
        *   `task_type: str`: Tipo de tarea para el embedding (ej. `RETRIEVAL_DOCUMENT`, `RETRIEVAL_QUERY`).
    *   **Retorna:** Una lista de flotantes que representan el embedding. Si la IA está deshabilitada, retorna un embedding dummy.

*   **`extract_text_from_pdf(file_path: str) -> str`**
    *   **Propósito:** Extrae todo el texto de un archivo PDF.
    *   **Parámetros:** `file_path: str`: Ruta al archivo PDF.
    *   **Retorna:** Una cadena con el texto extraído. Maneja errores de extracción.

*   **`extract_text_from_epub(file_path: str) -> str`**
    *   **Propósito:** Extrae todo el texto de un archivo EPUB.
    *   **Parámetros:** `file_path: str`: Ruta al archivo EPUB.
    *   **Retorna:** Una cadena con el texto extraído. Maneja errores de extracción.

*   **`extract_text(file_path: str) -> str`**
    *   **Propósito:** Función unificada para extraer texto de archivos, soportando PDF y EPUB.
    *   **Parámetros:** `file_path: str`: Ruta al archivo.
    *   **Retorna:** Una cadena con el texto extraído.
    *   **Excepciones:** `ValueError` para tipos de archivo no soportados.

*   **`chunk_text(text: str, max_tokens: int = 1000) -> list[str]`**
    *   **Propósito:** Divide un texto largo en fragmentos más pequeños (chunks) basándose en el recuento de tokens (usando un tokenizador de GPT-3.5 Turbo como aproximación).
    *   **Parámetros:**
        *   `text: str`: El texto a chunkear.
        *   `max_tokens: int`: Número máximo de tokens por chunk.
    *   **Retorna:** Una lista de cadenas, donde cada cadena es un chunk de texto.

*   **`_has_index_for_book(book_id: str) -> bool`**
    *   **Propósito:** Verifica internamente si ChromaDB contiene vectores para un `book_id` dado.
    *   **Parámetros:** `book_id: str`: El ID del libro en el sistema RAG.
    *   **Retorna:** `True` si se encuentran vectores, `False` en caso contrario o si hay un error.

*   **`delete_book_from_rag(book_id: str)`**
    *   **Propósito:** Elimina todos los embeddings y documentos asociados a un `book_id` de ChromaDB.
    *   **Parámetros:** `book_id: str`.
    *   **Retorna:** Nada.

*   **`get_index_count(book_id: str) -> int`**
    *   **Propósito:** Obtiene el número de vectores almacenados en ChromaDB para un `book_id`.
    *   **Parámetros:** `book_id: str`.
    *   **Retorna:** Un entero con el número de vectores.

*   **`has_index(book_id: str) -> bool`**
    *   **Propósito:** Función pública para verificar si un libro tiene índice RAG.
    *   **Parámetros:** `book_id: str`.
    *   **Retorna:** `True` si está indexado, `False` en caso contrario.

*   **`async process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**
    *   **Propósito:** Procesa un archivo de libro para el sistema RAG: extrae texto, lo chunkear, genera embeddings y los almacena en ChromaDB.
    *   **Parámetros:**
        *   `file_path: str`: Ruta al archivo del libro.
        *   `book_id: str`: ID del libro para asociar los embeddings.
        *   `force_reindex: bool`: Si es `True`, borra cualquier índice existente y reindexa.
    *   **Lógica:** Si `force_reindex` es `False` y ya está indexado, se salta el proceso. Extrae el texto, lo divide en chunks. Para cada chunk, genera un embedding y lo añade a la colección de ChromaDB.
    *   **Retorna:** Nada.
    *   **Excepciones:** `ValueError` para tipos de archivo no soportados o si no se puede extraer/chunkear texto.

*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`**
    *   **Propósito:** Estima el número de tokens y chunks que se generarían para un archivo.
    *   **Parámetros:**
        *   `file_path: str`.
        *   `max_tokens: int`.
    *   **Retorna:** Un diccionario con `"tokens"` y `"chunks"`.

*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`**
    *   **Propósito:** Estima el número total de tokens y chunks para una lista de archivos.
    *   **Parámetros:**
        *   `file_paths: list[str]`.
        *   `max_tokens: int`.
    *   **Retorna:** Un diccionario con `"tokens"`, `"chunks"` y `"files"` (archivos contados con éxito).

*   **`async query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**
    *   **Propósito:** Ejecuta una consulta RAG para obtener una respuesta basada en el contenido de un libro.
    *   **Parámetros:**
        *   `query: str`: La pregunta del usuario.
        *   `book_id: str`: El ID del libro en ChromaDB.
        *   `mode: str`: Define cómo la IA debe generar la respuesta:
            *   `'strict'`: Responde solo con el contexto del libro.
            *   `'balanced'`: Prioriza el libro, complementando con conocimiento general y marcando lo que no proviene del libro.
            *   `'open'`: Integra libremente el libro y el conocimiento general.
        *   `metadata: dict | None`: Metadatos opcionales del libro (título, autor, categoría) para enriquecer el prompt.
        *   `library: dict | None`: Contexto opcional de la biblioteca (ej. otros libros del autor) para enriquecer el prompt.
    *   **Lógica:**
        1.  Genera un embedding de la consulta.
        2.  Busca los chunks más relevantes en ChromaDB para el `book_id`.
        3.  Construye un prompt para el modelo de Gemini, incluyendo el contexto recuperado, los metadatos y las instrucciones según el `mode` de respuesta.
        4.  Genera la respuesta con el modelo de Gemini.
    *   **Retorna:** Una cadena con la respuesta de la IA. Si la IA está deshabilitada, retorna un mensaje de IA deshabilitada con el contexto recuperado.

### `backend/main.py`

Es el punto de entrada de la API de FastAPI. Configura la aplicación, define los endpoints y coordina las llamadas a los otros módulos.

*   **Configuración Inicial:**
    *   Carga las variables de entorno (`.env`).
    *   Configura la API de Google Gemini si `API_KEY` está presente y la IA no está deshabilitada.
    *   Crea las tablas de la base de datos si no existen (`models.Base.metadata.create_all`).
    *   Define las rutas absolutas para directorios de archivos (`STATIC_DIR_FS`, `STATIC_COVERS_DIR_FS`, `TEMP_BOOKS_DIR_FS`, `BOOKS_DIR_FS`).
    *   Monta los directorios estáticos para ser servidos (`/static`, `/temp_books`).
    *   Configura el middleware CORS para permitir solicitudes desde orígenes específicos.

*   **Funciones de IA y Procesamiento (internas):**
    *   **`async analyze_with_gemini(text: str) -> dict`**
        *   **Propósito:** Utiliza Google Gemini para extraer el título, autor y categoría de un fragmento de texto de un libro.
        *   **Parámetros:** `text: str`: El texto a analizar.
        *   **Retorna:** Un diccionario JSON con las claves `"title"`, `"author"`, `"category"`. Si hay un error o la IA está deshabilitada, devuelve valores predeterminados de error.

    *   **`def process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**
        *   **Propósito:** Extrae el texto inicial de un archivo PDF y busca/guarda una imagen de portada.
        *   **Parámetros:**
            *   `file_path: str`: Ruta al PDF.
            *   `covers_dir_fs: str`: Directorio donde guardar las portadas.
            *   `covers_url_prefix: str`: Prefijo URL para las portadas.
        *   **Retorna:** Un diccionario con el texto extraído (`"text"`) y la URL de la imagen de portada (`"cover_image_url"`, puede ser `None`).

    *   **`def process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**
        *   **Propósito:** Extrae el texto inicial de un archivo EPUB y busca/guarda una imagen de portada.
        *   **Parámetros:**
            *   `file_path: str`: Ruta al EPUB.
            *   `covers_dir_fs: str`: Directorio donde guardar las portadas.
            *   `covers_url_prefix: str`: Prefijo URL para las portadas.
        *   **Retorna:** Un diccionario con el texto extraído (`"text"`) y la URL de la imagen de portada (`"cover_image_url"`, puede ser `None`).
        *   **Excepciones:** `HTTPException` si no se puede extraer suficiente texto.

*   **Dependencia para la DB:**
    *   **`def get_db()`**: Generador que proporciona una sesión de base de datos (`SessionLocal`) y asegura su cierre. Utilizado con `FastAPI.Depends()`.

*   **Endpoints de la API:**

    *   **`POST /upload-book/`**
        *   **Propósito:** Sube un archivo de libro (PDF o EPUB), lo procesa (extrae texto y portada), lo analiza con IA para obtener metadatos y lo guarda en la base de datos.
        *   **Parámetros de Entrada:** `book_file: UploadFile` (el archivo del libro).
        *   **Retorna:** `schemas.Book` del libro creado.
        *   **Excepciones:**
            *   `409 Conflict` si el libro ya existe (misma ruta).
            *   `400 Bad Request` si el tipo de archivo no es soportado.
            *   `422 Unprocessable Entity` si la IA no puede identificar título y autor.

    *   **`GET /books/`**
        *   **Propósito:** Obtiene una lista de libros, con opciones para filtrar por `category`, `search` general, o `author`.
        *   **Parámetros de Consulta:** `category: str | None`, `search: str | None`, `author: str | None`.
        *   **Retorna:** `List[schemas.Book]`.

    *   **`GET /books/count`**
        *   **Propósito:** Obtiene el número total de libros en la biblioteca.
        *   **Retorna:** `int`.

    *   **`GET /books/search/`**
        *   **Propósito:** Busca libros por un título parcial, con opciones de paginación (`skip`, `limit`).
        *   **Parámetros de Consulta:** `title: str`, `skip: int = 0`, `limit: int = 100`.
        *   **Retorna:** `List[schemas.Book]`.

    *   **`GET /categories/`**
        *   **Propósito:** Obtiene una lista de todas las categorías únicas presentes en la biblioteca.
        *   **Retorna:** `List[str]`.

    *   **`DELETE /books/{book_id}`**
        *   **Propósito:** Elimina un libro de la base de datos por su ID, incluyendo sus archivos asociados y cualquier índice RAG.
        *   **Parámetros de Ruta:** `book_id: int`.
        *   **Retorna:** Mensaje de éxito.
        *   **Excepciones:** `404 Not Found` si el libro no existe.

    *   **`DELETE /categories/{category_name}`**
        *   **Propósito:** Elimina todos los libros pertenecientes a una categoría específica, junto con sus archivos e índices RAG.
        *   **Parámetros de Ruta:** `category_name: str`.
        *   **Retorna:** Mensaje de éxito y número de libros eliminados.
        *   **Excepciones:** `404 Not Found` si la categoría no existe o no tiene libros.

    *   **`GET /books/download/{book_id}`**
        *   **Propósito:** Permite la descarga o visualización en línea de un archivo de libro.
        *   **Parámetros de Ruta:** `book_id: int`.
        *   **Retorna:** `FileResponse` con el contenido del archivo.
        *   **Excepciones:** `404 Not Found` si el libro o el archivo no existen.

    *   **`POST /tools/convert-epub-to-pdf`**
        *   **Propósito:** Convierte un archivo EPUB subido a PDF y devuelve una URL temporal para su descarga.
        *   **Parámetros de Entrada:** `file: UploadFile` (el archivo EPUB).
        *   **Retorna:** `schemas.ConversionResponse` con la `download_url`.
        *   **Excepciones:** `400 Bad Request` si el archivo no es EPUB. `500 Internal Server Error` si la conversión falla.

    *   **`POST /rag/upload-book/`**
        *   **Propósito:** Sube un libro para ser procesado *directamente* por el sistema RAG, asignándole un `book_id` UUID. (Nota: esta ruta es menos utilizada en el frontend principal, que prefiere indexar libros ya en la DB).
        *   **Parámetros de Entrada:** `file: UploadFile`.
        *   **Retorna:** `schemas.RagUploadResponse`.
        *   **Excepciones:** `500 Internal Server Error` si el procesamiento falla.

    *   **`POST /rag/query/`**
        *   **Propósito:** Realiza una consulta al sistema RAG para obtener una respuesta basada en el contenido de un libro.
        *   **Parámetros de Entrada:** `query_data: schemas.RagQuery` (contiene la pregunta, ID del libro y modo de respuesta).
        *   **Retorna:** `schemas.RagQueryResponse` con la respuesta de la IA.
        *   **Excepciones:** `500 Internal Server Error` si la consulta RAG falla.

    *   **`POST /rag/index/{book_id}`**
        *   **Propósito:** Indexa un libro que ya existe en la base de datos para el sistema RAG.
        *   **Parámetros de Ruta:** `book_id: int`.
        *   **Parámetros de Consulta:** `force: bool = False` (si es `True`, reindexa).
        *   **Retorna:** Mensaje de éxito.
        *   **Excepciones:** `404 Not Found` si el libro o su archivo no existen. `500 Internal Server Error` si falla la indexación.

    *   **`GET /rag/status/{book_id}`**
        *   **Propósito:** Devuelve el estado de indexación RAG de un libro específico (si está indexado y cuántos vectores tiene).
        *   **Parámetros de Ruta:** `book_id: int`.
        *   **Retorna:** Objeto JSON con `book_id`, `indexed: bool`, `vector_count: int`.
        *   **Excepciones:** `500 Internal Server Error` si falla la consulta de estado.

    *   **`POST /rag/reindex/category/{category_name}`**
        *   **Propósito:** (Re)indexa todos los libros de una categoría específica en el sistema RAG.
        *   **Parámetros de Ruta:** `category_name: str`.
        *   **Parámetros de Consulta:** `force: bool = True`.
        *   **Retorna:** Resumen del proceso (libros procesados, fallidos).
        *   **Excepciones:** `404 Not Found` si la categoría no existe o no tiene libros.

    *   **`POST /rag/reindex/all`**
        *   **Propósito:** (Re)indexa todos los libros de la biblioteca en el sistema RAG.
        *   **Parámetros de Consulta:** `force: bool = True`.
        *   **Retorna:** Resumen del proceso.

    *   **`GET /rag/estimate/book/{book_id}`**
        *   **Propósito:** Estima el número de tokens, chunks y el coste opcional para indexar un libro.
        *   **Parámetros de Ruta:** `book_id: int`.
        *   **Parámetros de Consulta:** `per1k: float | None` (coste por 1000 tokens), `max_tokens: int = 1000`.
        *   **Retorna:** Objeto JSON con estimaciones.
        *   **Excepciones:** `404 Not Found` si el libro no existe.

    *   **`GET /rag/estimate/category/{category_name}`**
        *   **Propósito:** Estima el número de tokens, chunks y el coste opcional para indexar todos los libros de una categoría.
        *   **Parámetros de Ruta:** `category_name: str`.
        *   **Parámetros de Consulta:** `per1k: float | None`, `max_tokens: int = 1000`.
        *   **Retorna:** Objeto JSON con estimaciones.
        *   **Excepciones:** `404 Not Found` si la categoría no existe o no tiene libros.

    *   **`GET /rag/estimate/all`**
        *   **Propósito:** Estima el número de tokens, chunks y el coste opcional para indexar todos los libros de la biblioteca.
        *   **Parámetros de Consulta:** `per1k: float | None`, `max_tokens: int = 1000`.
        *   **Retorna:** Objeto JSON con estimaciones.

## 4. Análisis Detallado del Frontend (React)

El frontend está desarrollado con React y utiliza `react-router-dom` para el enrutamiento.

### `frontend/src/App.js`

*   **Propósito:** Es el componente raíz de la aplicación React. Configura el enrutamiento para las diferentes vistas.
*   **Estado:** No gestiona estado local.
*   **Propiedades (Props):** Ninguna.
*   **Efectos (Effects):** Ninguno.
*   **Interacciones del Usuario:**
    *   Sirve como contenedor para el `Header` y la `main` área de contenido.
    *   Las rutas definen qué componente de vista se renderiza según la URL.
*   **Comunicación con el Backend:** Indirecta, a través de los componentes de vista que se renderizan.

### `frontend/src/Header.js`

*   **Propósito:** Componente de la barra de navegación superior. Muestra el título de la aplicación, un contador de libros y los enlaces de navegación.
*   **Estado:**
    *   `menuOpen (boolean)`: Controla la visibilidad del menú de hamburguesa en pantallas pequeñas.
    *   `bookCount (number)`: El número total de libros en la biblioteca.
    *   `errorMessage (string | null)`: Mensaje de error si la carga del contador falla.
*   **Propiedades (Props):** Ninguna.
*   **Efectos (Effects):**
    *   `useEffect` al montar el componente: `fetchBookCount` hace una llamada a la API para obtener el número de libros y actualiza `bookCount`. Se configura para re-ejecutarse periódicamente cada 10 minutos.
*   **Interacciones del Usuario:**
    *   **Clic en el botón de hamburguesa:** Alterna el estado `menuOpen`.
    *   **Clic en los enlaces de navegación:** Navega a la ruta correspondiente y cierra el menú si está abierto.
*   **Comunicación con el Backend:**
    *   **GET `/books/count`**: Para obtener el número total de libros.

### `frontend/src/LibraryView.js`

*   **Propósito:** Muestra una cuadrícula de todos los libros en la biblioteca, permitiendo la búsqueda, el filtrado por autor/categoría y la eliminación de libros. También permite leer EPUBs o abrir PDFs.
*   **Estado:**
    *   `books (array)`: Lista de objetos libro a mostrar.
    *   `searchParams (URLSearchParams)`: Utilizado para gestionar los parámetros de la URL para filtrar (categoría, autor).
    *   `searchTerm (string)`: Valor del input de búsqueda.
    *   `debouncedSearchTerm (string)`: Versión "debounced" de `searchTerm` para optimizar las llamadas a la API de búsqueda.
    *   `error (string)`: Mensaje de error si falla la carga de libros.
    *   `loading (boolean)`: Indica si los libros están siendo cargados.
    *   `isMobile (boolean)`: Detecta si la aplicación se está ejecutando en un dispositivo móvil para adaptar la interfaz (ej. botón de descarga adicional para móviles).
*   **Propiedades (Props):** Ninguna.
*   **Efectos (Effects):**
    *   `useDebounce`: Un hook personalizado para aplicar un retardo (300ms) a la `searchTerm` antes de que se use para `fetchBooks`.
    *   `useEffect` (llamando a `fetchBooks` con `useCallback`): Se ejecuta cuando `debouncedSearchTerm` o `searchParams` cambian, para obtener los libros filtrados/buscados del backend.
    *   `useEffect` para `isMobile`: Escucha los cambios de tamaño de la ventana para actualizar el estado `isMobile`.
*   **Interacciones del Usuario:**
    *   **Input de búsqueda:** Actualiza `searchTerm`.
    *   **Clic en autor o categoría:** Actualiza `searchParams` para filtrar la vista y vuelve a cargar los libros.
    *   **Clic en botón "Eliminar libro":** Llama a `handleDeleteBook` para eliminar un libro (con confirmación).
    *   **Clic en "Abrir PDF" / "Leer EPUB":** Navega a la URL de descarga o a la vista `ReaderView` respectivamente.
    *   **Clic en "Descargar PDF" / "Descargar EPUB" (solo móvil):** Descarga el archivo directamente.
*   **Comunicación con el Backend:**
    *   **GET `/books/?category={category}` o `/books/?author={author}` o `/books/?search={term}`**: Para obtener la lista de libros con filtros.
    *   **DELETE `/books/{bookId}`**: Para eliminar un libro.
    *   **GET `/books/download/{bookId}`**: Para descargar el archivo del libro.

### `frontend/src/UploadView.js`

*   **Propósito:** Permite al usuario subir archivos de libros (PDF, EPUB) al servidor para que sean añadidos a la biblioteca.
*   **Estado:**
    *   `filesToUpload (array of objects)`: Cada objeto representa un archivo, incluyendo `file` (el objeto `File`), `status` (`'pending'`, `'uploading'`, `'success'`, `'error'`), y `message`.
    *   `isUploading (boolean)`: Indica si se está realizando una operación de subida.
*   **Propiedades (Props):** Ninguna.
*   **Efectos (Effects):** Ninguno.
*   **Interacciones del Usuario:**
    *   **Input de archivo o arrastrar/soltar:** Añade archivos a `filesToUpload`.
    *   **Botón "Subir {X} Archivo(s)":** Inicia la función `handleUpload`, que envía cada archivo pendiente al backend.
    *   **Botón "Ir a la Biblioteca":** Navega a la vista principal una vez que todas las subidas han terminado.
*   **Comunicación con el Backend:**
    *   **POST `/upload-book/`**: Para subir cada archivo de libro.

### `frontend/src/ToolsView.js`

*   **Propósito:** Proporciona un espacio para herramientas útiles de la biblioteca. Actualmente, incluye un "Convertidor de EPUB a PDF".
*   **Componente `EpubToPdfConverter` (interno):**
    *   **Estado:**
        *   `selectedFile (File | null)`: El archivo EPUB seleccionado para la conversión.
        *   `message (string)`: Mensaje de estado para el usuario (instrucciones, progreso, éxito, error).
        *   `isLoading (boolean)`: Indica si el proceso de conversión está activo.
    *   **Propiedades (Props):** Ninguna.
    *   **Efectos (Effects):** Ninguno.
    *   **Interacciones del Usuario:**
        *   **Input de archivo o arrastrar/soltar:** Permite seleccionar un archivo EPUB.
        *   **Botón "Convertir a PDF":** Llama a `handleConvert`, que sube el archivo al backend para su conversión.
    *   **Comunicación con el Backend:**
        *   **POST `/tools/convert-epub-to-pdf`**: Para enviar el EPUB y recibir una URL de descarga del PDF.

### `frontend/src/ReaderView.js`

*   **Propósito:** Proporciona un visor para libros EPUB integrado en la aplicación, utilizando la librería `react-reader`.
*   **Estado:**
    *   `location (string | null)`: Almacena la ubicación actual en el EPUB (CFI) para reanudar la lectura.
    *   `epubData (ArrayBuffer | null)`: Los datos binarios del archivo EPUB cargado.
    *   `isLoading (boolean)`: Indica si el libro está cargando.
    *   `error (string)`: Mensaje de error si la carga del libro falla.
*   **Propiedades (Props):**
    *   `bookId (string)`: Obtenido de los parámetros de la URL (`useParams`).
*   **Efectos (Effects):**
    *   `useEffect` al montar o cuando `bookId` cambia: `fetchBookData` hace una llamada a la API para descargar el archivo EPUB.
*   **Interacciones del Usuario:**
    *   El componente `ReactReader` gestiona las interacciones de lectura (paginación, desplazamiento).
*   **Comunicación con el Backend:**
    *   **GET `/books/download/{bookId}`**: Para obtener el contenido binario del archivo EPUB.

### `frontend/src/RagView.js`

*   **Propósito:** Proporciona una interfaz para seleccionar un libro de la biblioteca, indexarlo en el sistema RAG y luego conversar con un asistente de IA sobre su contenido.
*   **Estado:**
    *   `message (string)`: Mensaje de estado general al usuario (ej. "Indexando...", "Listo para chatear").
    *   `isLoading (boolean)`: Indica si la IA está generando una respuesta del chat.
    *   `bookId (string | null)`: El ID del libro actualmente configurado para la conversación RAG.
    *   `chatHistory (array of objects)`: Un array que almacena los mensajes de la conversación (`{ sender: 'user'|'gemini', text: string }`).
    *   `currentQuery (string)`: El texto que el usuario está escribiendo para la consulta.
    *   `libraryBooks (array)`: Lista de todos los libros disponibles en la biblioteca.
    *   `selectedLibraryId (string)`: El ID del libro de la biblioteca seleccionado en el dropdown/buscador.
    *   `libStatus (object)`: Objeto que contiene el estado del libro seleccionado en RAG (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy (boolean)`: Bloquea los botones de indexación/reindexación mientras están en curso.
    *   `refreshing (boolean)`: Indica que se está refrescando el estado RAG (sin bloquear acciones principales).
    *   `searchTerm (string)`: Término para buscar libros en la biblioteca.
    *   `searching (boolean)`: Indica si la búsqueda de libros está activa.
    *   `searchResults (array)`: Resultados de la búsqueda de libros.
    *   `resultsOpen (boolean)`: Controla la visibilidad de los resultados de búsqueda.
    *   `mode (string)`: El modo de respuesta del RAG ('strict', 'balanced', 'open').
    *   `selectedBook (object | null)`: El objeto libro completo del seleccionado en el buscador.
*   **Propiedades (Props):** Ninguna.
*   **Efectos (Effects):**
    *   `useEffect` al montar: `fetchBooks` para cargar la lista completa de libros de la biblioteca.
    *   `useEffect` para `searchTerm`: Implementa un debounce para buscar libros a medida que el usuario escribe.
    *   `useEffect` cuando `selectedLibraryId` cambia: Llama a `checkLibraryStatus` para obtener el estado de indexación RAG del libro.
    *   `useEffect` para `chatHistory` e `isLoading`: Hace scroll automático al final del chat.
*   **Interacciones del Usuario:**
    *   **Input de búsqueda:** Permite buscar libros por título, autor o categoría.
    *   **Selección de libro de los resultados:** Establece `selectedLibraryId` y `selectedBook`, lo que desencadena la comprobación de su estado RAG.
    *   **Botones "Comprobar RAG", "Indexar", "Reindexar":** Ejecutan las funciones `checkLibraryStatus` e `indexLibraryBook`.
    *   **Botón "Chatear":** Activa el modo de conversación para el libro seleccionado si está indexado.
    *   **Input de texto del chat:** Permite al usuario escribir sus preguntas.
    *   **Botón "Enviar":** Llama a `handleQuerySubmit` para enviar la pregunta a la IA.
    *   **Radios de modo:** Permiten elegir la estrategia de respuesta de la IA (`mode`).
*   **Comunicación con el Backend:**
    *   **GET `/books/` (y con parámetro `search`)**: Para obtener la lista y resultados de búsqueda de libros.
    *   **GET `/rag/status/{book_id}`**: Para comprobar si un libro está indexado en RAG.
    *   **POST `/rag/index/{book_id}`**: Para iniciar o forzar la indexación de un libro.
    *   **POST `/rag/query/`**: Para enviar una pregunta a la IA y obtener una respuesta.

## 5. Flujo de Datos y API

### Flujo de Subida de un Libro

1.  **Frontend (`UploadView.js`):**
    *   El usuario selecciona uno o varios archivos (PDF/EPUB) a través de un input de archivo o arrastrando y soltando en la zona designada.
    *   Cuando el usuario hace clic en "Subir", el componente itera sobre cada archivo seleccionado que esté en estado "pending".
    *   Para cada archivo, se crea un objeto `FormData` y se le añade el archivo (`'book_file'`).
    *   Se envía una petición `POST` asíncrona a la API del backend en `/upload-book/`.

2.  **Backend (`main.py` - endpoint `upload_book`):**
    *   FastAPI recibe el `UploadFile`.
    *   El archivo se guarda temporalmente en el directorio `BOOKS_DIR_FS`.
    *   Se detecta la extensión del archivo (`.pdf` o `.epub`).
    *   Se llama a la función `process_pdf` o `process_epub` (también en `main.py`) para:
        *   Extraer una porción inicial del texto del libro.
        *   Intentar extraer una imagen de portada y guardarla en `STATIC_COVERS_DIR_FS`, generando una `cover_image_url`.
    *   El texto extraído se envía a la función `analyze_with_gemini` (en `main.py`).
    *   `analyze_with_gemini` hace una llamada a la API de Google Gemini (si está habilitada) con un prompt que le pide identificar el título, autor y categoría del libro basándose en el texto proporcionado.
    *   La respuesta de Gemini se parsea. Si no se puede identificar el título y el autor, se considera un fallo de calidad, el archivo se borra y se devuelve un error 422.
    *   Si el análisis es exitoso, se llama a `crud.create_book` (del módulo `backend/crud.py`) para guardar los metadatos del libro (título, autor, categoría, `cover_image_url`, `file_path`) en la base de datos SQLite.
    *   El objeto `Book` recién creado (con su ID de DB) se serializa a `schemas.Book` y se devuelve al frontend como una respuesta JSON 200 OK.

3.  **Frontend (`UploadView.js`):**
    *   Recibe la respuesta del backend.
    *   Actualiza el `status` y `message` de cada archivo en `filesToUpload` (`'success'` o `'error'`) para reflejar el resultado de la subida.
    *   Una vez que todos los archivos han sido procesados, el usuario puede navegar a la `LibraryView`.

### Principales Endpoints de la API

La API del backend está documentada en el código fuente de `backend/main.py`. A continuación se resume:

*   **Gestión de Libros:**
    *   `POST /upload-book/`: Sube y procesa un libro.
    *   `GET /books/`: Lista libros (con filtros por categoría, búsqueda, autor).
    *   `GET /books/count`: Retorna el número total de libros.
    *   `GET /books/search/`: Busca libros por título parcial.
    *   `DELETE /books/{book_id}`: Elimina un libro.
    *   `GET /books/download/{book_id}`: Descarga o abre un libro.

*   **Gestión de Categorías:**
    *   `GET /categories/`: Lista todas las categorías únicas.
    *   `DELETE /categories/{category_name}`: Elimina una categoría y sus libros.

*   **Herramientas:**
    *   `POST /tools/convert-epub-to-pdf`: Convierte EPUB a PDF.

*   **Sistema RAG (Retrieval Augmented Generation):**
    *   `POST /rag/upload-book/`: Sube un libro *temporalmente* para RAG (usa UUID para `book_id` en RAG).
    *   `POST /rag/query/`: Envía una consulta de lenguaje natural sobre un libro específico.
    *   `POST /rag/index/{book_id}`: Indexa un libro existente en la base de datos para RAG.
    *   `GET /rag/status/{book_id}`: Obtiene el estado de indexación RAG de un libro.
    *   `POST /rag/reindex/category/{category_name}`: Reindexa todos los libros de una categoría.
    *   `POST /rag/reindex/all`: Reindexa todos los libros de la biblioteca.
    *   `GET /rag/estimate/book/{book_id}`: Estima el coste de indexación para un libro.
    *   `GET /rag/estimate/category/{category_name}`: Estima el coste de indexación para una categoría.
    *   `GET /rag/estimate/all`: Estima el coste de indexación para toda la biblioteca.
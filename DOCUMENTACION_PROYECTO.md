# Documentación Técnica del Proyecto "Mi Librería Inteligente"

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar una colección de libros digitales (PDF y EPUB). La aplicación no solo almacena y organiza los libros, sino que también utiliza capacidades de Inteligencia Artificial (IA) para analizar el contenido, extraer metadatos (título, autor, categoría) y facilitar la interacción conversacional (RAG) con los libros.

**Arquitectura General:**

*   **Frontend:** Desarrollado con **React**, proporciona una interfaz de usuario interactiva y responsiva. Se encarga de la visualización de la biblioteca, la subida de libros, la lectura de EPUBs y la interacción con las herramientas de IA.
*   **Backend:** Construido con **FastAPI** (Python), sirve como la API RESTful que maneja toda la lógica de negocio. Incluye la gestión de la base de datos, el procesamiento de archivos, la integración con modelos de lenguaje grandes (LLMs) de Gemini y el sistema de Recuperación Aumentada por Generación (RAG).
*   **Base de Datos:** Utiliza **SQLite** para un almacenamiento ligero y persistente de los metadatos de los libros, gestionado a través de SQLAlchemy.
*   **Almacenamiento de Archivos:** Los libros originales (PDF/EPUB) y las portadas extraídas se almacenan directamente en el sistema de archivos del servidor backend.
*   **Inteligencia Artificial (IA):** Integra la API de Google Gemini para:
    *   Análisis inicial de libros y extracción de metadatos.
    *   Generación de embeddings para el sistema RAG.
    *   Respuestas conversacionales basadas en el contenido de los libros.
*   **ChromaDB:** Un almacén vectorial utilizado por el módulo RAG para guardar y recuperar eficientemente los embeddings de los fragmentos de los libros.

## 2. Estructura del Proyecto

El proyecto sigue una estructura de directorios estándar para aplicaciones web con frontend y backend separados:

```
.
├── backend/
│   ├── alembic/                      # Migraciones de base de datos con Alembic
│   ├── tests/                        # Pruebas unitarias para el backend
│   ├── tests_curated/                # Pruebas adicionales/curadas
│   ├── __init__.py                   # Marcador de paquete Python
│   ├── crud.py                       # Operaciones CRUD para la base de datos
│   ├── database.py                   # Configuración de la conexión a la base de datos
│   ├── main.py                       # Aplicación principal de FastAPI y endpoints API
│   ├── models.py                     # Definiciones de modelos de SQLAlchemy
│   ├── rag.py                        # Lógica de Retrieval Augmented Generation (RAG)
│   ├── schemas.py                    # Esquemas Pydantic para validación de datos
│   ├── utils.py                      # Funciones de utilidad y helpers
│   ├── library.db                    # Archivo de base de datos SQLite (generado)
│   ├── books/                        # Directorio para almacenar los archivos de libros
│   ├── temp_books/                   # Directorio temporal para archivos de conversión/RAG
│   └── static/                       # Contenido estático servido por FastAPI
│       └── covers/                   # Portadas de libros extraídas
├── frontend/
│   ├── public/                       # Archivos estáticos de React (index.html, etc.)
│   ├── src/                          # Código fuente de la aplicación React
│   │   ├── App.css                   # Estilos globales de la aplicación
│   │   ├── App.js                    # Componente principal de React y enrutamiento
│   │   ├── CategoriesView.js         # Vista para listar categorías
│   │   ├── config.js                 # Configuración de la URL del API
│   │   ├── EditBookModal.js          # Componente modal para editar libros
│   │   ├── ErrorBoundary.js          # Componente para manejo de errores de UI
│   │   ├── Header.js                 # Componente del encabezado y navegación
│   │   ├── index.css                 # Estilos CSS de React
│   │   ├── index.js                  # Punto de entrada de la aplicación React
│   │   ├── LibraryView.js            # Vista principal de la biblioteca de libros
│   │   ├── RagView.js                # Vista para la interacción RAG (IA)
│   │   ├── ReaderView.js             # Vista para el lector de EPUB
│   │   ├── ToolsView.js              # Vista para herramientas adicionales (ej. conversión EPUB a PDF)
│   │   └── UploadView.js             # Vista para la subida de nuevos libros
│   ├── .env.development              # Variables de entorno para desarrollo
│   └── .env.production               # Variables de entorno para producción
├── .env                              # Variables de entorno para el backend
├── README.md
└── requirements.txt                  # Dependencias de Python
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/models.py`

Define el esquema de la base de datos para los objetos `Book` utilizando SQLAlchemy.

*   **Clase `Book`**:
    *   **Propósito**: Representa la tabla `books` en la base de datos.
    *   `__tablename__ = "books"`: Nombre de la tabla.
    *   `__table_args__ = {'extend_existing': True}`: Permite redefinir la tabla en caso de ejecuciones repetidas (útil en tests o entornos específicos).
    *   `id`: `Integer`, clave primaria, indexado. Identificador único del libro.
    *   `title`: `String`, indexado. Título del libro.
    *   `author`: `String`, indexado. Autor del libro.
    *   `category`: `String`, indexado. Categoría o género del libro.
    *   `cover_image_url`: `String`, `nullable=True`. URL de la imagen de portada del libro.
    *   `file_path`: `String`, `unique=True`. Ruta absoluta al archivo de libro original en el sistema de archivos.

### `backend/database.py`

Configura la conexión a la base de datos SQLite y las herramientas de SQLAlchemy.

*   `_base_dir`, `_db_path`: Calcula la ruta absoluta al archivo `library.db` en la raíz del proyecto.
*   `SQLALCHEMY_DATABASE_URL`: URL de conexión a la base de datos SQLite.
*   `engine`: Objeto `Engine` de SQLAlchemy, que gestiona la conexión a la base de datos.
    *   `connect_args={"check_same_thread": False}`: Necesario para SQLite cuando se usa con FastAPI, permite que múltiples hilos accedan a la misma conexión de forma segura.
*   `SessionLocal`: Constructor de sesiones de base de datos. Cada instancia (`db`) representa una sesión.
*   `Base`: Instancia de `declarative_base()`, utilizada por los modelos de SQLAlchemy para heredar y mapearse a tablas de la base de datos.

### `backend/crud.py`

Contiene funciones para realizar operaciones **C**rear, **R**eferenciar, **U**pdate y **D**elete (CRUD) sobre los libros en la base de datos.

*   **`get_book(db: Session, book_id: int) -> models.Book`**:
    *   **Lógica**: Consulta un libro por su `id`.
    *   **Parámetros**: `db` (sesión de DB), `book_id` (ID del libro).
    *   **Retorno**: El objeto `Book` o `None` si no se encuentra.
*   **`get_book_by_path(db: Session, file_path: str) -> models.Book`**:
    *   **Lógica**: Consulta un libro por su ruta de archivo.
    *   **Parámetros**: `db`, `file_path`.
    *   **Retorno**: El objeto `Book` o `None`.
*   **`get_book_by_title(db: Session, title: str) -> models.Book`**:
    *   **Lógica**: Consulta un libro por su título exacto.
    *   **Parámetros**: `db`, `title`.
    *   **Retorno**: El objeto `Book` o `None`.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100) -> list[models.Book]`**:
    *   **Lógica**: Busca libros con un título parcial (insensible a mayúsculas/minúsculas), con paginación.
    *   **Parámetros**: `db`, `title`, `skip` (elementos a omitir), `limit` (número máximo de resultados).
    *   **Retorno**: Lista de objetos `Book`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None) -> list[models.Book]`**:
    *   **Lógica**: Obtiene una lista de libros, con filtros opcionales por categoría, autor, o una búsqueda general en título/autor/categoría. Ordena por ID descendente.
    *   **Parámetros**: `db`, `category` (nombre de categoría), `search` (término de búsqueda general), `author` (nombre del autor).
    *   **Retorno**: Lista de objetos `Book`.
*   **`get_categories(db: Session) -> list[str]`**:
    *   **Lógica**: Obtiene una lista de todas las categorías únicas presentes en los libros.
    *   **Parámetros**: `db`.
    *   **Retorno**: Lista de strings con los nombres de las categorías.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str) -> models.Book`**:
    *   **Lógica**: Crea un nuevo registro de libro en la base de datos.
    *   **Parámetros**: `db`, `title`, `author`, `category`, `cover_image_url`, `file_path`.
    *   **Retorno**: El objeto `Book` recién creado.
*   **`delete_book(db: Session, book_id: int) -> models.Book`**:
    *   **Lógica**: Elimina un libro por su ID. También elimina los archivos asociados (libro y portada) del disco.
    *   **Parámetros**: `db`, `book_id`.
    *   **Retorno**: El objeto `Book` eliminado o `None`.
*   **`delete_books_by_category(db: Session, category: str) -> int`**:
    *   **Lógica**: Elimina todos los libros pertenecientes a una categoría específica, incluyendo sus archivos asociados.
    *   **Parámetros**: `db`, `category`.
    *   **Retorno**: El número de libros eliminados.
*   **`get_books_count(db: Session) -> int`**:
    *   **Lógica**: Cuenta el número total de libros en la biblioteca.
    *   **Parámetros**: `db`.
    *   **Retorno**: Un entero con el conteo.
*   **`update_book(db: Session, book_id: int, title: str, author: str, cover_image_url: str | None) -> models.Book`**:
    *   **Lógica**: Actualiza el título, autor y opcionalmente la URL de la portada de un libro.
    *   **Parámetros**: `db`, `book_id`, `title`, `author`, `cover_image_url`.
    *   **Retorno**: El objeto `Book` actualizado o `None`.

### `backend/schemas.py`

Define los esquemas de datos utilizando Pydantic para la validación de entrada y salida de las API de FastAPI.

*   **Clase `BookBase`**:
    *   **Propósito**: Esquema base para los datos de un libro, utilizado en las operaciones de creación y actualización.
    *   **Campos**: `title`, `author`, `category`, `cover_image_url` (opcional), `file_path`.
*   **Clase `Book(BookBase)`**:
    *   **Propósito**: Representa un libro completo tal como se devuelve desde la API, incluyendo el `id` generado por la base de datos.
    *   **Campo**: `id` (int).
    *   `Config.from_attributes = True`: Permite mapear directamente desde modelos de SQLAlchemy.
*   **Clase `ConversionResponse`**:
    *   **Propósito**: Esquema de respuesta para el endpoint de conversión EPUB a PDF.
    *   **Campo**: `download_url` (str).
*   **Clase `RagUploadResponse`**:
    *   **Propósito**: Esquema de respuesta para la subida de libros al sistema RAG.
    *   **Campos**: `book_id` (str), `message` (str).
*   **Clase `RagQuery`**:
    *   **Propósito**: Esquema de solicitud para realizar una consulta RAG.
    *   **Campos**: `query` (str), `book_id` (str), `mode` (str, opcional, puede ser 'strict', 'balanced' o 'open').
*   **Clase `RagQueryResponse`**:
    *   **Propósito**: Esquema de respuesta para una consulta RAG.
    *   **Campo**: `response` (str).

### `backend/utils.py`

Proporciona funciones de utilidad para la configuración de la IA, el manejo de archivos y la conversión de formatos.

*   **`configure_genai()`**:
    *   **Lógica**: Carga variables de entorno y configura la API de Google Gemini (requiere `GOOGLE_API_KEY` o `GEMINI_API_KEY`).
    *   **Parámetros**: Ninguno.
    *   **Retorno**: Ninguno. Lanza `ValueError` si no se encuentra la clave API.
*   **`get_gemini_model(model_name: str = "gemini-pro")`**:
    *   **Lógica**: Obtiene una instancia del modelo generativo de Gemini.
    *   **Parámetros**: `model_name` (str, por defecto "gemini-pro").
    *   **Retorno**: Una instancia de `genai.GenerativeModel`.
*   **`generate_text_from_prompt(prompt: str, model_name: str = "gemini-pro")`**:
    *   **Lógica**: Genera texto a partir de un prompt utilizando el modelo Gemini especificado.
    *   **Parámetros**: `prompt` (str), `model_name` (str).
    *   **Retorno**: El texto generado por la IA o un mensaje de error.
*   **`get_file_extension(filename: str) -> str`**:
    *   **Lógica**: Extrae la extensión de un nombre de archivo y la devuelve en minúsculas.
    *   **Parámetros**: `filename` (str).
    *   **Retorno**: La extensión del archivo (ej. ".pdf").
*   **`is_allowed_file(filename: str, allowed_extensions: set) -> bool`**:
    *   **Lógica**: Comprueba si la extensión de un archivo está en el conjunto de extensiones permitidas.
    *   **Parámetros**: `filename` (str), `allowed_extensions` (set de strings).
    *   **Retorno**: `True` si la extensión está permitida, `False` en caso contrario.
*   **`convert_epub_bytes_to_pdf_bytes(epub_content: bytes) -> bytes`**:
    *   **Lógica**: Función compleja que toma el contenido de un archivo EPUB (en bytes) y lo convierte a PDF (en bytes). Implica:
        1.  Extracción del contenido del EPUB (que es un archivo ZIP) a un directorio temporal.
        2.  Localización del archivo `.opf` (manifiesto del libro).
        3.  Análisis del `.opf` para identificar portada y archivos CSS/HTML.
        4.  Generación de una portada HTML si se encuentra una imagen.
        5.  Carga de todos los archivos CSS.
        6.  Lectura de los capítulos HTML en el orden especificado en el "spine" del EPUB.
        7.  Renderizado de todos los documentos HTML con sus estilos CSS usando WeasyPrint.
        8.  Unión de todas las páginas renderizadas en un único PDF.
    *   **Parámetros**: `epub_content` (bytes).
    *   **Retorno**: El contenido del PDF en bytes. Lanza `RuntimeError` en caso de fallo en la conversión.

### `backend/rag.py`

Implementa la lógica de Retrieval Augmented Generation (RAG) para permitir a la IA "conversar" sobre el contenido de un libro. Utiliza ChromaDB como almacén vectorial.

*   `EMBEDDING_MODEL`, `GENERATION_MODEL`: Variables de entorno para configurar los modelos Gemini.
*   **`_ensure_init()`**:
    *   **Lógica**: Inicializa la configuración de Gemini y ChromaDB (colección `book_rag_collection`) la primera vez que se llama. Persiste el índice de Chroma en disco.
    *   **Parámetros**: Ninguno.
    *   **Retorno**: Ninguno.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]`**:
    *   **Lógica**: Genera un vector de embedding para el texto dado usando el modelo Gemini de embeddings. Si la IA está deshabilitada, devuelve un embedding dummy.
    *   **Parámetros**: `text` (str), `task_type` (str, tipo de tarea para el embedding, ej. "RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY").
    *   **Retorno**: Una lista de flotantes (el vector de embedding).
*   **`extract_text_from_pdf(file_path: str) -> str`**:
    *   **Lógica**: Extrae texto de un archivo PDF utilizando `PyPDF2`.
    *   **Parámetros**: `file_path` (str).
    *   **Retorno**: El texto extraído.
*   **`extract_text_from_epub(file_path: str) -> str`**:
    *   **Lógica**: Extrae texto de un archivo EPUB utilizando `ebooklib` y `BeautifulSoup`.
    *   **Parámetros**: `file_path` (str).
    *   **Retorno**: El texto extraído.
*   **`extract_text(file_path: str) -> str`**:
    *   **Lógica**: Unifica la extracción de texto, llamando a la función adecuada según la extensión del archivo.
    *   **Parámetros**: `file_path` (str).
    *   **Retorno**: El texto extraído. Lanza `ValueError` para tipos no soportados.
*   **`chunk_text(text: str, max_tokens: int = 1000) -> list[str]`**:
    *   **Lógica**: Divide un texto largo en fragmentos más pequeños, basándose en un número máximo de tokens (utiliza `tiktoken` como aproximación).
    *   **Parámetros**: `text` (str), `max_tokens` (int).
    *   **Retorno**: Una lista de strings (los fragmentos).
*   **`_has_index_for_book(book_id: str) -> bool`**:
    *   **Lógica**: Comprueba si ya existen vectores indexados para un `book_id` en ChromaDB.
    *   **Parámetros**: `book_id` (str).
    *   **Retorno**: `True` si existen, `False` en caso contrario.
*   **`delete_book_from_rag(book_id: str)`**:
    *   **Lógica**: Elimina todos los vectores asociados a un `book_id` de ChromaDB.
    *   **Parámetros**: `book_id` (str).
    *   **Retorno**: Ninguno.
*   **`get_index_count(book_id: str) -> int`**:
    *   **Lógica**: Devuelve el número de vectores (fragmentos) almacenados para un `book_id`.
    *   **Parámetros**: `book_id` (str).
    *   **Retorno**: Un entero.
*   **`has_index(book_id: str) -> bool`**:
    *   **Lógica**: Wrapper público para `get_index_count` que devuelve un booleano.
    *   **Parámetros**: `book_id` (str).
    *   **Retorno**: `True` si tiene índice, `False` en caso contrario.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**:
    *   **Lógica**: Procesa un archivo de libro: extrae texto, lo divide en fragmentos, genera embeddings para cada fragmento y los almacena en ChromaDB. Si `force_reindex` es `True`, elimina cualquier índice existente primero.
    *   **Parámetros**: `file_path` (str), `book_id` (str, ID único del libro para RAG), `force_reindex` (bool).
    *   **Retorno**: Ninguno. Lanza `ValueError` si el archivo no es soportado o no se puede extraer texto/fragmentos.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`**:
    *   **Lógica**: Estima el número total de tokens y de fragmentos que se generarían para un archivo.
    *   **Parámetros**: `file_path` (str), `max_tokens` (int).
    *   **Retorno**: Un diccionario con `tokens` (int) y `chunks` (int).
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`**:
    *   **Lógica**: Estima el total de tokens y fragmentos para una lista de archivos.
    *   **Parámetros**: `file_paths` (list de str), `max_tokens` (int).
    *   **Retorno**: Un diccionario con `tokens` (int), `chunks` (int) y `files` (int).
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None) -> str`**:
    *   **Lógica**: Realiza una consulta al sistema RAG. Busca los fragmentos más relevantes del libro en ChromaDB, construye un prompt con el contexto recuperado, metadatos del libro y contexto de la biblioteca, y luego usa un modelo Gemini para generar una respuesta. El parámetro `mode` controla cómo la IA debe integrar el contexto del libro con su conocimiento general.
    *   **Parámetros**:
        *   `query` (str): La pregunta del usuario.
        *   `book_id` (str): El ID del libro sobre el que se consulta.
        *   `mode` (str): Estrategia de respuesta ("strict", "balanced", "open").
        *   `metadata` (dict, opcional): Metadatos del libro (título, autor, categoría).
        *   `library` (dict, opcional): Contexto adicional de la biblioteca (ej. otras obras del mismo autor).
    *   **Retorno**: La respuesta generada por la IA.

### `backend/main.py`

El archivo principal de la aplicación FastAPI. Configura la aplicación, define las rutas de la API, maneja la lógica de negocio y se integra con los otros módulos del backend.

*   **Configuración Inicial**:
    *   Carga variables de entorno, configura la API de Gemini si está habilitada.
    *   Crea las tablas de la base de datos si no existen (`models.Base.metadata.create_all`).
    *   Define las rutas absolutas para directorios de archivos (`STATIC_DIR_FS`, `BOOKS_DIR_FS`, etc.) y los crea si no existen.
    *   Configura el middleware CORS para permitir solicitudes desde el frontend.
*   **`get_db()`**:
    *   **Lógica**: Función de dependencia de FastAPI que proporciona una sesión de base de datos a los endpoints y asegura su cierre.
    *   **Parámetros**: Ninguno.
    *   **Retorno**: Un objeto `Session` de SQLAlchemy.
*   **`analyze_with_gemini(text: str) -> dict` (async)**:
    *   **Lógica**: Utiliza un modelo Gemini (configurable, `gemini-2.5-flash` por defecto) para analizar el texto de las primeras páginas de un libro y extraer su título, autor y categoría. Devuelve un objeto JSON.
    *   **Parámetros**: `text` (str, hasta 4000 caracteres).
    *   **Retorno**: Diccionario con `title`, `author`, `category` o valores de error.
*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
    *   **Lógica**: Procesa un archivo PDF: extrae texto de las primeras páginas para análisis de IA y busca una imagen de portada.
    *   **Parámetros**: `file_path`, `covers_dir_fs` (ruta del directorio de portadas), `covers_url_prefix` (prefijo URL para portadas).
    *   **Retorno**: Diccionario con `text` y `cover_image_url` (o `None`).
*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
    *   **Lógica**: Procesa un archivo EPUB: extrae texto para análisis de IA y busca una imagen de portada (con varios fallbacks).
    *   **Parámetros**: `file_path`, `covers_dir_fs`, `covers_url_prefix`.
    *   **Retorno**: Diccionario con `text` y `cover_image_url` (o `None`). Lanza `HTTPException` si no hay texto suficiente.

---

**Endpoints de la API (definidos en `main.py`)**:

*   **`POST /api/books/{book_id}/convert`**:
    *   **Propósito**: Convierte un libro EPUB existente en la biblioteca a PDF y lo añade como un nuevo libro.
    *   **Parámetros**: `book_id` (path), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (schemas.Book), `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`.
*   **`POST /tools/convert-epub-to-pdf`**:
    *   **Propósito**: Convierte un archivo EPUB subido temporalmente a PDF y devuelve una URL de descarga.
    *   **Parámetros**: `file` (UploadFile).
    *   **Cuerpo de la solicitud**: Archivo EPUB.
    *   **Respuestas**: `200 OK` (ConversionResponse), `400 Bad Request`, `500 Internal Server Error`.
*   **`POST /upload-book/`**:
    *   **Propósito**: Sube y procesa un nuevo libro (PDF/EPUB). La IA extrae metadatos y guarda el libro en la base de datos y en el disco.
    *   **Parámetros**: `book_file` (UploadFile), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Archivo de libro.
    *   **Respuestas**: `200 OK` (schemas.Book), `400 Bad Request`, `409 Conflict` (libro duplicado), `422 Unprocessable Entity` (IA no pudo extraer metadatos).
*   **`GET /books/`**:
    *   **Propósito**: Obtiene una lista de libros, con filtros opcionales.
    *   **Parámetros**: `category` (query, opcional), `search` (query, opcional), `author` (query, opcional), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (list[schemas.Book]).
*   **`PUT /books/{book_id}`**:
    *   **Propósito**: Actualiza los detalles de un libro (título, autor, portada).
    *   **Parámetros**: `book_id` (path), `db` (dependencia), `title` (form), `author` (form), `cover_image` (form, opcional).
    *   **Cuerpo de la solicitud**: Datos del formulario.
    *   **Respuestas**: `200 OK` (schemas.Book), `404 Not Found`.
*   **`GET /books/count`**:
    *   **Propósito**: Obtiene el número total de libros.
    *   **Parámetros**: `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (int).
*   **`GET /books/search/`**:
    *   **Propósito**: Busca libros por título parcial.
    *   **Parámetros**: `title` (query), `skip` (query, opcional), `limit` (query, opcional), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (list[schemas.Book]).
*   **`GET /categories/`**:
    *   **Propósito**: Obtiene una lista de todas las categorías únicas.
    *   **Parámetros**: `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (list[str]).
*   **`DELETE /books/{book_id}`**:
    *   **Propósito**: Elimina un libro específico y sus archivos asociados.
    *   **Parámetros**: `book_id` (path), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `404 Not Found`.
*   **`DELETE /categories/{category_name}`**:
    *   **Propósito**: Elimina todos los libros de una categoría específica.
    *   **Parámetros**: `category_name` (path), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `404 Not Found`.
*   **`GET /books/download/{book_id}`**:
    *   **Propósito**: Descarga un libro específico.
    *   **Parámetros**: `book_id` (path), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (FileResponse), `404 Not Found`.
*   **`POST /rag/upload-book/`**:
    *   **Propósito**: Sube un libro (temporalmente) para ser procesado por el sistema RAG.
    *   **Parámetros**: `file` (UploadFile).
    *   **Cuerpo de la solicitud**: Archivo de libro.
    *   **Respuestas**: `200 OK` (schemas.RagUploadResponse), `500 Internal Server Error`.
*   **`POST /rag/query/`**:
    *   **Propósito**: Realiza una consulta al sistema RAG sobre un libro.
    *   **Parámetros**: `query_data` (schemas.RagQuery), `db` (dependencia).
    *   **Cuerpo de la solicitud**: JSON con `query`, `book_id`, `mode`.
    *   **Respuestas**: `200 OK` (schemas.RagQueryResponse), `500 Internal Server Error`.
*   **`POST /rag/index/{book_id}`**:
    *   **Propósito**: Indexa un libro existente en la base de datos en el sistema RAG.
    *   **Parámetros**: `book_id` (path), `force` (query, bool, opcional), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `404 Not Found`, `500 Internal Server Error`.
*   **`GET /rag/status/{book_id}`**:
    *   **Propósito**: Devuelve el estado de indexación RAG de un libro (si está indexado y cuántos vectores tiene).
    *   **Parámetros**: `book_id` (path).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `500 Internal Server Error`.
*   **`POST /rag/reindex/category/{category_name}`**:
    *   **Propósito**: (Re)indexa todos los libros de una categoría específica en RAG.
    *   **Parámetros**: `category_name` (path), `force` (query, bool, opcional), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `404 Not Found`, `500 Internal Server Error`.
*   **`POST /rag/reindex/all`**:
    *   **Propósito**: (Re)indexa todos los libros de la biblioteca en RAG.
    *   **Parámetros**: `force` (query, bool, opcional), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `500 Internal Server Error`.
*   **`GET /rag/estimate/book/{book_id}`**:
    *   **Propósito**: Estima el número de tokens y fragmentos para un libro en RAG, con un coste opcional.
    *   **Parámetros**: `book_id` (path), `per1k` (query, float, opcional), `max_tokens` (query, int, opcional), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `404 Not Found`, `500 Internal Server Error`.
*   **`GET /rag/estimate/category/{category_name}`**:
    *   **Propósito**: Estima tokens y fragmentos para todos los libros de una categoría en RAG, con coste opcional.
    *   **Parámetros**: `category_name` (path), `per1k` (query, float, opcional), `max_tokens` (query, int, opcional), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `404 Not Found`, `500 Internal Server Error`.
*   **`GET /rag/estimate/all`**:
    *   **Propósito**: Estima tokens y fragmentos para todos los libros de la biblioteca en RAG, con coste opcional.
    *   **Parámetros**: `per1k` (query, float, opcional), `max_tokens` (query, int, opcional), `db` (dependencia).
    *   **Cuerpo de la solicitud**: Ninguno.
    *   **Respuestas**: `200 OK` (dict), `500 Internal Server Error`.

### `backend/__init__.py`

Un archivo `__init__.py` vacío que simplemente marca el directorio `backend` como un paquete Python. El `__all__ = []` indica que no hay módulos o nombres específicos que deban ser expuestos cuando se use `from backend import *`.

## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

El componente raíz de la aplicación React. Configura el enrutamiento y la estructura básica del layout.

*   **Propósito**: Orquestar la aplicación React, manejar la navegación entre diferentes vistas y renderizar el encabezado y el contenido principal.
*   **Estado**: Ninguno propio.
*   **Propiedades**: Ninguna.
*   **Efectos**: Ninguno directo.
*   **Interacciones**: Utiliza `react-router-dom` para manejar la navegación basada en URL. El `Header` siempre está presente, y las `Routes` cambian el contenido de `App-content`.
*   **Comunicación con Backend**: Ninguna directa, se delega a los componentes de vista.

### `frontend/src/index.js`

Punto de entrada principal de la aplicación React, donde se monta el componente `App` en el DOM.

*   **Propósito**: Inicializar la aplicación React y renderizar el componente `App` en el elemento HTML con el ID 'root'.
*   **`React.StrictMode`**: Habilita comprobaciones adicionales y advertencias para el modo de desarrollo de React.
*   **`reportWebVitals()`**: Función para medir el rendimiento de la aplicación (Web Vitals).

### `frontend/src/config.js`

Define la URL base para el backend de la API.

*   **Propósito**: Centralizar la configuración de la URL del API, permitiendo que sea fácilmente configurable a través de variables de entorno (`REACT_APP_API_URL`) para diferentes entornos (desarrollo, producción).
*   **Contenido**: Exporta una constante `API_URL`.

### `frontend/src/Header.js`

Componente que renderiza el encabezado de la aplicación, incluyendo el título, el contador de libros y el menú de navegación.

*   **Propósito**: Proporcionar una barra de navegación consistente y mostrar información clave como el número total de libros.
*   **Estado**:
    *   `menuOpen`: Booleano para controlar la visibilidad del menú hamburguesa en móviles.
    *   `bookCount`: Entero que almacena el número total de libros.
    *   `errorMessage`: String para mostrar errores al cargar el contador.
*   **Propiedades**: Ninguna.
*   **Efectos**:
    *   `useEffect` al montar: Llama a `fetchBookCount` para obtener el número de libros de la API.
    *   `setInterval`: Re-obtiene el contador de libros periódicamente (cada 10 minutos).
*   **Interacciones**:
    *   `handleLinkClick`: Cierra el menú en móviles al hacer clic en un enlace.
    *   Botón de hamburguesa: Alterna el estado `menuOpen`.
*   **Comunicación con Backend**: Realiza una solicitud GET a `/books/count` para obtener el número de libros.

### `frontend/src/LibraryView.js`

La vista principal de la aplicación, que muestra la colección de libros en la biblioteca.

*   **Propósito**: Listar libros, permitir búsquedas y filtrados, y ofrecer acciones como editar, eliminar, leer y convertir libros.
*   **Estado**:
    *   `books`: Array de objetos libro.
    *   `searchTerm`: String para el campo de búsqueda.
    *   `error`: String para mensajes de error.
    *   `loading`: Booleano para indicar si los libros están cargando.
    *   `isMobile`: Booleano para adaptar la UI a dispositivos móviles.
    *   `editingBook`: Objeto `Book` si hay un libro editándose en el modal.
    *   `convertingId`: ID del libro que se está convirtiendo a PDF.
*   **Propiedades**: Ninguna.
*   **Efectos**:
    *   `useDebounce`: Retrasa la ejecución de la búsqueda para evitar llamadas excesivas a la API.
    *   `useEffect` (para `fetchBooks`): Se activa cuando cambia `debouncedSearchTerm` o `searchParams`, volviendo a cargar los libros de la API.
    *   `useEffect` (para `handleResize`): Escucha los cambios en el tamaño de la ventana para adaptar la UI móvil.
*   **Interacciones**:
    *   `handleAuthorClick`, `handleCategoryClick`: Filtran los libros por autor o categoría.
    *   `setSearchTerm`: Actualiza el término de búsqueda.
    *   `handleDeleteBook`: Elimina un libro (con confirmación).
    *   `handleConvertToPdf`: Convierte un EPUB a PDF (con confirmación), añade el PDF a la biblioteca.
    *   `handleEditClick`: Abre el modal de edición para un libro.
    *   `handleCloseModal`: Cierra el modal de edición.
    *   `handleBookUpdated`: Actualiza la lista de libros después de editar uno.
*   **Comunicación con Backend**:
    *   `GET /books/`: Para obtener la lista de libros (con filtros `category`, `search`, `author`).
    *   `DELETE /books/{book_id}`: Para eliminar un libro.
    *   `POST /api/books/{book_id}/convert`: Para convertir un EPUB a PDF.
    *   `PUT /books/{book_id}`: Para actualizar los detalles de un libro (llamado desde `EditBookModal`).
    *   `GET /books/download/{book_id}`: Para descargar o abrir libros.

### `frontend/src/UploadView.js`

Permite a los usuarios subir uno o varios archivos de libros (PDF o EPUB) al servidor.

*   **Propósito**: Facilitar la adición de nuevos libros a la biblioteca, con seguimiento del estado de subida y análisis por parte de la IA.
*   **Estado**:
    *   `filesToUpload`: Array de objetos `{ file, status, message }` para cada archivo seleccionado.
    *   `isUploading`: Booleano para indicar si hay archivos en proceso de subida.
*   **Propiedades**: Ninguna.
*   **Efectos**: `useRef` para `fileInputRef` para gestionar el input del archivo.
*   **Interacciones**:
    *   `handleFileChange`: Añade archivos seleccionados a la lista `filesToUpload`.
    *   `handleDrop`, `handleDragOver`: Implementan la funcionalidad de "arrastrar y soltar" archivos.
    *   `handleUpload`: Itera sobre `filesToUpload`, sube cada archivo y actualiza su estado.
    *   `handleReset`: Limpia la lista de archivos y el input.
    *   Botón "Ir a la Biblioteca": Navega a la vista principal.
*   **Comunicación con Backend**: `POST /upload-book/` para subir cada archivo de libro.

### `frontend/src/CategoriesView.js`

Muestra una lista de todas las categorías de libros disponibles en la biblioteca.

*   **Propósito**: Ofrecer una forma de explorar los libros por categoría.
*   **Estado**:
    *   `categories`: Array de strings con los nombres de las categorías.
    *   `error`: String para mensajes de error.
    *   `loading`: Booleano para indicar si las categorías están cargando.
*   **Propiedades**: Ninguna.
*   **Efectos**: `useEffect` al montar para llamar a `fetchCategories`.
*   **Interacciones**:
    *   Cada categoría es un `Link` que lleva a la `LibraryView` filtrada por esa categoría.
*   **Comunicación con Backend**: `GET /categories/` para obtener la lista de categorías.

### `frontend/src/ErrorBoundary.js`

Un componente React de "Error Boundary" genérico.

*   **Propósito**: Capturar errores JavaScript en cualquier parte de su árbol de componentes hijo, registrarlos y mostrar una interfaz de usuario de reserva en lugar de una pantalla en blanco.
*   **Estado**:
    *   `hasError`: Booleano, true si se ha capturado un error.
    *   `error`: El objeto error capturado.
*   **Métodos del ciclo de vida**:
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para indicar que ha ocurrido un error.
    *   `componentDidCatch(error, info)`: Registra la información del error.
*   **Render**: Muestra un mensaje de error si `hasError` es true, de lo contrario renderiza los `children` normales.

### `frontend/src/EditBookModal.js`

Componente modal para editar el título, autor y portada de un libro existente.

*   **Propósito**: Proporcionar una interfaz de usuario para modificar los metadatos de un libro.
*   **Estado**:
    *   `title`: String, el título actual del libro en el formulario.
    *   `author`: String, el autor actual del libro en el formulario.
    *   `coverImage`: Objeto `File`, la nueva imagen de portada seleccionada (o `null`).
    *   `isSaving`: Booleano, indica si los cambios se están guardando.
*   **Propiedades**:
    *   `book`: Objeto `Book` que se va a editar.
    *   `onClose`: Función para cerrar el modal.
    *   `onBookUpdated`: Función callback para notificar a la vista padre que el libro se ha actualizado.
*   **Efectos**: `useEffect` para inicializar el título y autor del estado con los valores del `book` prop cuando este cambia.
*   **Interacciones**:
    *   `handleSubmit`: Envía los datos actualizados al backend.
    *   Botones "Cancelar" y "Guardar Cambios".
*   **Comunicación con Backend**: `PUT /books/{book_id}` para actualizar los detalles del libro.

### `frontend/src/ToolsView.js`

Vista que aloja herramientas auxiliares para la gestión de la biblioteca, como un convertidor de EPUB a PDF.

*   **Propósito**: Agrupar utilidades que extienden la funcionalidad de la aplicación.
*   **`EpubToPdfConverter` (Subcomponente)**:
    *   **Propósito**: Permitir al usuario subir un archivo EPUB y descargarlo convertido a PDF.
    *   **Estado**: `selectedFile`, `message`, `isLoading`.
    *   **Interacciones**: Selección de archivo, arrastrar y soltar, botón "Convertir a PDF".
    *   **Comunicación con Backend**: `POST /tools/convert-epub-to-pdf`.
*   **Estado de `ToolsView`**: Ninguno propio.
*   **Propiedades**: Ninguna.
*   **Efectos**: Ninguno.
*   **Interacciones**: Ninguna directa, se delega a los subcomponentes.
*   **Comunicación con Backend**: Ninguna directa, se delega a los subcomponentes.

### `frontend/src/ReaderView.js`

Un componente para la visualización de archivos EPUB dentro del navegador.

*   **Propósito**: Proporcionar una experiencia de lectura para los archivos EPUB de la biblioteca.
*   **Estado**:
    *   `location`: String que representa la ubicación actual en el EPUB (EPUB CFI).
    *   `epubData`: Objeto `ArrayBuffer` que contiene los datos binarios del EPUB.
    *   `isLoading`: Booleano para indicar si el libro está cargando.
    *   `error`: String para mensajes de error.
*   **Propiedades**: Ninguna, utiliza `useParams` para obtener `bookId` de la URL.
*   **Efectos**: `useEffect` al montar para `fetchBookData`, que obtiene el EPUB del backend.
*   **Interacciones**: `locationChanged` callback para actualizar la ubicación del lector.
*   **Comunicación con Backend**: `GET /books/download/{bookId}` para obtener el contenido binario del EPUB.

### `frontend/src/RagView.js`

Interfaz para interactuar con el sistema de Recuperación Aumentada por Generación (RAG), permitiendo a los usuarios hacer preguntas sobre el contenido de un libro.

*   **Propósito**: Ofrecer una funcionalidad de "chat" con la IA basada en el contenido de los libros de la biblioteca.
*   **Estado**:
    *   `message`: Mensajes informativos para el usuario.
    *   `isLoading`: Booleano para indicar si la IA está generando una respuesta.
    *   `bookId`: ID del libro actualmente seleccionado para la conversación RAG.
    *   `chatHistory`: Array de objetos `{ sender, text }` para almacenar la conversación.
    *   `currentQuery`: La pregunta actual que el usuario está escribiendo.
    *   `libraryBooks`: Lista de libros de la biblioteca para seleccionar.
    *   `selectedLibraryId`: ID del libro seleccionado de la lista de la biblioteca.
    *   `libStatus`: Estado de indexación RAG del libro seleccionado (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy`: Booleano para bloquear acciones de indexación/reindexación.
    *   `refreshing`: Booleano para indicar un refresco de estado (no bloqueante).
    *   `searchTerm`: Término de búsqueda para libros de la biblioteca.
    *   `searching`: Booleano para indicar si se está buscando libros.
    *   `searchResults`: Resultados de la búsqueda de libros.
    *   `resultsOpen`: Booleano para controlar la visibilidad de los resultados de búsqueda.
    *   `mode`: Modo de respuesta de la IA ("strict", "balanced", "open").
    *   `selectedBook`: Detalles completos del libro seleccionado.
*   **Propiedades**: Ninguna.
*   **Efectos**:
    *   `useEffect` (para `chatHistory`, `isLoading`): Auto-scroll al final del chat.
    *   `useEffect` (al montar): Carga la lista de `libraryBooks`.
    *   `useEffect` (para `searchTerm`): Realiza una búsqueda "debounced" de libros.
    *   `useEffect` (para `selectedLibraryId`): Comprueba automáticamente el estado RAG del libro seleccionado.
    *   `useRef`: Para el input del chat y el contenedor del historial de chat para el auto-scroll.
*   **Interacciones**:
    *   Entrada de búsqueda de libros: Para encontrar libros existentes en la biblioteca.
    *   Botones "Comprobar RAG", "Indexar antes de charlar", "Reindexar", "Chatear".
    *   Selección de `mode`: Para elegir la estrategia de respuesta de la IA.
    *   Formulario de chat: `handleQuerySubmit` envía la pregunta a la IA.
*   **Comunicación con Backend**:
    *   `GET /books/`: Para cargar la lista de libros de la biblioteca (y para la búsqueda).
    *   `GET /rag/status/{book_id}`: Para obtener el estado RAG de un libro.
    *   `POST /rag/index/{book_id}`: Para indexar un libro en RAG.
    *   `POST /rag/query/`: Para enviar consultas a la IA.

## 5. Flujo de Datos y API

El flujo de datos en "Mi Librería Inteligente" sigue un patrón cliente-servidor, con el frontend React consumiendo la API RESTful de FastAPI.

### Flujo Típico: Subida de un Nuevo Libro

1.  **Frontend (UploadView.js)**:
    *   El usuario selecciona archivos PDF/EPUB o los arrastra y suelta.
    *   `handleFileChange` / `handleDrop` actualiza el estado local (`filesToUpload`).
    *   Al hacer clic en "Subir", `handleUpload` se activa.
    *   Por cada archivo, crea un `FormData` y envía una solicitud `POST` a `/upload-book/`.

2.  **Backend (`main.py` - `upload_book` endpoint)**:
    *   FastAPI recibe el `UploadFile`.
    *   Guarda el archivo en el directorio `backend/books/`.
    *   Determina el tipo de archivo (PDF o EPUB).
    *   Llama a `process_pdf` o `process_epub` (en `main.py`):
        *   Extrae texto de las primeras páginas.
        *   Intenta extraer una imagen de portada y la guarda en `backend/static/covers/`.
    *   Llama a `analyze_with_gemini` (en `main.py`):
        *   Utiliza el texto extraído y el modelo Gemini para inferir título, autor y categoría.
    *   **Puerta de Calidad**: Si la IA no puede identificar el título y el autor, el archivo se elimina y se devuelve un error 422.
    *   Llama a `crud.create_book` (en `crud.py`):
        *   Guarda los metadatos del libro (título, autor, categoría, URL de portada, ruta de archivo) en la base de datos SQLite.
    *   Devuelve los datos del nuevo libro (incluyendo su `id`) al frontend.

3.  **Frontend (UploadView.js)**:
    *   Actualiza el estado de cada archivo (`status`, `message`).
    *   Si tiene éxito, el usuario es redirigido a `LibraryView` o puede añadir más libros.

### Flujo Típico: Conversación RAG (IA sobre Libros)

1.  **Frontend (RagView.js)**:
    *   El usuario busca o selecciona un libro existente de su biblioteca.
    *   Al seleccionar, `useEffect` llama a `checkLibraryStatus` para obtener el estado RAG del libro (`GET /rag/status/{book_id}`).
    *   Si el libro no está indexado, el usuario hace clic en "Indexar antes de charlar".
    *   Si ya está indexado (o después de indexar), el usuario escribe una pregunta y la envía. `handleQuerySubmit` se activa.
    *   Envía una solicitud `POST` a `/rag/query/` con la pregunta (`query`), el `book_id` y el `mode`.

2.  **Backend (`main.py` - `index_existing_book_for_rag` / `query_rag_endpoint`)**:
    *   **Para Indexación**:
        *   El endpoint `POST /rag/index/{book_id}` recupera el libro de la BD.
        *   Llama a `rag.process_book_for_rag` (en `rag.py`):
            *   Extrae texto completo del libro (`extract_text`).
            *   Divide el texto en fragmentos (`chunk_text`).
            *   Genera embeddings para cada fragmento (`get_embedding`).
            *   Almacena los fragmentos y sus embeddings en ChromaDB.
        *   Devuelve un mensaje de éxito.
    *   **Para Consulta**:
        *   El endpoint `POST /rag/query/` recupera los metadatos del libro desde la BD.
        *   Llama a `rag.query_rag` (en `rag.py`):
            *   Genera un embedding de la consulta del usuario.
            *   Busca los fragmentos más relevantes en ChromaDB para el `book_id` dado.
            *   Construye un prompt para el modelo Gemini incluyendo la consulta, los fragmentos relevantes, metadatos del libro y contexto de la biblioteca.
            *   Utiliza el modelo Gemini para generar una respuesta.
        *   Devuelve la respuesta de la IA.

3.  **Frontend (RagView.js)**:
    *   Añade la pregunta del usuario y la respuesta de la IA al historial del chat (`chatHistory`).
    *   La UI se desplaza automáticamente para mostrar los nuevos mensajes.

### Resumen de Endpoints de la API (referencia detallada en la sección 3)

| Método | Endpoint                             | Descripción                                                                       |
| :----- | :----------------------------------- | :-------------------------------------------------------------------------------- |
| `POST` | `/api/books/{book_id}/convert`       | Convierte un EPUB existente a PDF, añadiéndolo como nuevo libro.                |
| `POST` | `/tools/convert-epub-to-pdf`         | Herramienta para convertir EPUB a PDF subido temporalmente, con descarga.          |
| `POST` | `/upload-book/`                      | Sube y procesa un libro (PDF/EPUB), extrayendo metadatos con IA.                  |
| `GET`  | `/books/`                            | Lista libros, con filtros por categoría, búsqueda o autor.                          |
| `PUT`  | `/books/{book_id}`                   | Actualiza título, autor y/o portada de un libro.                                  |
| `GET`  | `/books/count`                       | Devuelve el número total de libros.                                               |
| `GET`  | `/books/search/`                     | Busca libros por título parcial.                                                  |
| `GET`  | `/categories/`                       | Lista todas las categorías únicas.                                                |
| `DELETE` | `/books/{book_id}`                 | Elimina un libro y sus archivos.                                                  |
| `DELETE` | `/categories/{category_name}`      | Elimina todos los libros de una categoría y sus archivos.                         |
| `GET`  | `/books/download/{book_id}`          | Descarga o abre el archivo de un libro.                                           |
| `POST` | `/rag/upload-book/`                  | (Deprecado en UI) Sube un libro para RAG.                                         |
| `POST` | `/rag/query/`                        | Realiza una consulta RAG sobre un libro.                                          |
| `POST` | `/rag/index/{book_id}`               | Indexa un libro existente en RAG.                                                 |
| `GET`  | `/rag/status/{book_id}`              | Estado de indexación RAG de un libro.                                             |
| `POST` | `/rag/reindex/category/{category_name}` | (Re)indexa libros de una categoría en RAG.                                     |
| `POST` | `/rag/reindex/all`                   | (Re)indexa todos los libros en RAG.                                               |
| `GET`  | `/rag/estimate/book/{book_id}`       | Estima tokens/fragmentos y coste para un libro en RAG.                            |
| `GET`  | `/rag/estimate/category/{category_name}` | Estima tokens/fragmentos y coste para libros de una categoría en RAG.         |
| `GET`  | `/rag/estimate/all`                  | Estima tokens/fragmentos y coste para todos los libros en RAG.                    |

---

Este documento abarca los componentes clave del proyecto "Mi Librería Inteligente", proporcionando una visión técnica profunda de su funcionamiento, desde la estructura de archivos hasta las interacciones de los usuarios con las funcionalidades del backend.
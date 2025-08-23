```markdown
# Documentación del Proyecto: Mi Librería Inteligente

"Mi Librería Inteligente" es una aplicación web diseñada para gestionar, organizar y permitir la interacción avanzada con una colección de libros digitales. Combina una interfaz de usuario moderna con un potente backend que incorpora capacidades de Inteligencia Artificial para el análisis de contenido, la gestión de documentos y la interacción conversacional basada en los libros de la biblioteca.

## 1. Descripción General del Proyecto

Mi Librería Inteligente es una plataforma que permite a los usuarios:
*   Subir libros en formato PDF y EPUB.
*   Organizar automáticamente los libros utilizando IA (Google Gemini) para extraer títulos, autores y categorías.
*   Buscar y filtrar libros por título, autor y categoría.
*   Leer libros EPUB directamente en el navegador.
*   Descargar libros.
*   Convertir archivos EPUB a PDF.
*   Interactuar conversacionalmente con el contenido de los libros mediante un sistema de Recuperación Aumentada por Generación (RAG), permitiendo a la IA responder preguntas específicas sobre los textos almacenados.

La aplicación sigue una arquitectura de microservicios con un frontend y un backend claramente separados:

*   **Frontend**: Desarrollado con **React**, proporciona la interfaz de usuario interactiva y se comunica con el backend a través de llamadas a la API.
*   **Backend**: Construido con **FastAPI** (Python), gestiona la lógica de negocio, la interacción con la base de datos, el procesamiento de archivos, la integración con la IA (Google Gemini y ChromaDB para RAG) y sirve la API para el frontend.
*   **Base de Datos**: Utiliza **SQLite** como base de datos relacional para almacenar los metadatos de los libros.
*   **Vector Database (RAG)**: Emplea **ChromaDB** para almacenar los embeddings de los chunks de texto de los libros, facilitando la recuperación de información relevante para las consultas de IA.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales: `backend/` para la lógica del servidor y `frontend/src/` para la aplicación de React.

```
.
├── backend/
│   ├── alembic/                    # Migraciones de base de datos SQLAlchemy
│   │   ├── versions/               # Scripts de versión de las migraciones
│   │   └── env.py                  # Entorno de configuración de Alembic
│   ├── books/                      # Directorio para almacenar los archivos de libros subidos
│   ├── crud.py                     # Operaciones CRUD para la base de datos
│   ├── database.py                 # Configuración de la base de datos SQLAlchemy
│   ├── main.py                     # Aplicación principal de FastAPI y endpoints de la API
│   ├── models.py                   # Modelos de base de datos SQLAlchemy
│   ├── rag.py                      # Lógica de Retrieval Augmented Generation (RAG)
│   ├── schemas.py                  # Modelos de datos Pydantic para validación y serialización
│   ├── static/                     # Archivos estáticos servidos por FastAPI
│   │   └── covers/                 # Portadas de libros extraídas
│   ├── temp_books/                 # Archivos temporales, como PDFs convertidos
│   ├── tests/                      # Pruebas unitarias e integración del backend
│   ├── tests_curated/              # Pruebas adicionales y/o curadas del backend
│   └── utils.py                    # Funciones de utilidad (ej. configuración de GenAI)
│
├── frontend/
│   ├── public/                     # Archivos públicos para la aplicación React
│   ├── src/                        # Código fuente de la aplicación React
│   │   ├── App.css                 # Estilos globales de la aplicación
│   │   ├── App.js                  # Componente principal de la aplicación
│   │   ├── CategoriesView.css      # Estilos para CategoriesView
│   │   ├── CategoriesView.js       # Componente para ver categorías
│   │   ├── config.js               # Configuración de la URL de la API
│   │   ├── ErrorBoundary.js        # Componente para manejo de errores de UI
│   │   ├── Header.css              # Estilos para Header
│   │   ├── Header.js               # Componente de encabezado y navegación
│   │   ├── index.css               # Estilos base
│   │   ├── index.js                # Punto de entrada de la aplicación React
│   │   ├── LibraryView.css         # Estilos para LibraryView
│   │   ├── LibraryView.js          # Componente para la vista principal de la biblioteca
│   │   ├── RagView.css             # Estilos para RagView
│   │   ├── RagView.js              # Componente para la interacción RAG con libros
│   │   ├── ReaderView.css          # Estilos para ReaderView
│   │   ├── ReaderView.js           # Componente para leer EPUBs
│   │   ├── reportWebVitals.js      # Medición de rendimiento de React
│   │   ├── ToolsView.css           # Estilos para ToolsView
│   │   └── ToolsView.js            # Componente para herramientas (ej. conversión EPUB a PDF)
│   └── package.json                # Dependencias y scripts de React
│
├── .env.example                    # Ejemplo de archivo de variables de entorno
└── README.md                       # Archivo README del proyecto
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/schemas.py`

**Propósito**: Define los modelos de datos (schemas) utilizando Pydantic. Estos modelos se usan para validar las solicitudes (requests) entrantes a la API, serializar las respuestas (responses) salientes y proporcionar una clara estructura de datos.

**Clases Principales**:

*   **`BookBase(BaseModel)`**:
    *   **Propósito**: Esquema base para los datos de un libro, sin el ID.
    *   **Campos**:
        *   `title (str)`: Título del libro.
        *   `author (str)`: Autor del libro.
        *   `category (str)`: Categoría a la que pertenece el libro.
        *   `cover_image_url (str | None)`: URL opcional de la imagen de portada.
        *   `file_path (str)`: Ruta local del archivo del libro.

*   **`Book(BookBase)`**:
    *   **Propósito**: Esquema completo de un libro, incluyendo el ID de la base de datos.
    *   **Campos**:
        *   `id (int)`: Identificador único del libro en la base de datos.
    *   **`Config`**: Habilita `from_attributes = True` para compatibilidad con SQLAlchemy (Pydantic v2).

*   **`ConversionResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta de una conversión de archivo.
    *   **Campos**:
        *   `download_url (str)`: URL donde se puede descargar el archivo convertido.

*   **`RagUploadResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta de la carga/indexación de un libro para RAG.
    *   **Campos**:
        *   `book_id (str)`: ID del libro que ha sido procesado para RAG.
        *   `message (str)`: Mensaje de estado de la operación.

*   **`RagQuery(BaseModel)`**:
    *   **Propósito**: Esquema para la consulta (query) al sistema RAG.
    *   **Campos**:
        *   `query (str)`: La pregunta del usuario.
        *   `book_id (str)`: El ID del libro sobre el que se realiza la consulta.
        *   `mode (str | None)`: Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`). Opcional, por defecto 'balanced'.

*   **`RagQueryResponse(BaseModel)`**:
    *   **Propósito**: Esquema para la respuesta de una consulta RAG.
    *   **Campos**:
        *   `response (str)`: La respuesta generada por la IA.

### `backend/models.py`

**Propósito**: Define los modelos de la base de datos SQLAlchemy que mapean las tablas de la base de datos a objetos Python.

**Clases Principales**:

*   **`Book(Base)`**:
    *   **Propósito**: Representa la tabla `books` en la base de datos.
    *   **`__tablename__ = "books"`**: Nombre de la tabla en la base de datos.
    *   **`__table_args__ = {'extend_existing': True}`**: Permite redefinir la tabla en entornos de pruebas.
    *   **Columnas**:
        *   `id (Integer, primary_key=True, index=True)`: Identificador único del libro. Clave primaria e indexado.
        *   `title (String, index=True)`: Título del libro. Indexado para búsquedas.
        *   `author (String, index=True)`: Autor del libro. Indexado para búsquedas.
        *   `category (String, index=True)`: Categoría del libro. Indexado para búsquedas.
        *   `cover_image_url (String, nullable=True)`: URL de la imagen de portada. Puede ser nulo.
        *   `file_path (String, unique=True)`: Ruta absoluta al archivo del libro en el sistema de archivos. Debe ser único.

### `backend/database.py`

**Propósito**: Configura la conexión a la base de datos y proporciona las utilidades necesarias para interactuar con ella utilizando SQLAlchemy.

**Detalles**:
*   Utiliza **SQLite** como motor de base de datos.
*   El archivo de la base de datos (`library.db`) se ubica en la raíz del proyecto.
*   `SQLALCHEMY_DATABASE_URL`: URL de conexión a la base de datos.
*   `engine`: Objeto `Engine` de SQLAlchemy, el punto de partida para interactuar con la base de datos. `connect_args={"check_same_thread": False}` es necesario para SQLite en entornos multihilo como FastAPI.
*   `SessionLocal`: Una clase `sessionmaker` configurada para no autocomitear ni autoflushear, vinculada al `engine`. Las sesiones de base de datos se crearán a partir de esta clase.
*   `Base`: Objeto `declarative_base()` de SQLAlchemy, que sirve como base para los modelos ORM.

### `backend/crud.py`

**Propósito**: Contiene funciones para realizar operaciones básicas de base de datos (Create, Read, Update, Delete) sobre el modelo `Book`. Estas funciones encapsulan la lógica de interacción con SQLAlchemy.

**Funciones Principales**:

*   **`get_book_by_path(db: Session, file_path: str)`**:
    *   **Lógica**: Busca un libro en la base de datos por su ruta de archivo.
    *   **Parámetros**: `db` (sesión de DB), `file_path` (ruta del archivo).
    *   **Retorno**: El objeto `Book` si se encuentra, `None` en caso contrario.

*   **`get_book_by_title(db: Session, title: str)`**:
    *   **Lógica**: Busca un libro por su título exacto.
    *   **Parámetros**: `db`, `title`.
    *   **Retorno**: El objeto `Book` si se encuentra, `None` en caso contrario.

*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**:
    *   **Lógica**: Busca libros por un título parcial (case-insensitive) con paginación.
    *   **Parámetros**: `db`, `title` (parte del título), `skip`, `limit`.
    *   **Retorno**: Una lista de objetos `Book` que coinciden.

*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**:
    *   **Lógica**: Recupera una lista de libros, permitiendo filtrar por categoría, autor o un término de búsqueda general (título, autor o categoría). Los resultados se ordenan por ID descendente.
    *   **Parámetros**: `db`, `category` (opcional), `search` (opcional, búsqueda en título, autor, categoría), `author` (opcional, búsqueda parcial de autor).
    *   **Retorno**: Una lista de objetos `Book`.

*   **`get_categories(db: Session) -> list[str]`**:
    *   **Lógica**: Obtiene una lista de todas las categorías únicas de libros, ordenadas alfabéticamente.
    *   **Parámetros**: `db`.
    *   **Retorno**: Una lista de cadenas de texto (nombres de categorías).

*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**:
    *   **Lógica**: Crea un nuevo registro de libro en la base de datos.
    *   **Parámetros**: `db`, `title`, `author`, `category`, `cover_image_url`, `file_path`.
    *   **Retorno**: El objeto `Book` recién creado.

*   **`delete_book(db: Session, book_id: int)`**:
    *   **Lógica**: Elimina un libro por su ID. También elimina los archivos asociados (libro y portada) del sistema de archivos.
    *   **Parámetros**: `db`, `book_id`.
    *   **Retorno**: El objeto `Book` eliminado si se encontró, `None` en caso contrario.

*   **`delete_books_by_category(db: Session, category: str)`**:
    *   **Lógica**: Elimina todos los libros de una categoría específica. También elimina los archivos asociados.
    *   **Parámetros**: `db`, `category`.
    *   **Retorno**: El número de libros eliminados.

*   **`get_books_count(db: Session) -> int`**:
    *   **Lógica**: Obtiene el número total de libros en la base de datos.
    *   **Parámetros**: `db`.
    *   **Retorno**: Un entero que representa el recuento de libros.

### `backend/utils.py`

**Propósito**: Proporciona funciones de utilidad general, principalmente para la configuración de APIs de IA.

**Funciones Principales**:

*   **`configure_genai()`**:
    *   **Lógica**: Carga las variables de entorno y configura la API de Google Generative AI (Gemini) utilizando la clave `GOOGLE_API_KEY` o `GEMINI_API_KEY`. Lanza un `ValueError` si no se encuentra ninguna clave.
    *   **Parámetros**: Ninguno.
    *   **Retorno**: Ninguno.

### `backend/rag.py`

**Propósito**: Implementa la lógica principal para el sistema de Recuperación Aumentada por Generación (RAG). Esto incluye la extracción de texto de documentos, la segmentación (chunking), la generación de embeddings y el almacenamiento/recuperación de información en ChromaDB para alimentar a un modelo generativo.

**Estado Global y Configuración**:
*   `_initialized`: Bandera para asegurar la inicialización única.
*   `_collection`: Instancia de ChromaDB para la colección de embeddings.
*   `_ai_enabled`: Indica si las funciones de IA están habilitadas (depende de `DISABLE_AI` y API Key).
*   `EMBEDDING_MODEL`: Modelo de Gemini para generar embeddings (configurable via `GEMINI_EMBEDDING_MODEL`).
*   `GENERATION_MODEL`: Modelo de Gemini para generación de texto (configurable via `GEMINI_GENERATION_MODEL`).

**Funciones Principales**:

*   **`_ensure_init()`**:
    *   **Lógica**: Inicializa `_ai_enabled` y configura `genai` si las claves de API están presentes y `DISABLE_AI` no está activado. También inicializa el cliente `chromadb.PersistentClient` y obtiene o crea la colección `book_rag_collection`. Se asegura de que estos componentes se configuren solo una vez.
    *   **Parámetros**: Ninguno.
    *   **Retorno**: Ninguno.

*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**:
    *   **Lógica**: Genera un vector de embedding para el texto dado utilizando el modelo `EMBEDDING_MODEL`. Si la IA está deshabilitada, devuelve un embedding dummy.
    *   **Parámetros**: `text` (el texto a embeber), `task_type` (tipo de tarea para el embedding).
    *   **Retorno**: Una lista de floats que representa el embedding.

*   **`extract_text_from_pdf(file_path: str)`**:
    *   **Lógica**: Extrae texto de un archivo PDF utilizando `PyPDF2`.
    *   **Parámetros**: `file_path`.
    *   **Retorno**: El texto extraído como una cadena.

*   **`extract_text_from_epub(file_path: str)`**:
    *   **Lógica**: Extrae texto de un archivo EPUB utilizando `ebooklib` y `BeautifulSoup`.
    *   **Parámetros**: `file_path`.
    *   **Retorno**: El texto extraído como una cadena.

*   **`extract_text(file_path: str)`**:
    *   **Lógica**: Función unificada para extraer texto, soporta PDF y EPUB. Lanza un `ValueError` para tipos no soportados.
    *   **Parámetros**: `file_path`.
    *   **Retorno**: El texto extraído.

*   **`chunk_text(text: str, max_tokens: int = 1000)`**:
    *   **Lógica**: Divide el texto en fragmentos más pequeños (chunks) basándose en un número máximo de tokens, utilizando `tiktoken` para la estimación de tokens.
    *   **Parámetros**: `text`, `max_tokens` (tamaño máximo de chunk).
    *   **Retorno**: Una lista de cadenas, cada una un chunk de texto.

*   **`_has_index_for_book(book_id: str)`**:
    *   **Lógica**: Comprueba si ya existen vectores de embeddings para un `book_id` dado en la colección ChromaDB.
    *   **Parámetros**: `book_id`.
    *   **Retorno**: `True` si existen, `False` en caso contrario.

*   **`delete_book_from_rag(book_id: str)`**:
    *   **Lógica**: Elimina todos los vectores de embeddings asociados a un `book_id` de ChromaDB.
    *   **Parámetros**: `book_id`.
    *   **Retorno**: Ninguno.

*   **`get_index_count(book_id: str)`**:
    *   **Lógica**: Devuelve el número de vectores almacenados para un `book_id` específico en ChromaDB.
    *   **Parámetros**: `book_id`.
    *   **Retorno**: Un entero.

*   **`has_index(book_id: str)`**:
    *   **Lógica**: Función pública para verificar si un libro tiene un índice RAG. (Alias para `get_index_count(book_id) > 0`).
    *   **Parámetros**: `book_id`.
    *   **Retorno**: `True` o `False`.

*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**:
    *   **Lógica**: Función principal de indexación RAG. Extrae texto, lo segmenta en chunks, genera embeddings para cada chunk y los almacena en ChromaDB junto con metadatos. Si `force_reindex` es `True`, elimina cualquier índice existente primero.
    *   **Parámetros**: `file_path` (ruta al archivo del libro), `book_id` (ID del libro), `force_reindex` (booleano).
    *   **Retorno**: Ninguno.

*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**:
    *   **Lógica**: Estima el recuento total de tokens y el número de chunks que se generarían para un archivo dado.
    *   **Parámetros**: `file_path`, `max_tokens`.
    *   **Retorno**: Un diccionario con `tokens` y `chunks`.

*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**:
    *   **Lógica**: Estima el recuento total de tokens y chunks para una lista de archivos.
    *   **Parámetros**: `file_paths`, `max_tokens`.
    *   **Retorno**: Un diccionario con `tokens`, `chunks` y `files` (archivos procesados exitosamente).

*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**:
    *   **Lógica**: Realiza una consulta al sistema RAG. Genera un embedding para la pregunta, recupera los chunks más relevantes del libro (en ChromaDB), construye un prompt con el contexto y la metadata/información de la librería, y utiliza el modelo generativo de Gemini para obtener una respuesta. El parámetro `mode` controla cómo se integra el conocimiento del libro con el conocimiento general de la IA.
    *   **Parámetros**: `query` (pregunta del usuario), `book_id` (ID del libro), `mode` (`strict`, `balanced`, `open`), `metadata` (metadatos del libro, opcional), `library` (contexto adicional de la librería, opcional).
    *   **Retorno**: La respuesta generada por la IA como una cadena.

### `backend/main.py`

**Propósito**: Es el corazón de la aplicación FastAPI. Define y expone todos los endpoints de la API, maneja las solicitudes HTTP, coordina las operaciones entre los módulos `crud`, `models`, `rag`, y gestiona el procesamiento de archivos y la integración con la IA.

**Configuración Inicial**:
*   Carga variables de entorno (`.env`).
*   Configura la API de Gemini si `AI_ENABLED` es `True`.
*   Crea todas las tablas de la base de datos definidas en `models.py` (si no existen).
*   Define rutas absolutas para directorios de archivos (`STATIC_DIR_FS`, `STATIC_COVERS_DIR_FS`, `TEMP_BOOKS_DIR_FS`, `BOOKS_DIR_FS`).
*   Configura el middleware **CORS** para permitir solicitudes desde orígenes específicos (configurable por `ALLOW_ORIGINS` y `ALLOW_ORIGIN_REGEX`).
*   Monta directorios estáticos para servir portadas y archivos temporales.

**Funciones de IA y Procesamiento (Internas/Auxiliares)**:

*   **`analyze_with_gemini(text: str) -> dict`**:
    *   **Lógica**: Envía las primeras páginas del texto de un libro a Google Gemini para que identifique el título, autor y categoría. Retorna un objeto JSON con estos datos. Si la IA está deshabilitada, devuelve valores "Desconocido". Incluye un "Quality Gate" para evitar errores si la IA no puede identificar nada.
    *   **Parámetros**: `text` (texto extraído del libro).
    *   **Retorno**: Un diccionario con `title`, `author`, `category`.

*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
    *   **Lógica**: Extrae texto de las primeras páginas de un PDF y busca una imagen de alta resolución que pueda ser la portada. Guarda la portada en `covers_dir_fs` y devuelve su URL.
    *   **Parámetros**: `file_path`, `covers_dir_fs` (ruta al directorio de portadas), `covers_url_prefix` (prefijo URL para portadas).
    *   **Retorno**: Un diccionario con el `text` extraído y la `cover_image_url` (si se encontró).

*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
    *   **Lógica**: Extrae texto de un EPUB y busca la imagen de portada (primero por metadatos, luego por nombre de archivo). Guarda la portada y devuelve su URL.
    *   **Parámetros**: `file_path`, `covers_dir_fs`, `covers_url_prefix`.
    *   **Retorno**: Un diccionario con el `text` extraído y la `cover_image_url` (si se encontró).

**Dependencias**:
*   **`get_db()`**: Dependencia que proporciona una sesión de base de datos (`SessionLocal`) y asegura que se cierre correctamente después de la solicitud.

**Endpoints de la API**:

*   **`POST /upload-book/`**
    *   **Propósito**: Sube un nuevo archivo de libro (PDF/EPUB), lo procesa con IA para extraer metadatos y lo guarda en la base de datos.
    *   **Solicitud**: `UploadFile` (archivo de libro).
    *   **Respuesta**: `schemas.Book` (el libro creado), o `HTTPException` si hay errores (ej. archivo duplicado, tipo no soportado, IA no identifica).

*   **`GET /books/`**
    *   **Propósito**: Obtiene una lista de libros, con opciones de filtrado por categoría, término de búsqueda general y autor.
    *   **Solicitud**: Parámetros de query `category`, `search`, `author` (opcionales).
    *   **Respuesta**: `List[schemas.Book]`.

*   **`GET /books/count`**
    *   **Propósito**: Devuelve el número total de libros en la biblioteca.
    *   **Solicitud**: Ninguna.
    *   **Respuesta**: `int`.

*   **`GET /books/search/`**
    *   **Propósito**: Busca libros por un título parcial (case-insensitive) con paginación.
    *   **Solicitud**: Parámetro de query `title` (requerido), `skip`, `limit` (opcionales).
    *   **Respuesta**: `List[schemas.Book]`.

*   **`GET /categories/`**
    *   **Propósito**: Devuelve una lista de todas las categorías de libros únicas.
    *   **Solicitud**: Ninguna.
    *   **Respuesta**: `List[str]`.

*   **`DELETE /books/{book_id}`**
    *   **Propósito**: Elimina un libro específico por su ID de la base de datos, incluyendo sus archivos asociados y cualquier índice RAG.
    *   **Solicitud**: `book_id` (path parameter).
    *   **Respuesta**: `{"message": str}`.

*   **`DELETE /categories/{category_name}`**
    *   **Propósito**: Elimina todos los libros de una categoría específica, incluyendo sus archivos e índices RAG.
    *   **Solicitud**: `category_name` (path parameter).
    *   **Respuesta**: `{"message": str}`.

*   **`GET /books/download/{book_id}`**
    *   **Propósito**: Permite descargar el archivo original de un libro. Para PDFs, se intenta abrir `inline`; para EPUBs, se fuerza la descarga como adjunto.
    *   **Solicitud**: `book_id` (path parameter).
    *   **Respuesta**: `FileResponse`.

*   **`POST /tools/convert-epub-to-pdf`**
    *   **Propósito**: Convierte un archivo EPUB subido a PDF y proporciona una URL de descarga temporal para el PDF resultante. Utiliza `weasyprint`, `BeautifulSoup` y `zipfile`.
    *   **Solicitud**: `UploadFile` (archivo EPUB).
    *   **Respuesta**: `schemas.ConversionResponse`.

*   **`POST /rag/upload-book/`** *(Nota: Este endpoint parece existir en el código, pero el frontend no lo usa directamente. El flujo de RAG del frontend se centra en indexar libros ya subidos en la biblioteca.)*
    *   **Propósito**: Sube un archivo de libro, lo procesa para RAG y devuelve un `book_id` temporal para futuras consultas.
    *   **Solicitud**: `UploadFile`.
    *   **Respuesta**: `schemas.RagUploadResponse`.

*   **`POST /rag/query/`**
    *   **Propósito**: Envía una pregunta a la IA para obtener una respuesta basada en el contenido de un libro indexado para RAG.
    *   **Solicitud**: `schemas.RagQuery` (pregunta, ID del libro, modo).
    *   **Respuesta**: `schemas.RagQueryResponse`.

*   **`POST /rag/index/{book_id}`**
    *   **Propósito**: Indexa un libro ya existente en la base de datos para su uso con RAG.
    *   **Solicitud**: `book_id` (path parameter), `force` (query parameter, para forzar reindexación).
    *   **Respuesta**: `{"message": str, "book_id": str, "force": bool}`.

*   **`GET /rag/status/{book_id}`**
    *   **Propósito**: Comprueba el estado de indexación RAG de un libro (si está indexado y cuántos vectores tiene).
    *   **Solicitud**: `book_id` (path parameter).
    *   **Respuesta**: `{"book_id": str, "indexed": bool, "vector_count": int}`.

*   **`POST /rag/reindex/category/{category_name}`**
    *   **Propósito**: Reindexa todos los libros de una categoría específica en RAG.
    *   **Solicitud**: `category_name` (path parameter), `force` (query parameter).
    *   **Respuesta**: `{"category": str, "processed": int, "failed": list, "force": bool}`.

*   **`POST /rag/reindex/all`**
    *   **Propósito**: Reindexa todos los libros de la biblioteca en RAG.
    *   **Solicitud**: `force` (query parameter).
    *   **Respuesta**: `{"processed": int, "failed": list, "total": int, "force": bool}`.

*   **`GET /rag/estimate/book/{book_id}`**
    *   **Propósito**: Estima el número de tokens y chunks para un libro específico que se usarían en RAG, con una estimación opcional de costo.
    *   **Solicitud**: `book_id` (path parameter), `per1k` (costo por 1000 tokens, opcional), `max_tokens` (tamaño de chunk, opcional).
    *   **Respuesta**: Diccionario con `book_id`, `tokens`, `chunks`, `per1k`, `estimated_cost`.

*   **`GET /rag/estimate/category/{category_name}`**
    *   **Propósito**: Estima el número de tokens y chunks para todos los libros de una categoría, con costo opcional.
    *   **Solicitud**: `category_name` (path parameter), `per1k`, `max_tokens`.
    *   **Respuesta**: Diccionario con `category`, `tokens`, `chunks`, `files` (contados), `per1k`, `estimated_cost`.

*   **`GET /rag/estimate/all`**
    *   **Propósito**: Estima el número de tokens y chunks para todos los libros de la biblioteca, con costo opcional.
    *   **Solicitud**: `per1k`, `max_tokens`.
    *   **Respuesta**: Diccionario con `tokens`, `chunks`, `files` (contados), `per1k`, `estimated_cost`.

## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

**Propósito**: Es el componente raíz de la aplicación React. Configura el enrutamiento de la aplicación utilizando `react-router-dom` y renderiza el `Header` y las diferentes vistas (páginas) de la aplicación.

*   **Estado (State)**: Ninguno directo.
*   **Propiedades (Props)**: Ninguna.
*   **Efectos (Effects)**: Ninguno directo.
*   **Interacciones**: Define las rutas (`/`, `/upload`, `/etiquetas`, `/herramientas`, `/rag`, `/leer/:bookId`) y renderiza el componente de vista correspondiente para cada una.

### `frontend/src/Header.js`

**Propósito**: Muestra el título de la aplicación, el recuento total de libros y la navegación principal. Incluye un menú de hamburguesa para dispositivos móviles.

*   **Estado (State)**:
    *   `menuOpen (boolean)`: Controla la visibilidad del menú de navegación en móvil.
    *   `bookCount (int)`: Número total de libros en la biblioteca.
    *   `errorMessage (string)`: Mensaje de error si falla la obtención del recuento de libros.
*   **Propiedades (Props)**: Ninguna.
*   **Efectos (Effects)**:
    *   `useEffect`: Al montar el componente, realiza una solicitud GET a `/books/count` para obtener el número de libros. Se actualiza periódicamente (cada 10 minutos).
*   **Interacciones**:
    *   `handleLinkClick()`: Cierra el menú móvil al hacer clic en un enlace de navegación.
    *   Botón de hamburguesa: Toggles `menuOpen`.
    *   `NavLink`: Permite la navegación entre las diferentes vistas de la aplicación.

### `frontend/src/LibraryView.js`

**Propósito**: Muestra la lista de libros de la biblioteca en una cuadrícula, permitiendo buscar, filtrar por autor/categoría, eliminar libros y abrir/descargar archivos.

*   **Estado (State)**:
    *   `books (array)`: Lista de objetos libro a mostrar.
    *   `searchTerm (string)`: Término de búsqueda introducido por el usuario.
    *   `debouncedSearchTerm (string)`: Versión con debounce de `searchTerm` para evitar solicitudes excesivas al backend.
    *   `error (string)`: Mensaje de error si falla la carga de libros.
    *   `loading (boolean)`: Indica si los libros están cargando.
    *   `isMobile (boolean)`: Detecta si la vista es en un dispositivo móvil para adaptar la UI (ej. botón de descarga adicional).
*   **Propiedades (Props)**: Ninguna, utiliza `useSearchParams` para parámetros de URL.
*   **Efectos (Effects)**:
    *   `useEffect` (para `fetchBooks`): Se ejecuta cuando `debouncedSearchTerm` o `searchParams` cambian, para obtener libros filtrados/buscados del backend (`/books/`).
    *   `useEffect` (para `isMobile`): Detecta el tamaño de la ventana para establecer `isMobile`.
*   **Interacciones**:
    *   `useDebounce`: Hook personalizado para retrasar la búsqueda.
    *   `BookCover`: Componente auxiliar que muestra la portada del libro o un fallback genérico.
    *   `handleAuthorClick(author)`: Al hacer clic en el nombre de un autor, actualiza los `searchParams` para filtrar por ese autor.
    *   `handleCategoryClick(category)`: Al hacer clic en una categoría, actualiza los `searchParams` para filtrar por esa categoría.
    *   `handleDeleteBook(bookId)`: Elimina un libro del backend (`DELETE /books/{book_id}`) y lo retira de la UI.
    *   `input.search-bar`: Permite buscar libros por título, autor o categoría.
    *   Enlaces "Abrir PDF" / "Leer EPUB": Navegan a la vista del lector o descargan el archivo.

### `frontend/src/UploadView.js`

**Propósito**: Permite a los usuarios subir uno o varios archivos de libros (PDF o EPUB) para que sean procesados y añadidos a la biblioteca.

*   **Estado (State)**:
    *   `filesToUpload (array)`: Lista de objetos `{file, status, message}` para cada archivo seleccionado.
    *   `isUploading (boolean)`: Indica si hay archivos en proceso de subida.
*   **Propiedades (Props)**: Utiliza `useNavigate` para redirigir después de la subida.
*   **Efectos (Effects)**: Ninguno directo.
*   **Interacciones**:
    *   `handleFileChange(event)`: Añade archivos seleccionados desde el input a `filesToUpload`.
    *   `handleDrop(event)`, `handleDragOver(event)`: Implementan la funcionalidad de arrastrar y soltar archivos.
    *   `updateFileStatus(index, status, message)`: Actualiza el estado y mensaje de un archivo específico en la lista.
    *   `handleUpload()`: Itera sobre `filesToUpload`, enviando cada archivo al endpoint `/upload-book/` del backend. Muestra el progreso y resultado de cada subida.
    *   Botón "Ir a la Biblioteca": Disponible cuando todas las subidas han terminado, redirige a la vista principal.

### `frontend/src/CategoriesView.js`

**Propósito**: Muestra todas las categorías únicas de libros como enlaces, permitiendo al usuario hacer clic en una para ver los libros de esa categoría.

*   **Estado (State)**:
    *   `categories (array)`: Lista de cadenas de texto con los nombres de las categorías.
    *   `error (string)`: Mensaje de error si falla la carga de categorías.
    *   `loading (boolean)`: Indica si las categorías están cargando.
*   **Propiedades (Props)**: Ninguna.
*   **Efectos (Effects)**:
    *   `useEffect`: Al montar el componente, realiza una solicitud GET a `/categories/` para obtener la lista de categorías.
*   **Interacciones**:
    *   Cada categoría se renderiza como un `Link` que, al hacer clic, navega a la `LibraryView` con el parámetro de URL `category` correspondiente.

### `frontend/src/ToolsView.js`

**Propósito**: Actúa como un contenedor para diversas herramientas de la biblioteca. Actualmente, alberga el `EpubToPdfConverter`.

*   **Componentes Internos**:
    *   **`EpubToPdfConverter`**:
        *   **Propósito**: Permite a los usuarios subir un archivo EPUB y convertirlo a PDF.
        *   **Estado**: `selectedFile`, `message`, `isLoading`.
        *   **Efectos**: Ninguno directo.
        *   **Interacciones**:
            *   `handleFileChange(event)`: Almacena el archivo EPUB seleccionado.
            *   `handleDrop(event)`, `handleDragOver(event)`: Funcionalidad de arrastrar y soltar.
            *   `handleConvert()`: Envía el archivo EPUB al endpoint `/tools/convert-epub-to-pdf` del backend. Al recibir la URL de descarga, inicia la descarga del PDF.

### `frontend/src/ReaderView.js`

**Propósito**: Proporciona una interfaz para leer archivos EPUB directamente en el navegador utilizando la librería `react-reader`.

*   **Estado (State)**:
    *   `location (string)`: Guarda la ubicación actual en el EPUB (CFI) para reanudar la lectura.
    *   `epubData (ArrayBuffer)`: Contenido del archivo EPUB cargado desde el backend.
    *   `isLoading (boolean)`: Indica si el libro está cargando.
    *   `error (string)`: Mensaje de error si el libro no se puede cargar.
*   **Propiedades (Props)**:
    *   `bookId` (de `useParams`): El ID del libro EPUB a leer.
*   **Efectos (Effects)**:
    *   `useEffect`: Al montar el componente o cambiar `bookId`, realiza una solicitud GET a `/books/download/{bookId}` para obtener el contenido binario del EPUB.
*   **Interacciones**:
    *   `ReactReader`: Componente de terceros que renderiza el EPUB. Se le pasa el `epubData` y gestiona la navegación por el libro.
    *   `locationChanged`: Callback para actualizar la ubicación de lectura.

### `frontend/src/RagView.js`

**Propósito**: Proporciona una interfaz para la interacción conversacional (chat) con la IA sobre el contenido de un libro específico de la biblioteca, utilizando el sistema RAG.

*   **Estado (State)**:
    *   `message (string)`: Mensajes informativos para el usuario.
    *   `isLoading (boolean)`: Indica si la IA está generando una respuesta.
    *   `bookId (string)`: El ID del libro actualmente seleccionado para el chat RAG.
    *   `chatHistory (array)`: Lista de objetos `{sender: 'user'/'gemini', text: string}` que representan la conversación.
    *   `currentQuery (string)`: La pregunta actual del usuario.
    *   `libraryBooks (array)`: Lista de todos los libros de la biblioteca.
    *   `selectedLibraryId (string)`: El ID del libro seleccionado por el usuario en la interfaz.
    *   `libStatus (object)`: Objeto que contiene el estado de indexación RAG del libro seleccionado (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy (boolean)`: Bloquea las acciones de indexación/reindexación para evitar conflictos.
    *   `refreshing (boolean)`: Indica si se está refrescando el estado RAG.
    *   `searchTerm (string)`: Término para buscar libros en la biblioteca.
    *   `searching (boolean)`: Indica si se está realizando una búsqueda.
    *   `searchResults (array)`: Resultados de la búsqueda de libros.
    *   `resultsOpen (boolean)`: Controla la visibilidad de los resultados de búsqueda.
    *   `mode (string)`: Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`).
    *   `selectedBook (object)`: Objeto completo del libro seleccionado.
*   **Referencias (Refs)**:
    *   `inputRef`: Referencia al `textarea` del chat para enfocarlo.
    *   `chatHistoryRef`: Referencia al contenedor del historial de chat para auto-scroll.
*   **Memo (Memoized Values)**:
    *   `currentBook`: Calcula el libro actualmente seleccionado de forma eficiente.
    *   `chatReady`: Booleano que indica si el chat está listo para usarse.
*   **Efectos (Effects)**:
    *   `useEffect`: Carga la lista completa de libros de la biblioteca (`/books/`).
    *   `useEffect` (para `searchTerm`): Implementa una búsqueda con debounce para libros de la biblioteca.
    *   `useEffect` (para `chatHistory`, `isLoading`): Auto-scrolls el historial del chat.
    *   `useEffect` (para `selectedLibraryId`): Al cambiar el libro seleccionado, comprueba automáticamente su estado RAG (`/rag/status/{book_id}`).
*   **Interacciones**:
    *   Input de búsqueda: Permite buscar y seleccionar un libro de la biblioteca para RAG.
    *   Botones "Comprobar RAG", "Indexar", "Reindexar", "Chatear":
        *   `checkLibraryStatus()`: Consulta el backend (`/rag/status/{book_id}`) para ver si un libro ya está indexado.
        *   `indexLibraryBook(force)`: Envía una solicitud al backend (`/rag/index/{book_id}`) para indexar o reindexar un libro.
        *   Botón "Chatear": Habilita el cuadro de chat si el libro está indexado.
    *   Radio buttons de `mode`: Permiten al usuario elegir el comportamiento de la IA (estricto, equilibrado, abierto).
    *   Formulario de chat:
        *   `textarea`: Para que el usuario escriba su pregunta. Auto-ajusta la altura.
        *   `handleQuerySubmit(event)`: Envía la pregunta actual al endpoint `/rag/query/` del backend. Actualiza el historial de chat con la pregunta del usuario y la respuesta de la IA.

### `frontend/src/config.js`

**Propósito**: Centraliza la configuración de la URL base del backend, facilitando la adaptación a diferentes entornos (desarrollo, producción).

*   **Detalles**: Exporta `API_URL`, que toma su valor de la variable de entorno `REACT_APP_API_URL` o, si no está definida, usa `http://localhost:8001` por defecto.

## 5. Flujo de Datos y API

El flujo de datos en "Mi Librería Inteligente" se puede describir a través de los escenarios principales:

### 5.1 Carga de un Libro

1.  **Frontend (`UploadView.js`)**: El usuario selecciona uno o varios archivos (PDF/EPUB) a través de un input o arrastrando y soltando.
2.  **Solicitud API**: `UploadView` envía cada archivo como `multipart/form-data` a `POST /upload-book/`.
3.  **Backend (`main.py`)**:
    *   Recibe el archivo y lo guarda temporalmente.
    *   Determina el tipo de archivo (PDF/EPUB) y llama a `process_pdf()` o `process_epub()` para extraer texto y, si es posible, una imagen de portada.
    *   Llama a `analyze_with_gemini()` para enviar el texto extraído a Google Gemini y obtener el título, autor y categoría del libro.
    *   Realiza una "puerta de calidad": si la IA no pudo identificar el título ni el autor, se rechaza el libro y se elimina el archivo.
    *   Si el análisis es exitoso, llama a `crud.create_book()` para almacenar los metadatos del libro (título, autor, categoría, URL de portada, ruta del archivo) en la base de datos SQLite.
    *   Devuelve el objeto `schemas.Book` al frontend.
4.  **Frontend (`UploadView.js`)**: Actualiza el estado de la subida con éxito o error y muestra el título del libro añadido.

### 5.2 Visualización y Filtrado de la Biblioteca

1.  **Frontend (`LibraryView.js`, `CategoriesView.js`, `Header.js`)**:
    *   `Header` solicita el `bookCount` a `GET /books/count`.
    *   `LibraryView` o `CategoriesView` inician una solicitud para obtener la lista de libros o categorías.
2.  **Solicitud API**:
    *   `GET /books/` (con parámetros opcionales `category`, `search`, `author`).
    *   `GET /categories/`.
3.  **Backend (`main.py`)**:
    *   Para `/books/`: llama a `crud.get_books()` (o `crud.get_books_by_partial_title()`) con los filtros proporcionados.
    *   Para `/categories/`: llama a `crud.get_categories()`.
    *   Recupera los datos de la base de datos SQLite a través de `models.Book`.
    *   Devuelve una lista de `schemas.Book` o `List[str]` al frontend.
4.  **Frontend (`LibraryView.js`, `CategoriesView.js`)**: Renderiza los libros o categorías recuperadas.

### 5.3 Conversión de EPUB a PDF

1.  **Frontend (`ToolsView.js`)**: El usuario selecciona un archivo EPUB.
2.  **Solicitud API**: `ToolsView` envía el archivo EPUB a `POST /tools/convert-epub-to-pdf`.
3.  **Backend (`main.py`)**:
    *   Recibe el archivo EPUB.
    *   Extrae el contenido del EPUB en un directorio temporal.
    *   Identifica los archivos HTML y CSS dentro del EPUB.
    *   Utiliza la librería `weasyprint` para renderizar el contenido HTML/CSS a PDF.
    *   Guarda el PDF generado en un directorio temporal público (`temp_books`).
    *   Devuelve un `schemas.ConversionResponse` que contiene la `download_url` del PDF.
4.  **Frontend (`ToolsView.js`)**: Recibe la URL y crea un enlace de descarga para que el usuario pueda obtener el PDF.

### 5.4 Interacción con RAG (Retrieval Augmented Generation)

1.  **Frontend (`RagView.js`) - Selección y estado de indexación**:
    *   El usuario busca y selecciona un libro de su biblioteca.
    *   `RagView` automáticamente envía una solicitud a `GET /rag/status/{book_id}`.
2.  **Backend (`main.py`) - Verificación de estado RAG**:
    *   Llama a `rag.get_index_count()` para verificar cuántos vectores existen para ese `book_id` en ChromaDB.
    *   Devuelve el estado de indexación (`indexed: bool`, `vector_count: int`).
3.  **Frontend (`RagView.js`) - Indexación (si es necesario)**:
    *   Si el libro no está indexado, el usuario hace clic en "Indexar antes de charlar".
    *   `RagView` envía una solicitud a `POST /rag/index/{book_id}`.
4.  **Backend (`main.py`) - Indexación RAG**:
    *   Recupera la `file_path` del libro de la base de datos SQLite.
    *   Llama a `rag.process_book_for_rag(file_path, str(book.id))`.
    *   `rag.py` se encarga de:
        *   Extraer el texto completo del libro (`extract_text()`).
        *   Dividir el texto en `chunks` (`chunk_text()`).
        *   Generar un `embedding` para cada chunk (`get_embedding()`).
        *   Almacenar los embeddings y los chunks originales en ChromaDB.
    *   Devuelve un mensaje de confirmación al frontend.
5.  **Frontend (`RagView.js`) - Consulta (Chat)**:
    *   Una vez que el libro está indexado y listo, el usuario introduce una pregunta en el chat.
    *   `RagView` envía la pregunta, el `book_id` y el `mode` de la consulta a `POST /rag/query/`.
6.  **Backend (`main.py`) - Procesamiento de consulta RAG**:
    *   Recupera los metadatos del libro (título, autor, categoría) de la base de datos SQLite.
    *   Llama a `rag.query_rag(query, book_id, mode, metadata, library_context)`.
    *   `rag.py` se encarga de:
        *   Generar un embedding para la pregunta del usuario.
        *   Realizar una búsqueda de similitud en ChromaDB para recuperar los `chunks` más relevantes del libro.
        *   Construir un `prompt` para el modelo generativo de Gemini que incluye la pregunta del usuario, los chunks recuperados (contexto del libro) y los metadatos/contexto adicional.
        *   Llamar a la API de Google Gemini para generar la respuesta.
    *   Devuelve la respuesta generada (`schemas.RagQueryResponse`) al frontend.
7.  **Frontend (`RagView.js`)**: Muestra la respuesta de la IA en el historial del chat.

---
```
# Documentación Técnica del Proyecto "Mi Librería Inteligente"

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación de gestión de biblioteca digital que permite a los usuarios subir, almacenar, organizar y leer sus libros. Lo que distingue a esta aplicación es su integración con capacidades de Inteligencia Artificial para el análisis de metadatos de libros (título, autor, categoría) y una funcionalidad de chat interactivo (RAG - Retrieval-Augmented Generation) que permite a los usuarios "conversar" con el contenido de sus libros.

La aplicación consta de dos componentes principales:
*   **Frontend:** Una interfaz de usuario moderna y responsiva desarrollada con **React**.
*   **Backend:** Un API robusto y de alto rendimiento construido con **FastAPI** (Python), que maneja la lógica de negocio, la interacción con la base de datos y la integración con modelos de IA.

**Características Clave:**
*   **Gestión de Libros:** Carga, visualización, edición y eliminación de libros (PDF y EPUB).
*   **Metadatos Inteligentes:** Extracción automática de título, autor y categoría de los libros subidos utilizando la API de **Google Gemini**.
*   **Organización:** Filtrado y búsqueda por categoría, autor o título. Listado de categorías únicas.
*   **Lectura y Descarga:** Lector de EPUB integrado y descarga directa de archivos.
*   **Conversión:** Herramienta para convertir libros EPUB a PDF.
*   **Búsqueda Semántica:** Búsqueda avanzada de libros basada en el significado y la temática, utilizando IA.
*   **Chat Inteligente (RAG):** Interfaz conversacional para interactuar con el contenido de los libros, permitiendo hacer preguntas y obtener respuestas contextualizadas del material indexado.
*   **Persistencia:** Utiliza **SQLite** como base de datos para almacenar la información de los libros y **ChromaDB** para el índice vectorial RAG.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales: `backend/` para el servidor FastAPI y `frontend/src/` para la aplicación React.

```
.
├── backend/
│   ├── alembic/                 # Herramienta de migración de base de datos SQLAlchemy (Alembic)
│   ├── static/                  # Archivos estáticos servidos por FastAPI (e.g., portadas, PDFs temporales)
│   │   ├── covers/              # Portadas de libros
│   │   └── ...
│   ├── temp_books/              # Archivos temporales (ej. PDFs convertidos antes de descarga, libros RAG)
│   ├── books/                   # Archivos de libros almacenados permanentemente
│   ├── __init__.py              # Inicialización del paquete backend
│   ├── main.py                  # Aplicación principal FastAPI, rutas API
│   ├── crud.py                  # Operaciones CRUD (Create, Read, Update, Delete) para la base de datos
│   ├── database.py              # Configuración de la base de datos SQLAlchemy
│   ├── models.py                # Modelos de base de datos SQLAlchemy
│   ├── schemas.py               # Esquemas de datos Pydantic para validación y serialización
│   ├── utils.py                 # Funciones de utilidad generales (IA, archivos, conversión)
│   ├── rag.py                   # Lógica de Retrieval-Augmented Generation (RAG)
│   └── tests/                   # Pruebas unitarias para el backend
│       └── ...
├── frontend/
│   ├── public/                  # Archivos estáticos para el frontend (index.html, favicon, etc.)
│   ├── src/                     # Código fuente de la aplicación React
│   │   ├── App.js               # Componente raíz de React, define rutas
│   │   ├── config.js            # Configuración del frontend (URL del API)
│   │   ├── Header.js            # Componente de encabezado y navegación
│   │   ├── LibraryView.js       # Vista principal de la biblioteca (lista de libros)
│   │   ├── UploadView.js        # Vista para subir nuevos libros
│   │   ├── CategoriesView.js    # Vista para listar categorías
│   │   ├── ToolsView.js         # Vista para herramientas adicionales (conversor EPUB a PDF)
│   │   ├── EditBookModal.js     # Modal para editar detalles de un libro
│   │   ├── ReaderView.js        # Componente para leer libros EPUB
│   │   ├── RagView.js           # Vista para la funcionalidad de chat RAG
│   │   ├── ErrorBoundary.js     # Componente para el manejo de errores de UI
│   │   ├── index.js             # Punto de entrada de la aplicación React
│   │   └── ...
│   ├── .env                     # Variables de entorno para el frontend
│   ├── package.json             # Dependencias y scripts de Node.js
│   └── ...
├── .env                         # Variables de entorno para el backend
├── library.db                   # Archivo de base de datos SQLite (generado)
├── rag_index/                   # Directorio para el índice vectorial de ChromaDB (generado)
└── README.md                    # Documentación del proyecto (este archivo)
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend es el corazón de la aplicación, gestionando la lógica de negocio, la interacción con la base de datos y la integración con la inteligencia artificial.

### `backend/main.py`

Este archivo es el punto de entrada principal para la aplicación FastAPI. Define los endpoints de la API, coordina la lógica de negocio entre diferentes módulos (CRUD, RAG, Utils) y maneja las operaciones de archivos.

**Funciones/Lógica Principal:**

*   **`save_optimized_image(pix_or_bytes, target_path, is_pixmap=True)`:**
    *   **Propósito:** Guarda una imagen (portada) en una ruta especificada, optimizándola para el tamaño y formato (JPEG, redimensionado a 400px de ancho máximo).
    *   **Parámetros:**
        *   `pix_or_bytes`: Objeto `fitz.Pixmap` (para PDF) o `bytes` (para EPUB).
        *   `target_path`: Ruta absoluta donde se guardará la imagen.
        *   `is_pixmap`: Booleano, `True` si `pix_or_bytes` es un `Pixmap`, `False` si son bytes.
    *   **Retorno:** None.
*   **`get_safe_path(db_path: str) -> str`:**
    *   **Propósito:** Convierte una ruta de archivo almacenada en la base de datos (que puede ser relativa o absoluta) a una ruta absoluta segura en el sistema de archivos.
    *   **Parámetros:**
        *   `db_path`: Ruta del archivo tal como está en la base de datos.
    *   **Retorno:** Ruta absoluta normalizada.
*   **`get_relative_path(abs_path: str) -> str`:**
    *   **Propósito:** Convierte una ruta de archivo absoluta a una ruta relativa al directorio `backend/`. Útil para almacenar rutas en la base de datos de forma portable.
    *   **Parámetros:**
        *   `abs_path`: Ruta absoluta del archivo.
    *   **Retorno:** Ruta relativa.
*   **`analyze_with_gemini(text: str) -> dict`:**
    *   **Propósito:** Envía un fragmento de texto a la API de Google Gemini para extraer metadatos del libro (título, autor, categoría).
    *   **Parámetros:**
        *   `text`: Texto extraído del libro (primeras páginas).
    *   **Retorno:** Diccionario con claves `title`, `author`, `category` o valores de error.
*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`:**
    *   **Propósito:** Procesa un archivo PDF: extrae texto y busca/guarda una imagen de portada.
    *   **Parámetros:**
        *   `file_path`: Ruta absoluta del archivo PDF.
        *   `covers_dir_fs`: Directorio físico donde se guardarán las portadas.
        *   `covers_url_prefix`: Prefijo URL para acceder a las portadas.
    *   **Retorno:** Diccionario con `text` (texto extraído) y `cover_image_url` (URL de la portada, si se encontró).
*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`:**
    *   **Propósito:** Procesa un archivo EPUB: extrae texto y busca/guarda una imagen de portada con lógica de `fallback`.
    *   **Parámetros:**
        *   `file_path`: Ruta absoluta del archivo EPUB.
        *   `covers_dir_fs`: Directorio físico donde se guardarán las portadas.
        *   `covers_url_prefix`: Prefijo URL para acceder a las portadas.
    *   **Retorno:** Diccionario con `text` (texto extraído) y `cover_image_url` (URL de la portada, si se encontró).
*   **`get_db()`:**
    *   **Propósito:** Función de dependencia de FastAPI para obtener una sesión de base de datos, asegurando que se cierre correctamente.
    *   **Retorno:** Objeto `Session` de SQLAlchemy.

**Endpoints API Principales:**

*   **`POST /upload-book/`**: Sube un libro (PDF/EPUB), lo procesa con IA, guarda sus metadatos y el archivo, e inicia su indexación RAG en segundo plano.
*   **`GET /books/`**: Obtiene una lista paginada y filtrada de libros.
*   **`PUT /books/{book_id}`**: Actualiza los detalles de un libro (título, autor, portada).
*   **`GET /books/count`**: Devuelve el número total de libros.
*   **`GET /books/search/`**: Busca libros por título parcial.
*   **`GET /categories/`**: Devuelve una lista de todas las categorías únicas.
*   **`DELETE /books/{book_id}`**: Elimina un libro por su ID, incluyendo sus archivos y el índice RAG.
*   **`DELETE /categories/{category_name}`**: Elimina una categoría y todos sus libros asociados, incluyendo sus archivos y el índice RAG.
*   **`GET /books/download/{book_id}`**: Permite descargar o abrir un libro por su ID.
*   **`POST /api/books/{book_id}/convert`**: Convierte un EPUB existente en la biblioteca a PDF, lo añade como un nuevo libro y lo indexa.
*   **`POST /tools/convert-epub-to-pdf`**: Convierte un EPUB subido temporalmente a PDF y devuelve una URL de descarga.
*   **`GET /api/books/search/semantic`**: Realiza una búsqueda semántica de libros utilizando RAG.
*   **`POST /rag/upload-book/`**: Endpoint (obsoleto en la UI actual) para subir y procesar un libro directamente para RAG.
*   **`POST /rag/query/`**: Consulta el sistema RAG para obtener respuestas basadas en el contenido de un libro.
*   **`POST /rag/index/{book_id}`**: Indexa un libro existente de la biblioteca en RAG.
*   **`GET /rag/status/{book_id}`**: Devuelve el estado de indexación RAG para un libro.
*   **`GET /rag/stats`**: Obtiene estadísticas generales del índice RAG.
*   **`POST /rag/reindex/category/{category_name}`**: Reindexa todos los libros de una categoría.
*   **`POST /rag/reindex/all`**: Reindexa todos los libros de la biblioteca en segundo plano.
*   **`GET /rag/estimate/...`**: Estima el número de tokens/chunks y el coste potencial de indexación RAG.

### `backend/utils.py`

Contiene funciones de utilidad generales que son utilizadas por otros módulos del backend.

**Funciones Principales:**

*   **`configure_genai()`:**
    *   **Propósito:** Carga variables de entorno y configura la API de Google Generative AI. Lanza un `ValueError` si no se encuentra la API Key.
*   **`get_gemini_model(model_name: str = "gemini-pro")`:**
    *   **Propósito:** Inicializa y devuelve una instancia del modelo Gemini especificado.
*   **`generate_text_from_prompt(prompt: str, model_name: str = "gemini-pro")`:**
    *   **Propósito:** Genera texto a partir de un prompt utilizando el modelo Gemini.
    *   **Parámetros:** `prompt` (texto de la consulta), `model_name` (nombre del modelo Gemini).
    *   **Retorno:** Texto generado por el modelo o un mensaje de error.
*   **`get_file_extension(filename: str) -> str`:**
    *   **Propósito:** Extrae la extensión de un nombre de archivo en minúsculas.
*   **`is_allowed_file(filename: str, allowed_extensions: set) -> bool`:**
    *   **Propósito:** Comprueba si un archivo tiene una extensión permitida.
*   **`convert_epub_bytes_to_pdf_bytes(epub_content: bytes) -> bytes`:**
    *   **Propósito:** Función compleja que convierte el contenido de un archivo EPUB (en bytes) a PDF (en bytes). Implica:
        1.  Extracción del EPUB (que es un ZIP) a un directorio temporal.
        2.  Análisis del manifiesto (`.opf`) para identificar la estructura y el contenido.
        3.  Extracción de la portada (si existe) y CSS.
        4.  Lectura de los capítulos HTML en el orden de lectura (`spine`).
        5.  Renderizado de cada parte (portada, capítulos) a PDF usando `weasyprint` y fusión en un único archivo PDF.
    *   **Parámetros:** `epub_content` (contenido del archivo EPUB en bytes).
    *   **Retorno:** Contenido del archivo PDF en bytes. Lanza `RuntimeError` en caso de fallo.
*   **`extract_text_from_pdf(file_path: str, max_pages: int = 5) -> str`:**
    *   **Propósito:** Extrae texto de las primeras `max_pages` de un archivo PDF utilizando `PyMuPDF (fitz)`.
*   **`extract_text_from_epub(file_path: str, max_chars: int = 5000) -> str`:**
    *   **Propósito:** Extrae texto de un archivo EPUB utilizando `ebooklib`.

### `backend/database.py`

Configuración fundamental para la conexión a la base de datos y la inicialización de SQLAlchemy.

**Variables Clave:**

*   **`SQLALCHEMY_DATABASE_URL`:** Define la cadena de conexión a la base de datos SQLite (`library.db` en la raíz del proyecto).
*   **`engine`:** La instancia del motor de SQLAlchemy, que gestiona la conexión a la base de datos.
*   **`SessionLocal`:** Una clase `sessionmaker` configurada para interactuar con la base de datos. Cada instancia de `SessionLocal` será una sesión de base de datos.
*   **`Base`:** La clase base declarativa de SQLAlchemy a partir de la cual se heredarán todos los modelos de la aplicación.

### `backend/models.py`

Define el modelo de la base de datos utilizando SQLAlchemy ORM, representando la estructura de los libros en la biblioteca.

**Clase Principal:**

*   **`class Book(Base):`**
    *   **`__tablename__ = "books"`:** Nombre de la tabla en la base de datos.
    *   **`id = Column(Integer, primary_key=True, index=True)`:** Identificador único del libro.
    *   **`title = Column(String, index=True)`:** Título del libro.
    *   **`author = Column(String, index=True)`:** Autor del libro.
    *   **`category = Column(String, index=True)`:** Categoría del libro.
    *   **`cover_image_url = Column(String, nullable=True)`:** URL o ruta a la imagen de portada (opcional).
    *   **`file_path = Column(String, unique=True)`:** Ruta al archivo del libro en el sistema de archivos (debe ser única).

### `backend/schemas.py`

Define los esquemas de datos utilizando Pydantic, que son esenciales para la validación de entrada y la serialización/deserialización de datos en la API de FastAPI.

**Clases Principales:**

*   **`class BookBase(BaseModel):`:**
    *   Esquema base para la información de un libro. Incluye `title`, `author`, `category`, `cover_image_url` (opcional) y `file_path`.
*   **`class Book(BookBase):`:**
    *   Extiende `BookBase` y añade el campo `id`. Se utiliza para las respuestas de la API que incluyen el ID del libro. `Config.from_attributes = True` permite mapear directamente desde objetos ORM.
*   **`class ConversionResponse(BaseModel):`:**
    *   Esquema para la respuesta de la API de conversión de EPUB a PDF, contiene `download_url`.
*   **`class RagUploadResponse(BaseModel):`:**
    *   Esquema para la respuesta de la API de subida de libros para RAG, contiene `book_id` y `message`.
*   **`class RagQuery(BaseModel):`:**
    *   Esquema para la solicitud de consulta RAG, incluye `query` (la pregunta), `book_id` (ID del libro a consultar) y `mode` (opcional, para controlar la estrategia de respuesta de la IA).
*   **`class RagQueryResponse(BaseModel):`:**
    *   Esquema para la respuesta de una consulta RAG, contiene `response` (el texto generado por la IA).

### `backend/crud.py`

Contiene funciones para realizar operaciones de Base de Datos (CRUD) sobre el modelo `Book`.

**Funciones Principales:**

*   **`get_abs_path(db_path: str) -> str`:**
    *   **Propósito:** Helper interno para convertir rutas de la DB a rutas absolutas.
*   **`get_book(db: Session, book_id: int)`:**
    *   **Propósito:** Recupera un libro por su ID.
*   **`get_book_by_path(db: Session, file_path: str)`:**
    *   **Propósito:** Recupera un libro por su ruta de archivo.
*   **`get_book_by_title(db: Session, title: str)`:**
    *   **Propósito:** Recupera un libro por su título exacto.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`:**
    *   **Propósito:** Busca libros por un título parcial (case-insensitive) con paginación.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None, skip: int = 0, limit: int = 20)`:**
    *   **Propósito:** Obtiene una lista paginada de libros, con opciones de filtrado por categoría, autor o término de búsqueda general.
*   **`get_categories(db: Session) -> list[str]`:**
    *   **Propósito:** Obtiene una lista de todas las categorías de libros únicas.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`:**
    *   **Propósito:** Crea un nuevo libro en la base de datos.
*   **`delete_book(db: Session, book_id: int)`:**
    *   **Propósito:** Elimina un libro y sus archivos asociados (libro y portada) del sistema.
*   **`delete_books_by_category(db: Session, category: str)`:**
    *   **Propósito:** Elimina todos los libros de una categoría y sus archivos asociados.
*   **`get_books_count(db: Session) -> int`:**
    *   **Propósito:** Obtiene el número total de libros en la base de datos.
*   **`update_book(db: Session, book_id: int, title: str, author: str, cover_image_url: str | None)`:**
    *   **Propósito:** Actualiza el título, autor y opcionalmente la URL de la portada de un libro.

### `backend/rag.py`

Este módulo implementa la lógica de Retrieval-Augmented Generation (RAG) para permitir interacciones inteligentes con el contenido de los libros. Utiliza embeddings de Google Gemini y ChromaDB como base de datos vectorial.

**Funciones Principales:**

*   **`_ensure_init()`:**
    *   **Propósito:** Inicializa el cliente de Google Generative AI (si la IA no está deshabilitada) y el cliente de ChromaDB, creando o conectándose a la colección `book_rag_collection`.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`:**
    *   **Propósito:** Genera un embedding vectorial (representación numérica) para un texto dado utilizando el modelo de embedding de Gemini. Asíncrono.
    *   **Parámetros:** `text` (texto a embeder), `task_type` (tipo de tarea para optimizar el embedding, e.g., `RETRIEVAL_DOCUMENT` o `RETRIEVAL_QUERY`).
    *   **Retorno:** Una lista de flotantes que representa el vector de embedding. Si la IA está deshabilitada, devuelve un embedding dummy.
*   **`extract_text_from_pdf(file_path: str)`:**
    *   **Propósito:** Wrapper para `utils.extract_text_from_pdf`, usado por RAG para extraer *todo* el texto posible.
*   **`extract_text_from_epub(file_path: str)`:**
    *   **Propósito:** Wrapper para `utils.extract_text_from_epub`, usado por RAG para extraer *todo* el texto posible.
*   **`extract_text(file_path: str)`:**
    *   **Propósito:** Función unificada para extraer texto de PDF o EPUB.
*   **`chunk_text(text: str, max_tokens: int = 1000) -> list[str]`:**
    *   **Propósito:** Divide un texto largo en trozos más pequeños (chunks) basándose en un número máximo de tokens, usando `tiktoken` como aproximación.
    *   **Parámetros:** `text` (el texto completo), `max_tokens` (número máximo de tokens por chunk).
    *   **Retorno:** Lista de strings, cada uno representando un chunk de texto.
*   **`_has_index_for_book(book_id: str) -> bool`:**
    *   **Propósito:** Comprueba si ya existen vectores indexados para un `book_id` específico en ChromaDB.
*   **`delete_book_from_rag(book_id: str)`:**
    *   **Propósito:** Elimina todos los vectores asociados a un `book_id` de ChromaDB.
*   **`get_index_count(book_id: str) -> int`:**
    *   **Propósito:** Devuelve el número de vectores almacenados para un `book_id`.
*   **`has_index(book_id: str) -> bool`:**
    *   **Propósito:** Helper público para `get_index_count > 0`.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`:**
    *   **Propósito:** Flujo completo de indexación RAG para un libro:
        1.  Extrae el texto del archivo.
        2.  Divide el texto en chunks.
        3.  Genera embeddings para cada chunk.
        4.  Almacena los embeddings, documentos (chunks) y metadatos (`book_id`, `chunk_index`) en ChromaDB.
        5.  Si `force_reindex` es `True`, elimina índices existentes primero. Si no, omite la indexación si ya existe.
    *   **Parámetros:** `file_path` (ruta del archivo del libro), `book_id` (ID único para el libro en ChromaDB), `force_reindex` (booleano para forzar reindexación).
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`:**
    *   **Propósito:** Estima el número de tokens y chunks para un archivo dado.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`:**
    *   **Propósito:** Estima el número total de tokens y chunks para una lista de archivos.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`:**
    *   **Propósito:** Realiza una consulta al sistema RAG para obtener una respuesta basada en el contenido del libro.
        1.  Genera un embedding para la consulta.
        2.  Busca los chunks más relevantes en ChromaDB para el `book_id` dado.
        3.  Construye un prompt para Gemini que incluye la consulta, los chunks recuperados, metadatos del libro y un "modo" de respuesta (strict, balanced, open).
        4.  Envía el prompt a Gemini para generar la respuesta final.
    *   **Parámetros:**
        *   `query`: La pregunta del usuario.
        *   `book_id`: El ID del libro con el que se está chateando.
        *   `mode`: Estrategia de respuesta de la IA ("strict", "balanced", "open").
        *   `metadata`: Diccionario opcional con metadatos del libro (título, autor, categoría).
        *   `library`: Diccionario opcional con contexto de la biblioteca (e.g., otros libros del mismo autor).
    *   **Retorno:** La respuesta generada por Gemini.
*   **`query_semantic_books(query: str, top_n_fragments: int = 20)`:**
    *   **Propósito:** Realiza una búsqueda semántica de libros en toda la colección RAG.
        1.  Genera un embedding para la consulta.
        2.  Busca los `top_n_fragments` chunks más relevantes en todo ChromaDB (sin filtrar por `book_id`).
        3.  Agrupa los resultados por `book_id` y calcula un score de relevancia.
        4.  Devuelve una lista de diccionarios `{"book_id": int, "score": float}` ordenados por relevancia.

## 4. Análisis Detallado del Frontend (React)

El frontend proporciona la interfaz de usuario para interactuar con la librería, implementando diversas vistas y funcionalidades.

### `frontend/src/App.js`

Este es el componente raíz de la aplicación React. Se encarga de configurar el enrutamiento de la aplicación.

*   **Propósito:** Configura las rutas principales de la aplicación utilizando `react-router-dom`.
*   **Estado/Props:** No tiene estado local ni recibe props.
*   **Efectos:** Ninguno.
*   **Interacciones:** Permite la navegación a través de las diferentes vistas de la aplicación.

### `frontend/src/Header.js`

El componente `Header` se muestra en todas las páginas y proporciona navegación, así como un contador de libros.

*   **Propósito:** Muestra el título de la aplicación, el número total de libros y los enlaces de navegación principales. Incluye un menú de hamburguesa para móviles.
*   **Estado:**
    *   `menuOpen`: `boolean` para controlar la visibilidad del menú en dispositivos móviles.
    *   `bookCount`: `number` que almacena el número total de libros en la biblioteca.
    *   `errorMessage`: `string` para mostrar errores al cargar el contador.
*   **Efectos:**
    *   `useEffect`: Fetches `bookCount` del backend al montar el componente y lo actualiza periódicamente (cada 10 minutos).
*   **Interacciones:**
    *   `handleLinkClick`: Cierra el menú móvil al hacer clic en un enlace de navegación.
    *   Botón de hamburguesa: Alterna el estado `menuOpen`.
    *   `NavLink`: Proporciona navegación entre las vistas.

### `frontend/src/LibraryView.js`

La vista principal de la aplicación, donde los usuarios pueden navegar, buscar, editar y gestionar sus libros.

*   **Propósito:** Muestra una cuadrícula de libros, con funcionalidades de paginación infinita, búsqueda (exacta y semántica con IA), filtrado por autor/categoría, eliminación, edición y conversión de EPUB a PDF.
*   **Estado:**
    *   `books`: `array` de objetos libro a mostrar.
    *   `page`: `number` de la página actual para la paginación infinita.
    *   `hasMore`: `boolean` indica si hay más libros para cargar.
    *   `searchTerm`: `string` valor del input de búsqueda.
    *   `debouncedSearchTerm`: `string` versión con debounce de `searchTerm` para evitar llamadas excesivas al API.
    *   `error`: `string` mensaje de error a mostrar.
    *   `loading`: `boolean` indica si los libros están cargando.
    *   `isMobile`: `boolean` para detectar si la vista es móvil.
    *   `searchMode`: `string` ('exact' o 'semantic') para el tipo de búsqueda.
    *   `ragStats`: `object` estadísticas del índice RAG (total_documents).
    *   `editingBook`: `object` (`book` o `null`) si un libro está siendo editado.
    *   `convertingId`: `number` (`book.id` o `null`) si un libro se está convirtiendo.
*   **Efectos:**
    *   `useEffect` (resize): Detecta cambios en el tamaño de la ventana para `isMobile`.
    *   `useEffect` (fetchStats): Carga estadísticas de RAG al montar y al cambiar el `searchMode`.
    *   `useEffect` (reset list): Resetea la lista de libros y paginación cuando cambian los términos de búsqueda o filtros.
    *   `useEffect` (fetchBooks): Llama al API para cargar libros, gestiona paginación, filtros y modo de búsqueda.
    *   `useCallback` (lastBookElementRef): Hook para implementar el "infinite scroll" utilizando `IntersectionObserver`.
*   **Interacciones:**
    *   `handleAuthorClick`, `handleCategoryClick`: Actualizan los parámetros de búsqueda para filtrar libros.
    *   `handleDeleteBook`: Elimina un libro del backend y de la UI.
    *   `handleConvertToPdf`: Inicia la conversión de un EPUB a PDF en el backend, añadiendo el nuevo PDF a la biblioteca.
    *   `handleEditClick`: Abre el `EditBookModal` para el libro seleccionado.
    *   `handleReindex`: Inicia el reindexado de toda la biblioteca en RAG en segundo plano.
    *   `BookCard` (componente memoizado interno): Muestra los detalles de cada libro y los botones de acción.
    *   `BookCover` (componente memoizado interno): Muestra la portada del libro o un placeholder genérico.

### `frontend/src/EditBookModal.js`

Un componente modal para editar el título, autor y portada de un libro existente.

*   **Propósito:** Permite a los usuarios modificar la información de un libro.
*   **Estado:**
    *   `title`: `string` título actual del libro.
    *   `author`: `string` autor actual del libro.
    *   `coverImage`: `File` objeto de la nueva imagen de portada seleccionada.
    *   `isSaving`: `boolean` indica si la información se está guardando.
*   **Props:** `book` (el libro a editar), `onClose` (función para cerrar el modal), `onBookUpdated` (callback al actualizar un libro).
*   **Efectos:**
    *   `useEffect`: Inicializa el estado `title` y `author` cuando el `book` prop cambia.
*   **Interacciones:**
    *   `handleSubmit`: Envía un `PUT` request al backend con los datos actualizados, incluyendo la nueva portada si se seleccionó.
    *   Botón "Cancelar": Llama a `onClose`.
    *   Input de archivo: Permite seleccionar una nueva imagen de portada.

### `frontend/src/CategoriesView.js`

Muestra todas las categorías únicas de los libros en la biblioteca.

*   **Propósito:** Lista todas las categorías existentes como enlaces clicables.
*   **Estado:**
    *   `categories`: `array` de strings, cada uno una categoría única.
    *   `error`: `string` mensaje de error.
    *   `loading`: `boolean` indica si las categorías están cargando.
*   **Efectos:**
    *   `useEffect`: Fetches las categorías del backend al montar el componente.
*   **Interacciones:**
    *   `Link`: Cada categoría es un enlace que navega a `LibraryView` filtrada por esa categoría.

### `frontend/src/RagView.js`

Esta vista permite a los usuarios interactuar con el contenido de sus libros usando el modelo de IA RAG.

*   **Propósito:** Ofrece una interfaz de chat para hacer preguntas sobre un libro específico, indexar libros para RAG y controlar el modo de respuesta de la IA.
*   **Estado:**
    *   `message`: `string` mensajes informativos para el usuario.
    *   `isLoading`: `boolean` indica si el chat está esperando una respuesta de la IA.
    *   `bookId`: `string` ID del libro actualmente "conversado" con la IA.
    *   `chatHistory`: `array` de objetos `{sender: 'user' | 'gemini', text: string}` que forman el historial de chat.
    *   `currentQuery`: `string` texto actual en el input del chat.
    *   `libraryBooks`: `array` de todos los libros de la biblioteca.
    *   `selectedLibraryId`: `string` ID del libro seleccionado en el dropdown (o búsqueda).
    *   `libStatus`: `object` con el estado RAG del libro seleccionado (`indexed`, `vector_count`, `error`).
    *   `actionsBusy`: `boolean` para bloquear acciones pesadas como indexar.
    *   `refreshing`: `boolean` para indicar que el estado RAG se está refrescando.
    *   `searchTerm`: `string` término de búsqueda para encontrar libros en la biblioteca.
    *   `searching`: `boolean` indica si la búsqueda de libros está activa.
    *   `searchResults`: `array` de libros que coinciden con `searchTerm`.
    *   `resultsOpen`: `boolean` para controlar la visibilidad de los resultados de búsqueda.
    *   `mode`: `string` ('strict', 'balanced', 'open') para la preferencia de respuesta de la IA.
    *   `selectedBook`: `object` detalles del libro seleccionado para chatear.
*   **Efectos:**
    *   `useEffect` (fetchBooks): Carga la lista completa de libros de la biblioteca.
    *   `useEffect` (searchTerm): Implementa un debounce para la búsqueda de libros en la biblioteca.
    *   `useEffect` (auto-scroll): Desplaza automáticamente el chat al final al recibir nuevos mensajes.
    *   `useEffect` (check status): Comprueba el estado RAG del libro seleccionado cuando `selectedLibraryId` cambia.
*   **Interacciones:**
    *   Input de búsqueda: Permite buscar y seleccionar un libro de la biblioteca para el chat RAG.
    *   Botones "Comprobar RAG", "Indexar", "Reindexar", "Chatear": Gestionan el estado de indexación RAG del libro y activan el modo chat.
    *   Input de chat (`textarea`): Permite al usuario escribir preguntas.
    *   `handleQuerySubmit`: Envía la pregunta del usuario al endpoint `/rag/query/` del backend y actualiza el historial de chat.
    *   Selectores de `mode`: Permiten al usuario elegir la estrategia de respuesta de la IA (estricta, equilibrada, abierta).

### `frontend/src/ToolsView.js`

Ofrece herramientas útiles, como un conversor de EPUB a PDF.

*   **Propósito:** Proporcionar utilidades adicionales. Actualmente, solo un conversor de EPUB a PDF.
*   **Estado:**
    *   `selectedFile`: `File` objeto del archivo seleccionado para la conversión.
    *   `message`: `string` mensajes de estado para el usuario.
    *   `isLoading`: `boolean` indica si la conversión está en curso.
*   **Efectos:** Ninguno.
*   **Interacciones:**
    *   Input de archivo y zona de arrastre: Permite seleccionar un archivo EPUB.
    *   `handleConvert`: Envía el archivo EPUB al endpoint `/tools/convert-epub-to-pdf` del backend y gestiona la descarga del PDF resultante.

### `frontend/src/ReaderView.js`

Componente dedicado a la lectura de libros EPUB.

*   **Propósito:** Muestra el contenido de un libro EPUB utilizando la librería `react-reader`.
*   **Estado:**
    *   `location`: `string` (CFI de EPUB) para guardar la posición de lectura.
    *   `epubData`: `ArrayBuffer` que contiene los datos binarios del EPUB.
    *   `isLoading`: `boolean` indica si el EPUB se está cargando.
    *   `error`: `string` mensaje de error.
*   **Props:** Recibe `bookId` de los parámetros de la URL.
*   **Efectos:**
    *   `useEffect`: Fetches los datos binarios del EPUB del backend (`/books/download/{bookId}`) al montar el componente.
*   **Interacciones:**
    *   `ReactReader`: Componente de terceros que gestiona la visualización y navegación del EPUB. `locationChanged` actualiza la posición de lectura.

### `frontend/src/UploadView.js`

Permite a los usuarios subir uno o varios archivos de libros a la biblioteca.

*   **Propósito:** Proporcionar una interfaz para cargar múltiples archivos PDF y EPUB al backend para su procesamiento.
*   **Estado:**
    *   `filesToUpload`: `array` de objetos `{file: File, status: string, message: string}` que representan los archivos seleccionados y su estado de carga.
    *   `isUploading`: `boolean` indica si hay archivos en proceso de subida.
*   **Efectos:** Ninguno.
*   **Interacciones:**
    *   Input de archivo y zona de arrastre: Permite seleccionar y añadir múltiples archivos a la cola de subida.
    *   `handleUpload`: Itera sobre los archivos pendientes, envía cada uno al endpoint `/upload-book/` del backend y actualiza su estado.
    *   `handleReset`: Limpia la lista de archivos y el input.
    *   Botón "Ir a la Biblioteca": Navega a la vista principal una vez que todos los archivos se han procesado.

### `frontend/src/config.js`

Un archivo de configuración simple para almacenar variables de entorno del frontend.

*   **Propósito:** Centralizar la URL del API del backend, haciéndola configurable a través de variables de entorno (`REACT_APP_API_URL`).
*   **Variables:** `API_URL` (valor por defecto `http://localhost:8001`).

### `frontend/src/ErrorBoundary.js`

Un componente React `ErrorBoundary` para capturar y mostrar errores de JavaScript en la interfaz de usuario.

*   **Propósito:** Prevenir que la aplicación se rompa completamente debido a errores en los componentes React, mostrando un mensaje de error amigable en su lugar.
*   **Estado:** `hasError` (booleano), `error` (objeto Error).
*   **Métodos del ciclo de vida:**
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para indicar que se ha producido un error.
    *   `componentDidCatch(error, info)`: Registra el error en la consola para depuración.
*   **Renderizado:** Si `hasError` es `true`, muestra un mensaje de error y el detalle del error; de lo contrario, renderiza los `children` normales.

## 5. Flujo de Datos y API

El flujo de datos en "Mi Librería Inteligente" se centra en la interacción entre el frontend de React y el backend de FastAPI, utilizando la base de datos SQLite y ChromaDB para la persistencia.

### Flujo Típico: Carga de un Nuevo Libro

1.  **Frontend (UploadView):**
    *   El usuario selecciona uno o varios archivos (PDF o EPUB) o los arrastra y suelta.
    *   Por cada archivo, `UploadView` crea un `FormData` y lo envía como `POST` a `/upload-book/`.
2.  **Backend (main.py -> /upload-book/):**
    *   Recibe el `UploadFile` (el archivo del libro).
    *   Guarda el archivo en el directorio `backend/books/`.
    *   Identifica el tipo de archivo (.pdf o .epub) y llama a `process_pdf` o `process_epub` (en `main.py`).
        *   Estas funciones extraen un fragmento de texto del libro y buscan una imagen de portada.
        *   La imagen de portada se guarda en `backend/static/covers/` y su URL relativa se almacena.
    *   El texto extraído se envía a `analyze_with_gemini` (en `main.py`).
        *   Gemini API analiza el texto y devuelve un JSON con el título, autor y categoría.
    *   Si los metadatos de IA son válidos, `crud.create_book` (en `crud.py`) guarda la información del libro (título, autor, categoría, URL de portada, ruta del archivo) en la tabla `books` de SQLite.
    *   Una tarea en segundo plano (`background_index_book`) se dispara para `rag.process_book_for_rag` (en `rag.py`).
        *   Esta función extrae todo el texto del libro, lo divide en chunks, genera embeddings con Gemini y los almacena en ChromaDB (`rag_index/`).
    *   Devuelve los detalles del libro recién creado al frontend.
3.  **Frontend (UploadView):**
    *   Actualiza el estado de carga del archivo y muestra el mensaje de éxito o error.
    *   Cuando todos los archivos se han procesado, ofrece al usuario ir a `LibraryView`.

### Flujo Típico: Búsqueda y Visualización de Libros

1.  **Frontend (LibraryView):**
    *   El usuario navega a la biblioteca, o aplica filtros (categoría, autor) o introduce un término de búsqueda (exacta o semántica).
    *   Realiza una solicitud `GET` a `/books/` (para búsqueda exacta/filtrado) o a `/api/books/search/semantic` (para búsqueda semántica).
2.  **Backend (main.py):**
    *   **Búsqueda Exacta/Filtrado (`GET /books/`):**
        *   Invoca a `crud.get_books` (en `crud.py`) con los parámetros de consulta (categoría, búsqueda, autor, paginación).
        *   `crud.get_books` consulta la base de datos SQLite y devuelve los libros que coinciden.
    *   **Búsqueda Semántica (`GET /api/books/search/semantic`):**
        *   Invoca a `rag.query_semantic_books` (en `rag.py`) con la consulta del usuario.
        *   `rag.query_semantic_books` genera un embedding para la consulta, lo usa para buscar los chunks más relevantes en ChromaDB (todos los libros indexados), calcula un score por libro y devuelve una lista ordenada de `book_id`s.
        *   El endpoint luego utiliza estos `book_id`s para recuperar los objetos `Book` completos de la base de datos a través de `crud.get_book`.
    *   Devuelve la lista de libros (o los IDs/scores en el caso semántico) al frontend.
3.  **Frontend (LibraryView):**
    *   Actualiza el estado `books` y renderiza la cuadrícula de libros.
    *   Para el "infinite scroll", si el usuario llega al final de la vista y `hasMore` es `true`, `LibraryView` incrementa `page` y repite el proceso de carga.

### Flujo Típico: Conversación con IA (RAG)

1.  **Frontend (RagView):**
    *   El usuario selecciona un libro de la lista (`selectedLibraryId`).
    *   El frontend llama a `/rag/status/{book_id}` para verificar si el libro está indexado.
    *   Si no está indexado, el usuario hace clic en "Indexar antes de charlar", lo que envía un `POST` a `/rag/index/{book_id}`.
2.  **Backend (main.py -> /rag/index/{book_id}):**
    *   Recupera el `file_path` del libro de la base de datos.
    *   Llama a `rag.process_book_for_rag` para indexar el libro en ChromaDB.
3.  **Frontend (RagView):**
    *   Una vez indexado (o si ya lo estaba), el usuario puede escribir una pregunta en el chat y enviarla (`handleQuerySubmit`). Esto hace un `POST` a `/rag/query/`.
4.  **Backend (main.py -> /rag/query/):**
    *   Recibe la `query` y el `book_id`.
    *   Llama a `rag.query_rag` con la pregunta, el ID del libro y el modo de respuesta de la IA.
    *   `rag.query_rag` genera un embedding para la consulta, busca chunks relevantes en ChromaDB (solo para ese `book_id`), construye un prompt con contexto y lo envía a Google Gemini.
    *   Devuelve la respuesta generada por Gemini al frontend.
5.  **Frontend (RagView):**
    *   Muestra la respuesta de Gemini en el historial de chat.

### Resumen de Endpoints Principales de la API

| Método | Endpoint                             | Descripción                                                                 | Módulo                                                                        |
| :----- | :----------------------------------- | :-------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| `POST` | `/upload-book/`                      | Sube y procesa un libro, extrae metadatos con IA, guarda en DB y ChromaDB.  | `main.py`                                                                     |
| `GET`  | `/books/`                            | Obtiene una lista paginada y filtrada de libros.                            | `main.py` (usa `crud.py`)                                                     |
| `GET`  | `/books/count`                       | Devuelve el número total de libros.                                         | `main.py` (usa `crud.py`)                                                     |
| `GET`  | `/books/search/`                     | Busca libros por título parcial.                                            | `main.py` (usa `crud.py`)                                                     |
| `GET`  | `/api/books/search/semantic`         | Busca libros por similitud semántica (RAG).                                 | `main.py` (usa `rag.py`)                                                      |
| `PUT`  | `/books/{book_id}`                   | Actualiza el título, autor y/o portada de un libro.                         | `main.py` (usa `crud.py`)                                                     |
| `DELETE`| `/books/{book_id}`                   | Elimina un libro (DB, archivos y RAG).                                      | `main.py` (usa `crud.py`, `rag.py`)                                           |
| `GET`  | `/categories/`                       | Lista todas las categorías únicas.                                          | `main.py` (usa `crud.py`)                                                     |
| `DELETE`| `/categories/{category_name}`        | Elimina una categoría y todos sus libros.                                   | `main.py` (usa `crud.py`, `rag.py`)                                           |
| `GET`  | `/books/download/{book_id}`          | Descarga el archivo de un libro.                                            | `main.py`                                                                     |
| `POST` | `/api/books/{book_id}/convert`       | Convierte un EPUB existente de la biblioteca a PDF y lo añade como nuevo libro. | `main.py` (usa `utils.py`)                                                    |
| `POST` | `/tools/convert-epub-to-pdf`         | Sube un EPUB, lo convierte a PDF temporal y devuelve URL de descarga.       | `main.py` (usa `utils.py`)                                                    |
| `POST` | `/rag/index/{book_id}`               | Indexa un libro existente en el sistema RAG.                                | `main.py` (usa `rag.py`)                                                      |
| `GET`  | `/rag/status/{book_id}`              | Obtiene el estado de indexación RAG para un libro.                          | `main.py` (usa `rag.py`)                                                      |
| `POST` | `/rag/query/`                        | Realiza una consulta al sistema RAG para un libro.                          | `main.py` (usa `rag.py`)                                                      |
| `GET`  | `/rag/stats`                         | Obtiene estadísticas generales del índice RAG.                              | `main.py` (usa `rag.py`)                                                      |
| `POST` | `/rag/reindex/all`                   | Inicia el reindexado de toda la biblioteca en segundo plano.                | `main.py` (usa `rag.py`)                                                      |
| `GET`  | `/static/{filepath:path}`            | Sirve archivos estáticos (e.g., portadas de libros).                        | `main.py` (configuración de `StaticFiles`)                                    |
| `GET`  | `/temp_books/{filename}`             | Sirve archivos temporales (e.g., PDFs convertidos para descarga).           | `main.py` (configuración de `StaticFiles`)                                    |
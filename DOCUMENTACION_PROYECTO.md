# Documentación del Proyecto: Mi Librería Inteligente

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web diseñada para gestionar y organizar colecciones de libros digitales. Permite a los usuarios subir libros en formato PDF y EPUB, los cuales son automáticamente analizados por inteligencia artificial (IA) para extraer metadatos como título, autor y categoría. La aplicación no solo ofrece una interfaz para explorar, buscar y leer libros, sino que también integra capacidades avanzadas de "Retrieval Augmented Generation" (RAG) para permitir a los usuarios conversar con el contenido de sus libros mediante IA.

La aplicación presenta una arquitectura de tipo cliente-servidor:
*   **Frontend**: Desarrollado con React, proporciona una interfaz de usuario interactiva y responsiva para todas las funcionalidades.
*   **Backend**: Construido con FastAPI (Python), expone una API RESTful para la gestión de libros, la integración con modelos de IA (Google Gemini) y el sistema RAG.
*   **Base de Datos**: Utiliza SQLite para almacenar los metadatos de los libros, configurado a través de SQLAlchemy.
*   **Sistema RAG**: Implementa ChromaDB para almacenar embeddings de los fragmentos de texto de los libros, permitiendo búsquedas semánticas y la generación de respuestas contextualizadas por la IA.
*   **Almacenamiento de Archivos**: Los archivos de libros (PDF, EPUB) y sus portadas se almacenan directamente en el sistema de archivos del servidor.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales: `backend/` y `frontend/`.

```
Mi Librería Inteligente/
├── backend/
│   ├── alembic/                      # Herramienta de migración de base de datos SQLAlchemy
│   │   └── versions/                 # Archivos de migración de la base de datos
│   ├── books/                        # Directorio para almacenar los archivos de libros subidos
│   ├── static/                       # Archivos estáticos servidos por FastAPI (e.g., portadas)
│   │   └── covers/                   # Subdirectorio para las imágenes de portada
│   ├── temp_books/                   # Directorio temporal para archivos durante la conversión o procesamiento RAG
│   ├── tests/                        # Pruebas unitarias y de integración del backend
│   ├── tests_curated/                # Pruebas adicionales/curadas
│   ├── __init__.py                   # Archivo de inicialización del módulo Python
│   ├── crud.py                       # Operaciones CRUD para la base de datos
│   ├── database.py                   # Configuración de la base de datos SQLAlchemy
│   ├── main.py                       # Aplicación FastAPI principal y endpoints
│   ├── models.py                     # Modelos de base de datos SQLAlchemy
│   ├── rag.py                        # Lógica de Retrieval Augmented Generation (RAG)
│   ├── schemas.py                    # Esquemas de Pydantic para validación de datos API
│   └── utils.py                      # Funciones de utilidad (conversión, IA, etc.)
├── frontend/
│   ├── public/                       # Archivos estáticos del frontend (index.html)
│   ├── src/                          # Código fuente de la aplicación React
│   │   ├── App.css                   # Estilos globales de la aplicación
│   │   ├── App.js                    # Componente principal de React y enrutamiento
│   │   ├── CategoriesView.css        # Estilos para CategoriesView
│   │   ├── CategoriesView.js         # Componente para mostrar categorías
│   │   ├── config.js                 # Configuración de la URL del API
│   │   ├── EditBookModal.css         # Estilos para EditBookModal
│   │   ├── EditBookModal.js          # Componente modal para editar libros
│   │   ├── ErrorBoundary.js          # Componente de límite de error de React
│   │   ├── Header.css                # Estilos para el encabezado
│   │   ├── Header.js                 # Componente de encabezado de la aplicación
│   │   ├── index.css                 # Estilos CSS globales
│   │   ├── index.js                  # Punto de entrada de la aplicación React
│   │   ├── LibraryView.css           # Estilos para LibraryView
│   │   ├── LibraryView.js            # Componente para mostrar la biblioteca de libros
│   │   ├── RagView.css               # Estilos para RagView
│   │   ├── RagView.js                # Componente para la interfaz de chat RAG
│   │   ├── ReaderView.css            # Estilos para ReaderView
│   │   ├── ReaderView.js             # Componente para leer EPUBs
│   │   ├── ToolsView.css             # Estilos para ToolsView
│   │   └── ToolsView.js              # Componente para herramientas (e.g., convertidor EPUB a PDF)
│   ├── .env.example                  # Ejemplo de variables de entorno
│   ├── package.json                  # Dependencias y scripts de Node.js
│   └── README.md
├── .env                              # Variables de entorno (no incluido en control de versiones)
└── library.db                        # Base de datos SQLite (generada por la aplicación)
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/models.py`

Define el modelo de la base de datos para los libros utilizando SQLAlchemy ORM.

*   **`class Book(Base)`**: Representa la tabla `books` en la base de datos.
    *   `__tablename__ = "books"`: Nombre de la tabla.
    *   `__table_args__ = {'extend_existing': True}`: Permite redefinir la tabla, útil en entornos de desarrollo o pruebas.
    *   `id = Column(Integer, primary_key=True, index=True)`: Identificador único del libro, clave primaria.
    *   `title = Column(String, index=True)`: Título del libro.
    *   `author = Column(String, index=True)`: Autor del libro.
    *   `category = Column(String, index=True)`: Categoría o género del libro.
    *   `cover_image_url = Column(String, nullable=True)`: URL de la imagen de portada, puede ser nula.
    *   `file_path = Column(String, unique=True)`: Ruta absoluta al archivo del libro en el sistema de archivos, debe ser única.

### `backend/database.py`

Configura la conexión a la base de datos y la sesión de SQLAlchemy.

*   **`SQLALCHEMY_DATABASE_URL`**: Define la URL de conexión a la base de datos SQLite, ubicada en la raíz del proyecto (`library.db`).
*   **`engine = create_engine(...)`**: Crea una instancia del motor de la base de datos. `connect_args={"check_same_thread": False}` es necesario para SQLite con múltiples hilos.
*   **`SessionLocal = sessionmaker(...)`**: Crea una fábrica de sesiones, que se usará para obtener instancias de `Session` para las operaciones de la base de datos.
*   **`Base = declarative_base()`**: La clase base de la que heredarán los modelos de SQLAlchemy.

### `backend/schemas.py`

Define los esquemas de datos utilizando Pydantic para la validación de entrada y salida de los endpoints de la API.

*   **`class BookBase(BaseModel)`**: Esquema base para los datos de un libro.
    *   `title: str`, `author: str`, `category: str`, `cover_image_url: str | None = None`, `file_path: str`.
*   **`class Book(BookBase)`**: Extiende `BookBase` añadiendo el `id` del libro.
    *   `id: int`.
    *   `Config.from_attributes = True`: Permite mapear los campos del modelo ORM de SQLAlchemy a los campos de Pydantic.
*   **`class ConversionResponse(BaseModel)`**: Esquema para la respuesta de la API de conversión.
    *   `download_url: str`.
*   **`class RagUploadResponse(BaseModel)`**: Esquema para la respuesta de la API de carga RAG.
    *   `book_id: str`, `message: str`.
*   **`class RagQuery(BaseModel)`**: Esquema para la consulta a la API RAG.
    *   `query: str`, `book_id: str`, `mode: str | None = None`: Define el modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`).
*   **`class RagQueryResponse(BaseModel)`**: Esquema para la respuesta de la API RAG.
    *   `response: str`.

### `backend/crud.py`

Contiene funciones para las operaciones `Create`, `Read`, `Update`, `Delete` (CRUD) sobre los libros en la base de datos.

*   **`get_book(db: Session, book_id: int)`**: Obtiene un libro por su ID.
*   **`get_book_by_path(db: Session, file_path: str)`**: Obtiene un libro por su ruta de archivo.
*   **`get_book_by_title(db: Session, title: str)`**: Obtiene un libro por su título exacto.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**: Busca libros por título parcial con paginación.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**: Obtiene una lista de libros, con filtros opcionales por categoría, búsqueda general (título, autor, categoría) y autor.
*   **`get_categories(db: Session) -> list[str]`**: Obtiene una lista de todas las categorías únicas.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**: Crea un nuevo registro de libro.
*   **`delete_book(db: Session, book_id: int)`**: Elimina un libro por su ID y los archivos asociados (libro y portada) del disco.
*   **`delete_books_by_category(db: Session, category: str)`**: Elimina todos los libros de una categoría y sus archivos asociados.
*   **`get_books_count(db: Session) -> int`**: Devuelve el número total de libros.
*   **`update_book(db: Session, book_id: int, title: str, author: str, cover_image_url: str | None)`**: Actualiza el título, autor y opcionalmente la URL de la portada de un libro.

### `backend/utils.py`

Contiene funciones de utilidad para la configuración de la IA, procesamiento de archivos y conversión de formatos.

*   **`configure_genai()`**: Carga variables de entorno y configura la API de Google Gemini utilizando `GOOGLE_API_KEY` o `GEMINI_API_KEY`. Lanza un `ValueError` si no se encuentra la clave.
*   **`get_gemini_model(model_name: str = "gemini-pro")`**: Devuelve una instancia del modelo generativo de Gemini especificado.
*   **`generate_text_from_prompt(prompt: str, model_name: str = "gemini-pro")`**: Genera texto a partir de un prompt usando el modelo Gemini.
*   **`get_file_extension(filename: str) -> str`**: Extrae la extensión de un nombre de archivo.
*   **`is_allowed_file(filename: str, allowed_extensions: set) -> bool`**: Comprueba si un archivo tiene una extensión permitida.
*   **`convert_epub_bytes_to_pdf_bytes(epub_content: bytes) -> bytes`**: Una función compleja que convierte el contenido de un archivo EPUB (en bytes) a PDF (en bytes). Extrae el contenido del EPUB, analiza el manifiesto `.opf`, identifica la portada y los capítulos HTML, aplica estilos CSS y renderiza todo a un PDF utilizando `weasyprint`.

### `backend/rag.py`

Implementa la lógica central del sistema de Retrieval Augmented Generation (RAG) utilizando ChromaDB y Google Gemini.

*   **`_ensure_init()`**: Inicializa el cliente de Gemini y ChromaDB (colección `book_rag_collection`). Carga variables de entorno. Configura la persistencia del índice RAG.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**: Genera un embedding vectorial para un texto dado utilizando el modelo `EMBEDDING_MODEL` de Gemini. Maneja el caso de IA deshabilitada para pruebas.
*   **`extract_text_from_pdf(file_path: str)`**: Extrae texto de un archivo PDF usando `PyPDF2`.
*   **`extract_text_from_epub(file_path: str)`**: Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`.
*   **`extract_text(file_path: str)`**: Función unificada para extraer texto de PDF o EPUB.
*   **`chunk_text(text: str, max_tokens: int = 1000)`**: Divide el texto en fragmentos más pequeños para la indexación, basándose en el recuento de tokens (aproximado con `tiktoken`).
*   **`_has_index_for_book(book_id: str)`**: Comprueba si un libro ya tiene vectores indexados en ChromaDB.
*   **`delete_book_from_rag(book_id: str)`**: Elimina todos los vectores asociados a un `book_id` de ChromaDB.
*   **`get_index_count(book_id: str)`**: Devuelve el número de vectores almacenados para un `book_id`.
*   **`has_index(book_id: str)`**: Helper público para verificar si un libro está indexado en RAG.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**: Extrae el texto de un libro, lo divide en fragmentos, genera embeddings y los almacena en ChromaDB. Si `force_reindex` es `True`, reindexa el libro.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**: Estima el número de tokens y fragmentos para un archivo.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**: Estima el número total de tokens y fragmentos para una lista de archivos.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**: Realiza una consulta al sistema RAG. Recupera los fragmentos más relevantes de ChromaDB para el `book_id` dado, los combina con el prompt del usuario y genera una respuesta utilizando el modelo `GENERATION_MODEL` de Gemini. Soporta diferentes `mode`s (`strict`, `balanced`, `open`) para controlar cómo la IA integra el contexto del libro con su conocimiento general. También puede usar `metadata` y `library` para un contexto adicional.

### `backend/main.py`

Es el punto de entrada de la aplicación FastAPI. Configura la API, maneja las rutas y orquesta las operaciones del backend.

*   **Configuración Inicial**:
    *   `FastAPI()`: Instancia la aplicación.
    *   `base_dir`: Establece rutas base para directorios estáticos, de libros y temporales.
    *   `STATIC_COVERS_URL_PREFIX`: Prefijo URL para las portadas.
    *   `os.makedirs(...)`: Asegura la existencia de los directorios necesarios.
    *   `app.mount(...)`: Monta los directorios estáticos para servir archivos.
    *   **CORS**: Configura el middleware `CORSMiddleware` para permitir solicitudes desde orígenes específicos (configurables vía `ALLOW_ORIGINS`, `FRONTEND_PORTS`, `ALLOW_ORIGIN_REGEX`).
    *   **AI_ENABLED**: Verifica la disponibilidad de la API Key de Gemini y configura `genai`.
    *   `models.Base.metadata.create_all(bind=database.engine)`: Crea las tablas de la base de datos si no existen.

*   **Funciones de IA y Procesamiento**:
    *   **`async def analyze_with_gemini(text: str) -> dict`**: Envía un fragmento de texto a un modelo Gemini para extraer título, autor y categoría. Retorna un diccionario JSON. Incluye lógica para deshabilitar la IA.
    *   **`def process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**: Extrae texto de las primeras páginas de un PDF y busca una imagen de portada. Guarda la portada y devuelve la URL.
    *   **`def process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**: Extrae texto de un EPUB y busca una imagen de portada (con fallbacks si no hay una oficial). Guarda la portada y devuelve la URL.

*   **Dependency (`get_db`)**: Función que proporciona una sesión de base de datos (`SessionLocal`) por cada solicitud.

*   **Rutas de la API**:
    *   **`POST /api/books/{book_id}/convert`**: Convierte un libro EPUB existente a PDF, lo procesa con IA y lo añade como un nuevo libro a la biblioteca.
    *   **`POST /tools/convert-epub-to-pdf`**: Recibe un EPUB, lo convierte a PDF y devuelve una URL temporal de descarga.
    *   **`POST /upload-book/`**: Sube un archivo de libro (PDF/EPUB), lo guarda, lo procesa para extraer texto y portada, lo analiza con Gemini para metadatos y lo guarda en la base de datos.
    *   **`GET /books/`**: Lista los libros, con opciones de filtrar por `category`, `search` (título, autor, categoría) y `author`.
    *   **`PUT /books/{book_id}`**: Actualiza el título, autor y opcionalmente la portada de un libro existente.
    *   **`GET /books/count`**: Devuelve el número total de libros.
    *   **`GET /books/search/`**: Busca libros por título parcial con paginación.
    *   **`GET /categories/`**: Devuelve una lista de todas las categorías únicas.
    *   **`DELETE /books/{book_id}`**: Elimina un libro por ID, sus archivos y su índice RAG asociado.
    *   **`DELETE /categories/{category_name}`**: Elimina todos los libros de una categoría y sus índices RAG.
    *   **`GET /books/download/{book_id}`**: Descarga un libro por ID. Permite ver PDFs en línea o descargar otros formatos.
    *   **`POST /rag/upload-book/` (Deprecated/Removed in current UI)**: (Ruta original para subir y procesar un libro para RAG directamente, pero la UI ahora usa `rag/index/{book_id}`)
    *   **`POST /rag/query/`**: Consulta el sistema RAG para obtener una respuesta basada en el contenido de un libro.
    *   **`POST /rag/index/{book_id}`**: Indexa un libro existente de la biblioteca en el sistema RAG.
    *   **`GET /rag/status/{book_id}`**: Devuelve si un libro está indexado en RAG y cuántos vectores tiene.
    *   **`POST /rag/reindex/category/{category_name}`**: (Re)indexa todos los libros de una categoría.
    *   **`POST /rag/reindex/all`**: (Re)indexa todos los libros de la biblioteca.
    *   **`GET /rag/estimate/book/{book_id}`**: Estima tokens y chunks para un libro.
    *   **`GET /rag/estimate/category/{category_name}`**: Estima tokens y chunks para una categoría.
    *   **`GET /rag/estimate/all`**: Estima tokens y chunks para todos los libros.

## 4. Análisis Detallado del Frontend (React)

### `frontend/src/index.js`

El punto de entrada principal de la aplicación React. Renderiza el componente `App` dentro de `React.StrictMode` y configura `reportWebVitals`.

### `frontend/src/App.js`

El componente raíz de la aplicación React, que configura el enrutamiento y la estructura básica de la página.

*   **Propósito**: Define las rutas de navegación y muestra el encabezado (`Header`) y el contenido principal (`main`) según la ruta actual.
*   **Estado/Props**: No gestiona estado ni recibe props directamente, actúa como un contenedor.
*   **Efectos**: No tiene efectos secundarios directos más allá del enrutamiento.
*   **Interacciones**: Usa `BrowserRouter` y `Routes`/`Route` de `react-router-dom` para manejar la navegación entre vistas (`/`, `/upload`, `/etiquetas`, `/herramientas`, `/rag`, `/leer/:bookId`).

### `frontend/src/Header.js`

El componente de la barra de navegación superior de la aplicación.

*   **Propósito**: Muestra el título de la aplicación, el contador de libros y los enlaces de navegación.
*   **Estado**:
    *   `menuOpen`: `boolean`, controla la visibilidad del menú de hamburguesa en móviles.
    *   `bookCount`: `number`, el número total de libros en la biblioteca.
    *   `errorMessage`: `string | null`, para mostrar errores al obtener el contador de libros.
*   **Efectos**:
    *   `useEffect` al montar el componente: Realiza una llamada a la API (`/books/count`) para obtener el número total de libros y actualiza `bookCount`. Se actualiza periódicamente (cada 10 minutos).
*   **Interacciones**:
    *   Clic en el botón de hamburguesa: Alterna el estado `menuOpen`.
    *   Clic en los enlaces de navegación: Navega a la ruta correspondiente y cierra el menú si está abierto.
    *   Comunicación con el backend: Realiza una solicitud GET a `/books/count`.

### `frontend/src/LibraryView.js`

La vista principal de la biblioteca, que muestra la lista de libros disponibles.

*   **Propósito**: Muestra los libros en una cuadrícula, permite buscar, filtrar por categoría o autor, eliminar, editar y convertir libros.
*   **Estado**:
    *   `books`: `Array`, la lista de objetos libro recuperados del backend.
    *   `searchTerm`: `string`, el término de búsqueda actual.
    *   `debouncedSearchTerm`: `string`, versión "debounced" de `searchTerm` para evitar demasiadas llamadas a la API.
    *   `error`: `string`, mensaje de error si la carga de libros falla.
    *   `loading`: `boolean`, indica si los libros se están cargando.
    *   `isMobile`: `boolean`, para adaptar la UI a dispositivos móviles.
    *   `editingBook`: `Object | null`, el libro que se está editando en el modal.
    *   `convertingId`: `number | null`, el ID del libro que se está convirtiendo (para deshabilitar el botón).
*   **Props**: Ninguno, usa `useSearchParams` para filtros de URL.
*   **Efectos**:
    *   `useEffect` para `debouncedSearchTerm` y `searchParams`: Llama a `fetchBooks` cuando cambian para obtener libros filtrados/buscados.
    *   `useEffect` para `handleResize`: Detecta cambios de tamaño de ventana para `isMobile`.
*   **Interacciones**:
    *   `BookCover` (componente memoizado): Muestra la portada o un placeholder si no está disponible.
    *   `BookCard` (componente memoizado): Representa cada libro, con botones para editar, eliminar, convertir y abrir/descargar.
    *   `handleAuthorClick`, `handleCategoryClick`: Actualizan los `searchParams` para filtrar por autor/categoría.
    *   `handleDeleteBook`: Envía una solicitud DELETE a `/books/{bookId}`.
    *   `handleConvertToPdf`: Envía una solicitud POST a `/api/books/{book_id}/convert`.
    *   `handleEditClick`: Abre el `EditBookModal` para el libro seleccionado.
    *   `handleBookUpdated`: Actualiza la lista de libros después de editar uno.
    *   Comunicación con el backend: GET a `/books/`, DELETE a `/books/{bookId}`, POST a `/api/books/{bookId}/convert`.

### `frontend/src/UploadView.js`

La vista para subir nuevos archivos de libros.

*   **Propósito**: Permite a los usuarios seleccionar o arrastrar y soltar múltiples archivos (PDF, EPUB) para subirlos y procesarlos con la IA.
*   **Estado**:
    *   `filesToUpload`: `Array` de objetos `{ file, status, message }`, rastrea el progreso de cada archivo.
    *   `isUploading`: `boolean`, indica si hay archivos en proceso de subida.
*   **Props**: Ninguno.
*   **Efectos**: Ninguno.
*   **Interacciones**:
    *   `handleFileChange`: Añade los archivos seleccionados al estado `filesToUpload`.
    *   `handleDrop`, `handleDragOver`: Implementan la funcionalidad de arrastrar y soltar.
    *   `handleUpload`: Itera sobre `filesToUpload`, enviando cada archivo al backend (`/upload-book/`). Actualiza el estado (`status`, `message`) de cada archivo.
    *   `handleReset`: Limpia la lista de archivos para subir.
    *   Comunicación con el backend: POST a `/upload-book/` para cada archivo.

### `frontend/src/CategoriesView.js`

Muestra una lista de todas las categorías de libros únicas.

*   **Propósito**: Ofrecer una vista de todas las categorías disponibles en la biblioteca para facilitar la navegación.
*   **Estado**:
    *   `categories`: `Array`, lista de strings de categorías.
    *   `error`: `string`, mensaje de error si la carga de categorías falla.
    *   `loading`: `boolean`, indica si las categorías se están cargando.
*   **Props**: Ninguno.
*   **Efectos**:
    *   `useEffect` al montar el componente: Realiza una llamada a la API (`/categories/`) para obtener la lista de categorías.
*   **Interacciones**:
    *   Clic en una tarjeta de categoría: Navega a la `LibraryView` filtrando por la categoría seleccionada.
    *   Comunicación con el backend: GET a `/categories/`.

### `frontend/src/ToolsView.js`

Ofrece herramientas útiles relacionadas con la gestión de libros. Actualmente, un convertidor de EPUB a PDF.

*   **Propósito**: Proporcionar utilidades adicionales para los libros, como la conversión de formatos.
*   **Componente `EpubToPdfConverter`**:
    *   **Estado**: `selectedFile`, `message`, `isLoading`.
    *   **Interacciones**: Permite seleccionar un archivo EPUB (o arrastrar y soltar), y un botón para iniciar la conversión. Tras la conversión, inicia la descarga del PDF resultante.
    *   Comunicación con el backend: POST a `/tools/convert-epub-to-pdf`.

### `frontend/src/ReaderView.js`

Un lector de libros EPUB integrado en la aplicación.

*   **Propósito**: Permitir a los usuarios leer archivos EPUB directamente en el navegador.
*   **Estado**:
    *   `location`: `string | null`, la ubicación actual de lectura en el EPUB (CFIs).
    *   `epubData`: `ArrayBuffer | null`, el contenido binario del archivo EPUB.
    *   `isLoading`: `boolean`, indica si el libro se está cargando.
    *   `error`: `string`, mensaje de error si la carga del libro falla.
*   **Props**: Ninguno, usa `useParams` para obtener `bookId`.
*   **Efectos**:
    *   `useEffect` al montar/cambiar `bookId`: Realiza una llamada a la API (`/books/download/{bookId}`) para obtener el contenido del EPUB como `ArrayBuffer`.
*   **Interacciones**:
    *   La `ReactReader` (librería externa) maneja la interacción con el libro (paginación, desplazamiento).
    *   Comunicación con el backend: GET a `/books/download/{bookId}`.

### `frontend/src/RagView.js`

La interfaz para interactuar con la funcionalidad de Retrieval Augmented Generation (RAG).

*   **Propósito**: Permite a los usuarios seleccionar un libro de su biblioteca, indexarlo en RAG y luego chatear con una IA sobre su contenido.
*   **Estado**:
    *   `message`, `isLoading`, `bookId` (del libro activo para chatear), `chatHistory`, `currentQuery`.
    *   `libraryBooks`: `Array`, lista de libros de la biblioteca para seleccionar.
    *   `selectedLibraryId`: `string`, el ID del libro seleccionado de la biblioteca.
    *   `libStatus`: `Object`, incluye `loading`, `indexed`, `vector_count`, `error` para el estado RAG del libro seleccionado.
    *   `actionsBusy`: `boolean`, bloquea acciones pesadas (indexación).
    *   `refreshing`: `boolean`, para el refresco de estado (no bloquea el chat).
    *   `searchTerm`, `searching`, `searchResults`, `resultsOpen`: Para buscar libros en la biblioteca.
    *   `mode`: `string`, el modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`).
    *   `selectedBook`: `Object | null`, el libro seleccionado de la búsqueda.
*   **Refs**: `inputRef` para el campo de texto del chat, `chatHistoryRef` para el área de historial de chat para auto-scroll.
*   **Efectos**:
    *   `useEffect` al montar: Carga `libraryBooks`.
    *   `useEffect` para `searchTerm`: Implementa un debounce para la búsqueda de libros.
    *   `useEffect` para `chatHistory`, `isLoading`: Auto-scroll del chat.
    *   `useEffect` para `selectedLibraryId`: Llama a `checkLibraryStatus` para el libro seleccionado.
*   **Interacciones**:
    *   Buscar/seleccionar libro de la biblioteca.
    *   Botones "Comprobar RAG", "Indexar antes de charlar", "Reindexar", "Chatear" para gestionar el estado RAG del libro.
    *   `handleQuerySubmit`: Envía la pregunta del usuario a la API RAG (`/rag/query/`) y actualiza el historial de chat.
    *   Selector de `mode`: Permite al usuario elegir cómo la IA debe integrar el contexto del libro y su conocimiento general.
    *   Comunicación con el backend: GET a `/books/`, GET a `/rag/status/{bookId}`, POST a `/rag/index/{bookId}`, POST a `/rag/query/`.

### `frontend/src/EditBookModal.js`

Un componente modal para editar los detalles de un libro.

*   **Propósito**: Permitir a los usuarios actualizar el título, autor y la portada de un libro existente.
*   **Estado**:
    *   `title`, `author`, `coverImage` (archivo de imagen seleccionado), `isSaving`.
*   **Props**:
    *   `book`: `Object`, el libro a editar.
    *   `onClose`: `Function`, para cerrar el modal.
    *   `onBookUpdated`: `Function`, callback para notificar a la vista padre sobre un libro actualizado.
*   **Efectos**:
    *   `useEffect` al cambiar `book`: Inicializa el estado con los datos del libro proporcionado.
*   **Interacciones**:
    *   Formulario para editar título, autor y seleccionar nueva portada.
    *   Botones "Cancelar" y "Guardar Cambios".
    *   Comunicación con el backend: PUT a `/books/{book.id}` con un `FormData`.

### `frontend/src/ErrorBoundary.js`

Un componente React de límite de error que captura errores en la UI.

*   **Propósito**: Mejorar la robustez de la aplicación al capturar errores de JavaScript en los componentes hijos y mostrar una UI de fallback en lugar de una pantalla en blanco.
*   **Estado**: `hasError`, `error`.
*   **Métodos del ciclo de vida**:
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para indicar que se ha producido un error.
    *   `componentDidCatch(error, info)`: Registra el error en la consola.

### `frontend/src/config.js`

Archivo de configuración para la URL del backend.

*   **Propósito**: Centralizar la URL del API para facilitar el cambio entre entornos de desarrollo y producción.
*   **Exporta**: `API_URL`, que toma el valor de la variable de entorno `REACT_APP_API_URL` o por defecto `http://localhost:8001`.

## 5. Flujo de Datos y API

El flujo de datos en "Mi Librería Inteligente" se centra en la gestión de libros y la interacción con la IA.

### Flujo de Subida de un Libro:

1.  **Frontend (`UploadView.js`)**: El usuario selecciona uno o varios archivos (PDF/EPUB) o los arrastra a la zona de "drop".
2.  **Frontend (`UploadView.js`)**: Para cada archivo, crea un `FormData` y envía una solicitud **`POST` a `/upload-book/`**.
3.  **Backend (`main.py` - `upload_book`)**:
    *   Recibe el `UploadFile`.
    *   Guarda el archivo en el directorio `backend/books/`.
    *   Detecta la extensión (`.pdf` o `.epub`) y llama a `process_pdf` o `process_epub` (en `main.py`) para extraer el texto inicial y buscar una imagen de portada. La portada se guarda en `backend/static/covers/`.
    *   Llama a `analyze_with_gemini` (en `main.py`) con el texto extraído para que la IA identifique el título, autor y categoría.
    *   Realiza una validación de calidad: Si la IA no puede identificar el título ni el autor, el archivo subido se elimina y se devuelve un error 422.
    *   Si el análisis es exitoso, llama a `crud.create_book` (en `backend/crud.py`) para guardar los metadatos del libro (título, autor, categoría, URL de portada, ruta del archivo) en la base de datos SQLite.
    *   Devuelve el objeto `Book` (esquema `schemas.Book`) al frontend.
4.  **Frontend (`UploadView.js`)**: Muestra el estado y el mensaje (`success` o `error`) para cada archivo subido.

### Flujo de Consulta RAG:

1.  **Frontend (`RagView.js`)**: El usuario selecciona un libro de la biblioteca y pulsa "Indexar antes de charlar" (si no está indexado).
2.  **Frontend (`RagView.js`)**: Envía una solicitud **`POST` a `/rag/index/{book_id}`**.
3.  **Backend (`main.py` - `index_existing_book_for_rag`)**:
    *   Recupera la ruta del archivo del libro de la base de datos.
    *   Llama a `rag.process_book_for_rag` (en `backend/rag.py`).
4.  **Backend (`rag.py` - `process_book_for_rag`)**:
    *   Extrae el texto completo del libro (`extract_text`).
    *   Divide el texto en `chunk_text`s.
    *   Para cada chunk, genera un embedding (`get_embedding`) usando Google Gemini.
    *   Almacena los chunks y sus embeddings en ChromaDB.
5.  **Frontend (`RagView.js`)**: El usuario introduce una pregunta en el chat y la envía.
6.  **Frontend (`RagView.js`)**: Envía una solicitud **`POST` a `/rag/query/`** con la pregunta (`query`), el `book_id` y el `mode` de respuesta.
7.  **Backend (`main.py` - `query_rag_endpoint`)**:
    *   Llama a `rag.query_rag` (en `backend/rag.py`).
8.  **Backend (`rag.py` - `query_rag`)**:
    *   Genera un embedding para la pregunta del usuario.
    *   Realiza una búsqueda de similitud en ChromaDB para el `book_id` especificado, recuperando los chunks más relevantes.
    *   Construye un prompt para el modelo Gemini incluyendo la pregunta del usuario, los chunks recuperados (contexto del libro), y opcionalmente metadatos del libro o de la biblioteca.
    *   Utiliza el modelo generativo de Gemini para producir una respuesta.
    *   Devuelve la respuesta generada al frontend.
9.  **Frontend (`RagView.js`)**: Muestra la respuesta de la IA en el historial del chat.

### Principales Endpoints de la API (definidos en `backend/main.py`):

| Método | Ruta                      | Descripción                                                                 |
| :----- | :------------------------ | :-------------------------------------------------------------------------- |
| `POST` | `/upload-book/`           | Sube y procesa un nuevo libro (PDF/EPUB) para añadirlo a la biblioteca.     |
| `GET`  | `/books/`                 | Lista todos los libros, con opciones de filtrado y búsqueda.                |
| `GET`  | `/books/count`            | Obtiene el número total de libros en la biblioteca.                        |
| `GET`  | `/books/search/`          | Busca libros por un título parcial.                                         |
| `GET`  | `/categories/`            | Obtiene una lista de todas las categorías únicas de libros.                 |
| `GET`  | `/books/download/{book_id}` | Descarga o visualiza un archivo de libro.                                   |
| `PUT`  | `/books/{book_id}`        | Actualiza los detalles de un libro (título, autor, portada).                |
| `DELETE`| `/books/{book_id}`        | Elimina un libro y sus archivos asociados, incluyendo el índice RAG.       |
| `DELETE`| `/categories/{category_name}` | Elimina una categoría y todos sus libros asociados.                         |
| `POST` | `/api/books/{book_id}/convert` | Convierte un EPUB existente a PDF y lo añade como un nuevo libro.           |
| `POST` | `/tools/convert-epub-to-pdf` | Convierte un archivo EPUB subido a PDF y devuelve un enlace de descarga temporal. |
| `POST` | `/rag/index/{book_id}`    | Indexa un libro existente en el sistema RAG para consultas con IA.          |
| `GET`  | `/rag/status/{book_id}`   | Devuelve el estado de indexación RAG de un libro.                           |
| `POST` | `/rag/query/`             | Realiza una consulta a la IA sobre el contenido de un libro indexado.       |
| `GET`  | `/rag/estimate/book/{book_id}` | Estima el coste/tamaño de indexación RAG para un libro.                     |
| `POST` | `/rag/reindex/category/{category_name}` | (Re)indexa todos los libros de una categoría en RAG.                  |
| `POST` | `/rag/reindex/all`        | (Re)indexa todos los libros de la biblioteca en RAG.                       |
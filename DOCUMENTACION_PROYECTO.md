```markdown
# Documentación del Proyecto: Mi Librería Inteligente

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web diseñada para gestionar y explorar una colección de libros digitales. Combina una interfaz de usuario moderna (frontend) con un potente backend que utiliza inteligencia artificial para catalogar, buscar y permitir la interacción conversacional con el contenido de los libros.

**Características Principales:**
*   **Gestión de Biblioteca:** Sube, visualiza y organiza libros digitales (PDF y EPUB).
*   **Catalogación Inteligente:** Utiliza modelos de IA (Google Gemini) para extraer automáticamente el título, autor y categoría de los libros recién subidos.
*   **Visualización y Descarga:** Permite leer libros EPUB directamente en el navegador y descargar archivos PDF/EPUB.
*   **Herramientas Útiles:** Incluye un conversor de EPUB a PDF.
*   **Chat con IA (RAG):** Indexa el contenido de los libros en una base de datos vectorial (ChromaDB) y permite a los usuarios hacer preguntas sobre el libro, obteniendo respuestas generadas por IA (Google Gemini) contextualizadas al contenido del libro. Soporta diferentes modos de respuesta (estricto, equilibrado, abierto).
*   **Filtrado y Búsqueda:** Busca libros por título, autor o categoría.

**Arquitectura General:**
La aplicación sigue una arquitectura cliente-servidor, dividida en dos componentes principales:

*   **Frontend (Cliente):** Desarrollado con **React**, proporciona la interfaz de usuario. Se encarga de la presentación de datos, la interacción del usuario y la comunicación con el backend a través de peticiones HTTP.
*   **Backend (Servidor):** Desarrollado con **Python** utilizando el framework **FastAPI**. Es el corazón de la lógica de negocio, gestiona la base de datos, la interacción con los modelos de IA y el procesamiento de archivos.
    *   **Base de Datos:** Utiliza **SQLite** para el almacenamiento de metadatos de los libros, gestionado con **SQLAlchemy ORM** y migraciones con **Alembic**.
    *   **Modelos de IA:** Integración con **Google Gemini** para la extracción de metadatos y la generación de respuestas en el sistema RAG.
    *   **Base de Datos Vectorial para RAG:** Utiliza **ChromaDB** para almacenar los embeddings (representaciones vectoriales) de los fragmentos de texto de los libros, permitiendo una recuperación semántica eficiente.
    *   **Procesamiento de Archivos:** Librerías como `PyPDF2`, `fitz` (PyMuPDF), `ebooklib` y `weasyprint` se utilizan para la extracción de texto, portadas y conversión de formatos.

## 2. Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas y archivos clave:

```
.
├── backend/
│   ├── alembic/                    # Directorio para las migraciones de base de datos de Alembic
│   │   └── versions/               # Scripts de migración
│   ├── static/                     # Archivos estáticos servidos por FastAPI (e.g., portadas de libros)
│   │   └── covers/                 # Imágenes de portada de libros
│   ├── temp_books/                 # Archivos temporales generados (e.g., PDFs convertidos, archivos subidos para RAG)
│   ├── books/                      # Ubicación donde se almacenan los archivos de libros originales
│   ├── tests/                      # Pruebas unitarias e integración para el backend
│   ├── tests_curated/              # Pruebas adicionales o curadas para el backend
│   ├── __init__.py                 # Marca el directorio como un paquete Python
│   ├── crud.py                     # Operaciones CRUD (Crear, Leer, Actualizar, Borrar) para la base de datos
│   ├── database.py                 # Configuración de la base de datos SQLAlchemy
│   ├── main.py                     # Aplicación principal FastAPI y definición de endpoints
│   ├── models.py                   # Modelos ORM de SQLAlchemy para la base de datos
│   ├── rag.py                      # Lógica para Retrieval Augmented Generation (RAG) con ChromaDB y Gemini
│   ├── schemas.py                  # Esquemas de Pydantic para validación de datos de entrada/salida de la API
│   └── utils.py                    # Funciones de utilidad (e.g., configuración de la API de Gemini)
├── frontend/
│   ├── public/                     # Archivos públicos para el frontend (e.g., index.html)
│   ├── src/                        # Código fuente de la aplicación React
│   │   ├── App.css                 # Estilos CSS globales
│   │   ├── App.js                  # Componente principal de la aplicación React y enrutamiento
│   │   ├── CategoriesView.css
│   │   ├── CategoriesView.js       # Vista para mostrar y gestionar categorías
│   │   ├── config.js               # Archivo de configuración para el frontend (e.g., URL del API)
│   │   ├── ErrorBoundary.js        # Componente de React para manejo de errores de UI
│   │   ├── Header.css
│   │   ├── Header.js               # Componente de encabezado y navegación
│   │   ├── index.css
│   │   ├── index.js                # Punto de entrada de la aplicación React
│   │   ├── LibraryView.css
│   │   ├── LibraryView.js          # Vista principal de la biblioteca (listado de libros)
│   │   ├── RagView.css
│   │   ├── RagView.js              # Vista para la interacción conversacional RAG
│   │   ├── ReaderView.css
│   │   ├── ReaderView.js           # Vista para leer libros EPUB
│   │   ├── ToolsView.css
│   │   ├── ToolsView.js            # Vista para herramientas adicionales (e.g., conversor EPUB a PDF)
│   │   └── UploadView.js           # Vista para subir nuevos libros
│   ├── package.json                # Dependencias y scripts del frontend
│   └── ...                         # Otros archivos de configuración de React
├── library.db                      # Archivo de la base de datos SQLite
├── .env                            # Variables de entorno (no versionado)
├── README.md                       # Archivo README del proyecto
└── ...                             # Otros archivos de configuración del proyecto (e.g., .gitignore)
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/schemas.py`

Define los modelos de datos utilizando Pydantic para la validación y serialización de las solicitudes y respuestas de la API.

*   **`class BookBase(BaseModel)`**: Esquema base para un libro, incluye los campos esenciales para crear o representar un libro sin el ID de la base de datos.
    *   `title` (str): Título del libro.
    *   `author` (str): Autor del libro.
    *   `category` (str): Categoría del libro.
    *   `cover_image_url` (str | None): URL de la imagen de portada, opcional.
    *   `file_path` (str): Ruta del archivo en el sistema de ficheros.
*   **`class Book(BookBase)`**: Extiende `BookBase` añadiendo el campo `id`. Se usa para representar un libro ya existente en la base de datos.
    *   `id` (int): Identificador único del libro en la base de datos.
    *   `Config.from_attributes = True`: Permite que Pydantic lea los atributos de un objeto ORM.
*   **`class ConversionResponse(BaseModel)`**: Respuesta para la conversión de EPUB a PDF.
    *   `download_url` (str): URL donde se puede descargar el PDF convertido.
*   **`class RagUploadResponse(BaseModel)`**: Respuesta al subir un libro para indexado RAG.
    *   `book_id` (str): ID asignado al libro en el sistema RAG.
    *   `message` (str): Mensaje de confirmación.
*   **`class RagQuery(BaseModel)`**: Esquema para una consulta al sistema RAG.
    *   `query` (str): La pregunta del usuario.
    *   `book_id` (str): ID del libro sobre el que se consulta (corresponde al `id` de `models.Book`).
    *   `mode` (str | None): Modo de la consulta (`'strict'`, `'balanced'`, `'open'`).
*   **`class RagQueryResponse(BaseModel)`**: Respuesta de una consulta al sistema RAG.
    *   `response` (str): La respuesta generada por la IA.

### `backend/crud.py`

Contiene funciones para interactuar con la base de datos, realizando operaciones CRUD (Create, Read, Update, Delete) sobre el modelo `Book`.

*   **`get_book_by_path(db: Session, file_path: str)`**:
    *   Propósito: Obtiene un libro por su ruta de archivo única.
    *   Parámetros: `db` (sesión de BD), `file_path` (ruta del archivo).
    *   Retorna: Objeto `models.Book` o `None` si no se encuentra.
*   **`get_book_by_title(db: Session, title: str)`**:
    *   Propósito: Obtiene un libro por su título exacto.
    *   Parámetros: `db`, `title`.
    *   Retorna: Objeto `models.Book` o `None`.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**:
    *   Propósito: Busca libros por un título parcial (insensible a mayúsculas/minúsculas).
    *   Parámetros: `db`, `title` (parte del título), `skip`, `limit` (para paginación).
    *   Retorna: Lista de objetos `models.Book`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**:
    *   Propósito: Obtiene una lista de libros, con opciones de filtrado.
    *   Parámetros: `db`, `category` (filtrar por categoría), `search` (búsqueda general en título, autor, categoría), `author` (filtrar por autor).
    *   Retorna: Lista de objetos `models.Book`.
*   **`get_categories(db: Session) -> list[str]`**:
    *   Propósito: Obtiene una lista de todas las categorías de libros únicas.
    *   Parámetros: `db`.
    *   Retorna: Lista de cadenas (`str`) con los nombres de las categorías.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**:
    *   Propósito: Crea un nuevo libro en la base de datos.
    *   Parámetros: `db`, `title`, `author`, `category`, `cover_image_url`, `file_path`.
    *   Retorna: El objeto `models.Book` recién creado.
*   **`delete_book(db: Session, book_id: int)`**:
    *   Propósito: Elimina un libro por su ID, incluyendo sus archivos asociados (libro y portada).
    *   Parámetros: `db`, `book_id`.
    *   Retorna: El objeto `models.Book` eliminado o `None`.
*   **`delete_books_by_category(db: Session, category: str)`**:
    *   Propósito: Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados.
    *   Parámetros: `db`, `category`.
    *   Retorna: Número de libros eliminados.
*   **`get_books_count(db: Session) -> int`**:
    *   Propósito: Obtiene el número total de libros en la base de datos.
    *   Parámetros: `db`.
    *   Retorna: Un entero con el conteo total.

### `backend/database.py`

Configura la conexión a la base de datos SQLAlchemy.

*   **`_base_dir`, `_db_path`, `SQLALCHEMY_DATABASE_URL`**: Definen la ruta a la base de datos SQLite (`library.db`) en la raíz del proyecto.
*   **`engine`**: El motor de la base de datos SQLAlchemy, configurado para SQLite. `connect_args={"check_same_thread": False}` es necesario para SQLite en entornos multihilo como FastAPI.
*   **`SessionLocal`**: Un constructor de sesiones de base de datos. Cada sesión es una instancia de `Session`.
*   **`Base`**: La clase base declarativa de SQLAlchemy, de la que heredan los modelos ORM.

### `backend/utils.py`

Provee funciones de utilidad generales.

*   **`configure_genai()`**:
    *   Propósito: Carga las variables de entorno desde `.env` y configura la API de Google Generative AI (Gemini) con la clave API.
    *   Lógica: Busca `GOOGLE_API_KEY` o `GEMINI_API_KEY`. Lanza un `ValueError` si ninguna clave es encontrada.
    *   Parámetros: None.
    *   Retorna: None.

### `backend/models.py`

Define el modelo ORM de SQLAlchemy para la tabla `books`.

*   **`class Book(Base)`**: Representa un libro en la base de datos.
    *   `__tablename__ = "books"`: Nombre de la tabla en la base de datos.
    *   `__table_args__ = {'extend_existing': True}`: Permite redefinir la tabla en caso de hot-reloading (útil en desarrollo/pruebas).
    *   `id = Column(Integer, primary_key=True, index=True)`: Clave primaria, autoincremental.
    *   `title = Column(String, index=True)`: Título del libro.
    *   `author = Column(String, index=True)`: Autor del libro.
    *   `category = Column(String, index=True)`: Categoría del libro.
    *   `cover_image_url = Column(String, nullable=True)`: URL a la imagen de portada, puede ser nulo.
    *   `file_path = Column(String, unique=True)`: Ruta al archivo original del libro, debe ser única.

### `backend/rag.py`

Implementa la lógica de Retrieval Augmented Generation (RAG) para permitir conversaciones sobre el contenido de los libros. Utiliza Gemini para embeddings y generación, y ChromaDB como base de datos vectorial.

*   **`_ensure_init()`**:
    *   Propósito: Inicializa de forma lazy el entorno de Gemini y el cliente de ChromaDB.
    *   Lógica: Se ejecuta una sola vez. Carga `.env`, configura Gemini si `DISABLE_AI` no está activado, e inicializa ChromaDB para persistir el índice en disco.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**:
    *   Propósito: Genera un embedding (representación vectorial) para un texto dado utilizando el modelo de embedding de Gemini.
    *   Parámetros: `text` (el texto a embeber), `task_type` (tipo de tarea para el embedding).
    *   Retorna: Una lista de floats (el embedding) o una lista de ceros si la IA está deshabilitada o el texto está vacío.
*   **`extract_text_from_pdf(file_path: str)`**:
    *   Propósito: Extrae texto de un archivo PDF.
    *   Parámetros: `file_path`.
    *   Retorna: El texto extraído como una cadena.
*   **`extract_text_from_epub(file_path: str)`**:
    *   Propósito: Extrae texto de un archivo EPUB.
    *   Parámetros: `file_path`.
    *   Retorna: El texto extraído como una cadena.
*   **`extract_text(file_path: str)`**:
    *   Propósito: Función unificada para extraer texto de PDF o EPUB.
    *   Parámetros: `file_path`.
    *   Retorna: El texto extraído. Lanza `ValueError` si el tipo de archivo no es soportado.
*   **`chunk_text(text: str, max_tokens: int = 1000)`**:
    *   Propósito: Divide un texto largo en fragmentos más pequeños, basándose en un número máximo de tokens (utiliza `tiktoken` como aproximación).
    *   Parámetros: `text`, `max_tokens`.
    *   Retorna: Lista de cadenas, cada una siendo un fragmento.
*   **`_has_index_for_book(book_id: str)`**:
    *   Propósito: Comprueba si un libro específico ya tiene vectores indexados en ChromaDB.
    *   Parámetros: `book_id` (el ID del libro usado en RAG, que es el `id` de BD).
    *   Retorna: `True` si tiene índice, `False` en caso contrario.
*   **`delete_book_from_rag(book_id: str)`**:
    *   Propósito: Elimina todos los vectores asociados a un `book_id` de ChromaDB.
    *   Parámetros: `book_id`.
    *   Retorna: None.
*   **`get_index_count(book_id: str)`**:
    *   Propósito: Devuelve el número de vectores almacenados para un `book_id` dado.
    *   Parámetros: `book_id`.
    *   Retorna: Un entero.
*   **`has_index(book_id: str)`**:
    *   Propósito: Alias público de `get_index_count(book_id) > 0`.
    *   Parámetros: `book_id`.
    *   Retorna: `True` si tiene índice, `False` en caso contrario.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**:
    *   Propósito: Extrae texto de un libro, lo divide en fragmentos, genera embeddings y los almacena en ChromaDB.
    *   Parámetros: `file_path` (ruta al archivo del libro), `book_id` (ID del libro), `force_reindex` (si es `True`, borra y vuelve a indexar).
    *   Retorna: None.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**:
    *   Propósito: Estima el número de tokens y fragmentos para un archivo. Útil para predecir costos de indexado.
    *   Parámetros: `file_path`, `max_tokens` (tamaño de fragmento).
    *   Retorna: Diccionario con `tokens` y `chunks`.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**:
    *   Propósito: Estima el número de tokens y fragmentos para una lista de archivos.
    *   Parámetros: `file_paths`, `max_tokens`.
    *   Retorna: Diccionario con `tokens`, `chunks` y `files` contados.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**:
    *   Propósito: Consulta el sistema RAG para obtener respuestas basadas en el contenido del libro.
    *   Parámetros: `query` (la pregunta del usuario), `book_id` (el libro a consultar), `mode` (estrategia de respuesta: 'strict', 'balanced', 'open'), `metadata` (metadatos del libro para enriquecer el prompt), `library` (contexto adicional de la biblioteca, e.g., otros libros del autor).
    *   Retorna: La respuesta generada por la IA como una cadena.

### `backend/main.py`

Archivo principal de la aplicación FastAPI. Contiene la configuración de la API, las dependencias de base de datos y todos los endpoints de la API.

*   **`base_dir`, `API_KEY`, `AI_ENABLED`**: Configuración de rutas base, clave API de Gemini y estado de la IA.
*   **`models.Base.metadata.create_all(bind=database.engine)`**: Inicializa las tablas de la base de datos si no existen.
*   **`async def analyze_with_gemini(text: str) -> dict`**:
    *   Propósito: Utiliza Google Gemini para analizar las primeras páginas de un libro y extraer su título, autor y categoría.
    *   Parámetros: `text` (texto extraído del libro).
    *   Retorna: Un diccionario con `title`, `author` y `category`.
*   **`def process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
    *   Propósito: Procesa un archivo PDF para extraer texto inicial y una imagen de portada.
    *   Parámetros: `file_path`, `covers_dir_fs` (directorio para guardar portadas), `covers_url_prefix` (prefijo URL para las portadas).
    *   Retorna: Un diccionario con `text` (texto extraído) y `cover_image_url` (URL de la portada).
*   **`def process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
    *   Propósito: Procesa un archivo EPUB para extraer texto inicial y una imagen de portada, con lógica de fallback.
    *   Parámetros: `file_path`, `covers_dir_fs`, `covers_url_prefix`.
    *   Retorna: Un diccionario con `text` (texto extraído) y `cover_image_url` (URL de la portada).
*   **`app = FastAPI()`**: Instancia principal de la aplicación FastAPI.
*   **Constantes de Rutas (`STATIC_DIR_FS`, `BOOKS_DIR_FS`, etc.)**: Rutas absolutas a los directorios de archivos estáticos, libros, temporales y portadas.
*   **CORS Middleware**: Configuración para permitir solicitudes desde el frontend React, con orígenes configurables.
*   **`def get_db()`**:
    *   Propósito: Dependencia de FastAPI para obtener una sesión de base de datos. Asegura que la sesión se cierre correctamente.
    *   Retorna: Un generador que produce una sesión de SQLAlchemy.
*   **Endpoints de la API**: (Se resumen en la sección "5. Flujo de Datos y API")

### `backend/__init__.py`

Este archivo es un marcador que indica que el directorio `backend` es un paquete Python. No contiene código funcional específico para documentar en este contexto.

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

Este es un script de migración de Alembic para la base de datos. Define cómo crear y revertir la tabla `books`.

*   **`revision`, `down_revision`, `branch_labels`, `depends_on`**: Metadatos de la migración.
*   **`upgrade()`**:
    *   Propósito: Crea la tabla `books` con las columnas `id`, `title`, `author`, `category`, `cover_image_url` y `file_path`. Define `id` como clave primaria y `file_path` como único. Crea índices en `id`, `title`, `author` y `category` para mejorar el rendimiento de las consultas.
*   **`downgrade()`**:
    *   Propósito: Elimina la tabla `books` y sus índices, revirtiendo la migración.

## 4. Análisis Detallado del Frontend (React)

La aplicación frontend está construida con React y utiliza `react-router-dom` para el enrutamiento y `react-reader` para la visualización de EPUB.

### `frontend/src/App.js`

El componente raíz de la aplicación React.

*   **Propósito:** Configura el enrutamiento principal de la aplicación usando `BrowserRouter` y `Routes`, y renderiza los componentes de vista según la URL.
*   **Estado (State):** Ninguno específico de `App.js`.
*   **Propiedades (Props):** Ninguna.
*   **Efectos (Effects):** Ninguno.
*   **Interacciones:** Maneja la navegación entre las diferentes secciones de la aplicación (`/`, `/upload`, `/etiquetas`, `/herramientas`, `/rag`, `/leer/:bookId`).

### `frontend/src/Header.js`

El componente de encabezado global que incluye la navegación y muestra el recuento de libros.

*   **Propósito:** Proporcionar una barra de navegación consistente en toda la aplicación y mostrar un contador dinámico de libros.
*   **Estado:**
    *   `menuOpen` (boolean): Controla la visibilidad del menú de hamburguesa en dispositivos móviles.
    *   `bookCount` (number): Número total de libros en la biblioteca.
    *   `errorMessage` (string | null): Mensaje de error si falla la carga del contador de libros.
*   **Propiedades:** Ninguna.
*   **Efectos:**
    *   `useEffect`: Fetches `bookCount` desde el backend al montar el componente y luego cada 10 minutos.
*   **Interacciones:**
    *   Botón de hamburguesa: Alterna el estado `menuOpen`.
    *   `NavLink`s: Permiten la navegación a diferentes rutas, cerrando el menú si está abierto.
    *   Se comunica con el backend (`GET /books/count`) para obtener el número de libros.

### `frontend/src/LibraryView.js`

La vista principal que muestra la colección de libros, permite buscar, filtrar y realizar acciones sobre ellos.

*   **Propósito:** Listar los libros de la biblioteca, ofrecer opciones de búsqueda y filtrado por categoría y autor, y permitir la interacción con cada libro (leer, descargar, eliminar).
*   **Estado:**
    *   `books` (array): Lista de objetos libro obtenidos del backend.
    *   `searchParams` (URLSearchParams): Objeto para gestionar los parámetros de la URL (filtros de categoría, autor).
    *   `searchTerm` (string): Término de búsqueda general introducido por el usuario.
    *   `debouncedSearchTerm` (string): Versión "debounced" de `searchTerm` para evitar peticiones excesivas.
    *   `error` (string): Mensaje de error si falla la carga de libros.
    *   `loading` (boolean): Indica si la vista está cargando datos.
    *   `isMobile` (boolean): Detecta si el dispositivo es móvil para mostrar botones de descarga condicionalmente.
*   **Propiedades:** Ninguna.
*   **Efectos:**
    *   `useDebounce`: Custom hook para retrasar la ejecución de la búsqueda.
    *   `useEffect`: Se encarga de llamar a `fetchBooks` cuando `debouncedSearchTerm` o `searchParams` cambian. También detecta el tamaño de la ventana para `isMobile`.
*   **Interacciones:**
    *   Barra de búsqueda: Actualiza `searchTerm`.
    *   Clic en autor/categoría: Actualiza `searchParams` para filtrar la lista.
    *   Botón "Eliminar libro": Llama a `handleDeleteBook` para borrar un libro (`DELETE /books/{bookId}`).
    *   Botones "Abrir PDF" / "Leer EPUB": Navegan a las vistas de lectura o descargan el archivo (`GET /books/download/{bookId}`).
    *   Se comunica con el backend (`GET /books/`, `DELETE /books/{bookId}`).
*   **`BookCover` Componente:** Muestra la portada del libro. Si la URL de la portada no está disponible o falla, muestra una portada genérica con la inicial del título.

### `frontend/src/UploadView.js`

La vista para subir nuevos libros a la biblioteca.

*   **Propósito:** Permitir a los usuarios subir archivos PDF o EPUB para ser procesados por el backend (análisis con IA, almacenamiento).
*   **Estado:**
    *   `filesToUpload` (array): Lista de objetos `{file, status, message}` para cada archivo a subir.
    *   `isUploading` (boolean): Indica si hay archivos en proceso de subida.
*   **Propiedades:** Ninguna.
*   **Efectos:** Ninguno.
*   **Interacciones:**
    *   Arrastrar y soltar archivos (`handleDrop`, `handleDragOver`).
    *   Botón "Seleccionar Archivos": Abre el selector de archivos (`handleFileChange`).
    *   Botón "Subir X Archivo(s)": Inicia la subida de los archivos pendientes (`handleUpload`).
    *   Muestra el estado de subida y procesamiento de cada archivo.
    *   Botón "Ir a la Biblioteca": Navega a la vista principal una vez que todas las subidas han terminado.
    *   Se comunica con el backend (`POST /upload-book/`).

### `frontend/src/ToolsView.js`

Una vista que agrupa herramientas adicionales para la biblioteca. Actualmente, solo incluye el conversor de EPUB a PDF.

*   **Propósito:** Servir como contenedor para diversas utilidades.
*   **Estado:** Ninguno directamente en `ToolsView`.
*   **Propiedades:** Ninguna.
*   **Efectos:** Ninguno.
*   **Interacciones:** Simplemente renderiza `EpubToPdfConverter`.
*   **`EpubToPdfConverter` Componente:**
    *   **Propósito:** Permite al usuario subir un archivo EPUB y convertirlo a PDF a través del backend.
    *   **Estado:**
        *   `selectedFile` (File | null): El archivo EPUB seleccionado para la conversión.
        *   `message` (string): Mensajes informativos para el usuario (progreso, errores).
        *   `isLoading` (boolean): Indica si la conversión está en curso.
    *   **Efectos:** Ninguno.
    *   **Interacciones:**
        *   Arrastrar y soltar archivos (`handleDrop`, `handleDragOver`).
        *   Botón "Seleccionar archivo": Permite elegir un archivo EPUB (`handleFileChange`).
        *   Botón "Convertir a PDF": Inicia la conversión (`handleConvert`) y, si tiene éxito, dispara la descarga del PDF resultante (`POST /tools/convert-epub-to-pdf`).
        *   Muestra el progreso y los mensajes de éxito/error.

### `frontend/src/ReaderView.js`

Una vista dedicada a la lectura de libros en formato EPUB.

*   **Propósito:** Renderizar libros EPUB directamente en el navegador utilizando la librería `react-reader`.
*   **Estado:**
    *   `location` (string | null): Ubicación actual en el EPUB (EPUB CFI).
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB.
    *   `isLoading` (boolean): Indica si el libro se está cargando.
    *   `error` (string): Mensaje de error si falla la carga.
*   **Propiedades:**
    *   `bookId` (string): Obtenido de los parámetros de la URL (`/leer/:bookId`).
*   **Efectos:**
    *   `useEffect`: Fetches los datos binarios del libro EPUB (`GET /books/download/{bookId}`) cuando el componente se monta o `bookId` cambia.
*   **Interacciones:**
    *   `react-reader`: La librería externa maneja la interfaz de lectura (paginación, navegación). El estado `location` se actualiza cuando el usuario cambia de página.

### `frontend/src/RagView.js`

La vista que permite a los usuarios conversar con el contenido de un libro utilizando el sistema RAG.

*   **Propósito:** Proporcionar una interfaz de chat interactiva para consultar libros indexados con IA, permitiendo buscar y seleccionar libros, indexarlos y chatear con ellos.
*   **Estado:**
    *   `message` (string): Mensajes generales para el usuario.
    *   `isLoading` (boolean): Indica si se está esperando una respuesta de la IA.
    *   `bookId` (string | null): ID del libro actualmente seleccionado para el chat (después de ser indexado).
    *   `chatHistory` (array): Lista de objetos `{sender, text}` que representan los mensajes del chat.
    *   `currentQuery` (string): El texto de la pregunta actual del usuario.
    *   `libraryBooks` (array): Lista de todos los libros disponibles en la biblioteca.
    *   `selectedLibraryId` (string): El ID del libro seleccionado de la biblioteca para el pre-procesamiento RAG.
    *   `libStatus` (object): Estado del libro seleccionado en el sistema RAG (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy` (boolean): Bloquea acciones de indexado/reindexado mientras se procesan.
    *   `refreshing` (boolean): Indica que se está refrescando el estado RAG.
    *   `searchTerm` (string): Término para buscar libros en la biblioteca.
    *   `searching` (boolean): Indica si la búsqueda de libros está activa.
    *   `searchResults` (array): Resultados de la búsqueda de libros.
    *   `resultsOpen` (boolean): Controla la visibilidad de los resultados de búsqueda.
    *   `mode` (string): Modo de respuesta del RAG ('strict', 'balanced', 'open').
    *   `selectedBook` (object | null): Objeto completo del libro seleccionado.
*   **Propiedades:** Ninguna.
*   **Efectos:**
    *   `useEffect` (carga inicial): Fetches la lista completa de libros (`GET /books/`).
    *   `useEffect` (búsqueda): Debounces `searchTerm` y busca libros en la biblioteca.
    *   `useEffect` (scroll): Auto-scrollea el historial del chat.
    *   `useEffect` (estado RAG): Llama a `checkLibraryStatus` cuando `selectedLibraryId` cambia.
*   **Interacciones:**
    *   Campo de búsqueda de libros: Para encontrar libros existentes en la biblioteca.
    *   Lista de resultados de búsqueda: Permite seleccionar un libro.
    *   Botones "Comprobar RAG", "Indexar antes de charlar", "Reindexar": Interactúan con el backend para gestionar el índice RAG del libro (`GET /rag/status/{book_id}`, `POST /rag/index/{book_id}`).
    *   Botón "Chatear": Habilita la interfaz de chat si el libro está indexado.
    *   Selección de `mode`: Cambia la estrategia de respuesta de la IA.
    *   Área de texto para consulta: Permite al usuario introducir preguntas (`currentQuery`).
    *   Botón "Enviar": Envía la pregunta al backend (`POST /rag/query/`) y actualiza `chatHistory`.
    *   Muestra el historial de chat y el estado de la IA.

### `frontend/src/ErrorBoundary.js`

Un componente React de "Error Boundary".

*   **Propósito:** Capturar errores JavaScript en cualquier parte de su árbol de componentes hijo, registrarlos y mostrar una interfaz de usuario alternativa en lugar de un componente que ha fallado.
*   **Estado:**
    *   `hasError` (boolean): Indica si se ha producido un error.
    *   `error` (Error | null): El objeto de error capturado.
*   **Propiedades:**
    *   `children`: Los componentes que `ErrorBoundary` protegerá.
*   **Métodos del ciclo de vida:**
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para que la próxima renderización muestre la UI de fallback.
    *   `componentDidCatch(error, info)`: Se utiliza para registrar el error en un servicio de registro de errores.
*   **Renderización:** Si `hasError` es `true`, muestra un mensaje de error y los detalles del error; de lo contrario, renderiza `this.props.children`.

### `frontend/src/config.js`

Un archivo simple para gestionar la URL del API.

*   **Propósito:** Centralizar la configuración de la URL base del backend para facilitar su cambio entre entornos de desarrollo y producción.
*   **`API_URL` (string):** Define la URL base del backend. Utiliza la variable de entorno `REACT_APP_API_URL` si está definida, de lo contrario, por defecto es `http://localhost:8001`.

### `frontend/src/index.js`

El punto de entrada principal de la aplicación React.

*   **Propósito:** Renderizar el componente raíz de `App.js` en el elemento DOM con `id="root"`. También inicializa `reportWebVitals` para la medición del rendimiento.
*   **Interacciones:** Ninguna interacción directa del usuario.

### `frontend/src/CategoriesView.js`

La vista para explorar todas las categorías de libros.

*   **Propósito:** Mostrar una lista de todas las categorías de libros únicas disponibles en la biblioteca y permitir navegar a una vista filtrada por categoría.
*   **Estado:**
    *   `categories` (array): Lista de cadenas, cada una representando una categoría única.
    *   `error` (string): Mensaje de error si falla la carga de categorías.
    *   `loading` (boolean): Indica si la vista está cargando datos.
*   **Propiedades:** Ninguna.
*   **Efectos:**
    *   `useEffect`: Fetches la lista de categorías desde el backend al montar el componente.
*   **Interacciones:**
    *   Cada categoría se muestra como un enlace (`Link`) que al hacer clic navega a la `LibraryView` con el filtro de categoría aplicado (`/?category=...`).
    *   Se comunica con el backend (`GET /categories/`).

## 5. Flujo de Datos y API

Esta sección describe cómo los datos fluyen a través de la aplicación y resume los principales endpoints de la API.

### Flujos Clave de Datos

1.  **Carga de un Libro (`UploadView` -> Backend -> DB/IA):**
    *   El usuario selecciona o arrastra archivos (PDF/EPUB) en `UploadView`.
    *   `UploadView` envía cada archivo mediante una petición `POST` a `/upload-book/`.
    *   El endpoint `/upload-book/` en `main.py`:
        *   Guarda el archivo en el directorio `backend/books/`.
        *   Llama a `process_pdf` o `process_epub` para extraer texto inicial y una posible portada.
        *   Llama a `analyze_with_gemini` para que la IA extraiga el título, autor y categoría.
        *   Si la IA tiene éxito, llama a `crud.create_book` para guardar los metadatos y la ruta del archivo en la base de datos (SQLite).
        *   Retorna un objeto `schemas.Book` al frontend.

2.  **Visualización y Búsqueda de Libros (`LibraryView` -> Backend -> DB):**
    *   `LibraryView` realiza una petición `GET` a `/books/` (opcionalmente con parámetros `category`, `search`, `author`).
    *   El endpoint `/books/` en `main.py` llama a `crud.get_books`.
    *   `crud.get_books` consulta la tabla `books` en la base de datos, aplica los filtros si es necesario, y retorna una lista de objetos `models.Book`.
    *   `main.py` serializa esta lista a `schemas.Book` y la envía a `LibraryView` para su renderización.

3.  **Chat RAG con un Libro (`RagView` -> Backend -> ChromaDB/Gemini):**
    *   El usuario selecciona un libro de la biblioteca en `RagView`.
    *   `RagView` comprueba el estado del índice RAG del libro mediante `GET /rag/status/{book_id}`.
    *   Si el libro no está indexado, el usuario pulsa "Indexar antes de charlar", lo que activa una petición `POST` a `/rag/index/{book_id}`.
    *   El endpoint `/rag/index/{book_id}` en `main.py` llama a `rag.process_book_for_rag`.
    *   `rag.process_book_for_rag` extrae el texto del libro, lo divide en fragmentos, genera embeddings usando `rag.get_embedding` y los almacena en ChromaDB.
    *   Una vez indexado, el usuario introduce una pregunta en el chat y `RagView` envía una petición `POST` a `/rag/query/` con la pregunta y el `book_id`.
    *   El endpoint `/rag/query/` en `main.py` llama a `rag.query_rag`.
    *   `rag.query_rag` genera un embedding para la pregunta, consulta ChromaDB para recuperar los fragmentos de texto más relevantes del libro y luego usa Gemini (`genai.GenerativeModel`) para generar una respuesta contextualizada basada en la pregunta y los fragmentos recuperados.
    *   La respuesta de la IA se envía de vuelta a `RagView` y se muestra en el historial de chat.

### Resumen de Endpoints de la API (Backend `main.py`)

| Método | Endpoint                      | Descripción                                                                                                                                                                                                                 | Parámetros / Cuerpo de la Petición                                                | Respuesta                                                 |
| :----- | :---------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------- | :-------------------------------------------------------- |
| `POST` | `/upload-book/`               | Sube un nuevo archivo de libro (PDF/EPUB). La IA lo analiza para extraer metadatos (título, autor, categoría) y lo guarda en la base de datos.                                                                           | `book_file` (UploadFile)                                                          | `schemas.Book` (libro creado)                             |
| `GET`  | `/books/`                     | Obtiene una lista de todos los libros en la biblioteca. Permite filtrar por categoría, autor o buscar por título/autor/categoría.                                                                                          | `category` (str, opcional), `search` (str, opcional), `author` (str, opcional)  | `List[schemas.Book]`                                      |
| `GET`  | `/books/count`                | Obtiene el número total de libros en la biblioteca.                                                                                                                                                                         | Ninguno                                                                           | `int`                                                     |
| `GET`  | `/books/search/`              | Busca libros por un título parcial (insensible a mayúsculas/minúsculas). Soporta paginación.                                                                                                                                | `title` (str), `skip` (int, opcional), `limit` (int, opcional)                    | `List[schemas.Book]`                                      |
| `GET`  | `/categories/`                | Obtiene una lista de todas las categorías de libros únicas presentes en la biblioteca.                                                                                                                                      | Ninguno                                                                           | `List[str]`                                               |
| `DELETE` | `/books/{book_id}`          | Elimina un libro específico de la base de datos y sus archivos asociados (libro y portada). También elimina su índice RAG.                                                                                                | `book_id` (int, en la URL)                                                        | `{"message": str}`                                        |
| `DELETE` | `/categories/{category_name}` | Elimina todos los libros de una categoría específica de la base de datos y sus archivos asociados. También elimina sus índices RAG.                                                                                      | `category_name` (str, en la URL)                                                  | `{"message": str}`                                        |
| `GET`  | `/books/download/{book_id}`   | Descarga o abre un archivo de libro específico. Devuelve el archivo original.                                                                                                                                               | `book_id` (int, en la URL)                                                        | `FileResponse` (PDF o EPUB)                               |
| `POST` | `/tools/convert-epub-to-pdf`  | Convierte un archivo EPUB subido a PDF. El PDF generado se guarda temporalmente y se devuelve una URL para su descarga.                                                                                                   | `file` (UploadFile, archivo EPUB)                                                 | `schemas.ConversionResponse`                              |
| `POST` | `/rag/upload-book/`           | **Deprecado/No usado directamente en frontend:** Sube un libro para indexarlo directamente en RAG. Genera un `book_id` temporal para ChromaDB.                                                                             | `file` (UploadFile, archivo de libro)                                             | `schemas.RagUploadResponse`                               |
| `POST` | `/rag/query/`                 | Realiza una consulta al sistema RAG para obtener una respuesta basada en el contenido de un libro indexado.                                                                                                               | `schemas.RagQuery` (`query`, `book_id`, `mode`)                                   | `schemas.RagQueryResponse`                                |
| `POST` | `/rag/index/{book_id}`        | Indexa un libro ya existente en la base de datos para el sistema RAG. Si `force` es `True`, reindexa el libro.                                                                                                            | `book_id` (int, en la URL), `force` (bool, query param, opcional, por defecto `False`) | `{"message": str, "book_id": str, "force": bool}`         |
| `GET`  | `/rag/status/{book_id}`       | Devuelve el estado de indexación RAG para un libro específico (si está indexado y cuántos vectores tiene).                                                                                                              | `book_id` (int, en la URL)                                                        | `{"book_id": str, "indexed": bool, "vector_count": int}`  |
| `POST` | `/rag/reindex/category/{category_name}` | (Re)indexa todos los libros de una categoría específica en el sistema RAG.                                                                                                                                          | `category_name` (str, en la URL), `force` (bool, query param, opcional, por defecto `True`) | `{"category": str, "processed": int, "failed": list, "force": bool}` |
| `POST` | `/rag/reindex/all`            | (Re)indexa todos los libros de la biblioteca en el sistema RAG.                                                                                                                                                             | `force` (bool, query param, opcional, por defecto `True`)                         | `{"processed": int, "failed": list, "total": int, "force": bool}` |
| `GET`  | `/rag/estimate/book/{book_id}` | Estima el número de tokens y fragmentos para un libro específico, con un coste opcional.                                                                                                                                  | `book_id` (int, en la URL), `per1k` (float, query param, opcional), `max_tokens` (int, query param, opcional) | `{"book_id": str, "tokens": int, "chunks": int, "per1k": float, "estimated_cost": float | null}` |
| `GET`  | `/rag/estimate/category/{category_name}` | Estima el número total de tokens y fragmentos para todos los libros de una categoría, con un coste opcional.                                                                                                       | `category_name` (str, en la URL), `per1k` (float, query param, opcional), `max_tokens` (int, query param, opcional) | `{"category": str, "tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float | null}` |
| `GET`  | `/rag/estimate/all`           | Estima el número total de tokens y fragmentos para todos los libros de la biblioteca, con un coste opcional.                                                                                                               | `per1k` (float, query param, opcional), `max_tokens` (int, query param, opcional) | `{"tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float | null}` |
```
```
```
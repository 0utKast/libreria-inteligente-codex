# Documentación del Proyecto: Mi Librería Inteligente

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales (PDF y EPUB). Va más allá de una simple biblioteca al integrar capacidades de inteligencia artificial para analizar los libros, extraer metadatos automáticamente y ofrecer una interfaz conversacional (RAG) para interactuar directamente con el contenido de los libros.

**Características Principales:**
*   **Gestión de Libros:** Sube, visualiza (lectura de EPUBs en el navegador), edita, descarga y elimina libros (PDF y EPUB).
*   **Análisis Inteligente:** Utiliza la API de Google Gemini para extraer automáticamente el título, autor y categoría de los libros subidos.
*   **Conversación con Libros (RAG):** Indexa el contenido de los libros en una base de datos vectorial (ChromaDB) para permitir a los usuarios hacer preguntas y obtener respuestas contextualizadas del libro a través de un modelo de lenguaje (Google Gemini).
*   **Herramientas Útiles:** Incluye un convertidor de EPUB a PDF.
*   **Organización:** Categorización automática y manual, búsqueda por título, autor y categoría.

**Arquitectura General:**
La aplicación sigue una arquitectura cliente-servidor, con un frontend desarrollado en React y un backend en Python utilizando FastAPI.

*   **Frontend (React):** Proporciona la interfaz de usuario interactiva, gestiona el estado de la aplicación y se comunica con el backend a través de una API RESTful.
*   **Backend (FastAPI):** Expone una API REST, maneja la lógica de negocio, interactúa con la base de datos, procesa archivos de libros, coordina las llamadas a la API de Google Gemini para el análisis y RAG, y gestiona el almacenamiento de archivos.
*   **Base de Datos (SQLite):** Utiliza SQLAlchemy como ORM para la gestión de los metadatos de los libros. La base de datos es un archivo `library.db` almacenado localmente.
*   **Base de Datos Vectorial (ChromaDB):** Almacena los embeddings (representaciones vectoriales) de los chunks de texto de los libros para la funcionalidad RAG. Se persiste en un directorio local (`./rag_index` por defecto).
*   **Servicios de IA (Google Gemini API):** Utilizado para:
    *   Extraer metadatos (título, autor, categoría) de los libros.
    *   Generar embeddings para el RAG.
    *   Generar respuestas a las preguntas del usuario en el módulo RAG.
*   **Almacenamiento de Archivos:** Los archivos de los libros y sus portadas se guardan en el sistema de archivos del servidor en directorios dedicados (`books/`, `static/covers/`, `temp_books/`).

## 2. Estructura del Proyecto

El proyecto se organiza en dos directorios principales: `backend/` para el servidor Python/FastAPI y `frontend/src/` para la aplicación React.

```
.
├── backend/
│   ├── alembic/                      # Migraciones de base de datos SQLAlchemy (Alembic)
│   ├── models.py                     # Definiciones de modelos de base de datos SQLAlchemy
│   ├── database.py                   # Configuración de la conexión a la base de datos
│   ├── schemas.py                    # Modelos de datos Pydantic para la API
│   ├── crud.py                       # Operaciones CRUD (Create, Read, Update, Delete) para la base de datos
│   ├── utils.py                      # Funciones de utilidad (ej. configuración de la IA)
│   ├── rag.py                        # Lógica para Retrieval-Augmented Generation (RAG)
│   ├── main.py                       # Archivo principal de la aplicación FastAPI, define endpoints
│   ├── __init__.py                   # Hace de 'backend' un paquete Python
│   ├── tests/                        # Pruebas unitarias para el backend
│   └── tests_curated/                # Pruebas adicionales "curated" para el backend
├── frontend/
│   ├── public/                       # Archivos estáticos públicos (index.html, etc.)
│   ├── src/                          # Código fuente de la aplicación React
│   │   ├── App.js                    # Componente principal de la aplicación React y router
│   │   ├── index.js                  # Punto de entrada de la aplicación React
│   │   ├── config.js                 # Configuración de la URL del API
│   │   ├── Header.js                 # Componente de la cabecera/navegación
│   │   ├── LibraryView.js            # Vista principal de la biblioteca de libros
│   │   ├── UploadView.js             # Vista para subir nuevos libros
│   │   ├── CategoriesView.js         # Vista para listar y filtrar por categorías
│   │   ├── ToolsView.js              # Vista de herramientas (ej. convertidor EPUB a PDF)
│   │   ├── ReaderView.js             # Vista para leer libros EPUB en el navegador
│   │   ├── RagView.js                # Vista para la interacción conversacional RAG
│   │   ├── EditBookModal.js          # Modal para editar detalles del libro
│   │   ├── ErrorBoundary.js          # Componente para manejo de errores de UI
│   │   ├── *.css                     # Hojas de estilo para los componentes
│   │   └── reportWebVitals.js        # Utilidad para medir el rendimiento web
│   └── package.json                  # Definiciones y scripts del proyecto Frontend (Node.js)
├── .env.example                      # Ejemplo de variables de entorno
├── library.db                        # Base de datos SQLite (generada al ejecutar)
├── rag_index/                        # Directorio para la base de datos vectorial ChromaDB (generada al usar RAG)
└── README.md                         # Archivo README del proyecto
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/models.py`
Define el modelo ORM `Book` para la base de datos utilizando SQLAlchemy.

*   **Clase `Book(Base)`**:
    *   `__tablename__ = "books"`: Nombre de la tabla en la base de datos.
    *   `__table_args__ = {'extend_existing': True}`: Permite la redefinición de la tabla si ya existe (útil para tests o recargas).
    *   `id (Column(Integer, primary_key=True, index=True))`: Clave primaria autoincremental.
    *   `title (Column(String, index=True))`: Título del libro.
    *   `author (Column(String, index=True))`: Autor del libro.
    *   `category (Column(String, index=True))`: Categoría del libro.
    *   `cover_image_url (Column(String, nullable=True))`: URL de la portada del libro (opcional).
    *   `file_path (Column(String, unique=True))`: Ruta absoluta al archivo del libro en el sistema de archivos (debe ser única).

### `backend/database.py`
Configura la conexión a la base de datos SQLite y las herramientas de SQLAlchemy.

*   `_base_dir`: Ruta del directorio base del proyecto.
*   `_db_path`: Ruta absoluta al archivo `library.db` (en la raíz del proyecto).
*   `SQLALCHEMY_DATABASE_URL`: URL de conexión a la base de datos SQLite.
*   `engine`: Objeto `Engine` de SQLAlchemy, la interfaz principal para la base de datos. Configurado con `check_same_thread=False` para SQLite con FastAPI.
*   `SessionLocal`: Una clase `sessionmaker` que crea sesiones de base de datos. Cada instancia de sesión es una "zona de ensayo" para todas las operaciones de la base de datos relacionadas con una transacción particular.
*   `Base`: La clase base declarativa de SQLAlchemy a partir de la cual se heredarán los modelos ORM.

### `backend/schemas.py`
Define los modelos Pydantic para la validación de datos de entrada y salida de la API.

*   **Clase `BookBase(BaseModel)`**: Esquema base para un libro, sin el ID de la base de datos.
    *   `title (str)`: Título del libro.
    *   `author (str)`: Autor del libro.
    *   `category (str)`: Categoría del libro.
    *   `cover_image_url (str | None)`: URL de la imagen de portada (opcional).
    *   `file_path (str)`: Ruta al archivo del libro.
*   **Clase `Book(BookBase)`**: Esquema completo para un libro, extendiendo `BookBase` con el ID.
    *   `id (int)`: ID único del libro en la base de datos.
    *   `Config.from_attributes = True`: Permite mapear directamente atributos de modelos ORM.
*   **Clase `ConversionResponse(BaseModel)`**: Respuesta para la conversión de EPUB a PDF.
    *   `download_url (str)`: URL del PDF convertido.
*   **Clase `RagUploadResponse(BaseModel)`**: Respuesta al subir un libro para RAG.
    *   `book_id (str)`: ID del libro procesado para RAG.
    *   `message (str)`: Mensaje de estado.
*   **Clase `RagQuery(BaseModel)`**: Estructura de la consulta al módulo RAG.
    *   `query (str)`: La pregunta del usuario.
    *   `book_id (str)`: ID del libro sobre el que se pregunta.
    *   `mode (str | None)`: Modo de respuesta ('strict', 'balanced', 'open').
*   **Clase `RagQueryResponse(BaseModel)`**: Respuesta de la consulta RAG.
    *   `response (str)`: La respuesta generada por la IA.

### `backend/crud.py`
Contiene las funciones de acceso a datos (CRUD) para interactuar con el modelo `Book`.

*   `get_book_by_path(db: Session, file_path: str)`: Recupera un libro por su ruta de archivo.
*   `get_book_by_title(db: Session, title: str)`: Recupera un libro por su título exacto.
*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial (case-insensitive).
*   `get_books(db: Session, category: str | None, search: str | None, author: str | None)`: Recupera una lista de libros, con filtros opcionales por categoría, autor o término de búsqueda general (título, autor o categoría).
*   `get_categories(db: Session) -> list[str]`: Recupera una lista de todas las categorías únicas.
*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea y guarda un nuevo libro en la base de datos.
*   `delete_book(db: Session, book_id: int)`: Elimina un libro por su ID, incluyendo sus archivos de libro y portada del sistema de archivos.
*   `delete_books_by_category(db: Session, category: str)`: Elimina todos los libros de una categoría dada, incluyendo sus archivos.
*   `get_books_count(db: Session) -> int`: Devuelve el número total de libros.
*   `update_book(db: Session, book_id: int, title: str, author: str, cover_image_url: str | None)`: Actualiza los detalles de un libro existente.

### `backend/utils.py`
Provee funciones de utilidad que pueden ser usadas en diferentes partes del backend.

*   `configure_genai()`: Carga las variables de entorno para la API de Google (desde `.env`), verifica que `GOOGLE_API_KEY` o `GEMINI_API_KEY` esté presente, y configura el SDK de `google.generativeai`. Lanza un `ValueError` si no se encuentra la clave.

### `backend/rag.py`
Contiene la implementación del sistema RAG (Retrieval-Augmented Generation) para interactuar con el contenido de los libros.

*   `_initialized`, `_collection`, `_ai_enabled`: Variables globales para el estado de inicialización del módulo RAG, la colección ChromaDB y si la IA está activa.
*   `EMBEDDING_MODEL`, `GENERATION_MODEL`: Modelos de Gemini configurables por entorno para embeddings y generación de texto.
*   `_ensure_init()`: Inicializa de forma perezosa el SDK de Gemini y la conexión a ChromaDB (persistente en la ruta `CHROMA_PATH` del `.env`, por defecto `./rag_index`). Verifica `DISABLE_AI` y `API_KEY`.
*   `get_embedding(text: str, task_type: str)`: Genera embeddings vectoriales para un texto dado utilizando el modelo `EMBEDDING_MODEL`. Si `DISABLE_AI` está activo, devuelve un embedding dummy.
*   `extract_text_from_pdf(file_path: str)`: Extrae texto de un archivo PDF usando `PyPDF2`.
*   `extract_text_from_epub(file_path: str)`: Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`.
*   `extract_text(file_path: str)`: Función unificada para extraer texto de PDF o EPUB.
*   `chunk_text(text: str, max_tokens: int = 1000)`: Divide un texto largo en chunks más pequeños basándose en el recuento de tokens (usando `tiktoken`).
*   `_has_index_for_book(book_id: str)`: Comprueba si un libro ya tiene vectores indexados en ChromaDB.
*   `delete_book_from_rag(book_id: str)`: Elimina todos los vectores asociados a un `book_id` de ChromaDB.
*   `get_index_count(book_id: str)`: Devuelve el número de vectores almacenados para un `book_id`.
*   `has_index(book_id: str)`: Alias para `get_index_count > 0`.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Extrae el texto de un libro, lo divide en chunks, genera embeddings para cada chunk y los almacena en ChromaDB. Puede forzar la reindexación (borrar y crear de nuevo).
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`: Estima el número de tokens y chunks para un solo archivo.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`: Estima el número total de tokens y chunks para una lista de archivos.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None, library: dict | None)`: Realiza una consulta RAG:
    1.  Genera un embedding para la consulta.
    2.  Busca los chunks más relevantes del libro en ChromaDB.
    3.  Construye un prompt para Gemini con la consulta, los chunks relevantes, metadatos del libro y contexto de la biblioteca.
    4.  Genera una respuesta utilizando el modelo `GENERATION_MODEL` de Gemini, siguiendo el `mode` especificado ('strict', 'balanced', 'open').

### `backend/main.py`
Es el archivo principal de la aplicación FastAPI, donde se definen todos los endpoints de la API.

**Configuración Inicial:**
*   `app = FastAPI()`: Instancia de la aplicación FastAPI.
*   Configuración CORS: Permite solicitudes desde orígenes específicos (configurable por variables de entorno `ALLOW_ORIGINS`, `ALLOW_ORIGIN_REGEX`, `FRONTEND_PORTS`).
*   Montaje de directorios estáticos: `static/`, `temp_books/` para servir portadas y archivos temporales.
*   `get_db()`: Función de dependencia para gestionar la sesión de la base de datos.
*   Inicialización de IA: Configura la API de Gemini si `GOOGLE_API_KEY` o `GEMINI_API_KEY` están presentes y `DISABLE_AI` no está activado.

**Funciones de IA y Procesamiento:**
*   `analyze_with_gemini(text: str)`: Envía texto a Gemini para extraer título, autor y categoría en formato JSON. Usa `GEMINI_MODEL_MAIN` (por defecto `gemini-2.5-flash`).
*   `process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str)`: Extrae texto de las primeras páginas de un PDF y busca una imagen de portada.
*   `process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str)`: Extrae texto de un EPUB y busca una imagen de portada (con varios fallbacks).

**Endpoints de la API:**

*   `POST /upload-book/`:
    *   Sube un archivo de libro (PDF o EPUB).
    *   Guarda el archivo, lo procesa para extraer texto y portada.
    *   Usa `analyze_with_gemini` para obtener metadatos.
    *   Realiza una "puerta de calidad": si la IA no puede identificar título y autor, el libro no se añade.
    *   Crea un registro en la BD usando `crud.create_book`.
*   `GET /books/`:
    *   Recupera una lista de libros, con filtros opcionales por `category`, `search` (título, autor, categoría) y `author`.
    *   Usa `crud.get_books`.
*   `PUT /books/{book_id}`:
    *   Actualiza el título, autor y, opcionalmente, la portada de un libro.
    *   Elimina la portada antigua si se sube una nueva.
    *   Usa `crud.update_book`.
*   `GET /books/count`:
    *   Devuelve el número total de libros. Usa `crud.get_books_count`.
*   `GET /books/search/`:
    *   Busca libros por título parcial con paginación. Usa `crud.get_books_by_partial_title`.
*   `GET /categories/`:
    *   Devuelve una lista de categorías únicas. Usa `crud.get_categories`.
*   `DELETE /books/{book_id}`:
    *   Elimina un libro por su ID.
    *   También elimina el libro del índice RAG y los archivos asociados.
    *   Usa `crud.delete_book` y `rag.delete_book_from_rag`.
*   `DELETE /categories/{category_name}`:
    *   Elimina todos los libros de una categoría.
    *   También elimina sus entradas del índice RAG y los archivos asociados.
    *   Usa `crud.delete_books_by_category` y `rag.delete_book_from_rag`.
*   `GET /books/download/{book_id}`:
    *   Permite descargar o abrir el archivo original de un libro.
    *   Usa `FileResponse` para servir el archivo con el tipo de medio adecuado.
*   `POST /tools/convert-epub-to-pdf`:
    *   Convierte un archivo EPUB a PDF.
    *   Utiliza `weasyprint` y `BeautifulSoup` para procesar el EPUB y generar el PDF.
    *   Guarda el PDF temporalmente en `temp_books/` y devuelve una URL de descarga.
*   `POST /rag/upload-book/` (Nota: Este endpoint existe pero el frontend actual usa `index_existing_book_for_rag` para libros ya en la biblioteca):
    *   Sube un libro temporalmente y lo procesa para el RAG.
*   `POST /rag/query/`:
    *   Realiza una consulta al módulo RAG sobre un libro específico.
    *   Recibe una `RagQuery` y devuelve una `RagQueryResponse`.
    *   Usa `rag.query_rag`.
*   `POST /rag/index/{book_id}`:
    *   Indexa un libro existente en la base de datos para el RAG.
    *   Usa `rag.process_book_for_rag`.
*   `GET /rag/status/{book_id}`:
    *   Devuelve el estado de indexación RAG de un libro (si está indexado y el número de vectores).
    *   Usa `rag.get_index_count`.
*   `POST /rag/reindex/category/{category_name}`:
    *   (Re)indexa todos los libros de una categoría.
*   `POST /rag/reindex/all`:
    *   (Re)indexa todos los libros de la biblioteca.
*   `GET /rag/estimate/book/{book_id}`:
    *   Estima tokens y chunks para un libro, con coste opcional.
*   `GET /rag/estimate/category/{category_name}`:
    *   Estima tokens y chunks para todos los libros de una categoría.
*   `GET /rag/estimate/all`:
    *   Estima tokens y chunks para todos los libros de la biblioteca.

### `backend/__init__.py`
Es un archivo vacío que simplemente marca el directorio `backend` como un paquete de Python.

## 4. Análisis Detallado del Frontend (React)

### `frontend/src/index.js`
Es el punto de entrada de la aplicación React. Renderiza el componente `App` dentro del elemento 'root' del DOM.

### `frontend/src/config.js`
Define la URL base para las llamadas a la API del backend.
*   `API_URL`: Obtiene la URL de la variable de entorno `REACT_APP_API_URL` o usa `http://localhost:8001` por defecto.

### `frontend/src/App.js`
Es el componente principal de la aplicación.
*   **Propósito:** Configura el enrutamiento de la aplicación (`BrowserRouter`, `Routes`, `Route`) y renderiza los componentes principales como `Header` y las vistas específicas según la URL.
*   **Estado / Props / Efectos:** No tiene estado propio, propiedades o efectos secundarios complejos. Su rol es estructural.
*   **Interacciones:** Gestiona la navegación entre las diferentes vistas de la aplicación.

### `frontend/src/Header.js`
Componente de la cabecera de la aplicación, que incluye el logo, un contador de libros y la navegación principal.
*   **Propósito:** Proporciona un elemento de navegación constante y muestra el número total de libros en la biblioteca.
*   **Estado:**
    *   `menuOpen`: Booleano para controlar la visibilidad del menú hamburguesa en móviles.
    *   `bookCount`: Número total de libros obtenido del backend.
    *   `errorMessage`: Mensaje de error si falla la carga del contador de libros.
*   **Efectos:**
    *   Al montarse (y periódicamente cada 10 minutos), hace una llamada `GET` a `/books/count` para actualizar el `bookCount`.
*   **Interacciones:**
    *   Los `NavLink`s permiten la navegación a diferentes rutas (`/`, `/upload`, `/etiquetas`, `/herramientas`, `/rag`).
    *   Botón de menú hamburguesa (`&#9776;`) para desplegar/contraer el menú en dispositivos móviles.

### `frontend/src/LibraryView.js`
La vista principal que muestra la lista de libros en la biblioteca.
*   **Propósito:** Muestra los libros en formato de cuadrícula, permite buscar, filtrar, editar, eliminar y acceder a los libros (leer EPUB o descargar/abrir PDF).
*   **Estado:**
    *   `books`: Array de objetos libro a mostrar.
    *   `searchParams`: Objeto para gestionar los parámetros de la URL (filtros de categoría/autor).
    *   `searchTerm`: Texto introducido en la barra de búsqueda.
    *   `debouncedSearchTerm`: Versión "debounced" de `searchTerm` para evitar llamadas excesivas al API.
    *   `error`: Mensaje de error si falla la carga de libros.
    *   `loading`: Booleano que indica si los libros están cargando.
    *   `isMobile`: Booleano para detectar si la pantalla es de tamaño móvil.
    *   `editingBook`: Objeto libro que se está editando en el modal.
*   **Efectos:**
    *   Al montarse o cuando cambian `debouncedSearchTerm` o `searchParams`, `fetchBooks` se ejecuta para cargar los libros filtrados.
    *   Detecta el tamaño de la ventana para `isMobile`.
*   **Interacciones:**
    *   `search-bar`: Campo de texto para buscar libros por título, autor o categoría.
    *   `handleAuthorClick`, `handleCategoryClick`: Al hacer clic en el nombre de un autor o categoría, filtra la vista por ese criterio.
    *   `edit-book-btn`: Abre el `EditBookModal` para el libro seleccionado.
    *   `delete-book-btn`: Elimina un libro de la biblioteca (con confirmación), llamando a `DELETE /books/{bookId}`.
    *   `download-button` (para PDF): Abre el PDF en una nueva pestaña o lo descarga en móvil.
    *   `Link` (para EPUB): Navega a la vista `ReaderView` para leer el EPUB.
*   **Componentes Internos:** `BookCover` (muestra la portada o un placeholder), `EditBookModal` (para editar libros).

### `frontend/src/UploadView.js`
Vista para subir nuevos archivos de libros.
*   **Propósito:** Permite a los usuarios seleccionar y subir uno o varios archivos PDF o EPUB al servidor, y muestra su estado de procesamiento.
*   **Estado:**
    *   `filesToUpload`: Array de objetos que representan los archivos seleccionados, incluyendo su `file` real, `status` (pending, uploading, success, error) y `message`.
    *   `isUploading`: Booleano que indica si el proceso de subida está en curso.
*   **Efectos:** Ninguno específico.
*   **Interacciones:**
    *   `input type="file"` y `drop-zone`: Permiten seleccionar archivos o arrastrarlos y soltarlos.
    *   `handleUpload`: Envía cada archivo pendiente al endpoint `POST /upload-book/` del backend. Actualiza el estado y mensaje de cada archivo.
    *   `handleReset`: Limpia la lista de archivos para subir.
    *   Una vez que todos los archivos están procesados, ofrece botones para "Ir a la Biblioteca" o "Añadir más libros".

### `frontend/src/CategoriesView.js`
Vista que muestra todas las categorías únicas presentes en la biblioteca.
*   **Propósito:** Ofrecer una forma rápida de explorar los libros por categoría.
*   **Estado:**
    *   `categories`: Array de strings con los nombres de las categorías.
    *   `error`: Mensaje de error si falla la carga de categorías.
    *   `loading`: Booleano que indica si las categorías están cargando.
*   **Efectos:**
    *   Al montarse, hace una llamada `GET` a `/categories/` para obtener la lista de categorías.
*   **Interacciones:**
    *   Cada categoría es un `Link` que, al hacer clic, redirige a `LibraryView` con un parámetro de URL para filtrar por esa categoría.

### `frontend/src/EditBookModal.js`
Componente modal para editar la información de un libro.
*   **Propósito:** Proporcionar una interfaz para que los usuarios puedan cambiar el título, el autor y la imagen de portada de un libro existente.
*   **Props:**
    *   `book`: El objeto libro a editar.
    *   `onClose`: Función para cerrar el modal.
    *   `onBookUpdated`: Función callback que se ejecuta al actualizar el libro con éxito, pasando el libro actualizado.
*   **Estado:**
    *   `title`, `author`: Campos del formulario, inicializados con los datos del libro.
    *   `coverImage`: Archivo de imagen seleccionado para la nueva portada.
    *   `isSaving`: Booleano para deshabilitar el formulario mientras se guarda.
*   **Efectos:**
    *   Al cambiar el prop `book`, actualiza el estado `title` y `author` del formulario.
*   **Interacciones:**
    *   Formulario: Permite introducir nuevo título, autor y seleccionar un nuevo archivo de imagen para la portada.
    *   `handleSubmit`: Envía los datos actualizados (incluyendo la nueva portada si se selecciona) como `FormData` al endpoint `PUT /books/{book.id}`.
    *   `Cancelar`: Cierra el modal sin guardar.

### `frontend/src/ToolsView.js`
Esta vista contiene varias herramientas auxiliares de la biblioteca. Actualmente, solo tiene un convertidor de EPUB a PDF.
*   **Propósito:** Agrupar funcionalidades adicionales que no encajan directamente en la gestión de la biblioteca.
*   **Componente Interno: `EpubToPdfConverter`**
    *   **Propósito:** Permite a los usuarios subir un archivo EPUB y convertirlo a PDF.
    *   **Estado:**
        *   `selectedFile`: El archivo EPUB seleccionado por el usuario.
        *   `message`: Mensajes de estado/error para el usuario.
        *   `isLoading`: Booleano que indica si la conversión está en curso.
    *   **Efectos:** Ninguno específico.
    *   **Interacciones:**
        *   `input type="file"` y `drop-zone`: Para seleccionar o arrastrar archivos EPUB.
        *   `handleConvert`: Envía el archivo EPUB al endpoint `POST /tools/convert-epub-to-pdf`. Si la conversión es exitosa, inicia la descarga del PDF resultante.

### `frontend/src/ReaderView.js`
Componente que muestra el contenido de un libro EPUB directamente en el navegador.
*   **Propósito:** Proporcionar una interfaz de lectura para los libros en formato EPUB.
*   **Estado:**
    *   `location`: La ubicación actual en el libro (EPUB CFI), usada para persistir la posición de lectura.
    *   `epubData`: Los datos binarios del archivo EPUB (como `ArrayBuffer`).
    *   `isLoading`: Booleano que indica si el libro está cargando.
    *   `error`: Mensaje de error si falla la carga del libro.
*   **Efectos:**
    *   Al montarse o cambiar `bookId` (obtenido de los parámetros de la URL), hace una llamada `GET` a `/books/download/{bookId}` para obtener el archivo EPUB como `ArrayBuffer`.
*   **Interacciones:**
    *   Integra `react-reader` para renderizar el contenido EPUB y gestionar la navegación.
    *   `locationChanged`: Actualiza el estado `location` con la posición de lectura.

### `frontend/src/RagView.js`
Interfaz para interactuar con la funcionalidad de Conversación con IA (RAG).
*   **Propósito:** Permite a los usuarios seleccionar un libro de la biblioteca, indexarlo para RAG y luego hacer preguntas sobre su contenido a una IA.
*   **Estado:**
    *   `message`: Mensajes informativos o de error para el usuario.
    *   `isLoading`: Booleano para el estado de las consultas de chat.
    *   `bookId`: El ID del libro activo con el que se está chateando.
    *   `chatHistory`: Array de objetos que representan la conversación (mensajes del usuario y de Gemini).
    *   `currentQuery`: Texto de la pregunta actual del usuario.
    *   `libraryBooks`: Lista de todos los libros de la biblioteca.
    *   `selectedLibraryId`: El ID del libro seleccionado en el buscador de la biblioteca.
    *   `libStatus`: Objeto con el estado del índice RAG del libro seleccionado (cargando, indexado, conteo de vectores, error).
    *   `actionsBusy`, `refreshing`: Booleanos para controlar el estado de las acciones de indexación/reindexación y refresco.
    *   `searchTerm`, `searching`, `searchResults`, `resultsOpen`: Para la funcionalidad de búsqueda de libros.
    *   `mode`: Modo de respuesta de la IA ('strict', 'balanced', 'open').
    *   `selectedBook`: Objeto del libro seleccionado en el buscador, para mostrar su título en el chat.
*   **Efectos:**
    *   Al montarse, carga todos los libros de la biblioteca (`GET /books/`).
    *   Cuando `searchTerm` cambia, realiza una búsqueda "debounced" de libros (`GET /books/?search=...`).
    *   Cuando `selectedLibraryId` cambia, comprueba automáticamente el estado RAG de ese libro (`GET /rag/status/{book_id}`).
    *   Auto-scroll al final del historial de chat.
*   **Interacciones:**
    *   Buscador de libros: Permite buscar y seleccionar un libro existente de la biblioteca.
    *   Botones de acción: "Comprobar RAG", "Indexar antes de charlar", "Reindexar" (llama a `POST /rag/index/{book_id}`).
    *   Selector de modo: Permite elegir el comportamiento de la IA en la conversación.
    *   `chat-input-form`: Campo de texto para escribir preguntas y botón de envío (`handleQuerySubmit`), que llama a `POST /rag/query/`.
    *   Muestra el `chat-history` con las preguntas del usuario y las respuestas de Gemini.

### `frontend/src/ErrorBoundary.js`
Un componente de React para capturar errores de JavaScript en su árbol de componentes hijo.
*   **Propósito:** Prevenir que toda la aplicación se rompa cuando un componente falla en la UI, mostrando un mensaje de error amigable en su lugar.
*   **Estado:** `hasError`, `error`.
*   **Métodos del Ciclo de Vida:**
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para indicar que ha ocurrido un error.
    *   `componentDidCatch(error, info)`: Registra el error en la consola.
*   **Renderizado:** Si `hasError` es verdadero, muestra un mensaje de error; de lo contrario, renderiza los `children`.

## 5. Flujo de Datos y API

El flujo de datos en "Mi Librería Inteligente" se centra en la interacción entre el frontend de React y el backend de FastAPI, con la base de datos SQLite y ChromaDB como almacenamiento persistente y la API de Gemini para la inteligencia artificial.

### Carga de un Libro

1.  **Frontend (`UploadView.js`):**
    *   El usuario selecciona archivos PDF o EPUB a través del input de archivo o arrastrando y soltando.
    *   Al hacer clic en "Subir", `handleUpload` itera sobre los archivos.
    *   Para cada archivo, crea un objeto `FormData` y lo envía a `POST /upload-book/`.
2.  **Backend (`main.py` - `upload_book`):**
    *   Recibe el `UploadFile`.
    *   Guarda el archivo en el directorio `books/`.
    *   Verifica si el libro ya existe en la BD por `file_path` (usando `crud.get_book_by_path`).
    *   Detecta la extensión del archivo (`.pdf` o `.epub`) y llama a `process_pdf` o `process_epub` para:
        *   Extraer una porción de texto inicial del libro.
        *   Extraer una imagen de portada y guardarla en `static/covers/`.
    *   Llama a `analyze_with_gemini` (en `main.py`) con el texto extraído para obtener automáticamente el `title`, `author` y `category`.
    *   Si la IA no puede identificar el título y el autor, el libro se rechaza (`HTTPException 422`).
    *   Llama a `crud.create_book` (en `crud.py`) para guardar los metadatos del libro (título, autor, categoría, URL de portada, ruta del archivo) en la tabla `books` de SQLite.
    *   Devuelve el objeto `Book` creado (con ID) al frontend.
3.  **Frontend (`UploadView.js`):**
    *   Actualiza el `status` y `message` de cada archivo en la UI, indicando éxito o error.
    *   Una vez completadas todas las subidas, permite al usuario navegar a la biblioteca o añadir más libros.

### Visualización y Gestión de la Biblioteca

1.  **Frontend (`LibraryView.js`):**
    *   Al cargar la vista, `fetchBooks` se activa.
    *   Construye parámetros de consulta (`category`, `author`, `search`) a partir de `searchParams` y `debouncedSearchTerm`.
    *   Realiza una llamada `GET /books/` con los parámetros de consulta.
2.  **Backend (`main.py` - `read_books`):**
    *   Recibe los parámetros de consulta.
    *   Llama a `crud.get_books` (en `crud.py`) para buscar los libros correspondientes en la base de datos.
    *   Devuelve una lista de objetos `Book` (Pydantic models) al frontend.
3.  **Frontend (`LibraryView.js`):**
    *   Renderiza la lista de `Book`s en la interfaz de usuario, mostrando la portada, título, autor y categoría.
    *   Los botones permiten:
        *   **Abrir/Descargar PDF:** `GET /books/download/{book_id}`
        *   **Leer EPUB:** Navega a `/leer/{book_id}`, que carga `ReaderView`.
        *   **Editar:** Abre `EditBookModal`, que envía `PUT /books/{book_id}`.
        *   **Eliminar:** Envía `DELETE /books/{book_id}`.

### Conversación con la IA (RAG)

1.  **Frontend (`RagView.js`):**
    *   El usuario busca y selecciona un libro de la biblioteca.
    *   `checkLibraryStatus` se llama para verificar si el libro ya está indexado para RAG (`GET /rag/status/{book_id}`).
    *   Si el libro no está indexado, el usuario hace clic en "Indexar antes de charlar".
    *   `indexLibraryBook` envía una `POST` request a `/rag/index/{book_id}`.
2.  **Backend (`main.py` - `index_existing_book_for_rag`):**
    *   Recupera la ruta del archivo del libro de la base de datos.
    *   Llama a `rag.process_book_for_rag` (en `rag.py`):
        *   Extrae el texto completo del libro.
        *   Divide el texto en `chunks` (fragmentos).
        *   Para cada `chunk`, genera un `embedding` (representación vectorial) utilizando `rag.get_embedding` (que usa la API de Gemini).
        *   Almacena los `embeddings` junto con los `chunks` y metadatos (`book_id`, `chunk_index`) en ChromaDB.
3.  **Frontend (`RagView.js`):**
    *   Una vez indexado, el estado `libStatus.indexed` se vuelve `true`.
    *   El usuario escribe una `query` (pregunta) y hace clic en "Enviar".
    *   `handleQuerySubmit` envía una `POST` request a `/rag/query/` con la pregunta, el `book_id` y el `mode` de respuesta.
4.  **Backend (`main.py` - `query_rag_endpoint`):**
    *   Recupera metadatos del libro de la base de datos (título, autor, categoría) para enriquecer el contexto.
    *   Llama a `rag.query_rag` (en `rag.py`):
        *   Genera un `embedding` para la `query` del usuario.
        *   Consulta ChromaDB para encontrar los `chunks` de texto del libro más similares semánticamente a la `query`.
        *   Construye un prompt detallado para el modelo de Gemini, incluyendo la `query`, los `chunks` relevantes y los metadatos del libro.
        *   Envía el prompt a la API de Gemini para generar una respuesta.
    *   Devuelve la respuesta generada por la IA al frontend.
5.  **Frontend (`RagView.js`):**
    *   Añade la pregunta del usuario y la respuesta de Gemini al `chatHistory` y la muestra en la UI.

### Resumen de Endpoints Principales de la API

*   **`POST /upload-book/`**: Sube y procesa un nuevo libro.
*   **`GET /books/`**: Obtiene la lista de libros, con filtros opcionales.
*   **`GET /books/count`**: Obtiene el número total de libros.
*   **`GET /books/search/`**: Busca libros por título parcial.
*   **`PUT /books/{book_id}`**: Actualiza los detalles de un libro.
*   **`DELETE /books/{book_id}`**: Elimina un libro y sus archivos.
*   **`GET /categories/`**: Obtiene una lista de categorías únicas.
*   **`DELETE /categories/{category_name}`**: Elimina una categoría y todos sus libros.
*   **`GET /books/download/{book_id}`**: Descarga/abre el archivo de un libro.
*   **`POST /tools/convert-epub-to-pdf`**: Convierte un EPUB a PDF.
*   **`POST /rag/index/{book_id}`**: Indexa un libro existente para RAG.
*   **`GET /rag/status/{book_id}`**: Obtiene el estado de indexación RAG de un libro.
*   **`POST /rag/query/`**: Realiza una consulta RAG sobre un libro.
*   **`POST /rag/reindex/category/{category_name}`**: Reindexa todos los libros de una categoría.
*   **`POST /rag/reindex/all`**: Reindexa todos los libros de la biblioteca.
*   **`GET /rag/estimate/book/{book_id}`**: Estima coste de RAG para un libro.
*   **`GET /rag/estimate/category/{category_name}`**: Estima coste de RAG para una categoría.
*   **`GET /rag/estimate/all`**: Estima coste de RAG para toda la biblioteca.
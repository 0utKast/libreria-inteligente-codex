```markdown
# Documentación del Proyecto: Mi Librería Inteligente

Este documento proporciona una visión técnica detallada del proyecto "Mi Librería Inteligente", abarcando su arquitectura, estructura de código, componentes de backend y frontend, y los flujos de datos clave.

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su biblioteca digital personal. Ofrece funcionalidades para cargar libros (PDF y EPUB), que son automáticamente analizados por inteligencia artificial (Google Gemini) para extraer su título, autor y categoría. Los libros se almacenan en una base de datos y se pueden visualizar, buscar, filtrar por categoría o autor, leer y descargar. Además, incorpora un sistema de Retrieval-Augmented Generation (RAG) que permite a los usuarios interactuar conversacionalmente con el contenido de sus libros mediante IA, haciendo preguntas y obteniendo respuestas basadas en el texto del libro. También incluye una herramienta de conversión de EPUB a PDF.

**Arquitectura General:**

*   **Frontend:** Desarrollado con React, proporcionando una interfaz de usuario interactiva y dinámica.
*   **Backend:** Construido con FastAPI (Python), que expone una API RESTful para la gestión de libros, la integración con la IA y las funcionalidades RAG y de conversión.
*   **Base de Datos:** SQLite se utiliza como base de datos persistente, con SQLAlchemy como Object-Relational Mapper (ORM) para la interacción con los modelos de datos. Las migraciones se gestionan con Alembic.
*   **Inteligencia Artificial:** Google Gemini es el motor de IA principal, utilizado para:
    *   Análisis inteligente del contenido de los libros (extracción de metadatos).
    *   Generación de embeddings de texto para el sistema RAG.
    *   Generación de respuestas conversacionales en el módulo RAG.
*   **Base de Datos Vectorial (VectorDB):** ChromaDB se utiliza para almacenar los embeddings de los fragmentos de texto de los libros, permitiendo una búsqueda semántica eficiente para el sistema RAG.
*   **Almacenamiento de Archivos:** Los archivos de los libros (PDF, EPUB) y sus portadas extraídas se almacenan directamente en el sistema de archivos del servidor.

## 2. Estructura del Proyecto

El proyecto se divide en dos directorios principales: `backend/` para la lógica del servidor y `frontend/` para la aplicación cliente.

```
.
├── backend/
│   ├── alembic/                      # Herramienta de migración de base de datos SQLAlchemy (Alembic)
│   │   ├── versions/                 # Scripts de migración de la base de datos
│   │   └── env.py
│   ├── tests/                        # Pruebas unitarias y de integración para el backend
│   ├── tests_curated/                # Pruebas adicionales, posiblemente generadas o curadas
│   ├── __init__.py                   # Archivo de inicialización del paquete Python
│   ├── crud.py                       # Operaciones CRUD para la base de datos
│   ├── database.py                   # Configuración de la conexión a la base de datos
│   ├── main.py                       # Punto de entrada de la aplicación FastAPI y definición de endpoints
│   ├── models.py                     # Definiciones de modelos de base de datos SQLAlchemy
│   ├── rag.py                        # Lógica para el sistema Retrieval-Augmented Generation (RAG)
│   ├── schemas.py                    # Modelos Pydantic para la validación de datos de la API
│   └── utils.py                      # Funciones de utilidad generales (ej. configuración de IA)
├── frontend/
│   ├── public/                       # Archivos estáticos públicos (index.html, etc.)
│   ├── src/                          # Código fuente de la aplicación React
│   │   ├── App.css                   # Estilos CSS globales
│   │   ├── App.js                    # Componente raíz de la aplicación
│   │   ├── CategoriesView.css
│   │   ├── CategoriesView.js         # Vista para mostrar y gestionar categorías
│   │   ├── ErrorBoundary.js          # Componente para manejar errores de UI
│   │   ├── Header.css
│   │   ├── Header.js                 # Componente de encabezado y navegación
│   │   ├── LibraryView.css
│   │   ├── LibraryView.js            # Vista principal de la biblioteca
│   │   ├── RagView.css
│   │   ├── RagView.js                # Vista para la conversación RAG con IA
│   │   ├── ReaderView.css
│   │   ├── ReaderView.js             # Vista para leer libros (EPUB)
│   │   ├── ToolsView.css
│   │   ├── ToolsView.js              # Vista de herramientas (ej. conversor EPUB a PDF)
│   │   ├── UploadView.css
│   │   ├── UploadView.js             # Vista para subir nuevos libros
│   │   ├── config.js                 # Configuración de la URL del API
│   │   ├── index.css
│   │   ├── index.js                  # Punto de entrada de React
│   │   └── reportWebVitals.js        # Utilidad para medir el rendimiento web
│   └── package.json                  # Definiciones de dependencias y scripts de React
├── .env.example                      # Archivo de ejemplo para variables de entorno
├── library.db                        # Base de datos SQLite
└── README.md                         # Archivo README del proyecto
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend es el núcleo de la lógica de negocio, la interacción con la base de datos y la integración de la IA.

### `backend/schemas.py`

**Propósito:** Define los modelos de datos Pydantic que se utilizan para la validación, serialización y documentación de los datos de entrada y salida de la API.

**Clases Principales:**

*   **`BookBase(BaseModel)`**
    *   **Lógica:** Esquema base para la información de un libro.
    *   **Parámetros:**
        *   `title` (str): Título del libro.
        *   `author` (str): Autor del libro.
        *   `category` (str): Categoría a la que pertenece el libro.
        *   `cover_image_url` (str | None): URL o ruta de la imagen de portada (opcional).
        *   `file_path` (str): Ruta absoluta al archivo del libro en el sistema de archivos del servidor.
*   **`Book(BookBase)`**
    *   **Lógica:** Extiende `BookBase` añadiendo el ID de la base de datos. Se configura `from_attributes = True` para permitir la conversión directa desde objetos ORM.
    *   **Parámetros:**
        *   `id` (int): Identificador único del libro en la base de datos.
*   **`ConversionResponse(BaseModel)`**
    *   **Lógica:** Esquema para la respuesta de la conversión de EPUB a PDF.
    *   **Parámetros:**
        *   `download_url` (str): URL donde se puede descargar el archivo PDF resultante.
*   **`RagUploadResponse(BaseModel)`**
    *   **Lógica:** Esquema para la respuesta cuando un libro se procesa para RAG.
    *   **Parámetros:**
        *   `book_id` (str): Identificador del libro procesado para RAG.
        *   `message` (str): Mensaje de estado de la operación.
*   **`RagQuery(BaseModel)`**
    *   **Lógica:** Esquema para las consultas al sistema RAG.
    *   **Parámetros:**
        *   `query` (str): La pregunta del usuario.
        *   `book_id` (str): El ID del libro al que se refiere la pregunta.
        *   `mode` (str | None): Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`). Por defecto es `None` (el backend lo interpreta como `balanced`).
*   **`RagQueryResponse(BaseModel)`**
    *   **Lógica:** Esquema para la respuesta del sistema RAG.
    *   **Parámetros:**
        *   `response` (str): La respuesta generada por la IA.

### `backend/crud.py`

**Propósito:** Contiene las operaciones básicas de acceso a datos (CRUD - Create, Read, Update, Delete) para los libros en la base de datos. Estas funciones actúan como una capa de abstracción sobre SQLAlchemy.

**Funciones Principales:**

*   **`get_book_by_path(db: Session, file_path: str)`**
    *   **Lógica:** Busca un libro en la base de datos utilizando su ruta de archivo única.
    *   **Parámetros:** `db` (Session), `file_path` (str).
    *   **Retorna:** Un objeto `models.Book` si se encuentra, `None` en caso contrario.
*   **`get_book_by_title(db: Session, title: str)`**
    *   **Lógica:** Busca un libro por su título exacto.
    *   **Parámetros:** `db` (Session), `title` (str).
    *   **Retorna:** Un objeto `models.Book` si se encuentra, `None` en caso contrario.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**
    *   **Lógica:** Busca libros cuyo título contenga una cadena parcial (sin distinción entre mayúsculas y minúsculas), con soporte para paginación.
    *   **Parámetros:** `db` (Session), `title` (str), `skip` (int), `limit` (int).
    *   **Retorna:** Una lista de objetos `models.Book`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**
    *   **Lógica:** Obtiene una lista de libros. Permite filtrar por `category`, `author` (búsqueda parcial insensible a mayúsculas) y una búsqueda general `search` que aplica a título, autor o categoría. Los resultados se ordenan por ID de forma descendente.
    *   **Parámetros:** `db` (Session), `category` (str | None), `search` (str | None), `author` (str | None).
    *   **Retorna:** Una lista de objetos `models.Book`.
*   **`get_categories(db: Session) -> list[str]`**
    *   **Lógica:** Recupera todas las categorías únicas de libros de la base de datos, ordenadas alfabéticamente.
    *   **Parámetros:** `db` (Session).
    *   **Retorna:** Una lista de cadenas, cada una representando una categoría.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**
    *   **Lógica:** Crea un nuevo registro de libro en la base de datos con los metadatos proporcionados.
    *   **Parámetros:** `db` (Session), `title` (str), `author` (str), `category` (str), `cover_image_url` (str), `file_path` (str).
    *   **Retorna:** El objeto `models.Book` recién creado y refrescado.
*   **`delete_book(db: Session, book_id: int)`**
    *   **Lógica:** Elimina un libro de la base de datos por su ID. También elimina físicamente el archivo del libro (`file_path`) y su imagen de portada (`cover_image_url`) del disco si existen.
    *   **Parámetros:** `db` (Session), `book_id` (int).
    *   **Retorna:** El objeto `models.Book` eliminado si se encontró, `None` en caso contrario.
*   **`delete_books_by_category(db: Session, category: str)`**
    *   **Lógica:** Elimina todos los libros que pertenecen a una categoría específica, junto con sus archivos asociados del disco.
    *   **Parámetros:** `db` (Session), `category` (str).
    *   **Retorna:** El número de libros eliminados (int).
*   **`get_books_count(db: Session) -> int`**
    *   **Lógica:** Retorna el número total de libros registrados en la base de datos.
    *   **Parámetros:** `db` (Session).
    *   **Retorna:** Un entero con la cantidad de libros.

### `backend/database.py`

**Propósito:** Configura la conexión a la base de datos SQLite y proporciona una sesión manejada por SQLAlchemy para las operaciones ORM.

**Componentes Principales:**

*   **`SQLALCHEMY_DATABASE_URL`:** Cadena de conexión que apunta a un archivo `library.db` ubicado en la raíz del proyecto.
*   **`engine`:** Instancia del motor de SQLAlchemy, configurado para SQLite con `connect_args={"check_same_thread": False}` para manejar accesos concurrentes.
*   **`SessionLocal`:** Una fábrica de sesiones de SQLAlchemy, configurada para no hacer autocommit ni autoflush, lo que permite un control transaccional explícito.
*   **`Base`:** La clase base declarativa de SQLAlchemy a partir de la cual se heredarán los modelos ORM.

### `backend/utils.py`

**Propósito:** Contiene funciones de utilidad compartidas, especialmente para la configuración de APIs externas.

**Funciones Principales:**

*   **`configure_genai()`**
    *   **Lógica:** Carga las variables de entorno (`.env`), busca `GOOGLE_API_KEY` o `GEMINI_API_KEY`, y utiliza la primera clave encontrada para configurar el SDK de Google Generative AI (`genai`). Si no se encuentra ninguna clave, lanza un `ValueError`.
    *   **Parámetros:** Ninguno.
    *   **Retorna:** Nada.

### `backend/models.py`

**Propósito:** Define el modelo ORM `Book` para la base de datos, utilizando SQLAlchemy. Este modelo representa la tabla `books`.

**Clase Principal:**

*   **`Book(Base)`**
    *   **`__tablename__ = "books"`:** Nombre de la tabla en la base de datos.
    *   **`__table_args__ = {'extend_existing': True}`:** Permite que la tabla se redefina en el mismo proceso (útil para tests).
    *   **Columnas:**
        *   `id` (Integer, Primary Key, Indexed): Identificador único del libro.
        *   `title` (String, Indexed): Título del libro.
        *   `author` (String, Indexed): Autor del libro.
        *   `category` (String, Indexed): Categoría del libro.
        *   `cover_image_url` (String, Nullable): URL o ruta de la imagen de portada.
        *   `file_path` (String, Unique): Ruta absoluta al archivo del libro en el sistema de archivos, debe ser única.

### `backend/rag.py`

**Propósito:** Implementa la lógica central del sistema de Retrieval-Augmented Generation (RAG), incluyendo la extracción de texto, la generación de embeddings, el almacenamiento en una base de datos vectorial (ChromaDB) y la consulta a modelos de lenguaje grandes (Google Gemini).

**Componentes y Funciones Principales:**

*   **Variables de Configuración:**
    *   `EMBEDDING_MODEL`: Modelo de Gemini utilizado para generar embeddings.
    *   `GENERATION_MODEL`: Modelo de Gemini utilizado para generar respuestas conversacionales.
*   **`_ensure_init()`**
    *   **Lógica:** Inicializa lazy-load la configuración de `genai` (si `DISABLE_AI` no está establecido) y el cliente de ChromaDB, creando la colección `book_rag_collection` si no existe.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**
    *   **Lógica:** Genera un embedding vectorial para el texto dado. Si la IA está deshabilitada, devuelve un embedding dummy.
    *   **Parámetros:** `text` (str), `task_type` (str).
    *   **Retorna:** Una lista de flotantes (el embedding).
*   **`extract_text_from_pdf(file_path: str)`**
    *   **Lógica:** Extrae todo el texto de un archivo PDF usando `PyPDF2`.
    *   **Parámetros:** `file_path` (str).
    *   **Retorna:** El texto extraído (str).
*   **`extract_text_from_epub(file_path: str)`**
    *   **Lógica:** Extrae todo el texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`.
    *   **Parámetros:** `file_path` (str).
    *   **Retorna:** El texto extraído (str).
*   **`extract_text(file_path: str)`**
    *   **Lógica:** Función unificada para extraer texto, selecciona el método adecuado según la extensión del archivo (`.pdf` o `.epub`).
    *   **Parámetros:** `file_path` (str).
    *   **Retorna:** El texto extraído (str).
    *   **Lanza:** `ValueError` si el tipo de archivo no es soportado.
*   **`chunk_text(text: str, max_tokens: int = 1000)`**
    *   **Lógica:** Divide un texto largo en fragmentos más pequeños, basándose en un número máximo de tokens (estimado con `tiktoken` para "gpt-3.5-turbo").
    *   **Parámetros:** `text` (str), `max_tokens` (int).
    *   **Retorna:** Una lista de cadenas (los fragmentos).
*   **`_has_index_for_book(book_id: str)`**
    *   **Lógica:** Comprueba si ya existen vectores indexados para un `book_id` dado en ChromaDB.
    *   **Parámetros:** `book_id` (str).
    *   **Retorna:** `True` si tiene índice, `False` en caso contrario.
*   **`delete_book_from_rag(book_id: str)`**
    *   **Lógica:** Elimina todos los vectores asociados a un `book_id` de ChromaDB.
    *   **Parámetros:** `book_id` (str).
    *   **Retorna:** Nada.
*   **`get_index_count(book_id: str)`**
    *   **Lógica:** Devuelve el número de vectores almacenados para un `book_id` específico.
    *   **Parámetros:** `book_id` (str).
    *   **Retorna:** Un entero (el conteo).
*   **`has_index(book_id: str)`**
    *   **Lógica:** Helper público que indica si un libro tiene índice RAG (`get_index_count > 0`).
    *   **Parámetros:** `book_id` (str).
    *   **Retorna:** `True` si tiene índice, `False` en caso contrario.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**
    *   **Lógica:** Proceso principal de indexación RAG. Extrae el texto del libro, lo divide en fragmentos, genera embeddings para cada fragmento y los almacena en ChromaDB. Si `force_reindex` es `True`, elimina cualquier índice existente primero.
    *   **Parámetros:** `file_path` (str), `book_id` (str), `force_reindex` (bool).
    *   **Retorna:** Nada.
    *   **Lanza:** `ValueError` si el tipo de archivo no es soportado o no se puede extraer/fragmentar el texto.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**
    *   **Lógica:** Estima la cantidad de tokens y fragmentos para un archivo individual.
    *   **Parámetros:** `file_path` (str), `max_tokens` (int).
    *   **Retorna:** Un diccionario con `tokens` y `chunks`.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**
    *   **Lógica:** Estima la cantidad total de tokens y fragmentos para una lista de archivos.
    *   **Parámetros:** `file_paths` (list[str]), `max_tokens` (int).
    *   **Retorna:** Un diccionario con `tokens`, `chunks` y `files`.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**
    *   **Lógica:** Procesa una consulta RAG. Genera un embedding de la consulta, recupera los fragmentos de texto más relevantes del libro de ChromaDB. Construye un prompt para el modelo de generación de Gemini, incluyendo el contexto del libro, metadatos y (opcionalmente) información de la biblioteca. El `mode` de respuesta (`strict`, `balanced`, `open`) ajusta las instrucciones de la IA.
    *   **Parámetros:** `query` (str), `book_id` (str), `mode` (str), `metadata` (dict | None), `library` (dict | None).
    *   **Retorna:** La respuesta generada por la IA (str).

### `backend/main.py`

**Propósito:** Es el punto de entrada de la aplicación FastAPI. Configura la aplicación, monta directorios estáticos, maneja CORS y define todos los endpoints de la API, coordinando la lógica de otros módulos (CRUD, RAG, IA).

**Configuración Inicial:**

*   **Rutas de archivos:** Define rutas absolutas para el almacenamiento de libros, portadas y archivos temporales (`BOOKS_DIR_FS`, `STATIC_COVERS_DIR_FS`, etc.).
*   **CORS:** Configura el middleware `CORSMiddleware` para permitir solicitudes desde orígenes específicos (incluyendo localhost y redes privadas), configurables mediante variables de entorno `ALLOW_ORIGINS` y `ALLOW_ORIGIN_REGEX`.
*   **Base de datos:** Inicializa la creación de tablas con `models.Base.metadata.create_all(bind=database.engine)`.
*   **IA:** Carga la clave API de Gemini desde el entorno (`GOOGLE_API_KEY` o `GEMINI_API_KEY`) y configura el SDK de `genai`. `AI_ENABLED` controla la activación de funciones de IA.

**Funciones Auxiliares:**

*   **`analyze_with_gemini(text: str) -> dict`**
    *   **Lógica:** Envía un fragmento de texto de un libro a Google Gemini con un prompt específico para que identifique el título, autor y categoría, esperando una respuesta en formato JSON.
    *   **Retorna:** Un diccionario con `title`, `author`, `category` o valores de error si la IA falla o está deshabilitada.
*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**
    *   **Lógica:** Extrae texto de las primeras páginas de un PDF usando `fitz` (PyMuPDF) y busca una imagen de portada dentro del documento. Si encuentra una portada adecuada, la guarda y devuelve su URL.
    *   **Retorna:** Un diccionario con el `text` extraído y opcionalmente `cover_image_url`.
*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**
    *   **Lógica:** Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`. Intenta encontrar una imagen de portada siguiendo varias estrategias (metadatos, nombre de archivo). Si la encuentra, la guarda y devuelve su URL.
    *   **Retorna:** Un diccionario con el `text` extraído y opcionalmente `cover_image_url`.
    *   **Lanza:** `HTTPException` si no se puede extraer suficiente texto.
*   **`get_db()`**
    *   **Lógica:** Función de inyección de dependencias para FastAPI, que proporciona una sesión de base de datos (`SessionLocal`) y asegura su cierre después de la solicitud.

**Endpoints de la API:**

*   **`POST /upload-book/`** (`response_model=schemas.Book`)
    *   **Descripción:** Sube un archivo de libro (PDF o EPUB), lo procesa (extracción de texto y portada), lo analiza con IA para obtener metadatos y lo guarda en la base de datos.
    *   **Parámetros:** `book_file` (UploadFile).
    *   **Lanza:** `HTTPException` (409 si el libro ya existe, 400 si el tipo de archivo no es soportado, 422 si la IA no puede analizar el libro).
*   **`GET /books/`** (`response_model=List[schemas.Book]`)
    *   **Descripción:** Obtiene una lista de libros.
    *   **Parámetros de Query (opcionales):** `category` (str), `search` (str), `author` (str).
*   **`GET /books/count`** (`response_model=int`)
    *   **Descripción:** Retorna el número total de libros en la biblioteca.
*   **`GET /books/search/`** (`response_model=List[schemas.Book]`)
    *   **Descripción:** Busca libros por un título parcial, con paginación.
    *   **Parámetros de Query:** `title` (str), `skip` (int), `limit` (int).
*   **`GET /categories/`** (`response_model=List[str]`)
    *   **Descripción:** Retorna una lista de todas las categorías únicas de libros.
*   **`DELETE /books/{book_id}`**
    *   **Descripción:** Elimina un libro específico por su ID, incluyendo sus archivos físicos y su índice RAG.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Lanza:** `HTTPException` (404 si el libro no existe).
*   **`DELETE /categories/{category_name}`**
    *   **Descripción:** Elimina todos los libros de una categoría específica, incluyendo sus archivos físicos y sus índices RAG.
    *   **Parámetros de Ruta:** `category_name` (str).
    *   **Lanza:** `HTTPException` (404 si la categoría no se encuentra o está vacía).
*   **`GET /books/download/{book_id}`**
    *   **Descripción:** Permite descargar o visualizar un archivo de libro.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Retorna:** `FileResponse` con el contenido del archivo.
    *   **Lanza:** `HTTPException` (404 si el libro o el archivo no existen).
*   **`POST /tools/convert-epub-to-pdf`** (`response_model=schemas.ConversionResponse`)
    *   **Descripción:** Convierte un archivo EPUB subido a PDF. Guarda el PDF resultante temporalmente y proporciona una URL de descarga.
    *   **Parámetros:** `file` (UploadFile).
    *   **Lanza:** `HTTPException` (400 si el archivo no es EPUB, 500 si hay un error de conversión).
*   **`POST /rag/upload-book/`** (`response_model=schemas.RagUploadResponse`)
    *   **Descripción:** (Nota: En el frontend actual, esta ruta parece no usarse directamente en favor de indexar libros existentes.) Sube un archivo y lo procesa directamente para RAG, asignándole un `book_id` temporal.
    *   **Parámetros:** `file` (UploadFile).
    *   **Lanza:** `HTTPException` (500 si hay un error de procesamiento).
*   **`POST /rag/query/`** (`response_model=schemas.RagQueryResponse`)
    *   **Descripción:** Ejecuta una consulta conversacional RAG sobre un libro indexado.
    *   **Parámetros:** `query_data` (schemas.RagQuery, en el cuerpo de la solicitud).
    *   **Lanza:** `HTTPException` (500 si hay un error en la consulta RAG).
*   **`POST /rag/index/{book_id}`**
    *   **Descripción:** Inicia la indexación de un libro existente en la base de datos para el sistema RAG.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Parámetros de Query (opcionales):** `force` (bool, si es `True`, reindexa).
    *   **Lanza:** `HTTPException` (404 si el libro o el archivo no existen, 500 si hay un error de indexación).
*   **`GET /rag/status/{book_id}`**
    *   **Descripción:** Comprueba si un libro específico tiene un índice RAG y, si es así, el número de vectores almacenados.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Lanza:** `HTTPException` (500 si hay un error al obtener el estado).
*   **`POST /rag/reindex/category/{category_name}`**
    *   **Descripción:** (Re)indexa todos los libros de una categoría específica para RAG.
    *   **Parámetros de Ruta:** `category_name` (str).
    *   **Parámetros de Query (opcionales):** `force` (bool, por defecto `True`).
    *   **Lanza:** `HTTPException` (404 si la categoría no existe o no tiene libros).
*   **`POST /rag/reindex/all`**
    *   **Descripción:** (Re)indexa todos los libros de la biblioteca para RAG.
    *   **Parámetros de Query (opcionales):** `force` (bool, por defecto `True`).
*   **`GET /rag/estimate/book/{book_id}`**
    *   **Descripción:** Estima la cantidad de tokens, fragmentos y un coste opcional para indexar un libro en RAG.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Parámetros de Query (opcionales):** `per1k` (float), `max_tokens` (int).
    *   **Lanza:** `HTTPException` (404 si el libro no existe, 500 si hay un error).
*   **`GET /rag/estimate/category/{category_name}`**
    *   **Descripción:** Estima la cantidad de tokens, fragmentos y un coste opcional para indexar todos los libros de una categoría en RAG.
    *   **Parámetros de Ruta:** `category_name` (str).
    *   **Parámetros de Query (opcionales):** `per1k` (float), `max_tokens` (int).
    *   **Lanza:** `HTTPException` (404 si la categoría no existe o no tiene libros, 500 si hay un error).
*   **`GET /rag/estimate/all`**
    *   **Descripción:** Estima la cantidad de tokens, fragmentos y un coste opcional para indexar todos los libros de la biblioteca en RAG.
    *   **Parámetros de Query (opcionales):** `per1k` (float), `max_tokens` (int).
    *   **Lanza:** `HTTPException` (500 si hay un error).

## 4. Análisis Detallado del Frontend (React)

El frontend proporciona la interfaz de usuario para interactuar con la aplicación, utilizando React y `react-router-dom` para la navegación.

### `frontend/src/App.js`

**Propósito:** Es el componente raíz de la aplicación React. Se encarga de configurar el enrutamiento del lado del cliente y de renderizar los componentes principales de la interfaz.

*   **Estado/Props/Efectos:** No gestiona estado ni props directamente. Su propósito es definir la estructura de enrutamiento.
*   **Interacciones del Usuario:** Gestiona la navegación entre las diferentes vistas de la aplicación mediante `BrowserRouter` y `Routes`.
*   **Comunicación con el Backend:** No se comunica directamente. Las vistas hijas son las encargadas de ello.

### `frontend/src/Header.js`

**Propósito:** Muestra el encabezado de la aplicación, incluyendo el título, un contador dinámico de libros en la biblioteca y los enlaces de navegación principales.

*   **Estado:**
    *   `menuOpen` (boolean): Controla la visibilidad del menú de navegación en dispositivos móviles.
    *   `bookCount` (number): Muestra el número total de libros obtenidos del backend.
    *   `errorMessage` (string | null): Mensaje de error si falla la obtención del contador de libros.
*   **Efectos:**
    *   `useEffect` (al montar y cada 10 minutos): Realiza una petición `GET` a `/books/count` para obtener el número total de libros y actualizar `bookCount`. Maneja errores y reintenta periódicamente.
*   **Interacciones del Usuario:**
    *   Clic en el icono de "hamburguesa": Abre/cierra el menú de navegación en móvil.
    *   Clic en los `NavLink`: Navega a la ruta correspondiente y cierra el menú móvil si está abierto.
*   **Comunicación con el Backend:**
    *   `GET /books/count`: Para obtener el número total de libros.

### `frontend/src/ToolsView.js`

**Propósito:** Proporciona un espacio para herramientas útiles de la biblioteca. Actualmente, incluye un convertidor de EPUB a PDF.

#### `EpubToPdfConverter` (componente anidado)

*   **Estado:**
    *   `selectedFile` (File | null): El archivo EPUB seleccionado por el usuario.
    *   `message` (string): Mensaje de estado o error para el usuario (ej. "Convirtiendo...", "Error...").
    *   `isLoading` (boolean): Indica si el proceso de conversión está en curso.
*   **Efectos:** Ninguno específico.
*   **Interacciones del Usuario:**
    *   `handleFileChange`: Se activa cuando el usuario selecciona un archivo a través del input.
    *   `handleDrop`, `handleDragOver`: Implementa la funcionalidad de arrastrar y soltar archivos.
    *   `handleConvert`: Inicia la conversión del archivo EPUB seleccionado a PDF.
*   **Comunicación con el Backend:**
    *   `POST /tools/convert-epub-to-pdf`: Sube el archivo EPUB al backend. Si la conversión es exitosa, el backend devuelve una URL de descarga que el frontend utiliza para iniciar la descarga del PDF resultante.

### `frontend/src/UploadView.js`

**Propósito:** Permite a los usuarios subir uno o varios archivos de libros (PDF o EPUB) a la biblioteca. El componente gestiona el estado de cada archivo durante la subida y el procesamiento por parte de la IA del backend.

*   **Estado:**
    *   `filesToUpload` (array de objetos): Cada objeto representa un archivo con `file` (el objeto File), `status` ('pending', 'uploading', 'success', 'error') y `message` (el estado actual o error).
    *   `isUploading` (boolean): Indica si alguna operación de subida y procesamiento está activa.
*   **Efectos:** Ninguno.
*   **Interacciones del Usuario:**
    *   `handleFileChange`: Añade los archivos seleccionados por el usuario a `filesToUpload`.
    *   `handleDrop`, `handleDragOver`: Permite arrastrar y soltar archivos en la zona de subida.
    *   `handleUpload`: Inicia el proceso de subida de cada archivo `pending` secuencialmente. Actualiza el estado y el mensaje de cada archivo.
    *   Botón "Ir a la Biblioteca": Disponible cuando todas las subidas han terminado, redirige al usuario a la vista principal.
*   **Comunicación con el Backend:**
    *   `POST /upload-book/`: Envía cada archivo al backend en un objeto `FormData`. Recibe información sobre el libro procesado (título, autor) o detalles del error.

### `frontend/src/ReaderView.js`

**Propósito:** Proporciona una interfaz para leer libros en formato EPUB directamente en el navegador, utilizando el componente `react-reader`.

*   **Props:** Ninguna explícita, utiliza `useParams` para obtener `bookId` de la URL.
*   **Estado:**
    *   `location` (string | null): Representa la ubicación actual del lector dentro del EPUB (CFI string).
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB, necesarios para el lector.
    *   `isLoading` (boolean): Indica si el archivo del libro se está cargando.
    *   `error` (string): Mensaje de error si la carga del libro falla.
*   **Efectos:**
    *   `useEffect` (cuando `bookId` cambia): Realiza una petición `GET` a `/books/download/{bookId}` para obtener los datos binarios del EPUB como un `ArrayBuffer`. Actualiza `isLoading` y `error`.
*   **Interacciones del Usuario:**
    *   El componente `ReactReader` gestiona la navegación y la interacción con el libro. `locationChanged` es un callback que actualiza el estado `location` con el CFI actual.
*   **Comunicación con el Backend:**
    *   `GET /books/download/{bookId}`: Para obtener el contenido del archivo EPUB.

### `frontend/src/ErrorBoundary.js`

**Propósito:** Un componente estándar de React que captura errores de JavaScript en sus componentes hijos y muestra una interfaz de usuario de fallback en lugar de dejar que la aplicación falle por completo.

*   **Estado:**
    *   `hasError` (boolean): `true` si se ha capturado un error en los componentes hijos.
    *   `error` (Error | null): El objeto de error que fue capturado.
*   **Métodos del Ciclo de Vida:**
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para indicar que ha ocurrido un error.
    *   `componentDidCatch(error, info)`: Se usa para registrar el error y la información del componente en la consola.
*   **Renderizado:** Si `hasError` es `true`, renderiza un mensaje de error con los detalles. De lo contrario, renderiza los `props.children`.

### `frontend/src/RagView.js`

**Propósito:** Proporciona la interfaz para el sistema RAG, permitiendo al usuario seleccionar un libro de su biblioteca, gestionar su indexación para RAG y luego conversar con él mediante un modelo de lenguaje.

*   **Estado:**
    *   `message` (string): Mensajes de estado o instrucción para el usuario.
    *   `isLoading` (boolean): Indica si una consulta a la IA está en curso.
    *   `bookId` (string | null): El ID del libro actualmente activo para el chat RAG.
    *   `chatHistory` (array de `{ sender: 'user' | 'gemini', text: string }`): Historial de la conversación.
    *   `currentQuery` (string): La entrada de texto actual del usuario para la consulta.
    *   `libraryBooks` (array de objetos Book): Lista de todos los libros disponibles en la biblioteca.
    *   `selectedLibraryId` (string): El ID del libro seleccionado en el buscador.
    *   `libStatus` (objeto): `{ loading, indexed, vector_count, error }` - estado del índice RAG para el libro seleccionado.
    *   `actionsBusy` (boolean): Bloquea acciones de indexación/reindexación para evitar concurrencia.
    *   `refreshing` (boolean): Indica que se está refrescando el estado RAG (no bloquea el chat).
    *   `searchTerm` (string): Texto de búsqueda para filtrar `libraryBooks`.
    *   `searching` (boolean): Indica si se está realizando una búsqueda.
    *   `searchResults` (array de objetos Book): Libros encontrados por el `searchTerm`.
    *   `resultsOpen` (boolean): Controla la visibilidad del dropdown de resultados de búsqueda.
    *   `mode` (string): Modo de respuesta de la IA seleccionada ('strict', 'balanced', 'open').
    *   `selectedBook` (objeto Book | null): El objeto completo del libro seleccionado.
*   **Refs:**
    *   `inputRef`: Referencia al `textarea` del chat para enfocarlo.
    *   `chatHistoryRef`: Referencia al contenedor del historial del chat para auto-scrolling.
*   **Efectos:**
    *   `useEffect` (al montar): Carga todos los libros de la biblioteca (`GET /books/`) para la selección.
    *   `useEffect` (cuando `searchTerm` cambia, con debounce): Realiza una búsqueda de libros (`GET /books/?search=...`) y actualiza `searchResults`.
    *   `useEffect` (cuando `selectedLibraryId` cambia): Llama a `checkLibraryStatus` para obtener el estado del índice RAG del libro seleccionado.
    *   `useEffect` (cuando `chatHistory` o `isLoading` cambian): Realiza auto-scrolling del historial de chat para mostrar los mensajes más recientes.
*   **Interacciones del Usuario:**
    *   Input de texto para `searchTerm`: Busca libros en la biblioteca.
    *   Selección de un libro de los `searchResults`: Establece `selectedLibraryId` y `selectedBook`.
    *   Botones "Comprobar RAG", "Indexar antes de charlar", "Reindexar": Llaman a `checkLibraryStatus` o `indexLibraryBook`.
    *   Botón "Chatear": Habilita el chat si el libro está indexado.
    *   Radio buttons para `mode`: Cambian la preferencia de respuesta de la IA.
    *   `textarea` para `currentQuery`: Permite al usuario introducir preguntas. Auto-redimensiona.
    *   Botón "Enviar": `handleQuerySubmit` envía la pregunta a la API RAG.
*   **Comunicación con el Backend:**
    *   `GET /books/` (y `/books/?search=...`): Para cargar y buscar libros en la biblioteca.
    *   `GET /rag/status/{book_id}`: Para obtener el estado de indexación RAG de un libro.
    *   `POST /rag/index/{book_id}`: Para indexar (o reindexar) un libro en el sistema RAG.
    *   `POST /rag/query/`: Para enviar la pregunta del usuario al sistema RAG y obtener una respuesta de la IA.

### `frontend/src/LibraryView.js`

**Propósito:** Es la vista principal de la aplicación donde se muestran todos los libros de la biblioteca. Permite buscar, filtrar por autor/categoría, y realizar acciones como leer, descargar o eliminar libros.

*   **Estado:**
    *   `books` (array de objetos Book): La lista de libros que se muestran.
    *   `searchParams` (URLSearchParams): Objeto para gestionar los parámetros de búsqueda en la URL (filtrado por categoría/autor).
    *   `searchTerm` (string): El término de búsqueda introducido por el usuario.
    *   `debouncedSearchTerm` (string): Una versión de `searchTerm` con retraso para optimizar las llamadas a la API.
    *   `error` (string): Mensaje de error si falla la carga de libros.
    *   `loading` (boolean): Indica si los libros se están cargando.
    *   `isMobile` (boolean): Indica si la aplicación se está ejecutando en un dispositivo móvil, usado para adaptar la UI (ej. botón de descarga).
*   **Hooks Personalizados:**
    *   `useDebounce`: Retrasa la actualización de un valor para evitar llamadas excesivas a la API.
*   **Componentes Anidados:**
    *   `BookCover`: Muestra la portada de un libro, con un fallback si la imagen no está disponible o falla.
*   **Efectos:**
    *   `useEffect` (al montar y redimensionar): Detecta si la pantalla es móvil (`window.innerWidth <= 768`).
    *   `useEffect` (cuando `debouncedSearchTerm` o `searchParams` cambian): Llama a `fetchBooks` para recargar la lista de libros con los filtros y la búsqueda actual.
*   **Interacciones del Usuario:**
    *   Input de `searchTerm`: Permite buscar libros por título, autor o categoría.
    *   Clic en el nombre del autor (`handleAuthorClick`): Filtra los libros por ese autor.
    *   Clic en la categoría (`handleCategoryClick`): Filtra los libros por esa categoría.
    *   Botón "×" (`handleDeleteBook`): Elimina un libro de la biblioteca.
    *   Botón "Abrir PDF": Abre el PDF en una nueva pestaña.
    *   Botón "Leer EPUB": Navega a `ReaderView` para leer el EPUB.
    *   Botón "Descargar PDF/EPUB" (solo en móvil): Descarga el archivo del libro.
*   **Comunicación con el Backend:**
    *   `GET /books/?category=...&search=...&author=...`: Para obtener la lista de libros filtrados/buscados.
    *   `DELETE /books/{bookId}`: Para eliminar un libro.
    *   `GET /books/download/{bookId}`: Para descargar o acceder al archivo del libro.

### `frontend/src/config.js`

**Propósito:** Define la URL base del API del backend, permitiendo que sea configurable mediante variables de entorno.

*   **Variables:**
    *   `API_URL`: `process.env.REACT_APP_API_URL` o `http://localhost:8001` por defecto. Esta variable se utiliza en todas las peticiones fetch del frontend.

### `frontend/src/CategoriesView.js`

**Propósito:** Muestra una lista de todas las categorías únicas de libros disponibles en la biblioteca, permitiendo al usuario navegar por ellas y filtrar la vista de la biblioteca.

*   **Estado:**
    *   `categories` (array de strings): Lista de nombres de categorías únicas.
    *   `error` (string): Mensaje de error si falla la carga de categorías.
    *   `loading` (boolean): Indica si las categorías se están cargando.
*   **Efectos:**
    *   `useEffect` (al montar): Realiza una petición `GET` a `/categories/` para obtener la lista de categorías únicas.
*   **Interacciones del Usuario:**
    *   Clic en una tarjeta de categoría: Navega a la `LibraryView` con el parámetro de URL `?category=nombre_categoria`, filtrando los libros por esa categoría.
*   **Comunicación con el Backend:**
    *   `GET /categories/`: Para obtener la lista de todas las categorías únicas.

### `frontend/src/index.js`

**Propósito:** Es el punto de entrada de la aplicación React. Renderiza el componente `App` dentro del elemento DOM con el ID 'root'.

*   No contiene lógica de aplicación ni estado propio, solo la inicialización de React.

## 5. Flujo de Datos y API

### Flujo de Datos para la Carga y Procesamiento de un Libro

1.  **Inicio en Frontend (`UploadView.js`):**
    *   El usuario selecciona uno o varios archivos (PDF o EPUB) desde su sistema local o los arrastra y suelta en la interfaz.
    *   `UploadView.js` crea un objeto `FormData` para cada archivo.
    *   Por cada archivo, `UploadView.js` envía una petición **`POST` a `/upload-book/`** con el archivo en el cuerpo.
2.  **Procesamiento en Backend (`main.py` - `upload_book` endpoint):**
    *   **Almacenamiento Temporal:** FastAPI recibe el archivo y lo guarda en el directorio `backend/books/`.
    *   **Extracción de Texto y Portada:**
        *   Se detecta la extensión del archivo (`.pdf` o `.epub`).
        *   Se llama a `process_pdf` o `process_epub` para:
            *   Extraer el texto de las primeras páginas del libro.
            *   Intentar identificar y extraer una imagen de portada. Si se encuentra, la portada se guarda en `backend/static/covers/` y se genera una URL para ella.
    *   **Análisis con IA:**
        *   El texto extraído se envía a `analyze_with_gemini`, que utiliza Google Gemini para identificar el `title`, `author` y `category` del libro.
        *   **Control de Calidad:** Si la IA no logra identificar el título y el autor (ambos son "Desconocido"), el archivo subido se elimina y se devuelve un error 422 al frontend.
    *   **Almacenamiento en Base de Datos:**
        *   Si el análisis con IA es exitoso, los metadatos (título, autor, categoría, URL de portada, ruta del archivo) se envían a `crud.create_book`.
        *   `crud.create_book` guarda el nuevo libro en la tabla `books` de la base de datos SQLite.
    *   **Respuesta al Frontend:** Se devuelve un objeto `schemas.Book` (incluyendo el ID generado) o un `HTTPException` con detalles del error.
3.  **Finalización en Frontend (`UploadView.js`):**
    *   `UploadView.js` recibe la respuesta y actualiza el estado de la carga de cada archivo, mostrando si el libro se añadió correctamente (con su título) o si hubo un error.
    *   Una vez que todos los archivos han sido procesados, se muestra un botón para que el usuario navegue a la vista de la biblioteca.

### Flujo de Datos para la Conversación RAG con un Libro

1.  **Inicio en Frontend (`RagView.js`):**
    *   El usuario busca y selecciona un libro existente de la biblioteca.
    *   `RagView.js` comprueba el estado de indexación RAG del libro seleccionado mediante una petición **`GET` a `/rag/status/{book_id}`**.
2.  **Indexación del Libro (si es necesario):**
    *   Si el libro no está indexado para RAG (según la respuesta de `/rag/status/`), el usuario hace clic en "Indexar antes de charlar".
    *   `RagView.js` envía una petición **`POST` a `/rag/index/{book_id}`**.
    *   **Procesamiento en Backend (`main.py` - `index_existing_book_for_rag` endpoint):**
        *   FastAPI recupera el `file_path` del libro de la base de datos (`crud`).
        *   Llama a `rag.process_book_for_rag`:
            *   `rag.extract_text` lee el contenido completo del libro (PDF/EPUB).
            *   `rag.chunk_text` divide el texto en fragmentos más pequeños.
            *   `rag.get_embedding` genera un embedding vectorial para cada fragmento usando Google Gemini.
            *   ChromaDB almacena estos fragmentos y sus embeddings, asociados al `book_id`.
    *   `RagView.js` recibe la confirmación de indexación.
3.  **Consulta Conversacional:**
    *   Una vez que el libro está indexado y el chat está "listo", el usuario escribe una pregunta en el `textarea`.
    *   `RagView.js` envía una petición **`POST` a `/rag/query/`** con la pregunta (`query`), el `book_id` y el `mode` de respuesta.
4.  **Procesamiento de Consulta en Backend (`main.py` - `query_rag_endpoint`):**
    *   FastAPI recupera los metadatos del libro (título, autor, categoría) de la base de datos para proporcionar contexto adicional a la IA.
    *   Llama a `rag.query_rag`:
        *   `rag.get_embedding` genera un embedding de la pregunta del usuario.
        *   ChromaDB realiza una búsqueda de similitud vectorial para encontrar los fragmentos de texto del libro más relevantes para la pregunta.
        *   Se construye un prompt detallado para Google Gemini, que incluye la pregunta del usuario, los fragmentos relevantes del libro, los metadatos del libro, información contextual de la biblioteca (otras obras del mismo autor) y las instrucciones según el `mode` seleccionado.
        *   Google Gemini procesa el prompt y genera una respuesta coherente.
    *   Se devuelve la respuesta de la IA como un objeto `schemas.RagQueryResponse`.
5.  **Visualización en Frontend (`RagView.js`):**
    *   `RagView.js` recibe la respuesta de Gemini y la añade al `chatHistory`, mostrándola al usuario.

### Principales Endpoints de la API (Backend FastAPI)

La API RESTful del backend expone los siguientes endpoints principales:

*   **Libros:**
    *   `POST /upload-book/`: Sube un libro (PDF/EPUB) para procesamiento y adición a la biblioteca.
    *   `GET /books/`: Obtiene una lista de libros, con filtros opcionales (`category`, `search`, `author`).
    *   `GET /books/count`: Retorna el número total de libros.
    *   `GET /books/search/`: Busca libros por título parcial.
    *   `DELETE /books/{book_id}`: Elimina un libro específico por ID.
    *   `GET /books/download/{book_id}`: Descarga o abre el archivo de un libro.

*   **Categorías:**
    *   `GET /categories/`: Obtiene una lista de todas las categorías únicas.
    *   `DELETE /categories/{category_name}`: Elimina una categoría y todos sus libros asociados.

*   **Herramientas:**
    *   `POST /tools/convert-epub-to-pdf`: Convierte un archivo EPUB a PDF.

*   **RAG (Retrieval-Augmented Generation):**
    *   `POST /rag/query/`: Envía una pregunta a la IA para un libro específico.
    *   `POST /rag/index/{book_id}`: Inicia o fuerza la indexación RAG de un libro existente.
    *   `GET /rag/status/{book_id}`: Comprueba el estado de indexación RAG de un libro.
    *   `POST /rag/reindex/category/{category_name}`: (Re)indexa todos los libros de una categoría.
    *   `POST /rag/reindex/all`: (Re)indexa todos los libros de la biblioteca.
    *   `GET /rag/estimate/book/{book_id}`: Estima costes y recursos para indexar un libro.
    *   `GET /rag/estimate/category/{category_name}`: Estima costes y recursos para indexar una categoría.
    *   `GET /rag/estimate/all`: Estima costes y recursos para indexar toda la biblioteca.
```
**Critique and Refinement:**

1.  **Completeness:** All requested sections are present, and all relevant files have been covered in detail for both backend and frontend. The explanation of each function/class/component includes its purpose, logic, parameters/state/props, and returns/effects.
2.  **Clarity and Structure:**
    *   The Markdown headings and subheadings are clear and follow the requested structure.
    *   Bullet points are used effectively for lists of functions, classes, and state variables.
    *   Code snippets (like parameter types) are included where appropriate to illustrate API schemas or function signatures.
    *   Flow descriptions for data are step-by-step and easy to follow.
3.  **Accuracy:**
    *   **Backend:**
        *   `schemas.py`: Correctly describes Pydantic models.
        *   `crud.py`: Correctly lists and describes CRUD functions. Mentions file deletion for `delete_book` and `delete_books_by_category`.
        *   `database.py`: Correctly describes SQLAlchemy setup.
        *   `utils.py`: Correctly describes `configure_genai`.
        *   `models.py`: Correctly describes the `Book` ORM model.
        *   `rag.py`: Correctly describes RAG components, `_ensure_init` for lazy loading, `tiktoken` for chunking, ChromaDB, and Gemini interaction modes.
        *   `main.py`: Correctly describes FastAPI setup, local helper functions (`analyze_with_gemini`, `process_pdf`, `process_epub`), and all API endpoints. Noted `rag/upload-book` seems unused by frontend.
        *   `alembic/...`: Briefly mentions its purpose.
    *   **Frontend:**
        *   `App.js`: Correctly describes routing.
        *   `Header.js`: Correctly describes state, effects (polling for book count), and interactions.
        *   `ToolsView.js`: Correctly describes conversion logic, state, and backend call.
        *   `UploadView.js`: Correctly describes multi-file upload, state management, and backend communication.
        *   `ReaderView.js`: Correctly describes EPUB reading, `react-reader`, and fetching binary data.
        *   `ErrorBoundary.js`: Standard description of an error boundary.
        *   `RagView.js`: Very detailed and accurate description of state, effects, interactions, and backend calls for the complex RAG feature (searching books, checking status, indexing, querying, modes).
        *   `LibraryView.js`: Correctly describes book display, search/filter (including custom `useDebounce` hook), actions, and mobile adaptations.
        *   `config.js`: Correctly describes API URL configuration.
        *   `CategoriesView.js`: Correctly describes category listing and filtering interaction.
        *   `index.js`: Standard description.
4.  **Formatting:** Markdown is correctly used for headers, lists, code blocks, and bold text. The file structure section uses a code block for clarity.
5.  **Language:** Spanish is used consistently as requested.
6.  **Senior Software Engineer / Technical Writer Tone:** The tone is professional, informative, and precise, suitable for a technical audience. It avoids jargon where simpler terms suffice but uses accurate technical terms for concepts like ORM, RAG, embeddings, etc.

One minor thing for `backend/models.py`, `__table_args__ = {'extend_existing': True}` is good to mention, especially its implication for tests (allowing redefinition), which is common for SQLAlchemy's declarative base. I included this.

The `STATIC_TEMP_DIR` variable in `backend/main.py` for `/rag/upload-book/` doesn't seem to be defined explicitly in `main.py` (it might be in a removed block or was an oversight). However, since the endpoint is noted as "deprecated/unused based on frontend", it's acceptable not to over-analyze a potentially incomplete or unused part of the code for this documentation. The main RAG flow uses existing book IDs, which is well-documented.

The documentation seems solid.
```markdown
# Documentación del Proyecto: Mi Librería Inteligente

Este documento proporciona una visión técnica detallada del proyecto "Mi Librería Inteligente", abarcando su arquitectura, estructura de código, componentes de backend y frontend, y los flujos de datos clave.

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su biblioteca digital personal. Ofrece funcionalidades para cargar libros (PDF y EPUB), que son automáticamente analizados por inteligencia artificial (Google Gemini) para extraer su título, autor y categoría. Los libros se almacenan en una base de datos y se pueden visualizar, buscar, filtrar por categoría o autor, leer y descargar. Además, incorpora un sistema de Retrieval-Augmented Generation (RAG) que permite a los usuarios interactuar conversacionalmente con el contenido de sus libros mediante IA, haciendo preguntas y obteniendo respuestas basadas en el texto del libro. También incluye una herramienta de conversión de EPUB a PDF.

**Arquitectura General:**

*   **Frontend:** Desarrollado con React, proporcionando una interfaz de usuario interactiva y dinámica.
*   **Backend:** Construido con FastAPI (Python), que expone una API RESTful para la gestión de libros, la integración con la IA y las funcionalidades RAG y de conversión.
*   **Base de Datos:** SQLite se utiliza como base de datos persistente, con SQLAlchemy como Object-Relational Mapper (ORM) para la interacción con los modelos de datos. Las migraciones se gestionan con Alembic.
*   **Inteligencia Artificial:** Google Gemini es el motor de IA principal, utilizado para:
    *   Análisis inteligente del contenido de los libros (extracción de metadatos).
    *   Generación de embeddings de texto para el sistema RAG.
    *   Generación de respuestas conversacionales en el módulo RAG.
*   **Base de Datos Vectorial (VectorDB):** ChromaDB se utiliza para almacenar los embeddings de los fragmentos de texto de los libros, permitiendo una búsqueda semántica eficiente para el sistema RAG.
*   **Almacenamiento de Archivos:** Los archivos de los libros (PDF, EPUB) y sus portadas extraídas se almacenan directamente en el sistema de archivos del servidor.

## 2. Estructura del Proyecto

El proyecto se divide en dos directorios principales: `backend/` para la lógica del servidor y `frontend/` para la aplicación cliente.

```
.
├── backend/
│   ├── alembic/                      # Herramienta de migración de base de datos SQLAlchemy (Alembic)
│   │   ├── versions/                 # Scripts de migración de la base de datos
│   │   └── env.py
│   ├── tests/                        # Pruebas unitarias y de integración para el backend
│   ├── tests_curated/                # Pruebas adicionales, posiblemente generadas o curadas
│   ├── __init__.py                   # Archivo de inicialización del paquete Python
│   ├── crud.py                       # Operaciones CRUD para la base de datos
│   ├── database.py                   # Configuración de la conexión a la base de datos
│   ├── main.py                       # Punto de entrada de la aplicación FastAPI y definición de endpoints
│   ├── models.py                     # Definiciones de modelos de base de datos SQLAlchemy
│   ├── rag.py                        # Lógica para el sistema Retrieval-Augmented Generation (RAG)
│   ├── schemas.py                    # Modelos Pydantic para la validación de datos de la API
│   └── utils.py                      # Funciones de utilidad generales (ej. configuración de IA)
├── frontend/
│   ├── public/                       # Archivos estáticos públicos (index.html, etc.)
│   ├── src/                          # Código fuente de la aplicación React
│   │   ├── App.css                   # Estilos CSS globales
│   │   ├── App.js                    # Componente raíz de la aplicación
│   │   ├── CategoriesView.css
│   │   ├── CategoriesView.js         # Vista para mostrar y gestionar categorías
│   │   ├── ErrorBoundary.js          # Componente para manejar errores de UI
│   │   ├── Header.css
│   │   ├── Header.js                 # Componente de encabezado y navegación
│   │   ├── LibraryView.css
│   │   ├── LibraryView.js            # Vista principal de la biblioteca
│   │   ├── RagView.css
│   │   ├── RagView.js                # Vista para la conversación RAG con IA
│   │   ├── ReaderView.css
│   │   ├── ReaderView.js             # Vista para leer libros (EPUB)
│   │   ├── ToolsView.css
│   │   ├── ToolsView.js              # Vista de herramientas (ej. conversor EPUB a PDF)
│   │   ├── UploadView.css
│   │   ├── UploadView.js             # Vista para subir nuevos libros
│   │   ├── config.js                 # Configuración de la URL del API
│   │   ├── index.css
│   │   ├── index.js                  # Punto de entrada de React
│   │   └── reportWebVitals.js        # Utilidad para medir el rendimiento web
│   └── package.json                  # Definiciones de dependencias y scripts de React
├── .env.example                      # Archivo de ejemplo para variables de entorno
├── library.db                        # Base de datos SQLite
└── README.md                         # Archivo README del proyecto
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend es el núcleo de la lógica de negocio, la interacción con la base de datos y la integración de la IA.

### `backend/schemas.py`

**Propósito:** Define los modelos de datos Pydantic que se utilizan para la validación, serialización y documentación de los datos de entrada y salida de la API de FastAPI.

**Clases Principales:**

*   **`BookBase(BaseModel)`**
    *   **Lógica:** Esquema base para la información de un libro.
    *   **Parámetros:**
        *   `title` (str): Título del libro.
        *   `author` (str): Autor del libro.
        *   `category` (str): Categoría a la que pertenece el libro.
        *   `cover_image_url` (str | None): URL o ruta de la imagen de portada (opcional).
        *   `file_path` (str): Ruta absoluta al archivo del libro en el sistema de archivos del servidor.
*   **`Book(BookBase)`**
    *   **Lógica:** Extiende `BookBase` añadiendo el ID de la base de datos. Se configura `from_attributes = True` para permitir la conversión directa desde objetos ORM.
    *   **Parámetros:**
        *   `id` (int): Identificador único del libro en la base de datos.
*   **`ConversionResponse(BaseModel)`**
    *   **Lógica:** Esquema para la respuesta de la conversión de EPUB a PDF.
    *   **Parámetros:**
        *   `download_url` (str): URL donde se puede descargar el archivo PDF resultante.
*   **`RagUploadResponse(BaseModel)`**
    *   **Lógica:** Esquema para la respuesta cuando un libro se procesa para RAG.
    *   **Parámetros:**
        *   `book_id` (str): Identificador del libro procesado para RAG.
        *   `message` (str): Mensaje de estado de la operación.
*   **`RagQuery(BaseModel)`**
    *   **Lógica:** Esquema para las consultas al sistema RAG.
    *   **Parámetros:**
        *   `query` (str): La pregunta del usuario.
        *   `book_id` (str): El ID del libro al que se refiere la pregunta.
        *   `mode` (str | None): Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`). Por defecto es `None` (el backend lo interpreta como `balanced`).
*   **`RagQueryResponse(BaseModel)`**
    *   **Lógica:** Esquema para la respuesta del sistema RAG.
    *   **Parámetros:**
        *   `response` (str): La respuesta generada por la IA.

### `backend/crud.py`

**Propósito:** Contiene las operaciones básicas de acceso a datos (CRUD - Create, Read, Update, Delete) para los libros en la base de datos. Estas funciones actúan como una capa de abstracción sobre SQLAlchemy.

**Funciones Principales:**

*   **`get_book_by_path(db: Session, file_path: str)`**
    *   **Lógica:** Busca un libro en la base de datos utilizando su ruta de archivo única.
    *   **Parámetros:** `db` (Session), `file_path` (str).
    *   **Retorna:** Un objeto `models.Book` si se encuentra, `None` en caso contrario.
*   **`get_book_by_title(db: Session, title: str)`**
    *   **Lógica:** Busca un libro por su título exacto.
    *   **Parámetros:** `db` (Session), `title` (str).
    *   **Retorna:** Un objeto `models.Book` si se encuentra, `None` en caso contrario.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**
    *   **Lógica:** Busca libros cuyo título contenga una cadena parcial (sin distinción entre mayúsculas y minúsculas), con soporte para paginación.
    *   **Parámetros:** `db` (Session), `title` (str), `skip` (int), `limit` (int).
    *   **Retorna:** Una lista de objetos `models.Book`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**
    *   **Lógica:** Obtiene una lista de libros. Permite filtrar por `category`, `author` (búsqueda parcial insensible a mayúsculas) y una búsqueda general `search` que aplica a título, autor o categoría. Los resultados se ordenan por ID de forma descendente.
    *   **Parámetros:** `db` (Session), `category` (str | None), `search` (str | None), `author` (str | None).
    *   **Retorna:** Una lista de objetos `models.Book`.
*   **`get_categories(db: Session) -> list[str]`**
    *   **Lógica:** Recupera todas las categorías únicas de libros de la base de datos, ordenadas alfabéticamente.
    *   **Parámetros:** `db` (Session).
    *   **Retorna:** Una lista de cadenas, cada una representando una categoría.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**
    *   **Lógica:** Crea un nuevo registro de libro en la base de datos con los metadatos proporcionados.
    *   **Parámetros:** `db` (Session), `title` (str), `author` (str), `category` (str), `cover_image_url` (str), `file_path` (str).
    *   **Retorna:** El objeto `models.Book` recién creado y refrescado.
*   **`delete_book(db: Session, book_id: int)`**
    *   **Lógica:** Elimina un libro de la base de datos por su ID. También elimina físicamente el archivo del libro (`file_path`) y su imagen de portada (`cover_image_url`) del disco si existen.
    *   **Parámetros:** `db` (Session), `book_id` (int).
    *   **Retorna:** El objeto `models.Book` eliminado si se encontró, `None` en caso contrario.
*   **`delete_books_by_category(db: Session, category: str)`**
    *   **Lógica:** Elimina todos los libros que pertenecen a una categoría específica, junto con sus archivos asociados del disco.
    *   **Parámetros:** `db` (Session), `category` (str).
    *   **Retorna:** El número de libros eliminados (int).
*   **`get_books_count(db: Session) -> int`**
    *   **Lógica:** Retorna el número total de libros registrados en la base de datos.
    *   **Parámetros:** `db` (Session).
    *   **Retorna:** Un entero con la cantidad de libros.

### `backend/database.py`

**Propósito:** Configura la conexión a la base de datos SQLite y proporciona una sesión manejada por SQLAlchemy para las operaciones ORM.

**Componentes Principales:**

*   **`SQLALCHEMY_DATABASE_URL`:** Cadena de conexión que apunta a un archivo `library.db` ubicado en la raíz del proyecto (a un nivel superior al directorio `backend`).
*   **`engine`:** Instancia del motor de SQLAlchemy, configurado para SQLite con `connect_args={"check_same_thread": False}` para manejar accesos concurrentes en un entorno multiproceso.
*   **`SessionLocal`:** Una fábrica de sesiones de SQLAlchemy, configurada para no hacer autocommit ni autoflush, lo que permite un control transaccional explícito.
*   **`Base`:** La clase base declarativa de SQLAlchemy a partir de la cual se heredarán los modelos ORM.

### `backend/utils.py`

**Propósito:** Contiene funciones de utilidad compartidas, específicamente para la configuración de APIs externas como la de Google Generative AI.

**Funciones Principales:**

*   **`configure_genai()`**
    *   **Lógica:** Carga las variables de entorno (`.env`), busca `GOOGLE_API_KEY` o `GEMINI_API_KEY` (priorizando `GOOGLE_API_KEY`), y utiliza la primera clave encontrada para configurar el SDK de Google Generative AI (`genai`). Si no se encuentra ninguna clave, lanza un `ValueError`.
    *   **Parámetros:** Ninguno.
    *   **Retorna:** Nada.

### `backend/models.py`

**Propósito:** Define el modelo ORM `Book` para la base de datos, utilizando SQLAlchemy. Este modelo representa la tabla `books`.

**Clase Principal:**

*   **`Book(Base)`**
    *   **`__tablename__ = "books"`:** Nombre de la tabla en la base de datos.
    *   **`__table_args__ = {'extend_existing': True}`:** Permite que la tabla se redefina en el mismo proceso (útil para tests, por ejemplo).
    *   **Columnas:**
        *   `id` (Integer, Primary Key, Indexed): Identificador único del libro.
        *   `title` (String, Indexed): Título del libro.
        *   `author` (String, Indexed): Autor del libro.
        *   `category` (String, Indexed): Categoría del libro.
        *   `cover_image_url` (String, Nullable): URL o ruta de la imagen de portada.
        *   `file_path` (String, Unique): Ruta absoluta al archivo del libro en el sistema de archivos, debe ser única.

### `backend/rag.py`

**Propósito:** Implementa la lógica central del sistema de Retrieval-Augmented Generation (RAG), incluyendo la extracción de texto de libros, la generación de embeddings, el almacenamiento en una base de datos vectorial (ChromaDB) y la consulta a modelos de lenguaje grandes (Google Gemini) para generar respuestas contextualizadas.

**Componentes y Funciones Principales:**

*   **Variables de Configuración:**
    *   `EMBEDDING_MODEL`: Modelo de Gemini utilizado para generar embeddings, configurable por `GEMINI_EMBEDDING_MODEL`.
    *   `GENERATION_MODEL`: Modelo de Gemini utilizado para generar respuestas conversacionales, configurable por `GEMINI_GENERATION_MODEL`.
*   **`_ensure_init()`**
    *   **Lógica:** Función interna para asegurar la inicialización perezosa de la configuración de `genai` (si `DISABLE_AI` no está establecido y hay API Key) y el cliente de ChromaDB, creando la colección `book_rag_collection` si no existe.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**
    *   **Lógica:** Genera un embedding vectorial para el texto dado utilizando el `EMBEDDING_MODEL`. Si la IA está deshabilitada (por `DISABLE_AI` o falta de API key), devuelve un embedding dummy determinista para propósitos de prueba.
    *   **Parámetros:** `text` (str), `task_type` (str).
    *   **Retorna:** Una lista de flotantes (el embedding).
*   **`extract_text_from_pdf(file_path: str)`**
    *   **Lógica:** Extrae todo el texto de un archivo PDF usando la librería `PyPDF2`.
    *   **Parámetros:** `file_path` (str).
    *   **Retorna:** El texto extraído (str).
*   **`extract_text_from_epub(file_path: str)`**
    *   **Lógica:** Extrae todo el texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup` para parsear el HTML.
    *   **Parámetros:** `file_path` (str).
    *   **Retorna:** El texto extraído (str).
*   **`extract_text(file_path: str)`**
    *   **Lógica:** Función unificada para extraer texto, selecciona el método adecuado (`extract_text_from_pdf` o `extract_text_from_epub`) según la extensión del archivo.
    *   **Parámetros:** `file_path` (str).
    *   **Retorna:** El texto extraído (str).
    *   **Lanza:** `ValueError` si el tipo de archivo no es soportado.
*   **`chunk_text(text: str, max_tokens: int = 1000)`**
    *   **Lógica:** Divide un texto largo en fragmentos más pequeños, basándose en un número máximo de tokens. Utiliza `tiktoken` (para "gpt-3.5-turbo") como una aproximación para la tokenización de Gemini.
    *   **Parámetros:** `text` (str), `max_tokens` (int).
    *   **Retorna:** Una lista de cadenas (los fragmentos).
*   **`_has_index_for_book(book_id: str)`**
    *   **Lógica:** Comprueba internamente si ya existen vectores indexados para un `book_id` dado en ChromaDB.
    *   **Parámetros:** `book_id` (str).
    *   **Retorna:** `True` si tiene índice, `False` en caso contrario.
*   **`delete_book_from_rag(book_id: str)`**
    *   **Lógica:** Elimina todos los vectores asociados a un `book_id` de la colección de ChromaDB.
    *   **Parámetros:** `book_id` (str).
    *   **Retorna:** Nada.
*   **`get_index_count(book_id: str)`**
    *   **Lógica:** Devuelve el número de vectores almacenados para un `book_id` específico en ChromaDB.
    *   **Parámetros:** `book_id` (str).
    *   **Retorna:** Un entero (el conteo).
*   **`has_index(book_id: str)`**
    *   **Lógica:** Helper público que indica si un libro tiene índice RAG (basado en `get_index_count > 0`).
    *   **Parámetros:** `book_id` (str).
    *   **Retorna:** `True` si tiene índice, `False` en caso contrario.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**
    *   **Lógica:** Proceso principal de indexación RAG. Extrae el texto completo del libro, lo divide en fragmentos, genera embeddings para cada fragmento y los almacena en ChromaDB. Si `force_reindex` es `True`, elimina cualquier índice existente primero. Si ya está indexado y no se fuerza la reindexación, la operación se omite.
    *   **Parámetros:** `file_path` (str), `book_id` (str), `force_reindex` (bool).
    *   **Retorna:** Nada.
    *   **Lanza:** `ValueError` si el tipo de archivo no es soportado o no se puede extraer/fragmentar el texto.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`**
    *   **Lógica:** Estima la cantidad de tokens y el número de fragmentos para un archivo individual, utilizando la misma lógica de tokenización y tamaño de fragmento que la indexación RAG.
    *   **Parámetros:** `file_path` (str), `max_tokens` (int).
    *   **Retorna:** Un diccionario con `tokens` (int) y `chunks` (int).
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`**
    *   **Lógica:** Estima la cantidad total de tokens, el número total de fragmentos y el número de archivos procesados para una lista de rutas de archivo.
    *   **Parámetros:** `file_paths` (list[str]), `max_tokens` (int).
    *   **Retorna:** Un diccionario con `tokens` (int), `chunks` (int) y `files` (int).
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**
    *   **Lógica:** Procesa una consulta RAG. Genera un embedding de la consulta, recupera los fragmentos de texto más relevantes del libro de ChromaDB. Construye un prompt para el modelo de generación de Gemini (`GENERATION_MODEL`), incluyendo el contexto del libro (fragmentos), metadatos (título, autor, categoría) y (opcionalmente) información contextual de la biblioteca (otras obras del mismo autor). El `mode` de respuesta (`strict`, `balanced`, `open`) ajusta las instrucciones de la IA sobre cómo combinar el contexto del libro con su conocimiento general.
    *   **Parámetros:** `query` (str), `book_id` (str), `mode` (str), `metadata` (dict | None), `library` (dict | None).
    *   **Retorna:** La respuesta generada por la IA (str).

### `backend/main.py`

**Propósito:** Es el punto de entrada de la aplicación FastAPI. Configura la aplicación, monta directorios estáticos para archivos, maneja la configuración de CORS y define todos los endpoints de la API, coordinando la lógica de otros módulos (CRUD, RAG, IA).

**Configuración Inicial:**

*   **Rutas de archivos:** Define rutas absolutas para el almacenamiento de libros (`BOOKS_DIR_FS`), portadas (`STATIC_COVERS_DIR_FS`) y archivos temporales (`TEMP_BOOKS_DIR_FS`).
*   **CORS:** Configura el middleware `CORSMiddleware` para permitir solicitudes desde orígenes específicos (incluyendo localhost y redes privadas), configurables mediante variables de entorno `ALLOW_ORIGINS` y `ALLOW_ORIGIN_REGEX`.
*   **Base de datos:** Inicializa la creación de tablas con `models.Base.metadata.create_all(bind=database.engine)` al inicio de la aplicación.
*   **IA:** Carga la clave API de Gemini desde el entorno (`GOOGLE_API_KEY` o `GEMINI_API_KEY`) y configura el SDK de `genai`. La variable `AI_ENABLED` indica si las funcionalidades de IA están activas.

**Funciones Auxiliares (internas de `main.py`):**

*   **`analyze_with_gemini(text: str) -> dict`**
    *   **Lógica:** Envía un fragmento de texto de un libro (primeras 4000 caracteres) a Google Gemini con un prompt específico para que identifique el título, autor y categoría, esperando una respuesta en formato JSON.
    *   **Retorna:** Un diccionario con `title`, `author`, `category` o valores de error si la IA falla o está deshabilitada.
*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**
    *   **Lógica:** Extrae texto de las primeras 5 páginas de un PDF usando `fitz` (PyMuPDF) y busca una imagen de portada dentro del documento (imágenes con dimensiones mínimas de 300x300). Si encuentra una portada adecuada, la guarda en `covers_dir_fs` y devuelve su URL.
    *   **Retorna:** Un diccionario con el `text` extraído y opcionalmente `cover_image_url`.
*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**
    *   **Lógica:** Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`. Intenta encontrar una imagen de portada siguiendo varias estrategias (metadatos oficiales, búsqueda por nombre "cover"). Si la encuentra, la guarda en `covers_dir_fs` y devuelve su URL.
    *   **Retorna:** Un diccionario con el `text` extraído y opcionalmente `cover_image_url`.
    *   **Lanza:** `HTTPException` (422) si no se puede extraer suficiente texto del EPUB.
*   **`get_db()`**
    *   **Lógica:** Función de inyección de dependencias para FastAPI, que proporciona una sesión de base de datos (`database.SessionLocal`) y asegura su cierre después de que la solicitud haya sido procesada.

**Endpoints de la API:**

*   **`POST /upload-book/`** (`response_model=schemas.Book`)
    *   **Descripción:** Sube un archivo de libro (PDF o EPUB), lo procesa (extracción de texto y portada), lo analiza con IA para obtener metadatos y lo guarda en la base de datos. Si un libro con la misma ruta de archivo ya existe, devuelve un error 409. Si la IA no puede identificar el título/autor, devuelve un error 422 y elimina el archivo subido.
    *   **Parámetros:** `book_file` (UploadFile).
    *   **Lanza:** `HTTPException` (409, 400, 422).
*   **`GET /books/`** (`response_model=List[schemas.Book]`)
    *   **Descripción:** Obtiene una lista de libros. Permite filtrar por `category`, `search` (búsqueda general en título, autor, categoría) y `author`.
    *   **Parámetros de Query (opcionales):** `category` (str), `search` (str), `author` (str).
*   **`GET /books/count`** (`response_model=int`)
    *   **Descripción:** Retorna el número total de libros en la biblioteca.
*   **`GET /books/search/`** (`response_model=List[schemas.Book]`)
    *   **Descripción:** Busca libros por un título parcial (case-insensitive), con opciones de paginación (`skip`, `limit`).
    *   **Parámetros de Query:** `title` (str), `skip` (int), `limit` (int).
*   **`GET /categories/`** (`response_model=List[str]`)
    *   **Descripción:** Retorna una lista de todas las categorías únicas de libros, ordenadas alfabéticamente.
*   **`DELETE /books/{book_id}`**
    *   **Descripción:** Elimina un libro específico por su ID. Esto incluye borrar el registro de la base de datos, eliminar los archivos físicos del libro y su portada, y limpiar cualquier índice RAG asociado al libro.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Lanza:** `HTTPException` (404 si el libro no existe).
*   **`DELETE /categories/{category_name}`**
    *   **Descripción:** Elimina todos los libros de una categoría específica. Esto incluye borrar los registros de la base de datos, eliminar los archivos físicos de los libros y sus portadas, y limpiar sus índices RAG asociados.
    *   **Parámetros de Ruta:** `category_name` (str).
    *   **Lanza:** `HTTPException` (404 si la categoría no se encuentra o ya está vacía).
*   **`GET /books/download/{book_id}`**
    *   **Descripción:** Permite descargar o visualizar un archivo de libro. Configura el `media_type` y `content_disposition_type` apropiadamente (ej. PDF in-line, EPUB attachment).
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Retorna:** `FileResponse` con el contenido del archivo.
    *   **Lanza:** `HTTPException` (404 si el libro o el archivo no existen).
*   **`POST /tools/convert-epub-to-pdf`** (`response_model=schemas.ConversionResponse`)
    *   **Descripción:** Convierte un archivo EPUB subido a PDF. Extrae el contenido del EPUB a un directorio temporal, construye un HTML unificado, y lo renderiza a PDF usando `weasyprint`. El PDF resultante se guarda en la carpeta `backend/temp_books/` y se proporciona una URL de descarga.
    *   **Parámetros:** `file` (UploadFile).
    *   **Lanza:** `HTTPException` (400 si el archivo no es EPUB, 500 si hay un error de conversión).
*   **`POST /rag/upload-book/`** (`response_model=schemas.RagUploadResponse`)
    *   **Descripción:** (Nota: Este endpoint no se utiliza directamente en el frontend actual para la indexación RAG principal, que se enfoca en libros ya existentes). Sube un archivo temporalmente y lo procesa directamente para RAG, asignándole un `book_id` único (UUID).
    *   **Parámetros:** `file` (UploadFile).
    *   **Lanza:** `HTTPException` (500 si hay un error de procesamiento).
*   **`POST /rag/query/`** (`response_model=schemas.RagQueryResponse`)
    *   **Descripción:** Ejecuta una consulta conversacional RAG sobre un libro previamente indexado. Recupera metadatos del libro y, si el modo no es "strict", información de otras obras del mismo autor para enriquecer el contexto del prompt de la IA.
    *   **Parámetros:** `query_data` (schemas.RagQuery, en el cuerpo de la solicitud).
    *   **Lanza:** `HTTPException` (500 si hay un error en la consulta RAG).
*   **`POST /rag/index/{book_id}`**
    *   **Descripción:** Inicia la indexación de un libro existente en la base de datos para el sistema RAG, utilizando su `file_path`.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Parámetros de Query (opcionales):** `force` (bool, si es `True`, se borra cualquier índice existente y se reindexa).
    *   **Lanza:** `HTTPException` (404 si el libro o el archivo no existen, 500 si hay un error de indexación).
*   **`GET /rag/status/{book_id}`**
    *   **Descripción:** Comprueba si un libro específico tiene un índice RAG y, si es así, devuelve el número de vectores almacenados para ese libro.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Lanza:** `HTTPException` (500 si hay un error al obtener el estado).
*   **`POST /rag/reindex/category/{category_name}`**
    *   **Descripción:** (Re)indexa todos los libros que pertenecen a una categoría específica para el sistema RAG.
    *   **Parámetros de Ruta:** `category_name` (str).
    *   **Parámetros de Query (opcionales):** `force` (bool, por defecto `True`).
    *   **Lanza:** `HTTPException` (404 si la categoría no existe o no contiene libros).
*   **`POST /rag/reindex/all`**
    *   **Descripción:** (Re)indexa todos los libros de la biblioteca para el sistema RAG.
    *   **Parámetros de Query (opcionales):** `force` (bool, por defecto `True`).
*   **`GET /rag/estimate/book/{book_id}`**
    *   **Descripción:** Proporciona una estimación de la cantidad de tokens, el número de fragmentos y un coste opcional (si se proporciona `per1k`) para indexar un libro específico en RAG.
    *   **Parámetros de Ruta:** `book_id` (int).
    *   **Parámetros de Query (opcionales):** `per1k` (float), `max_tokens` (int).
    *   **Lanza:** `HTTPException` (404 si el libro no existe, 500 si hay un error en la estimación).
*   **`GET /rag/estimate/category/{category_name}`**
    *   **Descripción:** Estima la cantidad total de tokens, fragmentos y un coste opcional para indexar todos los libros de una categoría.
    *   **Parámetros de Ruta:** `category_name` (str).
    *   **Parámetros de Query (opcionales):** `per1k` (float), `max_tokens` (int).
    *   **Lanza:** `HTTPException` (404 si la categoría no existe o no tiene libros, 500 si hay un error).
*   **`GET /rag/estimate/all`**
    *   **Descripción:** Estima la cantidad total de tokens, fragmentos y un coste opcional para indexar todos los libros de la biblioteca.
    *   **Parámetros de Query (opcionales):** `per1k` (float), `max_tokens` (int).
    *   **Lanza:** `HTTPException` (500 si hay un error).

## 4. Análisis Detallado del Frontend (React)

El frontend proporciona la interfaz de usuario para interactuar con la aplicación, utilizando React y `react-router-dom` para la navegación.

### `frontend/src/App.js`

**Propósito:** Es el componente raíz de la aplicación React. Se encarga de configurar el enrutamiento del lado del cliente y de renderizar los componentes principales de la interfaz.

*   **Estado/Props/Efectos:** No gestiona estado ni props directamente. Su propósito es definir la estructura de enrutamiento y renderizar el `Header` y la `main` content.
*   **Interacciones del Usuario:** Controla la navegación entre las diferentes vistas de la aplicación (`/`, `/upload`, `/etiquetas`, etc.) a través de los enlaces definidos en el `Header`.
*   **Comunicación con el Backend:** No se comunica directamente. Las vistas hijas son las encargadas de ello.

### `frontend/src/Header.js`

**Propósito:** Muestra el encabezado de la aplicación, incluyendo el título, un contador dinámico de libros en la biblioteca y los enlaces de navegación principales. Es sensible a pantallas móviles para la visualización del menú.

*   **Estado:**
    *   `menuOpen` (boolean): Controla la visibilidad del menú de navegación en dispositivos móviles.
    *   `bookCount` (number): Muestra el número total de libros obtenido del backend.
    *   `errorMessage` (string | null): Mensaje de error si falla la obtención del contador de libros.
*   **Efectos:**
    *   `useEffect` (al montar y cada 10 minutos): Realiza una petición `GET` a `/books/count` para obtener el número total de libros y actualizar `bookCount`. Incluye manejo de errores y reintento periódico.
*   **Interacciones del Usuario:**
    *   Clic en el botón de "hamburguesa": Abre/cierra el menú de navegación en móvil.
    *   Clic en los `NavLink`: Navega a la ruta correspondiente y cierra el menú móvil si está abierto (`handleLinkClick`).
*   **Comunicación con el Backend:**
    *   `GET /books/count`: Para obtener el número total de libros.

### `frontend/src/ToolsView.js`

**Propósito:** Proporciona un espacio para herramientas útiles de la biblioteca. Actualmente, incluye un convertidor de EPUB a PDF.

#### `EpubToPdfConverter` (componente anidado)

*   **Estado:**
    *   `selectedFile` (File | null): El archivo EPUB seleccionado por el usuario para la conversión.
    *   `message` (string): Mensaje de estado o error para el usuario (ej. "Convirtiendo...", "Error...").
    *   `isLoading` (boolean): Indica si el proceso de conversión está en curso, deshabilitando el botón.
*   **Efectos:** Ninguno específico.
*   **Interacciones del Usuario:**
    *   `handleFileChange`: Se activa cuando el usuario selecciona un archivo a través del input `type="file"`.
    *   `handleDrop`, `handleDragOver`: Implementa la funcionalidad de arrastrar y soltar archivos en la zona designada.
    *   `handleConvert`: Inicia la conversión del archivo EPUB seleccionado a PDF. Realiza una petición `POST` al backend.
*   **Comunicación con el Backend:**
    *   `POST /tools/convert-epub-to-pdf`: Sube el archivo EPUB al backend como `FormData`. Si la conversión es exitosa, el backend devuelve un JSON con la `download_url` que el frontend utiliza para crear un enlace temporal y simular un clic, iniciando la descarga del PDF resultante.

### `frontend/src/UploadView.js`

**Propósito:** Permite a los usuarios subir uno o varios archivos de libros (PDF o EPUB) a la biblioteca. El componente gestiona el estado individual de cada archivo durante la subida y el procesamiento por parte de la IA del backend.

*   **Estado:**
    *   `filesToUpload` (array de objetos): Cada objeto representa un archivo con `file` (el objeto File), `status` ('pending', 'uploading', 'success', 'error') y `message` (el estado actual o mensaje de error).
    *   `isUploading` (boolean): Indica si alguna operación de subida y procesamiento está activa, deshabilitando el botón de subida.
*   **Efectos:** Ninguno.
*   **Interacciones del Usuario:**
    *   `handleFileChange`: Añade los archivos seleccionados por el usuario a `filesToUpload`, estableciendo su estado inicial a 'pending'.
    *   `handleDrop`, `handleDragOver`: Permite arrastrar y soltar archivos en la zona de subida.
    *   `handleUpload`: Inicia el proceso de subida de cada archivo con estado `pending` de forma secuencial. Actualiza el `status` y `message` de cada archivo a medida que avanza el procesamiento.
    *   Botón "Ir a la Biblioteca": Disponible cuando todas las subidas han terminado, redirige al usuario a la vista principal (`/`).
*   **Comunicación con el Backend:**
    *   `POST /upload-book/`: Envía cada archivo al backend en un objeto `FormData`. Recibe información sobre el libro procesado (ej. su `title`) o detalles del error (`detail`).

### `frontend/src/ReaderView.js`

**Propósito:** Proporciona una interfaz para leer libros en formato EPUB directamente en el navegador, utilizando el componente de terceros `react-reader`.

*   **Props:** Ninguna explícita, obtiene `bookId` de los parámetros de la URL (`useParams`).
*   **Estado:**
    *   `location` (string | null): Representa la ubicación actual del lector dentro del EPUB (CFI string).
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB, que el componente `react-reader` necesita.
    *   `isLoading` (boolean): Indica si el archivo del libro se está cargando.
    *   `error` (string): Mensaje de error si la carga del libro falla.
*   **Efectos:**
    *   `useEffect` (cuando `bookId` cambia): Realiza una petición `GET` a `/books/download/{bookId}` para obtener los datos binarios del EPUB como un `ArrayBuffer`. Actualiza `isLoading` y `error` durante este proceso.
*   **Interacciones del Usuario:**
    *   El componente `ReactReader` gestiona la navegación y la interacción con el libro (paso de página, etc.). El callback `locationChanged` se utiliza para actualizar el estado `location` con el CFI actual del lector.
*   **Comunicación con el Backend:**
    *   `GET /books/download/{bookId}`: Para obtener el contenido del archivo EPUB como `ArrayBuffer`.

### `frontend/src/ErrorBoundary.js`

**Propósito:** Un componente estándar de React (Error Boundary) que captura errores de JavaScript en sus componentes hijos y muestra una interfaz de usuario de fallback en lugar de dejar que la aplicación falle por completo debido a errores inesperados en la UI.

*   **Estado:**
    *   `hasError` (boolean): `true` si se ha capturado un error en los componentes hijos.
    *   `error` (Error | null): El objeto de error que fue capturado.
*   **Métodos del Ciclo de Vida:**
    *   `static getDerivedStateFromError(error)`: Un método estático que actualiza el estado para indicar que ha ocurrido un error.
    *   `componentDidCatch(error, info)`: Se usa para registrar el error y la información del componente en la consola, lo que es útil para la depuración.
*   **Renderizado:** Si `hasError` es `true`, renderiza un mensaje de error con los detalles del mismo. De lo contrario, renderiza los `props.children` normalmente.

### `frontend/src/RagView.js`

**Propósito:** Proporciona la interfaz para el sistema RAG, permitiendo al usuario buscar y seleccionar un libro de su biblioteca, gestionar su indexación para RAG y luego conversar con él mediante un modelo de lenguaje (IA).

*   **Estado:**
    *   `message` (string): Mensajes de estado o instrucción para el usuario (ej. "Indexando...", "Listo para chatear").
    *   `isLoading` (boolean): Indica si una consulta a la IA está en curso, deshabilitando el input del chat.
    *   `bookId` (string | null): El ID del libro que actualmente está activo para el chat RAG. Se establece cuando el libro está indexado y listo.
    *   `chatHistory` (array de `{ sender: 'user' | 'gemini', text: string }`): Historial de la conversación, con mensajes del usuario y de la IA.
    *   `currentQuery` (string): La entrada de texto actual del usuario para la consulta.
    *   `libraryBooks` (array de objetos Book): Lista de todos los libros disponibles en la biblioteca, cargados al inicio.
    *   `selectedLibraryId` (string): El ID del libro seleccionado en el buscador para su gestión RAG.
    *   `libStatus` (objeto): `{ loading (boolean), indexed (boolean), vector_count (number), error (string | null) }` - estado del índice RAG para el libro seleccionado.
    *   `actionsBusy` (boolean): Bloquea las acciones de indexación/reindexación para evitar concurrencia.
    *   `refreshing` (boolean): Indica que se está refrescando el estado RAG (no bloquea otras acciones como chatear).
    *   `searchTerm` (string): Texto de búsqueda introducido por el usuario para filtrar `libraryBooks`.
    *   `searching` (boolean): Indica si se está realizando una búsqueda de libros.
    *   `searchResults` (array de objetos Book): Libros encontrados por el `searchTerm`.
    *   `resultsOpen` (boolean): Controla la visibilidad del dropdown de resultados de búsqueda.
    *   `mode` (string): Modo de respuesta de la IA seleccionada ('strict', 'balanced', 'open').
    *   `selectedBook` (objeto Book | null): El objeto completo del libro seleccionado de los resultados de búsqueda.
*   **Refs:**
    *   `inputRef`: Referencia al `textarea` del chat para poder enfocarlo programáticamente.
    *   `chatHistoryRef`: Referencia al contenedor del historial del chat para permitir el auto-scrolling al final.
*   **Efectos:**
    *   `useEffect` (al montar): Carga todos los libros de la biblioteca (`GET /books/`) para poblar la lista de selección.
    *   `useEffect` (cuando `searchTerm` cambia, con un debounce de 250ms): Realiza una búsqueda de libros (`GET /books/?search=...`) y actualiza `searchResults`.
    *   `useEffect` (cuando `selectedLibraryId` cambia): Si hay un ID seleccionado, llama a `checkLibraryStatus` para obtener y mostrar el estado del índice RAG del libro.
    *   `useEffect` (cuando `chatHistory` o `isLoading` cambian): Realiza auto-scrolling del historial de chat para mostrar los mensajes más recientes.
*   **Interacciones del Usuario:**
    *   Input de texto para `searchTerm`: Permite buscar libros en la biblioteca por título, autor o categoría.
    *   Clic en un libro de los `searchResults`: Establece `selectedLibraryId` y `selectedBook` y activa la comprobación de estado RAG.
    *   Botones "Comprobar RAG", "Indexar antes de charlar", "Reindexar": Llaman a `checkLibraryStatus` o `indexLibraryBook`, gestionando `actionsBusy`.
    *   Botón "Chatear": Si el libro está indexado, establece `bookId` para activar la interfaz de chat y resetea el historial.
    *   Radio buttons para `mode`: Permiten al usuario seleccionar la preferencia de respuesta de la IA (estricta, equilibrada, abierta).
    *   `textarea` para `currentQuery`: Permite al usuario introducir preguntas sobre el libro. El `textarea` se auto-redimensiona.
    *   Botón "Enviar": `handleQuerySubmit` envía la pregunta a la API RAG.
*   **Comunicación con el Backend:**
    *   `GET /books/` (y `/books/?search=...`): Para cargar y buscar libros en la biblioteca.
    *   `GET /rag/status/{book_id}`: Para obtener el estado de indexación RAG (si el libro está indexado y cuántos vectores tiene).
    *   `POST /rag/index/{book_id}`: Para indexar (o reindexar) un libro en el sistema RAG.
    *   `POST /rag/query/`: Para enviar la pregunta del usuario (`query`), el `book_id` y el `mode` al sistema RAG y obtener una respuesta de la IA.

### `frontend/src/LibraryView.js`

**Propósito:** La vista principal de la aplicación donde se muestran todos los libros de la biblioteca en una cuadrícula. Permite a los usuarios buscar, filtrar por autor o categoría, y realizar acciones como leer, descargar o eliminar libros.

*   **Estado:**
    *   `books` (array de objetos Book): La lista de libros que se muestran en la cuadrícula.
    *   `searchParams` (URLSearchParams): Objeto de `react-router-dom` para gestionar los parámetros de búsqueda en la URL (utilizado para filtrar por categoría y autor).
    *   `searchTerm` (string): El término de búsqueda introducido por el usuario en la barra de búsqueda general.
    *   `debouncedSearchTerm` (string): Una versión de `searchTerm` con un retraso aplicado por el `useDebounce` hook para optimizar las llamadas a la API y evitar peticiones excesivas.
    *   `error` (string): Mensaje de error si falla la carga de libros.
    *   `loading` (boolean): Indica si los libros se están cargando desde el backend.
    *   `isMobile` (boolean): Indica si la aplicación se está ejecutando en un dispositivo móvil (ancho de pantalla <= 768px), usado para adaptar la UI (ej. mostrar botón de descarga).
*   **Hooks Personalizados:**
    *   `useDebounce`: Un hook personalizado para aplicar un retraso (debounce) a la entrada de búsqueda, asegurando que la API no se llame hasta que el usuario haya dejado de escribir por un corto periodo.
*   **Componentes Anidados:**
    *   `BookCover`: Un componente para mostrar la portada de un libro. Incluye un mecanismo de fallback para mostrar una portada genérica si la imagen original no está disponible o falla al cargar.
*   **Efectos:**
    *   `useEffect` (al montar y en cada evento `resize`): Detecta si la pantalla es móvil (`window.innerWidth <= 768`).
    *   `useEffect` (cuando `debouncedSearchTerm` o `searchParams` cambian): Llama a la función `fetchBooks` para recargar la lista de libros desde el backend con los filtros y la búsqueda actuales.
*   **Interacciones del Usuario:**
    *   Input de `searchTerm`: Permite buscar libros por título, autor o categoría. La búsqueda se aplica después del debounce.
    *   Clic en el nombre del autor (`handleAuthorClick`): Limpia la búsqueda general y establece un filtro por autor en los `searchParams` de la URL.
    *   Clic en la categoría (`handleCategoryClick`): Establece un filtro por categoría en los `searchParams` de la URL.
    *   Botón "×" (`handleDeleteBook`): Muestra una confirmación y, si se acepta, elimina un libro específico de la biblioteca.
    *   Botones "Abrir PDF" / "Leer EPUB": Navegan a la `ReaderView` para EPUBs o abren PDFs en una nueva pestaña.
    *   Botón "Descargar PDF/EPUB" (condicionalmente en móvil): Permite la descarga directa del archivo del libro.
*   **Comunicación con el Backend:**
    *   `GET /books/?category=...&search=...&author=...`: Para obtener la lista de libros filtrados/buscados.
    *   `DELETE /books/{bookId}`: Para eliminar un libro de la base de datos y sus archivos asociados.
    *   `GET /books/download/{bookId}`: Para descargar o acceder al archivo binario del libro (usado tanto para la lectura de EPUBs como para la apertura/descarga de PDFs).

### `frontend/src/config.js`

**Propósito:** Centraliza la definición de la URL base del API del backend. Esto permite una configuración sencilla para diferentes entornos (desarrollo, producción) mediante variables de entorno.

*   **Variables:**
    *   `API_URL`: Obtiene su valor de `process.env.REACT_APP_API_URL`. Si esta variable de entorno no está definida, por defecto se usa `http://localhost:8001`.

### `frontend/src/CategoriesView.js`

**Propósito:** Muestra una lista de todas las categorías únicas de libros disponibles en la biblioteca, presentadas como tarjetas clicables que permiten al usuario navegar y filtrar la vista principal de la biblioteca.

*   **Estado:**
    *   `categories` (array de strings): Lista de nombres de categorías únicas obtenidas del backend.
    *   `error` (string): Mensaje de error si falla la carga de categorías.
    *   `loading` (boolean): Indica si las categorías se están cargando.
*   **Efectos:**
    *   `useEffect` (al montar): Realiza una petición `GET` a `/categories/` para obtener la lista de categorías únicas del backend.
*   **Interacciones del Usuario:**
    *   Clic en una tarjeta de categoría: Navega a la `LibraryView` con el parámetro de URL `?category=nombre_categoria`, lo que filtra los libros mostrados en esa vista por la categoría seleccionada.
*   **Comunicación con el Backend:**
    *   `GET /categories/`: Para obtener la lista de todas las categorías únicas.

### `frontend/src/index.js`

**Propósito:** Es el punto de entrada principal de la aplicación React. Se encarga de renderizar el componente raíz `App` dentro del elemento DOM con el ID 'root' en el archivo `public/index.html`.

*   No contiene lógica de aplicación ni estado propio, solo la inicialización de la aplicación React en modo estricto (`React.StrictMode`) para resaltar posibles problemas en el desarrollo.

## 5. Flujo de Datos y API

### Flujo de Datos para la Carga y Procesamiento de un Libro

1.  **Inicio en Frontend (`UploadView.js`):**
    *   El usuario selecciona uno o varios archivos (PDF o EPUB) desde su sistema local o los arrastra y suelta en la interfaz de subida.
    *   `UploadView.js` crea un objeto `FormData` para cada archivo, adjuntando el archivo como `book_file`.
    *   Por cada archivo, `UploadView.js` envía una petición **`POST` a `/upload-book/`** al backend.
2.  **Procesamiento en Backend (`main.py` - `upload_book` endpoint):**
    *   **Almacenamiento del Archivo:** FastAPI recibe el archivo subido y lo guarda en el directorio `backend/books/`.
    *   **Extracción de Contenido y Portada:**
        *   FastAPI determina el tipo de archivo (`.pdf` o `.epub`) basándose en la extensión.
        *   Llama a la función correspondiente (`process_pdf` o `process_epub`) para:
            *   Extraer el texto de las primeras páginas del libro.
            *   Intentar identificar y extraer una imagen de portada. Si se encuentra, la portada se guarda en `backend/static/covers/` y se genera una URL accesible públicamente.
    *   **Análisis con IA:**
        *   El texto extraído (hasta 4000 caracteres) se envía a `analyze_with_gemini`, que utiliza Google Gemini para identificar el `title`, `author` y `category` del libro.
        *   **Control de Calidad:** Si la IA no logra identificar el título y el autor (ambos son "Desconocido"), se lanza un `HTTPException` (422), el archivo subido se elimina del sistema de archivos, y se devuelve un error al frontend.
    *   **Almacenamiento en Base de Datos:**
        *   Si el análisis con IA es exitoso (o al menos un metadato principal se identificó), la información del libro se pasa a `crud.create_book`.
        *   `crud.create_book` guarda los metadatos del nuevo libro (título, autor, categoría, URL de portada, ruta del archivo) en la tabla `books` de la base de datos SQLite.
    *   **Respuesta al Frontend:** Se devuelve un objeto `schemas.Book` (incluyendo el ID generado) en caso de éxito, o un `HTTPException` con detalles del error.
3.  **Finalización en Frontend (`UploadView.js`):**
    *   `UploadView.js` recibe la respuesta y actualiza el estado de la carga de cada archivo, mostrando si el libro se añadió correctamente (con su título) o si hubo un error.
    *   Una vez que todos los archivos han sido procesados, se muestra un botón para que el usuario navegue a la vista de la biblioteca.

### Flujo de Datos para la Conversación RAG con un Libro

1.  **Selección del Libro en Frontend (`RagView.js`):**
    *   El usuario busca y selecciona un libro existente de su biblioteca utilizando la barra de búsqueda y los resultados que provienen de **`GET /books/?search=...`**.
    *   `RagView.js` comprueba el estado de indexación RAG del libro seleccionado mediante una petición **`GET` a `/rag/status/{book_id}`**.
2.  **Indexación del Libro (si es necesario):**
    *   Si el libro no está indexado para RAG, el usuario hace clic en "Indexar antes de charlar".
    *   `RagView.js` envía una petición **`POST` a `/rag/index/{book_id}`** (con `force=false` por defecto).
    *   **Procesamiento de Indexación en Backend (`main.py` - `index_existing_book_for_rag` endpoint):**
        *   FastAPI recupera el `file_path` del libro de la base de datos (`crud`).
        *   Llama a `rag.process_book_for_rag`:
            *   `rag.extract_text` lee el contenido completo del libro (PDF/EPUB).
            *   `rag.chunk_text` divide el texto en fragmentos más pequeños.
            *   `rag.get_embedding` genera un embedding vectorial para cada fragmento utilizando Google Gemini.
            *   ChromaDB almacena estos fragmentos y sus embeddings, asociados al `book_id`.
    *   `RagView.js` recibe la confirmación de indexación y actualiza el estado (`indexed`, `vector_count`).
3.  **Consulta Conversacional:**
    *   Una vez que el libro está indexado y el chat está "listo", el usuario escribe una pregunta en el `textarea` y la envía.
    *   `RagView.js` envía una petición **`POST` a `/rag/query/`** con un objeto `schemas.RagQuery` (que contiene la `query`, el `book_id` y el `mode` de respuesta seleccionado).
4.  **Procesamiento de Consulta en Backend (`main.py` - `query_rag_endpoint`):**
    *   FastAPI recupera los metadatos del libro (título, autor, categoría) de la base de datos para proporcionar contexto adicional a la IA.
    *   También consulta otras obras del mismo autor para el contexto de la biblioteca, si el `mode` no es "strict".
    *   Llama a `rag.query_rag`:
        *   `rag.get_embedding` genera un embedding de la pregunta del usuario.
        *   ChromaDB realiza una búsqueda de similitud vectorial para encontrar los fragmentos de texto del libro más relevantes para la pregunta.
        *   Se construye un prompt detallado para Google Gemini, que incluye la pregunta del usuario, los fragmentos relevantes del libro, los metadatos del libro, información contextual de la biblioteca y las instrucciones de `mode` (strict, balanced, open).
        *   Google Gemini procesa el prompt y genera una respuesta coherente.
    *   Se devuelve la respuesta de la IA como un objeto `schemas.RagQueryResponse`.
5.  **Visualización en Frontend (`RagView.js`):**
    *   `RagView.js` recibe la respuesta de Gemini y la añade al `chatHistory`, mostrándola al usuario en la interfaz del chat.

### Principales Endpoints de la API (Backend FastAPI)

La API RESTful del backend expone los siguientes endpoints principales:

*   **Libros (`/books/`)**
    *   `POST /upload-book/`: Sube un libro (PDF/EPUB) para procesamiento y adición a la biblioteca.
    *   `GET /books/`: Obtiene una lista de libros, con filtros opcionales (`category`, `search`, `author`).
    *   `GET /books/count`: Retorna el número total de libros.
    *   `GET /books/search/`: Busca libros por título parcial, con paginación.
    *   `DELETE /books/{book_id}`: Elimina un libro específico por ID (junto con sus archivos y datos RAG).
    *   `GET /books/download/{book_id}`: Descarga o abre el archivo de un libro.

*   **Categorías (`/categories/`)**
    *   `GET /categories/`: Obtiene una lista de todas las categorías únicas.
    *   `DELETE /categories/{category_name}`: Elimina una categoría y todos sus libros asociados (junto con sus archivos y datos RAG).

*   **Herramientas (`/tools/`)**
    *   `POST /tools/convert-epub-to-pdf`: Convierte un archivo EPUB subido a PDF y proporciona una URL de descarga.

*   **RAG (Retrieval-Augmented Generation) (`/rag/`)**
    *   `POST /rag/query/`: Envía una pregunta a la IA para un libro específico ya indexado, con control sobre el modo de respuesta.
    *   `POST /rag/index/{book_id}`: Inicia o fuerza la indexación RAG de un libro existente en la base de datos.
    *   `GET /rag/status/{book_id}`: Comprueba el estado de indexación RAG de un libro (si está indexado, cuántos vectores tiene).
    *   `POST /rag/reindex/category/{category_name}`: (Re)indexa todos los libros de una categoría específica para RAG.
    *   `POST /rag/reindex/all`: (Re)indexa todos los libros de la biblioteca para RAG.
    *   `GET /rag/estimate/book/{book_id}`: Estima la cantidad de tokens, fragmentos y un coste opcional para indexar un libro.
    *   `GET /rag/estimate/category/{category_name}`: Estima la cantidad de tokens, fragmentos y un coste opcional para indexar una categoría completa.
    *   `GET /rag/estimate/all`: Estima la cantidad de tokens, fragmentos y un coste opcional para indexar toda la biblioteca.
```
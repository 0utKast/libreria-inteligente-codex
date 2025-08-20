# Documentación del Proyecto: Mi Librería Inteligente

Este documento proporciona una visión técnica detallada del proyecto "Mi Librería Inteligente", abarcando su arquitectura, estructura de código y funcionalidades clave tanto del frontend como del backend.

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web diseñada para la gestión personal de una colección de libros digitales. Ofrece a los usuarios la capacidad de subir y organizar libros en formatos PDF y EPUB, explorar su biblioteca por diversos criterios y, de manera innovadora, interactuar con el contenido de sus libros mediante inteligencia artificial.

**Características Principales:**
*   **Gestión de Libros:** Subida de archivos PDF y EPUB.
*   **Organización Automática:** Extracción de metadatos (título, autor, categoría) asistida por IA al subir un libro.
*   **Exploración y Búsqueda:** Navegación por categorías, autores y búsqueda general de libros.
*   **Lectura en Navegador:** Capacidad de leer archivos EPUB directamente en la aplicación.
*   **Conversión de Archivos:** Herramienta para convertir libros de EPUB a PDF.
*   **Conversación Inteligente (RAG):** Permite a los usuarios hacer preguntas sobre el contenido de un libro específico y recibir respuestas contextualizadas generadas por IA.

**Arquitectura General:**

La aplicación sigue una arquitectura cliente-servidor con una clara separación de responsabilidades:

*   **Frontend (Cliente):** Desarrollado con **React**, proporciona la interfaz de usuario interactiva. Se encarga de la visualización de datos, la interacción del usuario y la comunicación con el backend a través de solicitudes HTTP.
*   **Backend (Servidor):** Construido con **FastAPI** (Python), actúa como el cerebro de la aplicación. Expone una API RESTful que maneja la lógica de negocio, la interacción con la base de datos, el procesamiento de archivos, la integración con servicios de IA y la funcionalidad RAG.
*   **Base de Datos Relacional:** **SQLite** se utiliza para almacenar los metadatos de los libros (título, autor, categoría, rutas de archivo, etc.). La gestión de la base de datos se realiza con **SQLAlchemy** como ORM y **Alembic** para las migraciones.
*   **Almacenamiento de Archivos:** Los archivos de libros originales (PDF/EPUB) y sus portadas extraídas se almacenan localmente en el sistema de archivos del servidor.
*   **Integración de Inteligencia Artificial:** La aplicación se conecta con la API de **Google Gemini** para dos propósitos principales:
    *   **Análisis de Metadatos:** Al subir un libro, Gemini analiza el texto inicial para inferir su título, autor y categoría.
    *   **Generación de Respuestas (RAG):** En la funcionalidad de conversación, Gemini genera respuestas a las preguntas del usuario basándose en el contexto relevante extraído del libro.
*   **Base de Datos Vectorial (RAG):** **ChromaDB** se emplea como una base de datos vectorial persistente. Al "indexar" un libro para RAG, su contenido se divide en fragmentos, se generan embeddings (representaciones numéricas) de estos fragmentos y se almacenan en ChromaDB. Esto permite una búsqueda eficiente de similitud semántica para recuperar los pasajes más relevantes del libro ante una consulta del usuario.
*   **Conversión de Documentos:** Para la funcionalidad de conversión de EPUB a PDF, el backend utiliza librerías como `PyPDF2`, `ebooklib`, `BeautifulSoup` y `weasyprint` para procesar y transformar los archivos.

## 2. Estructura del Proyecto

La estructura del proyecto está organizada en dos directorios principales, `backend/` y `frontend/`, reflejando la separación de la arquitectura.

```
.
├── backend/
│   ├── alembic/                    # Gestión de migraciones de base de datos con Alembic
│   │   ├── versions/
│   │   └── env.py
│   ├── books/                      # Directorio de almacenamiento para los archivos de libros subidos (PDF/EPUB)
│   ├── static/
│   │   └── covers/                 # Directorio de almacenamiento para las imágenes de portada de los libros
│   ├── temp_books/                 # Directorio temporal para archivos generados (ej. PDFs convertidos de EPUB)
│   ├── tests/                      # Pruebas unitarias y de integración para el backend
│   ├── tests_curated/              # Pruebas adicionales/curadas para el backend
│   ├── __init__.py                 # Archivo de inicialización del paquete Python (vacío)
│   ├── crud.py                     # Operaciones CRUD para la base de datos
│   ├── database.py                 # Configuración de la conexión a la base de datos SQLAlchemy
│   ├── main.py                     # Aplicación FastAPI, endpoints de la API y lógica principal
│   ├── models.py                   # Modelos ORM de SQLAlchemy para la base de datos
│   ├── rag.py                      # Lógica de Recuperación Aumentada por Generación (RAG)
│   └── schemas.py                  # Modelos Pydantic para validación de datos de la API
│   └── utils.py                    # Funciones de utilidad (ej. configuración de la IA)
├── frontend/
│   ├── public/                     # Archivos estáticos para la aplicación React
│   ├── src/                        # Código fuente de la aplicación React
│   │   ├── App.js                  # Componente principal que define las rutas
│   │   ├── CategoriesView.js       # Vista para explorar categorías de libros
│   │   ├── config.js               # Configuración de la URL de la API del backend
│   │   ├── ErrorBoundary.js        # Componente para manejar errores en la UI
│   │   ├── Header.js               # Componente de la cabecera y navegación
│   │   ├── LibraryView.js          # Vista principal de la biblioteca (listado, búsqueda, filtros)
│   │   ├── RagView.js              # Vista para la interacción de chat con IA (RAG)
│   │   ├── ReaderView.js           # Vista para la lectura de libros EPUB en el navegador
│   │   ├── ToolsView.js            # Vista para herramientas adicionales (ej. conversor EPUB a PDF)
│   │   ├── UploadView.js           # Vista para subir nuevos libros
│   │   ├── *.css                   # Archivos CSS para estilos de los componentes
│   │   └── index.js                # Punto de entrada de la aplicación React
│   └── package.json                # Dependencias y scripts de frontend
│   └── yarn.lock
├── .env                            # Archivo de configuración para variables de entorno (API Keys, etc.)
├── library.db                      # Archivo de la base de datos SQLite
└── rag_index/                      # Directorio de almacenamiento del índice vectorial de ChromaDB
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend es el corazón de la aplicación, manejando toda la lógica de negocio, la persistencia de datos y las integraciones con IA.

### `backend/schemas.py`

**Propósito:** Define los esquemas de datos utilizando la librería Pydantic. Estos esquemas son fundamentales para la validación de la entrada (peticiones) y la serialización de la salida (respuestas) de la API, asegurando que los datos se ajusten a una estructura predefinida.

**Clases Principales:**

*   `class BookBase(BaseModel)`:
    *   **Descripción:** Esquema base para la información de un libro.
    *   **Campos:**
        *   `title (str)`: Título del libro.
        *   `author (str)`: Autor del libro.
        *   `category (str)`: Categoría a la que pertenece el libro.
        *   `cover_image_url (str | None)`: URL de la imagen de portada (opcional).
        *   `file_path (str)`: Ruta absoluta o relativa al archivo del libro en el sistema de archivos del servidor.

*   `class Book(BookBase)`:
    *   **Descripción:** Extiende `BookBase` añadiendo el identificador único del libro. Se usa para las respuestas de la API que incluyen un libro completo de la base de datos.
    *   **Campos:**
        *   `id (int)`: Identificador único del libro en la base de datos.
    *   **Configuración:**
        *   `class Config: from_attributes = True`: Indica a Pydantic que puede crear instancias de este modelo a partir de atributos de objetos ORM (ej. de SQLAlchemy).

*   `class ConversionResponse(BaseModel)`:
    *   **Descripción:** Esquema para la respuesta del endpoint de conversión de EPUB a PDF.
    *   **Campos:**
        *   `download_url (str)`: URL donde el PDF convertido puede ser descargado o visualizado.

*   `class RagUploadResponse(BaseModel)`:
    *   **Descripción:** Esquema para la respuesta de la subida y procesamiento de un libro para el sistema RAG.
    *   **Campos:**
        *   `book_id (str)`: El identificador del libro que ha sido procesado para RAG.
        *   `message (str)`: Un mensaje informativo sobre el resultado de la operación.

*   `class RagQuery(BaseModel)`:
    *   **Descripción:** Esquema para la consulta que un usuario envía al sistema RAG.
    *   **Campos:**
        *   `query (str)`: La pregunta que el usuario desea hacer sobre el libro.
        *   `book_id (str)`: El identificador del libro al que se refiere la consulta.
        *   `mode (str | None)`: Modo opcional para controlar cómo la IA debe generar la respuesta ('strict', 'balanced', 'open').

*   `class RagQueryResponse(BaseModel)`:
    *   **Descripción:** Esquema para la respuesta generada por el sistema RAG.
    *   **Campos:**
        *   `response (str)`: La respuesta textual generada por el modelo de IA.

### `backend/crud.py`

**Propósito:** Contiene las funciones de lógica de negocio para interactuar directamente con la base de datos. Estas funciones son abstracciones para las operaciones CRUD (Create, Read, Update, Delete) sobre el modelo `Book`, desacoplando la lógica de la base de datos de los endpoints de la API.

**Funciones Principales:**

*   `get_book_by_path(db: Session, file_path: str)`:
    *   **Lógica:** Busca un libro en la base de datos por su ruta de archivo única.
    *   **Parámetros:** `db` (sesión de SQLAlchemy), `file_path` (la ruta del archivo).
    *   **Retorno:** Un objeto `models.Book` si se encuentra, de lo contrario `None`.

*   `get_book_by_title(db: Session, title: str)`:
    *   **Lógica:** Recupera un libro por su título exacto.
    *   **Parámetros:** `db`, `title`.
    *   **Retorno:** Un objeto `models.Book` si se encuentra, de lo contrario `None`.

*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`:
    *   **Lógica:** Realiza una búsqueda de libros donde el título coincida parcialmente (insensible a mayúsculas/minúsculas) con el término dado. Incluye paginación.
    *   **Parámetros:** `db`, `title` (el término de búsqueda), `skip` (número de resultados a saltar), `limit` (número máximo de resultados a devolver).
    *   **Retorno:** Una lista de objetos `models.Book`.

*   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`:
    *   **Lógica:** Obtiene una lista de libros. Permite filtrar por `category` o `author` exactos, y una búsqueda `search` general que aplica al título, autor o categoría. Los resultados se ordenan por ID de forma descendente.
    *   **Parámetros:** `db`, `category` (categoría exacta), `search` (término de búsqueda general), `author` (autor parcial, insensible a mayúsculas/minúsculas).
    *   **Retorno:** Una lista de objetos `models.Book`.

*   `get_categories(db: Session) -> list[str]`:
    *   **Lógica:** Recupera una lista de todas las categorías únicas presentes en la base de datos, ordenadas alfabéticamente.
    *   **Parámetros:** `db`.
    *   **Retorno:** Una lista de cadenas de texto (nombres de categorías).

*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`:
    *   **Lógica:** Crea una nueva entrada de libro en la base de datos con los datos proporcionados. Persiste los cambios y refresca el objeto para obtener su ID.
    *   **Parámetros:** `db`, `title`, `author`, `category`, `cover_image_url`, `file_path`.
    *   **Retorno:** El objeto `models.Book` recién creado y persistido.

*   `delete_book(db: Session, book_id: int)`:
    *   **Lógica:** Elimina un libro de la base de datos por su ID. Además, elimina el archivo del libro y su imagen de portada asociada del sistema de archivos, si existen.
    *   **Parámetros:** `db`, `book_id` (el ID del libro a eliminar).
    *   **Retorno:** El objeto `models.Book` que fue eliminado, o `None` si el libro no se encontró.

*   `delete_books_by_category(db: Session, category: str)`:
    *   **Lógica:** Elimina todos los libros que pertenecen a una categoría específica. También borra los archivos de libro y las portadas asociadas del sistema de archivos.
    *   **Parámetros:** `db`, `category` (el nombre de la categoría).
    *   **Retorno:** El número de libros eliminados (`int`).

*   `get_books_count(db: Session) -> int`:
    *   **Lógica:** Cuenta el número total de libros almacenados en la base de datos.
    *   **Parámetros:** `db`.
    *   **Retorno:** El número total de libros (`int`).

### `backend/database.py`

**Propósito:** Este módulo se encarga de configurar la conexión a la base de datos de la aplicación, utilizando SQLite y SQLAlchemy. Proporciona los objetos necesarios para interactuar con la base de datos: el motor de conexión (`engine`), el constructor de sesiones (`SessionLocal`) y la base declarativa para los modelos ORM (`Base`).

**Elementos Principales:**

*   `_base_dir`, `_db_path`: Variables internas que construyen la ruta absoluta al archivo de base de datos `library.db`, ubicado en la raíz del proyecto.
*   `SQLALCHEMY_DATABASE_URL`: Una cadena que define la URL de conexión a la base de datos SQLite.
*   `engine`: Instancia de `sqlalchemy.create_engine`. Es el punto de entrada para su base de datos, encargado de manejar la conexión y la interacción con SQLite. `check_same_thread=False` es crucial para SQLite en entornos multihilo como FastAPI.
*   `SessionLocal`: Una clase `sessionmaker` de SQLAlchemy. Las instancias de esta clase (`db` en los endpoints de FastAPI) serán las sesiones de base de datos que se usarán para realizar operaciones. Está configurada para no autocommitir ni autoflushar, dando control explícito al programador.
*   `Base`: Una instancia de `declarative_base()`. Esta es la clase base de la cual deben heredar todos los modelos ORM de SQLAlchemy. Proporciona las funcionalidades para mapear clases Python a tablas de base de datos.

### `backend/utils.py`

**Propósito:** Contiene funciones de utilidad diversas que pueden ser reutilizadas a lo largo del backend. Actualmente, su función principal es la configuración de la API de Google Generative AI (Gemini) utilizando claves de API almacenadas en variables de entorno.

**Funciones Principales:**

*   `configure_genai()`:
    *   **Lógica:** Carga las variables de entorno desde un archivo `.env` (utilizando `python-dotenv`). Intenta obtener la clave de API de Gemini de las variables `GOOGLE_API_KEY` o `GEMINI_API_KEY` (priorizando la primera si ambas están presentes). Si no se encuentra ninguna clave válida, lanza un `ValueError`. Una vez obtenida, configura globalmente la API de `google.generativeai` con esa clave.
    *   **Parámetros:** Ninguno.
    *   **Retorno:** Ninguno.
    *   **Lanza:** `ValueError` si no se encuentra una clave API.

### `backend/models.py`

**Propósito:** Define los modelos de datos que mapean directamente a las tablas de la base de datos utilizando el ORM (Object-Relational Mapper) de SQLAlchemy. Estos modelos representan la estructura de los datos que se almacenarán y recuperarán.

**Clases Principales:**

*   `class Book(Base)`:
    *   **Descripción:** Representa la tabla `books` en la base de datos. Cada instancia de `Book` corresponde a una fila en esta tabla.
    *   **`__tablename__ = "books"`:** Define el nombre de la tabla en la base de datos.
    *   **`__table_args__ = {'extend_existing': True}`:** Una configuración que permite a SQLAlchemy re-declarar la tabla si ya existe, lo cual puede ser útil en entornos de desarrollo o pruebas.
    *   **Columnas:**
        *   `id = Column(Integer, primary_key=True, index=True)`: Columna de clave primaria entera, se indexa automáticamente para búsquedas rápidas.
        *   `title = Column(String, index=True)`: Cadena para el título del libro, también indexada.
        *   `author = Column(String, index=True)`: Cadena para el autor del libro, indexada.
        *   `category = Column(String, index=True)`: Cadena para la categoría del libro, indexada.
        *   `cover_image_url = Column(String, nullable=True)`: Cadena para la URL de la imagen de portada. Puede ser `None` (nulo) si no hay portada.
        *   `file_path = Column(String, unique=True)`: Cadena para la ruta del archivo del libro en el sistema de archivos. Debe ser única para cada libro, evitando duplicados.

### `backend/rag.py`

**Propósito:** Este módulo encapsula toda la lógica relacionada con el sistema de Recuperación Aumentada por Generación (RAG). Incluye funciones para la extracción de texto de diferentes formatos de archivo, la división del texto en fragmentos (chunking), la generación de embeddings, la interacción con la base de datos vectorial ChromaDB y la consulta a modelos de lenguaje grandes (LLMs) de Gemini.

**Funciones Principales:**

*   `_ensure_init()`:
    *   **Lógica:** Inicializa las dependencias externas (carga variables de entorno, configura `genai`, inicializa `chromadb.PersistentClient`) solo una vez, la primera vez que se llama a una función RAG. Permite deshabilitar la IA para pruebas (`DISABLE_AI=1`).
    *   **Variables Globales Afectadas:** `_initialized`, `_collection`, `_ai_enabled`.

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`:
    *   **Lógica:** Genera un embedding vectorial para el texto de entrada utilizando el modelo `EMBEDDING_MODEL` (por defecto, `models/text-embedding-004`). Si la IA está deshabilitada, devuelve un embedding dummy.
    *   **Parámetros:** `text` (la cadena de texto a embeber), `task_type` (tipo de tarea para el embedding, ej., "RETRIEVAL_DOCUMENT" o "RETRIEVAL_QUERY").
    *   **Retorno:** Una lista de números flotantes que representan el embedding.

*   `extract_text_from_pdf(file_path: str) -> str`:
    *   **Lógica:** Extrae todo el texto de un archivo PDF utilizando `PyPDF2`.
    *   **Parámetros:** `file_path` (ruta al archivo PDF).
    *   **Retorno:** El texto extraído como una cadena.

*   `extract_text_from_epub(file_path: str) -> str`:
    *   **Lógica:** Extrae el contenido textual de un archivo EPUB. Lee el libro, itera sobre los ítems de tipo documento y usa `BeautifulSoup` para limpiar el HTML y obtener el texto plano.
    *   **Parámetros:** `file_path` (ruta al archivo EPUB).
    *   **Retorno:** El texto extraído como una cadena, o una cadena vacía si hay un error.

*   `extract_text(file_path: str) -> str`:
    *   **Lógica:** Función unificada que detecta el tipo de archivo (PDF o EPUB) y llama a la función de extracción de texto correspondiente. Lanza un `ValueError` si el tipo de archivo no es soportado.
    *   **Parámetros:** `file_path`.
    *   **Retorno:** El texto extraído.

*   `chunk_text(text: str, max_tokens: int = 1000) -> list[str]`:
    *   **Lógica:** Divide una cadena de texto larga en fragmentos más pequeños, asegurándose de que cada fragmento no exceda `max_tokens`. Utiliza `tiktoken` (basado en tokenizador de GPT-3.5) para una estimación de tokens.
    *   **Parámetros:** `text` (el texto a fragmentar), `max_tokens` (el tamaño máximo de tokens por fragmento).
    *   **Retorno:** Una lista de cadenas, donde cada cadena es un fragmento de texto.

*   `_has_index_for_book(book_id: str) -> bool`:
    *   **Lógica:** Consulta ChromaDB para verificar si ya existen vectores de embedding asociados a un `book_id` específico.
    *   **Parámetros:** `book_id` (el ID del libro).
    *   **Retorno:** `True` si se encuentran vectores, `False` en caso contrario o si ocurre un error.

*   `delete_book_from_rag(book_id: str)`:
    *   **Lógica:** Elimina todos los vectores de embedding y metadatos asociados a un `book_id` de la colección de ChromaDB.
    *   **Parámetros:** `book_id`.
    *   **Retorno:** Ninguno.

*   `get_index_count(book_id: str) -> int`:
    *   **Lógica:** Devuelve el número de vectores que ChromaDB tiene indexados para un `book_id` dado.
    *   **Parámetros:** `book_id`.
    *   **Retorno:** El número de vectores (`int`).

*   `has_index(book_id: str) -> bool`:
    *   **Lógica:** Función pública que delega en `get_index_count` para verificar si un libro tiene índice RAG.
    *   **Parámetros:** `book_id`.
    *   **Retorno:** `True` si tiene índice, `False` en caso contrario.

*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`:
    *   **Lógica:** Orquesta el proceso completo de indexación RAG para un libro. Extrae el texto, lo divide en fragmentos, genera embeddings para cada fragmento y los almacena en ChromaDB junto con los metadatos `book_id` y `chunk_index`. Si `force_reindex` es `True`, primero elimina cualquier índice existente para ese libro.
    *   **Parámetros:** `file_path` (ruta al archivo del libro), `book_id` (ID del libro), `force_reindex` (booleano para forzar la reindexación).
    *   **Retorno:** Ninguno.
    *   **Lanza:** `ValueError` si el tipo de archivo no es soportado o si no se puede extraer/fragmentar el texto.

*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`:
    *   **Lógica:** Estima el número total de tokens y el número de fragmentos que se generarían para un archivo dado, utilizando la misma lógica de fragmentación que `chunk_text`.
    *   **Parámetros:** `file_path`, `max_tokens` (tamaño de fragmento para la estimación).
    *   **Retorno:** Un diccionario con `tokens` y `chunks`.

*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`:
    *   **Lógica:** Extiende la estimación a una lista de archivos, sumando los totales de tokens y fragmentos.
    *   **Parámetros:** `file_paths` (lista de rutas), `max_tokens`.
    *   **Retorno:** Un diccionario con `tokens`, `chunks` y `files` (número de archivos procesados exitosamente).

*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`:
    *   **Lógica:** El corazón del sistema de conversación RAG.
        1.  Genera un embedding para la `query` del usuario.
        2.  Realiza una búsqueda de similitud en ChromaDB para recuperar los 5 fragmentos de texto más relevantes del libro (`book_id`).
        3.  Combina estos fragmentos relevantes con la `query`, y opcionalmente con `metadata` del libro y `library` (contexto adicional de la biblioteca, ej. otros libros del autor), para construir un `prompt` contextual.
        4.  Envía este `prompt` a un modelo de lenguaje de Gemini (`GENERATION_MODEL`).
        5.  La `mode` del prompt controla el comportamiento de la IA (`strict`: solo libro; `balanced`: prioriza libro, complementa y señala; `open`: combina libremente).
    *   **Parámetros:** `query` (la pregunta), `book_id` (el ID del libro), `mode` (la estrategia de respuesta), `metadata` (dict con título, autor, categoría), `library` (dict con contexto adicional como `author_other_books`).
    *   **Retorno:** La respuesta generada por la IA como una cadena de texto.

### `backend/main.py`

**Propósito:** Este es el archivo principal de la aplicación FastAPI. Define y configura la API RESTful, enrutando las solicitudes HTTP a las funciones de lógica de negocio apropiadas, gestionando la interacción con la base de datos, el procesamiento de archivos y la integración con las funcionalidades de IA y RAG.

**Elementos de Configuración Inicial:**

*   **`base_dir`**: Ruta base del directorio del backend.
*   **Carga de `.env`**: Carga las variables de entorno para API keys y configuración.
*   **`API_KEY`, `AI_ENABLED`**: Configura la clave de la API de Gemini y habilita/deshabilita la IA.
*   **`models.Base.metadata.create_all(bind=database.engine)`**: Crea todas las tablas de la base de datos si no existen, basándose en los modelos ORM definidos.
*   **`app = FastAPI()`**: Instancia principal de la aplicación FastAPI.
*   **Rutas de Archivos**: Define las rutas absolutas para directorios de almacenamiento de libros (`BOOKS_DIR_FS`), portadas (`STATIC_COVERS_DIR_FS`) y archivos temporales (`TEMP_BOOKS_DIR_FS`).
*   **Montaje de Estáticos**: Monta los directorios `static` y `temp_books` para servir archivos directamente.
*   **Configuración CORS**: Permite solicitudes desde orígenes específicos (configurables vía `ALLOW_ORIGINS` y `ALLOW_ORIGIN_REGEX` en `.env`).

**Funciones Auxiliares:**

*   `async analyze_with_gemini(text: str) -> dict`:
    *   **Lógica:** Envía un fragmento de texto de las primeras páginas de un libro a un modelo de Gemini (`GEMINI_MODEL_MAIN`) para que identifique el título, autor y categoría. Espera un JSON como respuesta.
    *   **Retorno:** Diccionario con `title`, `author`, `category` o valores de "Error de IA".
    *   **Manejo de Errores:** Captura excepciones de Gemini y devuelve valores de error.

*   `process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`:
    *   **Lógica:** Abre un PDF, extrae texto de las primeras páginas y busca la imagen más grande (potencial portada) para guardarla.
    *   **Retorno:** Diccionario con `text` extraído y `cover_image_url` (si se encontró).

*   `process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`:
    *   **Lógica:** Abre un EPUB, extrae texto de los capítulos y busca una imagen de portada (primero en metadatos, luego por nombre "cover").
    *   **Retorno:** Diccionario con `text` extraído y `cover_image_url` (si se encontró).
    *   **Lanza:** `HTTPException` si no se puede extraer suficiente texto.

*   `get_db()`:
    *   **Lógica:** Dependencia de FastAPI para gestionar sesiones de base de datos. Abre una sesión, la `yield` al endpoint y asegura que se cierra al finalizar.

**Endpoints de la API:**

*   **`POST /upload-book/`**:
    *   **Función:** `upload_book`
    *   **Descripción:** Recibe un archivo de libro (PDF o EPUB), lo guarda, lo procesa para extraer texto y portada, lo envía a Gemini para auto-identificación de metadatos. Si la IA no identifica el libro, se rechaza la subida. Finalmente, crea la entrada en la DB.
    *   **Entrada:** `book_file: UploadFile`
    *   **Salida:** `schemas.Book`

*   **`GET /books/`**:
    *   **Función:** `read_books`
    *   **Descripción:** Lista los libros en la biblioteca, permitiendo filtrar por `category`, `search` general (título, autor, categoría) o `author`.
    *   **Entrada:** `category: str | None`, `search: str | None`, `author: str | None`
    *   **Salida:** `List[schemas.Book]`

*   **`GET /books/count`**:
    *   **Función:** `get_books_count`
    *   **Descripción:** Devuelve el número total de libros en la base de datos.
    *   **Salida:** `int`

*   **`GET /books/search/`**:
    *   **Función:** `search_books`
    *   **Descripción:** Permite buscar libros por un título parcial, con opciones de paginación (`skip`, `limit`).
    *   **Entrada:** `title: str`, `skip: int`, `limit: int`
    *   **Salida:** `List[schemas.Book]`

*   **`GET /categories/`**:
    *   **Función:** `read_categories`
    *   **Descripción:** Devuelve una lista de todas las categorías de libros únicas.
    *   **Salida:** `List[str]`

*   **`DELETE /books/{book_id}`**:
    *   **Función:** `delete_single_book`
    *   **Descripción:** Elimina un libro de la base de datos por su ID, incluyendo sus archivos asociados y su índice RAG.
    *   **Entrada:** `book_id: int`
    *   **Salida:** `{"message": str}`

*   **`DELETE /categories/{category_name}`**:
    *   **Función:** `delete_category_and_books`
    *   **Descripción:** Elimina todos los libros de una categoría específica, así como sus archivos e índices RAG.
    *   **Entrada:** `category_name: str`
    *   **Salida:** `{"message": str}`

*   **`GET /books/download/{book_id}`**:
    *   **Función:** `download_book`
    *   **Descripción:** Permite la descarga o visualización en línea del archivo original del libro (PDF o EPUB).
    *   **Entrada:** `book_id: int`
    *   **Salida:** `FileResponse`

*   **`POST /tools/convert-epub-to-pdf`**:
    *   **Función:** `convert_epub_to_pdf`
    *   **Descripción:** Recibe un archivo EPUB, lo extrae, lo procesa con `weasyprint` y librerías HTML para generar un PDF, lo guarda temporalmente y devuelve una URL para su descarga.
    *   **Entrada:** `file: UploadFile` (EPUB)
    *   **Salida:** `schemas.ConversionResponse`

*   **`POST /rag/upload-book/`**:
    *   **Función:** `upload_book_for_rag`
    *   **Descripción:** Sube un archivo de libro y lo procesa directamente para el sistema RAG (crea embeddings, indexa en ChromaDB). Genera un `book_id` UUID para este fin. (Esta ruta es un caso de uso alternativo, no el principal del frontend actual para indexar libros ya subidos a la librería).
    *   **Entrada:** `file: UploadFile`
    *   **Salida:** `schemas.RagUploadResponse`

*   **`POST /rag/query/`**:
    *   **Función:** `query_rag_endpoint`
    *   **Descripción:** Recibe una consulta del usuario junto con un `book_id` y un `mode` de conversación. Utiliza el módulo `rag` para obtener una respuesta de la IA.
    *   **Entrada:** `query_data: schemas.RagQuery`
    *   **Salida:** `schemas.RagQueryResponse`

*   **`POST /rag/index/{book_id}`**:
    *   **Función:** `index_existing_book_for_rag`
    *   **Descripción:** Indexa (o reindexa si `force` es `True`) un libro ya existente en la base de datos para el sistema RAG, utilizando su `file_path`.
    *   **Entrada:** `book_id: int`, `force: bool = False`
    *   **Salida:** `{"message": str, "book_id": str, "force": bool}`

*   **`GET /rag/status/{book_id}`**:
    *   **Función:** `rag_status`
    *   **Descripción:** Devuelve el estado de indexación RAG de un libro (si está indexado y cuántos vectores tiene).
    *   **Entrada:** `book_id: int`
    *   **Salida:** `{"book_id": str, "indexed": bool, "vector_count": int}`

*   **`POST /rag/reindex/category/{category_name}`**:
    *   **Función:** `rag_reindex_category`
    *   **Descripción:** (Re)indexa todos los libros que pertenecen a una categoría específica para el sistema RAG.
    *   **Entrada:** `category_name: str`, `force: bool = True`
    *   **Salida:** `{"category": str, "processed": int, "failed": list, "force": bool}`

*   **`POST /rag/reindex/all`**:
    *   **Función:** `rag_reindex_all`
    *   **Descripción:** (Re)indexa *todos* los libros en la biblioteca para el sistema RAG.
    *   **Entrada:** `force: bool = True`
    *   **Salida:** `{"processed": int, "failed": list, "total": int, "force": bool}`

*   **`GET /rag/estimate/book/{book_id}`**:
    *   **Función:** `estimate_rag_for_book`
    *   **Descripción:** Proporciona una estimación del número de tokens y fragmentos de un libro, y un coste estimado si se proporciona un valor `per1k`.
    *   **Entrada:** `book_id: int`, `per1k: float | None`, `max_tokens: int`
    *   **Salida:** `dict` con estimaciones.

*   **`GET /rag/estimate/category/{category_name}`**:
    *   **Función:** `estimate_rag_for_category`
    *   **Descripción:** Proporciona una estimación agregada del número de tokens y fragmentos para todos los libros de una categoría.
    *   **Entrada:** `category_name: str`, `per1k: float | None`, `max_tokens: int`
    *   **Salida:** `dict` con estimaciones.

*   **`GET /rag/estimate/all`**:
    *   **Función:** `estimate_rag_for_all`
    *   **Descripción:** Proporciona una estimación agregada del número de tokens y fragmentos para *todos* los libros de la biblioteca.
    *   **Entrada:** `per1k: float | None`, `max_tokens: int`
    *   **Salida:** `dict` con estimaciones.

### `backend/__init__.py`

**Propósito:** Es un archivo vacío que simplemente marca el directorio `backend` como un paquete Python, permitiendo que sus módulos (como `schemas`, `models`, `crud`, etc.) sean importados por otros módulos dentro del mismo paquete o desde fuera.

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

**Propósito:** Este archivo es un script de migración de base de datos generado por Alembic. Contiene las instrucciones SQL (o las operaciones ORM equivalentes) para crear y eliminar la tabla `books` en la base de datos. Se utiliza para gestionar los cambios en el esquema de la base de datos de manera controlada.

**Funciones Principales:**

*   `upgrade()`:
    *   **Lógica:** Define las operaciones para aplicar la migración. En este caso, crea la tabla `books` con las columnas `id`, `title`, `author`, `category`, `cover_image_url` y `file_path`. Establece `id` como clave primaria y añade índices a `id`, `title`, `author`, `category`. Además, `file_path` tiene una restricción `UniqueConstraint`.
*   `downgrade()`:
    *   **Lógica:** Define las operaciones para revertir la migración. En este caso, elimina todos los índices creados y luego la tabla `books`.

### `backend/tests/` y `backend/tests_curated/`

**Propósito:** Estos directorios contienen las pruebas automatizadas del backend. Están escritos utilizando `pytest` y `unittest.mock` para simular dependencias externas (como la base de datos o las APIs de Google Gemini).

*   **Tipos de Pruebas:**
    *   **Pruebas de esquemas (`test_schemas.py`, `test_test_schemas_curated.py`):** Verifican que los modelos Pydantic (`schemas.py`) validan correctamente los datos y manejan errores de tipo.
    *   **Pruebas de modelos ORM (`test_models.py`):** Aseguran que el modelo `Book` en `models.py` se puede instanciar correctamente y simulan algunas propiedades.
    *   **Pruebas CRUD (`test_crud.py`, `test_crud_curated.py`):** Comprueban las funciones en `crud.py` para asegurar que las operaciones de base de datos (crear, leer, eliminar) se comportan como se espera, incluyendo el manejo de archivos asociados.
    *   **Pruebas de utilidades (`test_utils.py`, `test_test_utils_curated.py`):** Verifican la función `configure_genai` en `utils.py`, asegurando que la configuración de la API de Gemini funciona correctamente con diferentes variables de entorno.
    *   **Pruebas RAG (`test_rag.py`, `test_test_rag_curated.py`):** Validan las funciones del módulo `rag.py`, como la generación de embeddings, la extracción de texto, el fragmentado, y las interacciones con ChromaDB y Gemini (usando mocks).
    *   **Pruebas de la API principal (`test_main.py`, `test_test_api_curated.py`, `test_main_async_curated.py`):** Utilizan `TestClient` de FastAPI para simular solicitudes HTTP a los endpoints de la API en `main.py`. Prueban la subida de libros, la búsqueda, la eliminación, la conversión de archivos y las interacciones RAG a nivel de API, con mocks para todas las dependencias internas.
    *   **Pruebas de Humo (CI) (`test_ci_smoke.py`):** Pruebas muy básicas para verificar que el entorno de CI puede importar los módulos esenciales y ejecutar pruebas mínimas.

## 4. Análisis Detallado del Frontend (React)

El frontend, construido con React, proporciona una interfaz de usuario interactiva y fluida.

### `frontend/src/App.js`

**Propósito:** Es el componente raíz de la aplicación React. Se encarga de establecer la estructura general de la aplicación, incluyendo la cabecera (`Header`) y la configuración de las rutas (`Routes`) utilizando `react-router-dom`.

*   **Estado / Props:** No gestiona estado propio ni recibe props.
*   **Efectos Secundarios:** No tiene efectos secundarios directos. Su función principal es la composición de componentes y la definición del enrutamiento.
*   **Interacciones del Usuario:** Indirectamente, permite la navegación entre las diferentes vistas de la aplicación al hacer clic en los enlaces definidos en el `Header`.
*   **Comunicación con el Backend:** No se comunica directamente con el backend; delega esta responsabilidad a los componentes de vista específicos.

### `frontend/src/Header.js`

**Propósito:** Componente de la cabecera de la aplicación. Muestra el título, un contador de libros y la barra de navegación principal.

*   **Estado (State):**
    *   `menuOpen (boolean)`: Controla la visibilidad del menú de navegación, especialmente para dispositivos móviles (menú hamburguesa).
    *   `bookCount (number)`: Almacena el número total de libros en la biblioteca, obtenido del backend.
    *   `errorMessage (string)`: Mensaje de error si la obtención del contador de libros falla.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect`: Al montarse el componente, realiza una llamada a la API (`${API_URL}/books/count`) para obtener el número total de libros. Esta llamada se repite periódicamente (cada 10 minutos) para mantener el contador actualizado.
*   **Interacciones del Usuario:**
    *   Clic en el botón de menú hamburguesa: Alterna el estado `menuOpen` para mostrar u ocultar el menú de navegación.
    *   Clic en cualquier `NavLink`: Navega a la ruta correspondiente y cierra el menú (`handleLinkClick`).
*   **Comunicación con el Backend:** Realiza solicitudes `GET` al endpoint `/books/count`.

### `frontend/src/LibraryView.js`

**Propósito:** Es la vista principal de la aplicación, donde los usuarios pueden ver y gestionar su colección de libros. Permite buscar, filtrar por categoría o autor, descargar/abrir libros y eliminarlos.

*   **Estado (State):**
    *   `books (array)`: Almacena la lista de objetos libro recuperados del backend para mostrar.
    *   `searchParams (URLSearchParams)`: Objeto para gestionar los parámetros de consulta de la URL (ej., `?category=Fantasia`, `?author=...). Se usa con `useSearchParams` de React Router.
    *   `searchTerm (string)`: El texto introducido por el usuario en la barra de búsqueda general.
    *   `debouncedSearchTerm (string)`: Una versión de `searchTerm` que se actualiza con un retardo (`useDebounce` hook), para optimizar las llamadas a la API de búsqueda.
    *   `error (string)`: Mensaje de error si la carga de libros falla.
    *   `loading (boolean)`: Indica si los libros se están cargando actualmente.
    *   `isMobile (boolean)`: Determina si el dispositivo es móvil para mostrar u ocultar ciertos elementos (ej. botón de descarga de PDF).
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect` (para `isMobile`): Ajusta el estado `isMobile` basándose en el ancho de la ventana al inicializar y en cada cambio de tamaño.
    *   `useEffect` (para `fetchBooks`): Se dispara cuando `debouncedSearchTerm` o `searchParams` cambian, lo que provoca una nueva llamada a la API para cargar/filtrar libros.
*   **Interacciones del Usuario:**
    *   **Barra de Búsqueda:** Al escribir, actualiza `searchTerm`, que luego se debouncea y activa una búsqueda en el backend.
    *   **Clic en Autor:** Llama a `handleAuthorClick`, que actualiza `searchParams` para filtrar la vista por ese autor.
    *   **Clic en Categoría:** Llama a `handleCategoryClick`, que actualiza `searchParams` para filtrar la vista por esa categoría.
    *   **Botón "Eliminar libro" (`×`):** Llama a `handleDeleteBook`, que envía una solicitud `DELETE` al backend.
    *   **Botones "Abrir PDF" / "Leer EPUB":** Para PDF, abre el archivo en una nueva pestaña (visualización en línea). Para EPUB, navega a la `ReaderView` de la aplicación. En móvil, para ambos, puede aparecer también un botón de descarga.
*   **Comunicación con el Backend:**
    *   `GET /books/`: Para obtener la lista de libros con filtros y búsqueda.
    *   `DELETE /books/{bookId}`: Para eliminar un libro.
    *   `GET /books/download/{bookId}`: Para obtener el archivo del libro.

### `frontend/src/UploadView.js`

**Propósito:** Permite a los usuarios seleccionar y subir uno o varios archivos de libros (PDF o EPUB) al backend. Muestra el estado de cada archivo durante el proceso de subida y análisis por parte de la IA.

*   **Estado (State):**
    *   `filesToUpload (array)`: Un array de objetos, donde cada objeto representa un archivo a subir. Cada objeto contiene el `file` (el objeto File original), su `status` (`pending`, `uploading`, `success`, `error`) y un `message` descriptivo.
    *   `isUploading (boolean)`: Un flag que indica si algún archivo está actualmente en proceso de subida o análisis.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):** Ninguno directo.
*   **Interacciones del Usuario:**
    *   **Selección de archivos (input `type="file"`) o Arrastrar y Soltar (`handleDrop`):** Añade los archivos seleccionados a la lista `filesToUpload` con un estado `pending`.
    *   **Botón "Subir Archivo(s)":** Llama a `handleUpload`. Este método itera sobre `filesToUpload`, envía cada archivo al backend y actualiza su estado y mensaje individualmente.
    *   **Botón "Ir a la Biblioteca":** Aparece una vez que todos los archivos han sido procesados (éxito o error), y redirige al usuario a la `LibraryView`.
*   **Comunicación con el Backend:**
    *   `POST /upload-book/`: Envía cada archivo como `FormData`. Espera una respuesta JSON que incluye el título del libro si la subida fue exitosa, o detalles del error.

### `frontend/src/CategoriesView.js`

**Propósito:** Muestra una lista de todas las categorías de libros únicas presentes en la biblioteca. Permite a los usuarios filtrar la vista de la biblioteca principal por una categoría específica.

*   **Estado (State):**
    *   `categories (array)`: Un array de cadenas de texto, cada una representando una categoría única obtenida del backend.
    *   `error (string)`: Mensaje de error si la carga de categorías falla.
    *   `loading (boolean)`: Indica si las categorías se están cargando actualmente.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect`: Al montarse el componente, realiza una solicitud `GET` al endpoint `/categories/` para obtener la lista de categorías.
*   **Interacciones del Usuario:**
    *   Clic en una "tarjeta" de categoría: Utiliza `Link` de `react-router-dom` para navegar a la ruta raíz (`/`) pero con un parámetro de consulta `?category=`, lo que activa el filtrado en `LibraryView`.
*   **Comunicación con el Backend:**
    *   `GET /categories/`: Para obtener la lista de categorías.

### `frontend/src/ToolsView.js`

**Propósito:** Proporciona un espacio para herramientas útiles relacionadas con la gestión de libros. Actualmente, incluye un "Convertidor de EPUB a PDF".

*   **Componentes Internos:**
    *   `EpubToPdfConverter`: Un subcomponente funcional que implementa la lógica y la UI para la conversión.
*   **Estado (dentro de `EpubToPdfConverter`):**
    *   `selectedFile (File)`: El archivo EPUB que el usuario ha seleccionado para convertir.
    *   `message (string)`: Muestra el estado actual del proceso de conversión (ej., "Convirtiendo...", "Error:", "¡Conversión completada!").
    *   `isLoading (boolean)`: Indica si el proceso de conversión está en curso.
*   **Propiedades (Props):** Ninguna para `ToolsView` o `EpubToPdfConverter`.
*   **Efectos Secundarios (Effects):** Ninguno directo para `ToolsView`. `EpubToPdfConverter` no tiene efectos de `useEffect` en sí, pero gestiona el estado local.
*   **Interacciones del Usuario (dentro de `EpubToPdfConverter`):**
    *   **Selección de archivo (input `type="file"`) o Arrastrar y Soltar (`handleDrop`):** Permite al usuario elegir un archivo EPUB.
    *   **Botón "Convertir a PDF":** Llama a `handleConvert`, que inicia la comunicación con el backend.
*   **Comunicación con el Backend (dentro de `EpubToPdfConverter`):**
    *   `POST /tools/convert-epub-to-pdf`: Envía el archivo EPUB al backend. Espera una respuesta JSON con una `download_url` que apunta al PDF convertido temporalmente almacenado en el servidor. Luego, inicia la descarga o abre el PDF en una nueva pestaña.

### `frontend/src/ReaderView.js`

**Propósito:** Permite a los usuarios leer libros en formato EPUB directamente dentro de la aplicación, utilizando la librería `react-reader`.

*   **Estado (State):**
    *   `location (string)`: Representa la ubicación actual del lector dentro del EPUB (un CFI - "Content Fragment Identifier"). Esto permite recordar la última posición de lectura.
    *   `epubData (ArrayBuffer)`: Contiene los datos binarios del archivo EPUB, necesarios para que `react-reader` pueda renderizar el libro.
    *   `isLoading (boolean)`: Indica si el libro se está cargando desde el backend.
    *   `error (string)`: Mensaje de error si la carga del libro falla.
*   **Propiedades (Props):** Obtiene `bookId` de los parámetros de la URL (`useParams`).
*   **Efectos Secundarios (Effects):**
    *   `useEffect`: Al montarse el componente o cuando cambia `bookId`, realiza una solicitud `GET` a `/books/download/{bookId}` para obtener el contenido binario del EPUB.
*   **Interacciones del Usuario:**
    *   La navegación dentro del libro (pasar páginas, saltar capítulos) es manejada por la librería `react-reader`. Los cambios de ubicación se capturan y actualizan el estado `location` para persistencia.
*   **Comunicación con el Backend:**
    *   `GET /books/download/{bookId}`: Para obtener el archivo binario del libro EPUB.

### `frontend/src/RagView.js`

**Propósito:** Proporciona la interfaz de usuario para interactuar con el sistema de Recuperación Aumentada por Generación (RAG). Los usuarios pueden seleccionar un libro de su biblioteca, indexarlo si es necesario y luego hacer preguntas sobre su contenido para obtener respuestas generadas por IA.

*   **Estado (State):**
    *   `message (string)`: Mensajes informativos para el usuario (ej., "Indexando...", "Listo para chatear").
    *   `isLoading (boolean)`: Indica si se está esperando una respuesta de la IA en el chat.
    *   `bookId (string)`: El ID del libro actualmente activo para la conversación RAG.
    *   `chatHistory (array)`: Un array de objetos que representan la conversación (`{ sender: 'user' | 'gemini', text: string }`).
    *   `currentQuery (string)`: El texto que el usuario está escribiendo en el campo de entrada del chat.
    *   `libraryBooks (array)`: Lista de todos los libros disponibles en la biblioteca, para que el usuario pueda seleccionar uno.
    *   `selectedLibraryId (string)`: El ID del libro seleccionado en el buscador/selector de libros.
    *   `libStatus (object)`: Contiene el estado de indexación RAG del `selectedLibraryId` (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy (boolean)`: Bloquea los botones de indexación/reindexación mientras una operación está en curso.
    *   `refreshing (boolean)`: Indica que se está refrescando el estado RAG (sin bloquear el chat).
    *   `searchTerm (string)`: Término de búsqueda para filtrar la lista de `libraryBooks`.
    *   `searching (boolean)`: Indica si la búsqueda de libros está en curso.
    *   `searchResults (array)`: Los resultados filtrados de la búsqueda de libros.
    *   `resultsOpen (boolean)`: Controla la visibilidad del desplegable de `searchResults`.
    *   `mode (string)`: Define el modo de respuesta de la IA (`strict`, `balanced`, `open`).
    *   `selectedBook (object)`: El objeto completo del libro seleccionado en el buscador.
*   **Propiedades (Props):** Ninguna.
*   **Efectos Secundarios (Effects):**
    *   `useEffect` (inicial): Carga la lista completa de libros de la biblioteca al montarse.
    *   `useEffect` (para `searchTerm`): Implementa un retardo (debounce) en la búsqueda de libros para optimizar las llamadas a la API de búsqueda.
    *   `useEffect` (para `chatHistory`, `isLoading`): Asegura que el scroll del chat se mantenga al final al añadir nuevos mensajes o al estar esperando una respuesta.
    *   `useEffect` (para `selectedLibraryId`): Cuando se selecciona un libro del selector, comprueba automáticamente su estado RAG y actualiza `libStatus`.
*   **Interacciones del Usuario:**
    *   **Buscador de Libros:** Permite buscar libros por título, autor o categoría para seleccionar sobre cuál chatear.
    *   **Selección de Libro:** Al hacer clic en un resultado de búsqueda, establece el `selectedLibraryId` y `selectedBook`.
    *   **Botones de RAG:** "Comprobar RAG" (refresca el estado), "Indexar antes de charlar" (crea el índice RAG), "Reindexar" (recrea el índice).
    *   **Botón "Chatear":** Habilita el panel de chat si el libro seleccionado está indexado.
    *   **Modo de Respuesta:** Permite elegir entre `strict`, `balanced` y `open` para influir en cómo la IA genera las respuestas.
    *   **Campo de Entrada de Consulta:** Para escribir preguntas sobre el libro. El tamaño del campo de texto se ajusta automáticamente.
    *   **Botón "Enviar":** Envía la consulta al backend (`handleQuerySubmit`), añade la pregunta al `chatHistory` y espera la respuesta de la IA.
*   **Comunicación con el Backend:**
    *   `GET /books/`: Para obtener la lista de libros de la biblioteca (para el buscador).
    *   `GET /rag/status/{bookId}`: Para comprobar el estado de indexación RAG de un libro.
    *   `POST /rag/index/{bookId}`: Para iniciar la indexación o reindexación de un libro.
    *   `POST /rag/query/`: Para enviar una pregunta y obtener una respuesta de la IA.

### `frontend/src/config.js`

**Propósito:** Este archivo simple define la URL base para el backend de la API. Está diseñado para ser configurable mediante una variable de entorno, facilitando el despliegue en diferentes entornos (desarrollo, producción).

*   **Variables:**
    *   `API_URL`: Exporta la URL del backend. Por defecto, usa `http://localhost:8001` si la variable de entorno `REACT_APP_API_URL` no está definida.

### `frontend/src/ErrorBoundary.js`

**Propósito:** Es un componente de límite de error de React (`React.Component`). Su función es capturar errores JavaScript en cualquier parte de su árbol de componentes hijo, registrarlos y mostrar una interfaz de usuario de fallback en lugar de dejar que la aplicación completa falle.

*   **Estado (State):**
    *   `hasError (boolean)`: Indica si se ha producido un error dentro de los componentes hijos.
    *   `error (Error)`: El objeto de error que fue capturado.
*   **Propiedades (Props):**
    *   `children`: Los componentes hijos que este ErrorBoundary protegerá.
*   **Métodos del Ciclo de Vida:**
    *   `static getDerivedStateFromError(error)`: Un método estático que se llama cuando un componente hijo lanza un error. Devuelve un objeto para actualizar el estado del límite de error, indicando que se ha producido un error.
    *   `componentDidCatch(error, info)`: Se llama después de que un error haya sido capturado. Se utiliza para registrar la información del error (en este caso, a la consola) o enviarla a un servicio de reporte de errores.
*   **Renderizado:**
    *   Si `this.state.hasError` es `true`, renderiza un mensaje de error genérico junto con los detalles del error capturado.
    *   De lo contrario, renderiza los `this.props.children` normalmente.

### `frontend/src/index.js`

**Propósito:** Es el punto de entrada principal de la aplicación React. Se encarga de inicializar la aplicación, renderizando el componente raíz (`App`) en el elemento del DOM con el `id` 'root'.

*   **Clases/Funciones Principales:**
    *   `ReactDOM.createRoot(document.getElementById('root'))`: Crea una raíz de React concurrente, el punto de inicio para la aplicación.
    *   `root.render(...)`: Renderiza el componente `App` dentro del modo estricto de React (`<React.StrictMode>`), que ayuda a detectar problemas potenciales en desarrollo.
    *   `reportWebVitals()`: Función para medir el rendimiento de la aplicación web (informes de Core Web Vitals).

## 5. Flujo de Datos y API

La interacción entre el frontend y el backend se realiza a través de llamadas a la API RESTful. Aquí se describe un flujo de datos común (subida de un libro) y se resumen los principales endpoints.

### Flujo de Subida de un Libro

1.  **Inicio en Frontend (`UploadView.js`):**
    *   El usuario selecciona uno o varios archivos (PDF/EPUB) a través de un input de archivo o arrastrándolos y soltándolos.
    *   La aplicación React actualiza su estado interno para mostrar los archivos seleccionados como "pendientes".
    *   Cuando el usuario hace clic en "Subir Archivo(s)", el componente inicia un bucle de subida para cada archivo.

2.  **Envío al Backend (`UploadView.js` -> `main.py`):**
    *   Para cada archivo, `UploadView.js` crea un objeto `FormData` y lo envía al endpoint `POST /upload-book/` del backend.
    *   El estado del archivo en el frontend cambia a "Subiendo y analizando...".

3.  **Procesamiento en Backend (`main.py`):**
    *   FastAPI recibe el archivo (`book_file: UploadFile`).
    *   El backend guarda el archivo subido en el directorio `backend/books/`.
    *   Detecta la extensión del archivo (`.pdf` o `.epub`).
    *   Llama a `process_pdf()` o `process_epub()`:
        *   Extrae el texto de las primeras páginas del libro.
        *   Intenta identificar y guardar una imagen de portada en `backend/static/covers/`.
        *   Si la extracción falla (ej. EPUB vacío), el backend devuelve un error 422, y el archivo subido se borra.
    *   Llama a `analyze_with_gemini()`:
        *   Envía el texto extraído a la API de Google Gemini.
        *   Gemini (el modelo `gemini-2.5-flash`) analiza el texto e intenta identificar el título, autor y categoría del libro, devolviendo un JSON.
        *   Si Gemini no puede identificar el título ni el autor ("Desconocido"), el backend devuelve un error 422, y el archivo subido se borra.

4.  **Almacenamiento en Base de Datos (`main.py` -> `crud.py` -> `models.py`):**
    *   Si el análisis de Gemini es exitoso y los metadatos son válidos, `main.py` invoca `crud.create_book()`.
    *   `crud.create_book()` crea una nueva instancia del modelo `models.Book` con los metadatos (título, autor, categoría, URL de portada, ruta del archivo local).
    *   Esta instancia se añade a la sesión de SQLAlchemy, se persiste en la base de datos `library.db` y el objeto se refresca para obtener su `id`.

5.  **Respuesta al Frontend (`main.py` -> `UploadView.js`):**
    *   El backend devuelve una respuesta JSON al frontend, incluyendo el `id` del libro creado y los metadatos confirmados (`schemas.Book`).
    *   Si ocurre un error en cualquier paso (ej. archivo duplicado, error de IA), se devuelve un `HTTPException` con un código de estado de error (ej. 409, 422, 500) y un mensaje `detail`.

6.  **Actualización en Frontend (`UploadView.js`):**
    *   El frontend recibe la respuesta. Si es exitosa, actualiza el estado del archivo a "success" y muestra un mensaje como "'[Título del libro]' añadido correctamente.".
    *   Si es un error, el estado cambia a "error" y se muestra el mensaje de error del backend.
    *   Una vez que todos los archivos han sido procesados, aparece un botón para "Ir a la Biblioteca", redirigiendo al usuario a la `LibraryView`.

### Endpoints Principales de la API (Backend: `backend/main.py`)

A continuación se resumen los endpoints clave expuestos por la API de FastAPI:

| Método HTTP | Ruta                                     | Descripción                                                                 | Petición (Request Body/Query Params)                           | Respuesta (Response Model)                           |
| :---------- | :--------------------------------------- | :-------------------------------------------------------------------------- | :------------------------------------------------------------- | :--------------------------------------------------- |
| `POST`      | `/upload-book/`                          | Sube un libro (PDF/EPUB), lo analiza con IA y lo añade a la biblioteca.    | `book_file: UploadFile`                                        | `schemas.Book`                                       |
| `GET`       | `/books/`                                | Obtiene una lista de libros, con opciones de filtrado.                      | `category (str)`, `search (str)`, `author (str)` (opcional)  | `List[schemas.Book]`                                 |
| `GET`       | `/books/count`                           | Obtiene el número total de libros en la biblioteca.                         | Ninguno                                                        | `int`                                                |
| `GET`       | `/books/search/`                         | Busca libros por título parcial.                                            | `title (str)`, `skip (int)`, `limit (int)`                   | `List[schemas.Book]`                                 |
| `GET`       | `/categories/`                           | Obtiene una lista de todas las categorías de libros únicas.                 | Ninguno                                                        | `List[str]`                                          |
| `DELETE`    | `/books/{book_id}`                       | Elimina un libro de la base de datos y sus archivos asociados.             | `book_id (path parameter)`                                     | `{"message": str}`                                   |
| `DELETE`    | `/categories/{category_name}`            | Elimina todos los libros de una categoría y sus archivos asociados.        | `category_name (path parameter)`                               | `{"message": str}`                                   |
| `GET`       | `/books/download/{book_id}`              | Permite descargar o visualizar el archivo de un libro.                      | `book_id (path parameter)`                                     | `FileResponse`                                       |
| `POST`      | `/tools/convert-epub-to-pdf`             | Convierte un archivo EPUB subido a formato PDF.                             | `file: UploadFile` (EPUB)                                      | `schemas.ConversionResponse`                         |
| `POST`      | `/rag/query/`                            | Envía una consulta al sistema RAG para obtener una respuesta sobre un libro. | `schemas.RagQuery` (JSON: `query`, `book_id`, `mode`)        | `schemas.RagQueryResponse`                           |
| `POST`      | `/rag/index/{book_id}`                   | Indexa un libro existente en la base de datos para el sistema RAG.          | `book_id (path parameter)`, `force (query param, bool)`      | `{"message": str, "book_id": str, "force": bool}`  |
| `GET`       | `/rag/status/{book_id}`                  | Obtiene el estado de indexación RAG de un libro.                            | `book_id (path parameter)`                                     | `{"book_id": str, "indexed": bool, "vector_count": int}` |
| `POST`      | `/rag/reindex/category/{category_name}`  | (Re)indexa todos los libros de una categoría en RAG.                       | `category_name (path parameter)`, `force (query param, bool)`| `{"category": str, "processed": int, "failed": list, "force": bool}` |
| `POST`      | `/rag/reindex/all`                       | (Re)indexa todos los libros de la biblioteca en RAG.                       | `force (query param, bool)`                                  | `{"processed": int, "failed": list, "total": int, "force": bool}` |
| `GET`       | `/rag/estimate/book/{book_id}`           | Estima tokens, chunks y coste de embeddings para un libro.                  | `book_id (path parameter)`, `per1k (float)`, `max_tokens (int)` | `dict` (con `tokens`, `chunks`, `estimated_cost`)    |
| `GET`       | `/rag/estimate/category/{category_name}` | Estima tokens, chunks y coste de embeddings para una categoría.             | `category_name (path parameter)`, `per1k (float)`, `max_tokens (int)` | `dict` (con `tokens`, `chunks`, `estimated_cost`, `files`) |
| `GET`       | `/rag/estimate/all`                      | Estima tokens, chunks y coste de embeddings para toda la biblioteca.        | `per1k (float)`, `max_tokens (int)`                          | `dict` (con `tokens`, `chunks`, `estimated_cost`, `files`) |
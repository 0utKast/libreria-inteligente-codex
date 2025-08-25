# Documentación Técnica del Proyecto "Mi Librería Inteligente"

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web diseñada para gestionar y interactuar con una biblioteca digital personal. Permite a los usuarios subir libros en formatos PDF y EPUB, los cuales son automáticamente analizados por inteligencia artificial para extraer metadatos como título, autor y categoría. La aplicación ofrece una interfaz para explorar la biblioteca, buscar libros, leer EPUBs directamente en el navegador, descargar archivos y utilizar herramientas de conversión.

Una característica central es la funcionalidad de *Retrieval Augmented Generation* (RAG), que permite a los usuarios conversar con la IA sobre el contenido de los libros. Esto se logra indexando los textos de los libros en una base de datos vectorial y utilizando modelos de lenguaje grandes (LLMs) para generar respuestas informadas por el contenido del libro.

### Arquitectura General

El proyecto sigue una arquitectura de cliente-servidor, dividida en dos componentes principales:

*   **Frontend (React):** La interfaz de usuario, desarrollada con React, que proporciona la experiencia interactiva al usuario. Se comunica con el backend a través de llamadas a la API.
*   **Backend (FastAPI):** Una API RESTful desarrollada con FastAPI en Python. Se encarga de la lógica de negocio, la interacción con la base de datos, el procesamiento de archivos, la integración con servicios de IA y la gestión del sistema RAG.

**Componentes Clave:**

*   **Base de Datos Relacional (SQLite):** Utilizada por el backend para almacenar los metadatos de los libros (título, autor, categoría, URL de portada, ruta de archivo). Se gestiona con SQLAlchemy y Alembic para migraciones.
*   **Almacenamiento de Archivos:** Los archivos de los libros y sus portadas se guardan en el sistema de archivos del servidor.
*   **Inteligencia Artificial (Google Gemini API):** Integrada en el backend para dos propósitos principales:
    *   **Análisis de Libros:** Extrae automáticamente metadatos de los libros subidos.
    *   **Generación de Embeddings y Respuestas RAG:** Procesa el texto de los libros para crear representaciones vectoriales y genera respuestas contextualizadas a las consultas del usuario.
*   **Base de Datos Vectorial (ChromaDB):** Utilizada por el sistema RAG para almacenar los embeddings de los fragmentos de texto de los libros, permitiendo una búsqueda semántica eficiente.
*   **Conversión de EPUB a PDF (WeasyPrint):** El backend incluye una herramienta para convertir libros EPUB a PDF.

## 2. Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas principales:

```
mi_libreria_inteligente/
├── backend/
│   ├── alembic/              # Configuraciones y scripts de migración de la base de datos (SQLAlchemy Alembic)
│   ├── static/               # Archivos estáticos servidos por FastAPI (e.g., portadas de libros)
│   │   └── covers/           # Imágenes de portadas de libros
│   ├── temp_books/           # Archivos temporales (e.g., PDFs convertidos, EPUBs subidos para RAG)
│   ├── books/                # Archivos de libros originales almacenados permanentemente
│   ├── tests/                # Pruebas unitarias e integración para el backend
│   ├── tests_curated/        # Pruebas "curadas" o de referencia para el backend (posiblemente generadas por IA)
│   ├── __init__.py           # Archivo de inicialización del paquete Python
│   ├── crud.py               # Operaciones CRUD (Create, Read, Update, Delete) para la base de datos
│   ├── database.py           # Configuración de la base de datos SQLAlchemy
│   ├── main.py               # Aplicación principal de FastAPI, definición de rutas y lógica principal
│   ├── models.py             # Definición de modelos de base de datos SQLAlchemy
│   ├── rag.py                # Lógica del sistema Retrieval Augmented Generation (RAG)
│   ├── schemas.py            # Modelos de datos Pydantic para validación y serialización de la API
│   └── utils.py              # Funciones de utilidad diversas
├── frontend/
│   ├── public/               # Archivos públicos para el frontend (HTML, etc.)
│   ├── src/                  # Código fuente de la aplicación React
│   │   ├── components/       # (Implícito) Posibles subcomponentes. En este caso, componentes principales están en src/
│   │   ├── App.js            # Componente raíz de la aplicación React
│   │   ├── CategoriesView.js # Vista para mostrar y gestionar categorías
│   │   ├── config.js         # Configuración del URL de la API
│   │   ├── ErrorBoundary.js  # Componente para manejo de errores de UI
│   │   ├── Header.js         # Componente de encabezado/navegación
│   │   ├── LibraryView.js    # Vista principal de la biblioteca (listado de libros)
│   │   ├── RagView.js        # Vista para interactuar con el sistema RAG
│   │   ├── ReaderView.js     # Vista para leer libros EPUB en el navegador
│   │   ├── ToolsView.js      # Vista para herramientas adicionales (e.g., conversor EPUB a PDF)
│   │   ├── UploadView.js     # Vista para subir nuevos libros
│   │   └── *.css             # Archivos CSS para estilos
│   ├── .env                  # Variables de entorno para el frontend
│   ├── package.json          # Metadatos y dependencias del proyecto React
│   └── ...                   # Otros archivos de configuración de React
├── .env                      # Variables de entorno para el backend (e.g., API keys, configuración de DB)
├── library.db                # Base de datos SQLite (generada al iniciar la aplicación)
├── rag_index/                # Directorio para la base de datos vectorial ChromaDB (índices RAG)
└── ...                       # Otros archivos de configuración de proyecto (e.g., docker-compose.yml, README.md)
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend es el corazón de la aplicación, gestionando la lógica de negocio, la base de datos y la interacción con la IA.

### `backend/main.py`

Archivo principal de la aplicación FastAPI. Configura el servidor, define las rutas de la API, integra la lógica de procesamiento de libros, la IA de Gemini y las funcionalidades RAG.

**Configuración Inicial:**

*   Inicializa FastAPI, configura CORS para permitir la comunicación entre frontend y backend.
*   Monta directorios estáticos (`/static`, `/temp_books`) para servir portadas y archivos temporales.
*   Carga variables de entorno (como `GOOGLE_API_KEY` o `GEMINI_API_KEY`) y configura el SDK de Gemini.
*   Crea las tablas de la base de datos si no existen, utilizando `models.Base.metadata.create_all`.

**Funciones Principales:**

*   **`analyze_with_gemini(text: str) -> dict`**
    *   **Propósito:** Analiza un fragmento de texto de un libro utilizando un modelo de Gemini para extraer el título, autor y categoría.
    *   **Lógica:** Envía un `prompt` estructurado a la API de Gemini con el texto inicial del libro. Espera un objeto JSON como respuesta. Incluye un *fallback* a valores "Desconocido" en caso de error o IA deshabilitada.
    *   **Parámetros:** `text` (str) - Texto inicial del libro a analizar.
    *   **Retorno:** `dict` con `title`, `author`, `category`.
*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**
    *   **Propósito:** Extrae texto inicial y, si es posible, una imagen de portada de un archivo PDF.
    *   **Lógica:** Abre el PDF con `fitz` (PyMuPDF), extrae texto de las primeras páginas y busca imágenes que puedan ser la portada basándose en su tamaño. Guarda la portada extraída.
    *   **Parámetros:**
        *   `file_path` (str): Ruta completa al archivo PDF.
        *   `covers_dir_fs` (str): Ruta del sistema de archivos donde guardar las portadas.
        *   `covers_url_prefix` (str): Prefijo URL para acceder a las portadas.
    *   **Retorno:** `dict` con `text` (texto extraído) y `cover_image_url` (URL relativa de la portada).
*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**
    *   **Propósito:** Extrae texto inicial y una imagen de portada de un archivo EPUB.
    *   **Lógica:** Lee el EPUB con `ebooklib`, extrae texto de los ítems `ITEM_DOCUMENT`. Intenta encontrar la portada en los metadatos o por heurística (`cover` en el nombre del archivo de imagen). Guarda la portada.
    *   **Parámetros:**
        *   `file_path` (str): Ruta completa al archivo EPUB.
        *   `covers_dir_fs` (str): Ruta del sistema de archivos donde guardar las portadas.
        *   `covers_url_prefix` (str): Prefijo URL para acceder a las portadas.
    *   **Retorno:** `dict` con `text` (texto extraído) y `cover_image_url` (URL relativa de la portada).
*   **`get_db()`**
    *   **Propósito:** Dependencia de FastAPI para obtener una sesión de base de datos SQLAlchemy.
    *   **Lógica:** Crea una sesión `SessionLocal` y la cede a la ruta, asegurando que se cierre al finalizar la petición.
    *   **Retorno:** Un generador que produce una sesión de SQLAlchemy.

**Rutas de la API (Endpoints):**

*   **`POST /upload-book/`** (`response_model=schemas.Book`)
    *   **Propósito:** Recibe un archivo de libro (PDF o EPUB), lo guarda, lo procesa con IA para extraer metadatos y lo almacena en la base de datos.
    *   **Parámetros:** `book_file` (UploadFile).
    *   **Retorno:** Detalles del libro creado.
*   **`GET /books/`** (`response_model=List[schemas.Book]`)
    *   **Propósito:** Obtiene una lista de libros, con opciones para filtrar por categoría, búsqueda general y autor.
    *   **Parámetros:** `category` (str | None), `search` (str | None), `author` (str | None).
    *   **Retorno:** Lista de objetos `Book`.
*   **`GET /books/count`** (`response_model=int`)
    *   **Propósito:** Devuelve el número total de libros en la biblioteca.
    *   **Retorno:** Entero.
*   **`GET /books/search/`** (`response_model=List[schemas.Book]`)
    *   **Propósito:** Busca libros por un título parcial (case-insensitive) con paginación.
    *   **Parámetros:** `title` (str), `skip` (int), `limit` (int).
    *   **Retorno:** Lista de objetos `Book`.
*   **`GET /categories/`** (`response_model=List[str]`)
    *   **Propósito:** Obtiene una lista de todas las categorías únicas de libros.
    *   **Retorno:** Lista de cadenas (nombres de categorías).
*   **`DELETE /books/{book_id}`**
    *   **Propósito:** Elimina un libro específico de la base de datos y sus archivos asociados (libro y portada), también limpia su índice RAG.
    *   **Parámetros:** `book_id` (int).
    *   **Retorno:** Mensaje de confirmación.
*   **`DELETE /categories/{category_name}`**
    *   **Propósito:** Elimina todos los libros de una categoría específica, incluyendo sus archivos y sus índices RAG.
    *   **Parámetros:** `category_name` (str).
    *   **Retorno:** Mensaje de confirmación con el número de libros eliminados.
*   **`GET /books/download/{book_id}`**
    *   **Propósito:** Permite descargar o abrir un archivo de libro.
    *   **Parámetros:** `book_id` (int).
    *   **Retorno:** `FileResponse` con el contenido del archivo.
*   **`POST /tools/convert-epub-to-pdf`** (`response_model=schemas.ConversionResponse`)
    *   **Propósito:** Convierte un archivo EPUB subido a PDF.
    *   **Lógica:** Utiliza `tempfile`, `zipfile`, `BeautifulSoup` y `weasyprint` para extraer contenido del EPUB y renderizarlo como PDF. Guarda el PDF resultante en `temp_books`.
    *   **Parámetros:** `file` (UploadFile).
    *   **Retorno:** URL de descarga del PDF generado.
*   **`POST /rag/upload-book/`** (`response_model=schemas.RagUploadResponse`)
    *   **Propósito:** Sube un libro (PDF/EPUB) temporalmente para su indexación inmediata en RAG. Genera un `book_id` UUID para este libro temporal.
    *   **Parámetros:** `file` (UploadFile).
    *   **Retorno:** `book_id` y mensaje de confirmación.
*   **`POST /rag/query/`** (`response_model=schemas.RagQueryResponse`)
    *   **Propósito:** Permite al usuario consultar el sistema RAG sobre el contenido de un libro específico.
    *   **Lógica:** Recibe una consulta, recupera chunks relevantes del libro del ChromaDB, los contextualiza con metadatos del libro y de la biblioteca (si se proporciona) y usa Gemini para generar una respuesta.
    *   **Parámetros:** `query_data` (schemas.RagQuery).
    *   **Retorno:** Respuesta generada por la IA.
*   **`POST /rag/index/{book_id}`**
    *   **Propósito:** Indexa un libro existente en la base de datos para su uso en RAG.
    *   **Parámetros:** `book_id` (int), `force` (bool, opcional, para reindexar).
    *   **Retorno:** Mensaje de confirmación.
*   **`GET /rag/status/{book_id}`**
    *   **Propósito:** Devuelve el estado de indexación RAG de un libro (si está indexado y cuántos vectores tiene).
    *   **Parámetros:** `book_id` (int).
    *   **Retorno:** `dict` con `book_id`, `indexed`, `vector_count`.
*   **`POST /rag/reindex/category/{category_name}`**
    *   **Propósito:** Reindexa (o indexa) todos los libros de una categoría específica para RAG.
    *   **Parámetros:** `category_name` (str), `force` (bool).
    *   **Retorno:** `dict` con `category`, `processed`, `failed`, `force`.
*   **`POST /rag/reindex/all`**
    *   **Propósito:** Reindexa (o indexa) todos los libros de la biblioteca para RAG.
    *   **Parámetros:** `force` (bool).
    *   **Retorno:** `dict` con `processed`, `failed`, `total`, `force`.
*   **`GET /rag/estimate/book/{book_id}`**, **`/rag/estimate/category/{category_name}`**, **`/rag/estimate/all`**
    *   **Propósito:** Proporciona estimaciones del número de tokens y chunks para la indexación RAG de un libro, categoría o toda la biblioteca. Opcionalmente, calcula un coste estimado.
    *   **Parámetros:** `book_id` (int) / `category_name` (str), `per1k` (float, coste por 1000 tokens), `max_tokens` (int, tamaño de chunk).
    *   **Retorno:** `dict` con estimaciones.

### `backend/schemas.py`

Define los modelos Pydantic para la serialización y validación de datos en la API.

*   **`BookBase(BaseModel)`**: Esquema base para los datos de un libro, utilizado para la creación.
    *   `title` (str): Título del libro.
    *   `author` (str): Autor del libro.
    *   `category` (str): Categoría del libro.
    *   `cover_image_url` (str | None): URL de la imagen de portada.
    *   `file_path` (str): Ruta interna del archivo del libro.
*   **`Book(BookBase)`**: Esquema completo de un libro, extendiendo `BookBase` con un ID.
    *   `id` (int): ID único del libro en la base de datos.
*   **`ConversionResponse(BaseModel)`**: Respuesta para la conversión de EPUB a PDF.
    *   `download_url` (str): URL para descargar el PDF convertido.
*   **`RagUploadResponse(BaseModel)`**: Respuesta para la subida de un libro para RAG.
    *   `book_id` (str): ID asignado al libro en el sistema RAG.
    *   `message` (str): Mensaje de estado.
*   **`RagQuery(BaseModel)`**: Cuerpo de la solicitud para una consulta RAG.
    *   `query` (str): La pregunta del usuario.
    *   `book_id` (str): ID del libro sobre el que se consulta.
    *   `mode` (str | None): Estrategia de respuesta ('strict', 'balanced', 'open').
*   **`RagQueryResponse(BaseModel)`**: Respuesta de una consulta RAG.
    *   `response` (str): La respuesta generada por la IA.

### `backend/models.py`

Define el modelo de la base de datos `Book` utilizando SQLAlchemy ORM.

*   **`Book(Base)`**
    *   `__tablename__ = "books"`: Nombre de la tabla en la base de datos.
    *   `id` (Integer): Clave primaria, autoincremental, indexada.
    *   `title` (String): Título del libro, indexado.
    *   `author` (String): Autor del libro, indexado.
    *   `category` (String): Categoría del libro, indexada.
    *   `cover_image_url` (String, nullable=True): URL de la imagen de portada.
    *   `file_path` (String, unique=True): Ruta única al archivo original del libro.

### `backend/crud.py`

Contiene funciones para interactuar directamente con la base de datos (CRUD - Create, Read, Update, Delete) para los objetos `Book`.

*   **`get_book_by_path(db: Session, file_path: str)`**: Obtiene un libro por su ruta de archivo.
*   **`get_book_by_title(db: Session, title: str)`**: Obtiene un libro por su título exacto.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**: Busca libros por título parcial (case-insensitive) con paginación.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`**: Obtiene una lista de libros, con filtrado opcional por categoría, autor y término de búsqueda general (título, autor, categoría).
*   **`get_categories(db: Session) -> list[str]`**: Obtiene una lista de todas las categorías únicas presentes en la base de datos.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**: Crea un nuevo registro de libro en la base de datos.
*   **`delete_book(db: Session, book_id: int)`**: Elimina un libro por su ID, borrando también los archivos de libro y portada asociados del disco.
*   **`delete_books_by_category(db: Session, category: str)`**: Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados del disco.
*   **`get_books_count(db: Session) -> int`**: Obtiene el número total de libros.

### `backend/database.py`

Configura la conexión a la base de datos SQLite y las utilidades de SQLAlchemy.

*   `_db_path`: Ruta absoluta al archivo `library.db` en la raíz del proyecto.
*   `SQLALCHEMY_DATABASE_URL`: URL de conexión a la base de datos SQLite. `check_same_thread=False` es necesario para SQLite con FastAPI en múltiples hilos.
*   `engine`: Objeto `Engine` de SQLAlchemy, el punto de entrada a la base de datos.
*   `SessionLocal`: Una fábrica de sesiones configurada para no autocomitear ni auto-vaciar.
*   `Base`: La clase base declarativa para los modelos de SQLAlchemy.

### `backend/utils.py`

Contiene funciones de utilidad.

*   **`configure_genai()`**
    *   **Propósito:** Configura la API de Google Gemini utilizando una clave de API obtenida de las variables de entorno (`GOOGLE_API_KEY` o `GEMINI_API_KEY`).
    *   **Lógica:** Carga variables de entorno y si no encuentra ninguna clave, lanza un `ValueError`. Si encuentra una, configura el SDK de `google.generativeai`.

### `backend/rag.py`

Implementa la lógica central del sistema Retrieval Augmented Generation (RAG).

**Variables Globales y Configuración:**

*   `EMBEDDING_MODEL`: Modelo de Gemini utilizado para generar embeddings (configurable via `GEMINI_EMBEDDING_MODEL`).
*   `GENERATION_MODEL`: Modelo de Gemini utilizado para la generación de texto (configurable via `GEMINI_GENERATION_MODEL`).

**Funciones Principales:**

*   **`_ensure_init()`**: Inicializa las dependencias de RAG (Gemini, ChromaDB). Se ejecuta de forma lazy para asegurar que las variables de entorno estén cargadas y que la AI pueda ser deshabilitada para tests.
*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**:
    *   **Propósito:** Genera el embedding vectorial de un texto dado utilizando el modelo de embedding de Gemini.
    *   **Lógica:** Llama a `genai.embed_content`. Si la IA está deshabilitada (por `DISABLE_AI` env var), devuelve un embedding dummy.
*   **`extract_text_from_pdf(file_path: str) -> str`**: Extrae texto de un archivo PDF usando `PyPDF2`.
*   **`extract_text_from_epub(file_path: str) -> str`**: Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`.
*   **`extract_text(file_path: str) -> str`**: Función unificada para extraer texto de PDF o EPUB.
*   **`chunk_text(text: str, max_tokens: int = 1000) -> list[str]`**:
    *   **Propósito:** Divide un texto largo en fragmentos más pequeños, adecuados para la generación de embeddings, basándose en un recuento de tokens.
    *   **Lógica:** Utiliza `tiktoken` (tokenizer de GPT-3.5) como aproximación para el conteo de tokens, dividiendo el texto para evitar exceder los límites de tamaño del modelo de embedding.
*   **`_has_index_for_book(book_id: str) -> bool`**: Comprueba si ya existen vectores para un `book_id` dado en ChromaDB.
*   **`delete_book_from_rag(book_id: str)`**: Elimina todos los embeddings asociados a un `book_id` de ChromaDB.
*   **`get_index_count(book_id: str) -> int`**: Devuelve el número de vectores almacenados para un `book_id`.
*   **`has_index(book_id: str) -> bool`**: Alias público para `get_index_count(book_id) > 0`.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**:
    *   **Propósito:** Procesa un archivo de libro para RAG: extrae texto, lo divide en chunks, genera embeddings y los almacena en ChromaDB.
    *   **Lógica:** Realiza la extracción de texto, chunking y generación de embeddings. Para cada chunk, añade el embedding y los metadatos (`book_id`, `chunk_index`) a ChromaDB. Permite la reindexación forzada.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`**: Estima el número de tokens y chunks para un solo archivo.
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`**: Estima el número total de tokens y chunks para una lista de archivos.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**:
    *   **Propósito:** Realiza una consulta al sistema RAG, recuperando información relevante y generando una respuesta contextualizada.
    *   **Lógica:**
        1.  Genera un embedding de la consulta del usuario.
        2.  Busca los chunks más relevantes en ChromaDB para el `book_id` dado.
        3.  Combina los chunks recuperados con metadatos del libro y contexto de la biblioteca (si se proporcionan).
        4.  Construye un prompt para el modelo de generación de Gemini, incluyendo el contexto recuperado y las preferencias de `mode` (strict, balanced, open).
        5.  Llama al modelo de Gemini para generar la respuesta.
    *   **Parámetros:**
        *   `query` (str): La pregunta del usuario.
        *   `book_id` (str): El ID del libro objetivo.
        *   `mode` (str): Define la estrategia de respuesta:
            *   `strict`: Solo respuestas del libro.
            *   `balanced`: Prioriza el libro, complementa con conocimiento general (marcado como "Nota:").
            *   `open`: Integra libremente, priorizando el libro.
        *   `metadata` (dict | None): Información adicional sobre el libro (título, autor, categoría).
        *   `library` (dict | None): Contexto de la biblioteca (e.g., otras obras del autor).
    *   **Retorno:** La respuesta generada por el modelo de Gemini.

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

Script de migración de Alembic para la creación inicial de la tabla `books`.

*   `upgrade()`: Crea la tabla `books` con columnas `id`, `title`, `author`, `category`, `cover_image_url`, `file_path`, estableciendo `id` como clave primaria y `file_path` como única. También crea índices en `id`, `title`, `author` y `category`.
*   `downgrade()`: Elimina la tabla `books` y sus índices.

### `backend/__init__.py`

Archivo de inicialización del paquete, actualmente vacío, pero necesario para que Python reconozca `backend` como un paquete.

## 4. Análisis Detallado del Frontend (React)

El frontend proporciona la interfaz de usuario interactiva para la aplicación.

### `frontend/src/App.js`

El componente raíz de la aplicación React.

*   **Propósito:** Configura el enrutamiento de la aplicación utilizando `react-router-dom` y renderiza el `Header` y el contenido de la ruta actual.
*   **Estado:** Ninguno directamente.
*   **Props:** Ninguna.
*   **Efectos Secundarios:** Ninguno directamente, su función principal es envolver el enrutamiento.
*   **Interacciones:** Dirige la navegación a través de las diferentes vistas de la aplicación.

### `frontend/src/Header.js`

El componente de la barra de navegación superior.

*   **Propósito:** Proporciona enlaces de navegación a las diferentes secciones de la aplicación y muestra el número total de libros en la biblioteca.
*   **Estado:**
    *   `menuOpen` (boolean): Controla la visibilidad del menú de hamburguesa en dispositivos móviles.
    *   `bookCount` (number): Número total de libros en la biblioteca.
    *   `errorMessage` (string | null): Mensaje de error si falla la carga del contador de libros.
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useEffect`: Realiza una llamada a la API (`GET /books/count`) al montar el componente y luego periódicamente (cada 10 minutos) para actualizar el contador de libros.
*   **Interacciones:**
    *   Los enlaces `NavLink` permiten la navegación entre las vistas.
    *   Un botón de hamburguesa (`hamburger-menu`) alterna la visibilidad del menú en pantallas pequeñas.

### `frontend/src/LibraryView.js`

La vista principal de la biblioteca, muestra un listado de libros.

*   **Propósito:** Muestra los libros disponibles en la biblioteca en una cuadrícula, permitiendo buscar, filtrar por autor/categoría y realizar acciones como descargar/leer o eliminar libros.
*   **Estado:**
    *   `books` (array): Lista de objetos libro obtenidos del backend.
    *   `searchParams` (URLSearchParams): Objeto para gestionar los parámetros de búsqueda en la URL.
    *   `searchTerm` (string): Término de búsqueda introducido por el usuario en la barra de búsqueda general.
    *   `debouncedSearchTerm` (string): Versión *debounced* de `searchTerm` para evitar peticiones API excesivas.
    *   `error` (string): Mensaje de error si falla la carga o eliminación de libros.
    *   `loading` (boolean): Indica si la lista de libros está cargando.
    *   `isMobile` (boolean): Detecta si el dispositivo es móvil para adaptar la interfaz (ej. botones de descarga).
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useEffect` (para `isMobile`): Se ejecuta al montar el componente y en cada redimensionamiento de la ventana para detectar si el dispositivo es móvil.
    *   `useEffect` (para `debouncedSearchTerm`, `searchParams`): `fetchBooks` se ejecuta cada vez que el término de búsqueda *debounced* o los parámetros de URL (categoría, autor) cambian.
*   **Funciones Principales:**
    *   `useDebounce(value, delay)`: Hook personalizado para retrasar la actualización de un valor, útil para búsquedas.
    *   `BookCover({ src, alt, title })`: Componente funcional para renderizar la portada de un libro, con un *fallback* a una portada genérica si la imagen no carga o no está disponible.
    *   `handleAuthorClick(author)`: Establece el parámetro de URL `author` y borra `searchTerm` para filtrar por autor.
    *   `handleCategoryClick(category)`: Establece el parámetro de URL `category` para filtrar por categoría.
    *   `fetchBooks()`: Realiza la llamada a la API (`GET /books/`) con los parámetros de búsqueda/filtrado actuales.
    *   `handleDeleteBook(bookId)`: Llama a la API (`DELETE /books/{book_id}`) para eliminar un libro tras confirmación.
*   **Interacciones:**
    *   Barra de búsqueda: Permite buscar libros por título, autor o categoría.
    *   Clic en autor/categoría: Filtra la vista de la biblioteca.
    *   Botones en tarjetas de libro: "Abrir PDF" (abre en nueva pestaña), "Leer EPUB" (navega a `ReaderView`), "Descargar PDF/EPUB" (para móviles) y "Eliminar libro".

### `frontend/src/UploadView.js`

La vista para subir nuevos libros.

*   **Propósito:** Permite a los usuarios seleccionar y subir uno o varios archivos de libros (PDF o EPUB) al servidor para que sean procesados y añadidos a la biblioteca.
*   **Estado:**
    *   `filesToUpload` (array): Lista de objetos con información sobre los archivos seleccionados (`file`, `status`, `message`).
    *   `isUploading` (boolean): Indica si hay una subida en curso.
*   **Props:** Ninguna.
*   **Efectos Secundarios:** Ninguno directamente.
*   **Funciones Principales:**
    *   `handleFileChange(event)`: Añade los archivos seleccionados del input a `filesToUpload`.
    *   `handleDrop(event)`: Gestiona el arrastre y suelta de archivos en la zona designada.
    *   `handleDragOver(event)`: Evita el comportamiento por defecto del navegador para el arrastre.
    *   `updateFileStatus(index, status, message)`: Actualiza el estado y mensaje de un archivo específico en la lista `filesToUpload`.
    *   `handleUpload()`: Itera sobre `filesToUpload`, envía cada archivo al backend (`POST /upload-book/`) y actualiza su estado (subiendo, éxito, error).
*   **Interacciones:**
    *   Área de arrastre o botón "Seleccionar Archivos": Permite añadir archivos.
    *   Botón "Subir Archivo(s)": Inicia el proceso de subida y análisis.
    *   Indicadores de estado: Muestran el progreso y resultado de cada archivo.
    *   Botón "Ir a la Biblioteca": Aparece cuando todas las subidas han terminado.

### `frontend/src/ToolsView.js`

Una vista que agrupa herramientas adicionales, actualmente solo un conversor de EPUB a PDF.

*   **Propósito:** Proporcionar acceso a utilidades prácticas de la biblioteca.
*   **Estado:** Ninguno a nivel de `ToolsView`.
*   **Props:** Ninguna.
*   **Efectos Secundarios:** Ninguno.
*   **Interacciones:** Renderiza subcomponentes de herramientas.

#### `EpubToPdfConverter` (sub-componente dentro de `ToolsView.js`)

*   **Propósito:** Permite al usuario subir un archivo EPUB y convertirlo a PDF a través del backend.
*   **Estado:**
    *   `selectedFile` (File | null): El archivo EPUB seleccionado para la conversión.
    *   `message` (string): Mensajes de estado para el usuario (instrucciones, errores, éxito).
    *   `isLoading` (boolean): Indica si la conversión está en progreso.
*   **Props:** Ninguna.
*   **Efectos Secundarios:** Ninguno.
*   **Funciones Principales:**
    *   `handleFileChange(event)`: Almacena el archivo seleccionado.
    *   `handleDrop(event)`, `handleDragOver(event)`: Funcionalidad de arrastrar y soltar.
    *   `handleConvert()`:
        1.  Valida que se haya seleccionado un archivo EPUB.
        2.  Envía el archivo al backend (`POST /tools/convert-epub-to-pdf`).
        3.  Si es exitoso, obtiene la `download_url` del PDF del backend y simula un clic en un enlace oculto para iniciar la descarga en el navegador.
        4.  Muestra mensajes de estado y errores.
*   **Interacciones:**
    *   Área de arrastre o botón "Seleccionar archivo": Para elegir un EPUB.
    *   Botón "Convertir a PDF": Inicia la conversión.
    *   Mensajes: Informan sobre el proceso y el resultado.

### `frontend/src/ReaderView.js`

La vista para leer libros EPUB directamente en el navegador.

*   **Propósito:** Permite a los usuarios leer libros EPUB utilizando el componente `react-reader`.
*   **Estado:**
    *   `location` (string | null): La ubicación actual dentro del EPUB (CFI), para mantener el progreso de lectura.
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB, cargados desde el backend.
    *   `isLoading` (boolean): Indica si el libro se está cargando.
    *   `error` (string): Mensaje de error si el libro no puede cargarse.
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useEffect` (para `bookId`): Al montar el componente o cambiar `bookId`, llama a la API (`GET /books/download/{bookId}`) para obtener los datos binarios del EPUB.
*   **Interacciones:**
    *   Navegación dentro del libro: `react-reader` gestiona los clics para avanzar/retroceder páginas.
    *   `locationChanged` (callback): Actualiza el estado `location` con la posición actual de lectura.

### `frontend/src/RagView.js`

La vista para interactuar con la funcionalidad de "Charla sobre libros con la IA".

*   **Propósito:** Permite a los usuarios seleccionar un libro de su biblioteca, indexarlo para RAG (si no lo está) y luego conversar con la IA sobre su contenido.
*   **Estado:**
    *   `message` (string): Mensajes de información o error para el usuario.
    *   `isLoading` (boolean): Indica si la IA está generando una respuesta.
    *   `bookId` (string | null): El ID del libro actualmente seleccionado para la conversación RAG.
    *   `chatHistory` (array): Historial de la conversación (preguntas del usuario y respuestas de Gemini).
    *   `currentQuery` (string): La pregunta actual que el usuario está escribiendo.
    *   `libraryBooks` (array): Lista de todos los libros en la biblioteca para selección.
    *   `selectedLibraryId` (string): ID del libro seleccionado en el buscador de la biblioteca.
    *   `libStatus` (object): Objeto con el estado del índice RAG para el libro seleccionado (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy` (boolean): Bloquea los botones de indexación/reindexación mientras se procesa.
    *   `refreshing` (boolean): Indica que se está refrescando el estado RAG (no bloquea el chat).
    *   `searchTerm` (string): Término de búsqueda para buscar libros en la biblioteca.
    *   `searching` (boolean): Indica si se está realizando una búsqueda de libros.
    *   `searchResults` (array): Resultados de la búsqueda de libros.
    *   `resultsOpen` (boolean): Controla la visibilidad de los resultados de búsqueda.
    *   `mode` (string): Modo de conversación RAG (`strict`, `balanced`, `open`).
    *   `selectedBook` (object | null): Objeto libro completo del seleccionado en el buscador.
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useEffect` (para `chatHistory`, `isLoading`): Auto-scroll al final del historial de chat.
    *   `useEffect` (inicial): Carga todos los libros de la biblioteca (`GET /books/`).
    *   `useEffect` (para `searchTerm`): Implementa un *debounce* para la barra de búsqueda de libros, llamando a la API (`GET /books/?search=...`).
    *   `useEffect` (para `selectedLibraryId`): Llama a `checkLibraryStatus()` cuando se selecciona un libro para actualizar su estado RAG.
*   **Funciones Principales:**
    *   `qNonEmpty(s)`: Comprueba si una cadena no está vacía después de recortar espacios.
    *   `chatReady`: Variable calculada que indica si el chat está listo para usarse.
    *   `currentBook`: Memoiza el libro actualmente en conversación.
    *   `focusChatInput()`: Intenta enfocar el input de texto del chat.
    *   `handleQuerySubmit(event)`:
        1.  Añade la pregunta del usuario al `chatHistory`.
        2.  Envía la consulta al backend (`POST /rag/query/`).
        3.  Añade la respuesta de la IA (o un error) al `chatHistory`.
    *   `checkLibraryStatus(silent = false)`: Llama a la API (`GET /rag/status/{book_id}`) para verificar el estado de indexación RAG de un libro y actualiza `libStatus`.
    *   `indexLibraryBook(force = false)`: Llama a la API (`POST /rag/index/{book_id}`) para iniciar el proceso de indexación RAG de un libro.
*   **Interacciones:**
    *   Buscador de libros: Permite encontrar y seleccionar un libro de la biblioteca.
    *   Botones de acción (Comprobar RAG, Indexar, Reindexar, Chatear): Gestionan el estado de indexación y el inicio de la conversación.
    *   Opciones de modo de respuesta (Solo libro, Equilibrado, Abierto): Permiten al usuario configurar cómo la IA debe usar el contexto del libro.
    *   Área de chat: Muestra el historial de la conversación.
    *   Input de texto y botón "Enviar": Para enviar preguntas a la IA.

### `frontend/src/config.js`

*   **Propósito:** Centraliza la URL base del backend para facilitar la configuración en diferentes entornos.
*   **Contenido:** `API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';`
    *   Permite definir la URL del API a través de una variable de entorno `REACT_APP_API_URL` (para producción) o usar `http://localhost:8001` como valor por defecto (para desarrollo).

### `frontend/src/CategoriesView.js`

*   **Propósito:** Muestra una lista de todas las categorías de libros únicas como enlaces.
*   **Estado:**
    *   `categories` (array): Lista de nombres de categorías obtenidos del backend.
    *   `error` (string): Mensaje de error si las categorías no pueden cargarse.
    *   `loading` (boolean): Indica si las categorías están cargando.
*   **Props:** Ninguna.
*   **Efectos Secundarios:**
    *   `useEffect`: Llama a la API (`GET /categories/`) al montar el componente para obtener la lista de categorías.
*   **Interacciones:**
    *   Cada categoría es un `Link` que al hacer clic redirige a `LibraryView`, filtrando los libros por esa categoría.

### `frontend/src/ErrorBoundary.js`

*   **Propósito:** Componente de React para capturar errores JavaScript en el árbol de componentes hijo que no son capturados por el mismo.
*   **Estado:**
    *   `hasError` (boolean): True si se ha detectado un error.
    *   `error` (Error | null): El objeto de error capturado.
*   **Props:** `children` (ReactNode).
*   **Funciones:**
    *   `static getDerivedStateFromError(error)`: Método estático para actualizar el estado cuando se lanza un error.
    *   `componentDidCatch(error, info)`: Para loguear información de errores en el console.
*   **Retorno:** Si hay un error, muestra un mensaje de error genérico. De lo contrario, renderiza los componentes hijos.

### `frontend/src/index.js`

*   **Propósito:** Punto de entrada de la aplicación React.
*   **Contenido:** Renderiza el componente `App` dentro de un `React.StrictMode` y gestiona `reportWebVitals`.

## 5. Flujo de Datos y API

La aplicación "Mi Librería Inteligente" orquesta el flujo de datos entre el frontend y el backend para ofrecer sus funcionalidades.

### Flujo de Carga/Ingestión de Libros

1.  **Frontend (`UploadView.js`):** El usuario selecciona uno o varios archivos (PDF o EPUB) a través de un input de archivo o arrastrando y soltando.
2.  **API (`POST /upload-book/`):** La vista `UploadView` envía cada archivo al backend como `multipart/form-data`.
3.  **Backend (`main.py`):**
    *   Recibe el archivo y lo guarda en el directorio `backend/books/`.
    *   Identifica el tipo de archivo (PDF/EPUB).
    *   Llama a `process_pdf` o `process_epub` para extraer el texto inicial del libro y, si es posible, una imagen de portada. La portada se guarda en `backend/static/covers/`.
    *   Llama a `analyze_with_gemini` con el texto extraído para obtener el título, autor y categoría.
    *   Si la IA logra identificar el título y el autor (o al menos uno de ellos), el libro se considera válido.
    *   Llama a `crud.create_book` para guardar los metadatos del libro (título, autor, categoría, URL de portada, ruta del archivo) en la base de datos SQLite (`library.db`).
    *   Si hay errores en el procesamiento (ej. IA no identifica metadatos), el archivo subido se elimina y se devuelve un error.
4.  **Frontend (`UploadView.js`):** Recibe la confirmación (o error) de la API y actualiza el estado de cada archivo en la interfaz de usuario.

### Flujo de Indexación RAG

1.  **Frontend (`RagView.js`):** El usuario selecciona un libro de su biblioteca mediante el buscador.
2.  **API (`GET /rag/status/{book_id}`):** El frontend consulta el estado de indexación RAG del libro seleccionado.
3.  **Backend (`rag.py`):** `get_index_count` comprueba en ChromaDB si existen ya embeddings para ese `book_id`.
4.  **Frontend (`RagView.js`):** Si el libro no está indexado, el usuario hace clic en "Indexar antes de charlar".
5.  **API (`POST /rag/index/{book_id}`):** El frontend envía la solicitud de indexación.
6.  **Backend (`main.py` -> `rag.py`):**
    *   `index_existing_book_for_rag` recupera la `file_path` del libro de la base de datos.
    *   Llama a `rag.process_book_for_rag` con la ruta del archivo y el `book_id` (el ID de BD).
    *   `rag.process_book_for_rag`:
        *   Extrae el texto completo del libro (PDF/EPUB).
        *   Divide el texto en `chunks` utilizando `chunk_text`.
        *   Para cada `chunk`, llama a `get_embedding` para generar un vector de embedding usando Gemini.
        *   Almacena el embedding, el texto original (`chunk`) y metadatos (`book_id`, `chunk_index`) en la base de datos vectorial ChromaDB (`rag_index/`).
7.  **Frontend (`RagView.js`):** Recibe la confirmación de indexación y habilita la interfaz de chat.

### Flujo de Consulta RAG

1.  **Frontend (`RagView.js`):** El usuario introduce una pregunta en el área de chat y selecciona un `mode` de respuesta.
2.  **API (`POST /rag/query/`):** El frontend envía la consulta (`query`, `book_id`, `mode`) al backend.
3.  **Backend (`main.py` -> `rag.py`):**
    *   `query_rag_endpoint` recupera los metadatos del libro (`title`, `author`, `category`) de la base de datos. Si el modo no es 'strict', también recupera otras obras del autor de la biblioteca para contextualizar.
    *   Llama a `rag.query_rag`.
    *   `rag.query_rag`:
        *   Genera un embedding de la `query` del usuario.
        *   Consulta ChromaDB para recuperar los `n_results` (ej. 5) `chunks` de texto más relevantes del libro.
        *   Construye un `prompt` para el modelo de generación de Gemini, incluyendo la `query`, los `relevant_chunks`, los metadatos del libro, el contexto de la biblioteca y las instrucciones basadas en el `mode` seleccionado.
        *   Envía el `prompt` a Gemini (`genai.GenerativeModel.generate_content`).
        *   Devuelve la respuesta generada por Gemini.
4.  **Frontend (`RagView.js`):** Recibe la respuesta de la IA y la añade al `chatHistory` en la interfaz.

### Flujo de Visualización y Descarga de Libros

1.  **Frontend (`LibraryView.js`):** El usuario navega por la biblioteca.
2.  **API (`GET /books/`):** `LibraryView` solicita la lista de libros al backend (posiblemente con filtros).
3.  **Backend (`crud.py`):** `get_books` consulta la base de datos y devuelve los metadatos de los libros.
4.  **Frontend (`LibraryView.js`):** Muestra los libros en la cuadrícula.
5.  **Acción del Usuario:**
    *   **"Abrir PDF" (desktop):** El navegador abre el PDF en una nueva pestaña usando la `FileResponse` del backend (`GET /books/download/{book_id}`).
    *   **"Descargar PDF/EPUB" (mobile):** El navegador descarga el archivo usando la `FileResponse` del backend.
    *   **"Leer EPUB":** Navega a `/leer/{bookId}`.
6.  **Frontend (`ReaderView.js`):** Al cargar, solicita el EPUB específico.
7.  **API (`GET /books/download/{book_id}`):** `ReaderView` solicita el archivo del libro al backend.
8.  **Backend (`main.py`):** Recupera la `file_path` del libro de la base de datos y devuelve el archivo como `FileResponse`.
9.  **Frontend (`ReaderView.js`):** Recibe los datos binarios del EPUB y los pasa al componente `ReactReader` para su visualización.

### Flujo de Conversión de EPUB a PDF

1.  **Frontend (`ToolsView.js`):** El usuario selecciona un archivo EPUB en la sección "Convertidor de EPUB a PDF".
2.  **API (`POST /tools/convert-epub-to-pdf`):** El frontend envía el archivo EPUB al backend.
3.  **Backend (`main.py`):**
    *   Recibe el archivo EPUB.
    *   Utiliza `zipfile` para descomprimir el EPUB en un directorio temporal.
    *   Analiza el archivo `.opf` para identificar el orden de los capítulos y los recursos (CSS, imágenes).
    *   Utiliza `weasyprint` para renderizar el contenido HTML de cada capítulo, aplicando estilos CSS, y los une en un único documento PDF.
    *   Guarda el PDF generado en el directorio `backend/temp_books/`.
    *   Devuelve una `ConversionResponse` con la `download_url` relativa al PDF temporal.
4.  **Frontend (`ToolsView.js`):** Recibe la `download_url` y simula un clic en un enlace oculto para iniciar la descarga del PDF en el navegador del usuario.

---

### Resumen de los principales Endpoints de la API

| Método | Endpoint                             | Descripción                                                                                                                                                                                                                     | Esquema de Entrada       | Esquema de Salida          |
| :----- | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------- | :------------------------- |
| `POST` | `/upload-book/`                      | Sube un archivo de libro (PDF/EPUB), lo analiza con IA y lo añade a la biblioteca.                                                                                                                                              | `UploadFile`             | `Book`                     |
| `GET`  | `/books/`                            | Obtiene una lista de libros, con filtros opcionales por `category`, `search` (título, autor, categoría) y `author`.                                                                                                          | -                        | `List[Book]`               |
| `GET`  | `/books/count`                       | Devuelve el número total de libros.                                                                                                                                                                                             | -                        | `int`                      |
| `GET`  | `/books/search/`                     | Busca libros por un `title` parcial, con paginación (`skip`, `limit`).                                                                                                                                                          | -                        | `List[Book]`               |
| `GET`  | `/categories/`                       | Obtiene una lista de todas las categorías únicas en la biblioteca.                                                                                                                                                              | -                        | `List[str]`                |
| `DELETE`| `/books/{book_id}`                   | Elimina un libro específico, sus archivos asociados y su índice RAG.                                                                                                                                                            | -                        | `dict` (mensaje)           |
| `DELETE`| `/categories/{category_name}`        | Elimina todos los libros de una categoría específica, sus archivos y sus índices RAG.                                                                                                                                           | -                        | `dict` (mensaje)           |
| `GET`  | `/books/download/{book_id}`          | Descarga o abre un archivo de libro específico.                                                                                                                                                                                 | -                        | `FileResponse`             |
| `POST` | `/tools/convert-epub-to-pdf`         | Convierte un archivo EPUB subido a PDF y devuelve una URL de descarga temporal para el PDF resultante.                                                                                                                          | `UploadFile`             | `ConversionResponse`       |
| `POST` | `/rag/upload-book/`                  | Sube un archivo de libro temporalmente y lo procesa para el sistema RAG. Retorna un `book_id` UUID para la conversación RAG.                                                                                                    | `UploadFile`             | `RagUploadResponse`        |
| `POST` | `/rag/query/`                        | Consulta al sistema RAG sobre el contenido de un libro específico utilizando una pregunta y un `mode` de respuesta.                                                                                                             | `RagQuery`               | `RagQueryResponse`         |
| `POST` | `/rag/index/{book_id}`               | Indexa un libro existente en la base de datos para RAG.                                                                                                                                                                         | Query param: `force` (bool) | `dict` (mensaje)           |
| `GET`  | `/rag/status/{book_id}`              | Devuelve el estado de indexación RAG de un libro (si está indexado y cuántos vectores tiene).                                                                                                                                   | -                        | `dict` (status)            |
| `POST` | `/rag/reindex/category/{category_name}`| Reindexa todos los libros de una categoría.                                                                                                                                                                                     | Query param: `force` (bool) | `dict` (processed, failed) |
| `POST` | `/rag/reindex/all`                   | Reindexa todos los libros de la biblioteca.                                                                                                                                                                                     | Query param: `force` (bool) | `dict` (processed, failed) |
| `GET`  | `/rag/estimate/book/{book_id}`       | Estima tokens/chunks/coste para indexar un libro.                                                                                                                                                                               | Query params: `per1k`, `max_tokens` | `dict` (estimation)        |
| `GET`  | `/rag/estimate/category/{category_name}`| Estima tokens/chunks/coste para indexar una categoría.                                                                                                                                                                          | Query params: `per1k`, `max_tokens` | `dict` (estimation)        |
| `GET`  | `/rag/estimate/all`                  | Estima tokens/chunks/coste para indexar toda la biblioteca.                                                                                                                                                                     | Query params: `per1k`, `max_tokens` | `dict` (estimation)        |
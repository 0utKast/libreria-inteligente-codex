# Documentación del Proyecto: Mi Librería Inteligente

Este documento detalla la arquitectura, estructura y funcionamiento de "Mi Librería Inteligente", una aplicación para la gestión y enriquecimiento de colecciones de libros digitales.

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web diseñada para ayudar a los usuarios a organizar, leer e interactuar con su colección de libros digitales (PDF y EPUB). La aplicación va más allá de un simple gestor de archivos, incorporando capacidades de inteligencia artificial para enriquecer la experiencia del usuario.

**Características principales:**

*   **Gestión de Biblioteca:** Sube, visualiza y organiza libros digitales.
*   **Análisis Inteligente:** Utiliza modelos de lenguaje de Google Gemini para extraer automáticamente el título, autor y categoría de los libros subidos.
*   **Conversión de Formato:** Herramienta para convertir archivos EPUB a PDF.
*   **Lectura Integrada:** Permite leer libros EPUB directamente en el navegador.
*   **Búsqueda y Filtrado:** Busca libros por título, autor o categoría.
*   **Interacción con IA (RAG):** Ofrece una funcionalidad de **Retrieval Augmented Generation (RAG)** que permite a los usuarios hacer preguntas sobre el contenido específico de sus libros, recibiendo respuestas contextualizadas generadas por IA.
*   **Edición de Metadatos:** Edita los detalles del libro y actualiza su portada.

**Arquitectura General:**

La aplicación sigue una arquitectura de microservicios con un enfoque de backend-frontend:

*   **Frontend (React.js):** Proporciona una interfaz de usuario interactiva y responsiva.
*   **Backend (FastAPI - Python):** Sirve como la API REST principal, gestionando la lógica de negocio, la interacción con la base de datos, el procesamiento de archivos y la integración con servicios de IA.
*   **Base de Datos (SQLite):** Utilizada para almacenar los metadatos de los libros.
*   **Almacenamiento de Archivos:** Los libros y las portadas se almacenan directamente en el sistema de archivos del servidor.
*   **IA/LLM (Google Gemini API):** Se utiliza para dos propósitos principales:
    *   **Extracción de Metadatos:** Analiza el texto inicial de los libros para sugerir título, autor y categoría.
    *   **RAG (Retrieval Augmented Generation):** Genera embeddings vectoriales de los contenidos de los libros y responde preguntas basándose en el contexto recuperado.
*   **Base de Datos Vectorial (ChromaDB):** Almacena los embeddings de los libros para la funcionalidad RAG, permitiendo una búsqueda semántica eficiente.
*   **Herramientas de Procesamiento:** Utiliza librerías como `weasyprint` para la conversión de EPUB a PDF, `fitz` (PyMuPDF) para el procesamiento de PDF y `ebooklib` para EPUB.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales, `backend` y `frontend`, reflejando la separación de preocupaciones entre el servidor y la interfaz de usuario.

```
.
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │       └── 1a2b3c4d5e6f_create_books_table.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── __init__.py
│   ├── rag.py
│   ├── schemas.py
│   ├── tests/
│   ├── tests_curated/
│   └── utils.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.css
│   │   ├── App.js
│   │   ├── CategoriesView.css
│   │   ├── CategoriesView.js
│   │   ├── config.js
│   │   ├── EditBookModal.css
│   │   ├── EditBookModal.js
│   │   ├── ErrorBoundary.js
│   │   ├── Header.css
│   │   ├── Header.js
│   │   ├── index.css
│   │   ├── index.js
│   │   ├── LibraryView.css
│   │   ├── LibraryView.js
│   │   ├── RagView.css
│   │   ├── RagView.js
│   │   ├── ReaderView.css
│   │   ├── ReaderView.js
│   │   ├── reportWebVitals.js
│   │   ├── ToolsView.css
│   │   ├── ToolsView.js
│   │   ├── UploadView.css
│   │   └── UploadView.js
│   ├── .env
│   ├── package.json
│   └── README.md
├── .env                  # Archivo de configuración de variables de entorno
├── library.db            # Base de datos SQLite (generada)
└── rag_index/            # Directorio de persistencia de ChromaDB (generado)
```

**Descripción de directorios y archivos clave:**

*   **`backend/`**: Contiene todo el código Python para la API y la lógica de negocio.
    *   **`alembic/`**: Directorio para las migraciones de base de datos (`alembic`).
    *   **`crud.py`**: Funciones para las operaciones CRUD (Create, Read, Update, Delete) con la base de datos.
    *   **`database.py`**: Configuración de la conexión a la base de datos (SQLite) y objetos de SQLAlchemy.
    *   **`main.py`**: Punto de entrada de FastAPI, define los endpoints y coordina las operaciones.
    *   **`models.py`**: Definición de los modelos de la base de datos (SQLAlchemy ORM).
    *   **`rag.py`**: Lógica para el sistema de RAG (Retrieval Augmented Generation).
    *   **`schemas.py`**: Modelos Pydantic para la validación de datos de entrada/salida de la API.
    *   **`tests/`**, **`tests_curated/`**: Pruebas unitarias para el backend.
    *   **`utils.py`**: Funciones de utilidad diversas (configuración de Gemini, conversión de EPUB a PDF, manejo de archivos).
*   **`frontend/`**: Contiene todo el código React para la interfaz de usuario.
    *   **`src/`**: Código fuente de la aplicación React.
        *   **`App.js`**: Componente principal de la aplicación, configura el enrutamiento.
        *   **`Header.js`**: Componente de navegación y cabecera.
        *   **`LibraryView.js`**: Vista principal de la librería, muestra los libros y permite interactuar con ellos.
        *   **`UploadView.js`**: Vista para subir nuevos libros.
        *   **`CategoriesView.js`**: Vista para explorar categorías de libros.
        *   **`ToolsView.js`**: Vista con herramientas adicionales, como el convertidor de EPUB a PDF.
        *   **`ReaderView.js`**: Componente para la lectura de libros EPUB.
        *   **`RagView.js`**: Componente para interactuar con la IA a través del sistema RAG.
        *   **`EditBookModal.js`**: Modal para editar los detalles de un libro.
        *   **`config.js`**: Configuración de la URL base de la API.
        *   **`ErrorBoundary.js`**: Componente para la gestión de errores en la interfaz de usuario.
        *   **`*.css`**: Archivos CSS para los estilos de los componentes.
*   **`.env`**: Archivo para definir variables de entorno, como las API keys de Google Gemini y la ruta de ChromaDB.
*   **`library.db`**: Base de datos SQLite donde se almacenan los metadatos de los libros.
*   **`rag_index/`**: Directorio donde ChromaDB persiste los índices vectoriales de los libros.

## 3. Análisis Detallado del Backend (Python/FastAPI)

Esta sección describe los archivos clave del backend, sus propósitos y las funciones/clases principales que contienen.

### `backend/main.py`

Este archivo es el corazón de la API REST. Contiene la configuración de FastAPI, los endpoints y la lógica de negocio de alto nivel para manejar solicitudes, procesar archivos, interactuar con la IA y la base de datos.

**Funciones y Clases principales:**

*   **`save_optimized_image(pix_or_bytes, target_path, is_pixmap: bool = True)`**:
    *   **Propósito:** Guarda una imagen (normalmente una portada) en una ruta especificada, optimizándola (redimensionando y comprimiendo) para reducir el tamaño y mejorar el rendimiento.
    *   **Parámetros:**
        *   `pix_or_bytes`: Un objeto `fitz.Pixmap` (para PDF) o `bytes` (para EPUB) que representa la imagen.
        *   `target_path`: Ruta completa donde se guardará la imagen.
        *   `is_pixmap`: Booleano que indica si `pix_or_bytes` es un `fitz.Pixmap`.
    *   **Retorno:** Ninguno.

*   **`get_safe_path(db_path: str) -> str`**:
    *   **Propósito:** Convierte una ruta de archivo almacenada en la base de datos (que puede ser relativa o absoluta) a una ruta absoluta en el sistema de archivos del servidor.
    *   **Parámetros:**
        *   `db_path`: Ruta del archivo como está almacenada en la base de datos.
    *   **Retorno:** La ruta absoluta del archivo.

*   **`get_relative_path(abs_path: str) -> str`**:
    *   **Propósito:** Convierte una ruta de archivo absoluta a una ruta relativa al directorio `backend`, que es el formato preferido para almacenar en la base de datos.
    *   **Parámetros:**
        *   `abs_path`: La ruta absoluta del archivo.
    *   **Retorno:** La ruta relativa.

*   **`analyze_with_gemini(text: str) -> dict`**:
    *   **Propósito:** Envía un fragmento de texto a la API de Google Gemini para que identifique el título, autor y categoría del libro. Utiliza un prompt específico para guiar la respuesta en formato JSON.
    *   **Parámetros:**
        *   `text`: El texto extraído de las primeras páginas del libro.
    *   **Retorno:** Un diccionario con las claves `title`, `author` y `category`. En caso de error o que la IA no pueda identificar, devuelve valores "Desconocido" o "Error de IA".

*   **`process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
    *   **Propósito:** Extrae texto de las primeras páginas de un archivo PDF y, si es posible, una imagen de portada.
    *   **Parámetros:**
        *   `file_path`: Ruta al archivo PDF.
        *   `covers_dir_fs`: Ruta absoluta al directorio donde se guardarán las portadas.
        *   `covers_url_prefix`: Prefijo URL para acceder a las portadas estáticas.
    *   **Retorno:** Un diccionario con el texto extraído y la URL de la portada (`cover_image_url`) si se encontró.

*   **`process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict`**:
    *   **Propósito:** Extrae texto de las primeras páginas de un archivo EPUB y una imagen de portada, utilizando lógicas de búsqueda robustas para la portada.
    *   **Parámetros:**
        *   `file_path`: Ruta al archivo EPUB.
        *   `covers_dir_fs`: Ruta absoluta al directorio donde se guardarán las portadas.
        *   `covers_url_prefix`: Prefijo URL para acceder a las portadas estáticas.
    *   **Retorno:** Un diccionario con el texto extraído y la URL de la portada (`cover_image_url`) si se encontró.

*   **`app = FastAPI(...)`**:
    *   **Propósito:** La instancia principal de la aplicación FastAPI, configurada con middleware CORS y directorios estáticos.

*   **`add_cache_headers(request, call_next)`**:
    *   **Propósito:** Middleware que añade cabeceras de caché (1 día) a las respuestas de archivos estáticos (`/static/`).

*   **`get_db()`**:
    *   **Propósito:** Función de dependencia para FastAPI que proporciona una sesión de base de datos a los endpoints y asegura que se cierre al finalizar la solicitud.

*   **`background_index_book(book_id: int, file_path: str)`**:
    *   **Propósito:** Tarea de segundo plano que inicia el proceso de indexación RAG para un libro.
    *   **Parámetros:**
        *   `book_id`: ID del libro en la base de datos.
        *   `file_path`: Ruta absoluta al archivo del libro.
    *   **Retorno:** Ninguno.

*   **Endpoints de la API:**

    *   **`POST /api/books/{book_id}/convert`**:
        *   **Propósito:** Convierte un libro EPUB existente de la biblioteca a formato PDF y lo añade como un nuevo libro, junto con su indexación RAG.
        *   **Parámetros (path):** `book_id` (int).
        *   **Lógica:** Lee el EPUB original, lo convierte a PDF, guarda el nuevo PDF, extrae metadatos con IA, crea un nuevo registro en BD y dispara la indexación RAG.
        *   **Retorno:** `schemas.Book` del nuevo libro PDF.

    *   **`POST /tools/convert-epub-to-pdf`**:
        *   **Propósito:** Herramienta para convertir un archivo EPUB subido a PDF y proporcionar un enlace de descarga temporal.
        *   **Parámetros (form):** `file` (UploadFile).
        *   **Lógica:** Convierte el EPUB a PDF, guarda el PDF en un directorio temporal y devuelve una URL para su descarga.
        *   **Retorno:** `{"download_url": str}`.

    *   **`POST /upload-book/`**:
        *   **Propósito:** Sube un nuevo libro (PDF o EPUB), lo procesa (extrae texto y portada), utiliza IA para identificar metadatos y lo guarda en la base de datos y el sistema de archivos. También inicia la indexación RAG.
        *   **Parámetros (form):** `book_file` (UploadFile).
        *   **Lógica:** Guarda el archivo, lo procesa con `process_pdf` o `process_epub`, analiza el texto con `analyze_with_gemini`, crea el libro en la BD con `crud.create_book` y dispara `background_index_book`.
        *   **Retorno:** `schemas.Book` del libro creado.

    *   **`GET /books/`**:
        *   **Propósito:** Recupera una lista paginada de libros, con opciones para filtrar por categoría, buscar por términos generales o por autor.
        *   **Parámetros (query):** `category` (str, opcional), `search` (str, opcional), `author` (str, opcional), `skip` (int), `limit` (int).
        *   **Retorno:** `List[schemas.Book]`.

    *   **`PUT /books/{book_id}`**:
        *   **Propósito:** Actualiza los detalles de un libro existente (título, autor y, opcionalmente, la portada).
        *   **Parámetros (path):** `book_id` (int). **(form):** `title` (str), `author` (str), `cover_image` (UploadFile, opcional).
        *   **Lógica:** Actualiza el libro en la BD con `crud.update_book`. Si se proporciona una nueva portada, la guarda y actualiza la URL.
        *   **Retorno:** `schemas.Book` del libro actualizado.

    *   **`GET /books/count`**:
        *   **Propósito:** Devuelve el número total de libros en la biblioteca.
        *   **Retorno:** `int`.

    *   **`GET /books/search/`**:
        *   **Propósito:** Busca libros por un título parcial.
        *   **Parámetros (query):** `title` (str), `skip` (int), `limit` (int).
        *   **Retorno:** `List[schemas.Book]`.

    *   **`GET /categories/`**:
        *   **Propósito:** Devuelve una lista de todas las categorías de libros únicas presentes en la biblioteca.
        *   **Retorno:** `List[str]`.

    *   **`DELETE /books/{book_id}`**:
        *   **Propósito:** Elimina un libro de la base de datos y sus archivos asociados (libro y portada). También intenta limpiar su índice RAG.
        *   **Parámetros (path):** `book_id` (int).
        *   **Retorno:** `{"message": str}`.

    *   **`DELETE /categories/{category_name}`**:
        *   **Propósito:** Elimina todos los libros asociados a una categoría específica, incluyendo sus archivos y sus índices RAG.
        *   **Parámetros (path):** `category_name` (str).
        *   **Retorno:** `{"message": str}`.

    *   **`GET /books/download/{book_id}`**:
        *   **Propósito:** Permite descargar o abrir un libro del servidor. Determina el tipo de contenido y el nombre de archivo.
        *   **Parámetros (path):** `book_id` (int).
        *   **Retorno:** `FileResponse`.

    *   **`POST /rag/upload-book/`**:
        *   **Propósito:** (Principalmente para pruebas/uso interno) Sube y procesa un libro para indexación RAG sin añadirlo a la biblioteca principal.
        *   **Parámetros (form):** `file` (UploadFile).
        *   **Retorno:** `schemas.RagUploadResponse`.

    *   **`POST /rag/query/`**:
        *   **Propósito:** Realiza una consulta al sistema RAG para obtener una respuesta contextualizada basada en el contenido de un libro.
        *   **Parámetros (body):** `schemas.RagQuery` (`query`, `book_id`, `mode`).
        *   **Retorno:** `schemas.RagQueryResponse`.

    *   **`POST /rag/index/{book_id}`**:
        *   **Propósito:** Inicia o fuerza la reindexación en RAG de un libro ya existente en la base de datos.
        *   **Parámetros (path):** `book_id` (int). **(query):** `force` (bool, opcional).
        *   **Retorno:** `{"message": str, "book_id": str, "force": bool}`.

    *   **`GET /rag/status/{book_id}`**:
        *   **Propósito:** Devuelve el estado de indexación RAG de un libro (si está indexado y cuántos vectores tiene).
        *   **Parámetros (path):** `book_id` (int).
        *   **Retorno:** `{"book_id": str, "indexed": bool, "vector_count": int}`.

    *   **`POST /rag/reindex/category/{category_name}`**:
        *   **Propósito:** (Re)indexa todos los libros de una categoría específica en RAG.
        *   **Parámetros (path):** `category_name` (str). **(query):** `force` (bool, opcional).
        *   **Retorno:** `{"category": str, "processed": int, "failed": list, "force": bool}`.

    *   **`POST /rag/reindex/all`**:
        *   **Propósito:** (Re)indexa todos los libros de la biblioteca en RAG.
        *   **Parámetros (query):** `force` (bool, opcional).
        *   **Retorno:** `{"processed": int, "failed": list, "total": int, "force": bool}`.

    *   **`GET /rag/estimate/book/{book_id}`**:
        *   **Propósito:** Estima el número de tokens y chunks para un libro, y un coste opcional.
        *   **Parámetros (path):** `book_id` (int). **(query):** `per1k` (float, opcional), `max_tokens` (int, opcional).
        *   **Retorno:** `{"book_id": str, "tokens": int, "chunks": int, "per1k": float, "estimated_cost": float}`.

    *   **`GET /rag/estimate/category/{category_name}`**:
        *   **Propósito:** Estima el número total de tokens y chunks para todos los libros de una categoría, y un coste opcional.
        *   **Parámetros (path):** `category_name` (str). **(query):** `per1k` (float, opcional), `max_tokens` (int, opcional).
        *   **Retorno:** `{"category": str, "tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float}`.

    *   **`GET /rag/estimate/all`**:
        *   **Propósito:** Estima el número total de tokens y chunks para todos los libros de la biblioteca, y un coste opcional.
        *   **Parámetros (query):** `per1k` (float, opcional), `max_tokens` (int, opcional).
        *   **Retorno:** `{"tokens": int, "chunks": int, "files": int, "per1k": float, "estimated_cost": float}`.

### `backend/utils.py`

Este archivo contiene un conjunto de funciones de utilidad genéricas utilizadas por el backend.

**Funciones principales:**

*   **`configure_genai()`**:
    *   **Propósito:** Carga las variables de entorno (`GOOGLE_API_KEY` o `GEMINI_API_KEY`) y configura el SDK de Google Generative AI. Lanza un `ValueError` si no se encuentra ninguna clave.
    *   **Parámetros:** Ninguno.
    *   **Retorno:** Ninguno.

*   **`get_gemini_model(model_name: str = "gemini-pro")`**:
    *   **Propósito:** Devuelve una instancia del modelo Gemini especificado.
    *   **Parámetros:**
        *   `model_name`: Nombre del modelo Gemini a utilizar.
    *   **Retorno:** Una instancia de `genai.GenerativeModel`.

*   **`generate_text_from_prompt(prompt: str, model_name: str = "gemini-pro")`**:
    *   **Propósito:** Genera texto utilizando el modelo Gemini configurado y un prompt dado.
    *   **Parámetros:**
        *   `prompt`: El prompt de texto para la generación.
        *   `model_name`: Nombre del modelo Gemini a utilizar.
    *   **Retorno:** El texto generado por el modelo, o un mensaje de error si ocurre una excepción.

*   **`get_file_extension(filename: str) -> str`**:
    *   **Propósito:** Extrae la extensión de un nombre de archivo y la devuelve en minúsculas.
    *   **Parámetros:**
        *   `filename`: El nombre del archivo.
    *   **Retorno:** La extensión del archivo (ej. `.pdf`, `.epub`).

*   **`is_allowed_file(filename: str, allowed_extensions: set) -> bool`**:
    *   **Propósito:** Comprueba si un archivo tiene una de las extensiones permitidas.
    *   **Parámetros:**
        *   `filename`: El nombre del archivo.
        *   `allowed_extensions`: Un conjunto de extensiones permitidas (ej. `{'.pdf', '.epub'}`).
    *   **Retorno:** `True` si la extensión es permitida, `False` en caso contrario.

*   **`convert_epub_bytes_to_pdf_bytes(epub_content: bytes) -> bytes`**:
    *   **Propósito:** Convierte el contenido binario de un archivo EPUB a contenido binario de un archivo PDF. Esta es una función compleja que implica la extracción del contenido del EPUB, el análisis de su estructura (OPF, CSS, HTML) y la renderización a PDF utilizando `weasyprint`.
    *   **Parámetros:**
        *   `epub_content`: Los bytes del archivo EPUB.
    *   **Retorno:** Los bytes del archivo PDF generado.

### `backend/database.py`

Este archivo se encarga de configurar la conexión a la base de datos para SQLAlchemy.

**Variables y Objetos principales:**

*   **`SQLALCHEMY_DATABASE_URL`**:
    *   **Propósito:** Define la cadena de conexión para la base de datos. En este caso, apunta a una base de datos SQLite llamada `library.db` ubicada en la raíz del proyecto.
*   **`engine`**:
    *   **Propósito:** El objeto `Engine` de SQLAlchemy, que es el punto de conexión principal entre la aplicación y la base de datos.
*   **`SessionLocal`**:
    *   **Propósito:** Una clase `sessionmaker` de SQLAlchemy, utilizada para crear instancias de `Session` (el "área de preparación" para los objetos de la base de datos) en el código.
*   **`Base`**:
    *   **Propósito:** La clase base declarativa de SQLAlchemy, de la cual heredarán todos los modelos de la base de datos.

### `backend/models.py`

Este archivo define los modelos de la base de datos utilizando el ORM de SQLAlchemy.

**Clases principales:**

*   **`class Book(Base)`**:
    *   **Propósito:** Representa la tabla `books` en la base de datos y define su esquema.
    *   **Columnas:**
        *   `id`: `Integer`, clave primaria, indexada. Identificador único para cada libro.
        *   `title`: `String`, indexada. Título del libro.
        *   `author`: `String`, indexada. Autor del libro.
        *   `category`: `String`, indexada. Categoría a la que pertenece el libro.
        *   `cover_image_url`: `String`, `nullable=True`. URL relativa a la imagen de portada del libro.
        *   `file_path`: `String`, `unique=True`. Ruta relativa al archivo real del libro en el sistema de archivos.

### `backend/crud.py`

Este archivo contiene las funciones de Create, Read, Update y Delete (CRUD) que interactúan directamente con la base de datos a través de SQLAlchemy.

**Funciones principales:**

*   **`get_abs_path(db_path: str) -> str`**:
    *   **Propósito:** Función auxiliar para resolver rutas de archivo almacenadas en la base de datos a rutas absolutas, similar a `main.get_safe_path`.
    *   **Parámetros:** `db_path` (ruta desde la base de datos).
    *   **Retorno:** Ruta absoluta.

*   **`get_book(db: Session, book_id: int)`**:
    *   **Propósito:** Recupera un libro por su ID.
    *   **Parámetros:** `db` (sesión de BD), `book_id` (ID del libro).
    *   **Retorno:** Objeto `models.Book` o `None`.

*   **`get_book_by_path(db: Session, file_path: str)`**:
    *   **Propósito:** Recupera un libro por su ruta de archivo única.
    *   **Parámetros:** `db` (sesión de BD), `file_path` (ruta del archivo).
    *   **Retorno:** Objeto `models.Book` o `None`.

*   **`get_book_by_title(db: Session, title: str)`**:
    *   **Propósito:** Recupera un libro por su título exacto.
    *   **Parámetros:** `db` (sesión de BD), `title` (título del libro).
    *   **Retorno:** Objeto `models.Book` o `None`.

*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`**:
    *   **Propósito:** Busca libros cuyo título contenga una subcadena (case-insensitive) y aplica paginación.
    *   **Parámetros:** `db`, `title`, `skip`, `limit`.
    *   **Retorno:** Lista de objetos `models.Book`.

*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None, skip: int = 0, limit: int = 20)`**:
    *   **Propósito:** Recupera una lista paginada de libros, con opciones de filtrado por categoría, autor, o un término de búsqueda general que coincide con título, autor o categoría.
    *   **Parámetros:** `db`, `category`, `search`, `author`, `skip`, `limit`.
    *   **Retorno:** Lista de objetos `models.Book`.

*   **`get_categories(db: Session) -> list[str]`**:
    *   **Propósito:** Recupera una lista de todas las categorías únicas de libros en la base de datos.
    *   **Parámetros:** `db`.
    *   **Retorno:** Lista de cadenas de texto (nombres de categorías).

*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`**:
    *   **Propósito:** Crea un nuevo registro de libro en la base de datos.
    *   **Parámetros:** `db`, `title`, `author`, `category`, `cover_image_url`, `file_path`.
    *   **Retorno:** El objeto `models.Book` recién creado.

*   **`delete_book(db: Session, book_id: int)`**:
    *   **Propósito:** Elimina un libro de la base de datos y también borra sus archivos asociados (el archivo del libro y la portada) del sistema de archivos.
    *   **Parámetros:** `db`, `book_id`.
    *   **Retorno:** El objeto `models.Book` eliminado o `None` si no se encontró.

*   **`delete_books_by_category(db: Session, category: str)`**:
    *   **Propósito:** Elimina todos los libros que pertenecen a una categoría específica, junto con sus archivos asociados.
    *   **Parámetros:** `db`, `category`.
    *   **Retorno:** El número de libros eliminados.

*   **`get_books_count(db: Session) -> int`**:
    *   **Propósito:** Devuelve el número total de libros almacenados en la base de datos.
    *   **Parámetros:** `db`.
    *   **Retorno:** Entero.

*   **`update_book(db: Session, book_id: int, title: str, author: str, cover_image_url: str | None)`**:
    *   **Propósito:** Actualiza el título, autor y opcionalmente la URL de la portada de un libro existente.
    *   **Parámetros:** `db`, `book_id`, `title`, `author`, `cover_image_url`.
    *   **Retorno:** El objeto `models.Book` actualizado o `None` si no se encontró.

### `backend/rag.py`

Este archivo implementa la funcionalidad de Retrieval Augmented Generation (RAG) utilizando Google Gemini y ChromaDB.

**Funciones principales:**

*   **`_ensure_init()`**:
    *   **Propósito:** Inicializa las dependencias globales como la configuración de Google Gemini y la conexión a ChromaDB. Se asegura de que ChromaDB persista su índice en el disco.
    *   **Parámetros:** Ninguno.
    *   **Retorno:** Ninguno.

*   **`async get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`**:
    *   **Propósito:** Genera un vector de embedding para un fragmento de texto dado utilizando el modelo de embeddings de Gemini. Se ejecuta de forma asíncrona.
    *   **Parámetros:**
        *   `text`: El texto para el que se generará el embedding.
        *   `task_type`: Tipo de tarea para el embedding (e.g., "RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY").
    *   **Retorno:** Una lista de flotantes que representa el vector de embedding.

*   **`extract_text_from_pdf(file_path: str) -> str`**:
    *   **Propósito:** Extrae todo el texto de un archivo PDF utilizando `PyPDF2`.
    *   **Parámetros:** `file_path`.
    *   **Retorno:** El texto extraído como una cadena de texto.

*   **`extract_text_from_epub(file_path: str) -> str`**:
    *   **Propósito:** Extrae todo el texto de un archivo EPUB, procesando su contenido HTML con `ebooklib` y `BeautifulSoup`.
    *   **Parámetros:** `file_path`.
    *   **Retorno:** El texto extraído como una cadena de texto.

*   **`extract_text(file_path: str) -> str`**:
    *   **Propósito:** Función unificada para extraer texto, detectando automáticamente si el archivo es PDF o EPUB.
    *   **Parámetros:** `file_path`.
    *   **Retorno:** El texto extraído.
    *   **Excepciones:** `ValueError` para tipos de archivo no soportados.

*   **`chunk_text(text: str, max_tokens: int = 1000) -> list[str]`**:
    *   **Propósito:** Divide un texto largo en fragmentos (chunks) más pequeños, asegurando que cada chunk no exceda un número máximo de tokens (utiliza `tiktoken` como aproximación).
    *   **Parámetros:**
        *   `text`: El texto a dividir.
        *   `max_tokens`: El número máximo de tokens por chunk.
    *   **Retorno:** Una lista de cadenas de texto, donde cada cadena es un chunk.

*   **`_has_index_for_book(book_id: str) -> bool`**:
    *   **Propósito:** Comprueba si ya existen vectores indexados en ChromaDB para un `book_id` dado.
    *   **Parámetros:** `book_id` (identificador del libro en RAG, que es el ID de la BD).
    *   **Retorno:** `True` si hay un índice, `False` en caso contrario.

*   **`delete_book_from_rag(book_id: str)`**:
    *   **Propósito:** Elimina todos los vectores y documentos asociados a un `book_id` de la colección de ChromaDB.
    *   **Parámetros:** `book_id`.
    *   **Retorno:** Ninguno.

*   **`get_index_count(book_id: str) -> int`**:
    *   **Propósito:** Devuelve el número de vectores (chunks) almacenados para un `book_id` específico en ChromaDB.
    *   **Parámetros:** `book_id`.
    *   **Retorno:** Entero.

*   **`has_index(book_id: str) -> bool`**:
    *   **Propósito:** Función auxiliar pública que utiliza `get_index_count` para verificar si un libro tiene un índice RAG.
    *   **Parámetros:** `book_id`.
    *   **Retorno:** `True` si tiene índice, `False` si no.

*   **`async process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`**:
    *   **Propósito:** Procesa un libro completo para el sistema RAG. Extrae el texto, lo divide en chunks, genera embeddings para cada chunk y los almacena en ChromaDB. Puede forzar la reindexación.
    *   **Parámetros:**
        *   `file_path`: Ruta al archivo del libro.
        *   `book_id`: ID del libro.
        *   `force_reindex`: Si es `True`, elimina los índices existentes antes de procesar.
    *   **Retorno:** Ninguno.

*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`**:
    *   **Propósito:** Estima el número total de tokens y el número de chunks que se generarían para un archivo específico, basándose en la estrategia de chunking.
    *   **Parámetros:** `file_path`, `max_tokens`.
    *   **Retorno:** Diccionario con `tokens` y `chunks`.

*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`**:
    *   **Propósito:** Estima el número total de tokens y chunks para una lista de archivos.
    *   **Parámetros:** `file_paths`, `max_tokens`.
    *   **Retorno:** Diccionario con `tokens`, `chunks` y `files`.

*   **`async query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`**:
    *   **Propósito:** Realiza una consulta al sistema RAG. Recupera los chunks más relevantes del libro para la pregunta del usuario, construye un prompt con este contexto y los metadatos opcionales, y lo envía a Gemini para generar una respuesta. Soporta diferentes `mode`s de respuesta.
    *   **Parámetros:**
        *   `query`: La pregunta del usuario.
        *   `book_id`: ID del libro sobre el que se pregunta.
        *   `mode`: Estrategia de respuesta de la IA ("strict", "balanced", "open").
        *   `metadata`: Diccionario opcional con metadatos del libro (título, autor, categoría).
        *   `library`: Diccionario opcional con contexto adicional de la biblioteca (otras obras del mismo autor).
    *   **Retorno:** La respuesta generada por Gemini.

### `backend/schemas.py`

Este archivo define los esquemas de datos utilizando Pydantic para la validación de entrada y serialización de salida en la API.

**Clases principales:**

*   **`class BookBase(BaseModel)`**:
    *   **Propósito:** Esquema base para un libro, conteniendo los atributos comunes.
    *   **Atributos:** `title` (str), `author` (str), `category` (str), `cover_image_url` (str | None), `file_path` (str).

*   **`class Book(BookBase)`**:
    *   **Propósito:** Esquema completo de un libro, extendiendo `BookBase` e incluyendo el `id` del libro. Utiliza `Config.from_attributes = True` para compatibilidad con SQLAlchemy.
    *   **Atributos:** `id` (int).

*   **`class ConversionResponse(BaseModel)`**:
    *   **Propósito:** Esquema para la respuesta de la conversión de EPUB a PDF.
    *   **Atributos:** `download_url` (str).

*   **`class RagUploadResponse(BaseModel)`**:
    *   **Propósito:** Esquema para la respuesta de la carga de un libro para RAG.
    *   **Atributos:** `book_id` (str), `message` (str).

*   **`class RagQuery(BaseModel)`**:
    *   **Propósito:** Esquema para la solicitud de una consulta RAG.
    *   **Atributos:** `query` (str), `book_id` (str), `mode` (str | None, con valores permitidos 'strict', 'balanced', 'open').

*   **`class RagQueryResponse(BaseModel)`**:
    *   **Propósito:** Esquema para la respuesta de una consulta RAG.
    *   **Atributos:** `response` (str).

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

Este archivo es una migración de Alembic que define los cambios en la estructura de la base de datos.

**Funciones principales:**

*   **`upgrade()`**:
    *   **Propósito:** Aplica los cambios de esquema para crear la tabla `books`. Define las columnas (`id`, `title`, `author`, `category`, `cover_image_url`, `file_path`), la clave primaria y los índices (`ix_books_author`, `ix_books_category`, `ix_books_id`, `ix_books_title`). También establece `file_path` como una restricción de unicidad.
    *   **Parámetros:** Ninguno.
    *   **Retorno:** Ninguno.

*   **`downgrade()`**:
    *   **Propósito:** Revierte los cambios de esquema, eliminando la tabla `books` y sus índices.
    *   **Parámetros:** Ninguno.
    *   **Retorno:** Ninguno.

## 4. Análisis Detallado del Frontend (React)

Esta sección describe los componentes principales de React, sus funcionalidades, estados y cómo interactúan con el usuario y el backend.

### `frontend/src/App.js`

El componente principal que configura el enrutamiento de la aplicación.

*   **Propósito:** Componente raíz de la aplicación. Utiliza `react-router-dom` para definir las rutas y cargar los componentes de vista correspondientes. Renderiza un `Header` en todas las páginas.
*   **Estado:** Ninguno directamente.
*   **Props:** Ninguna.
*   **Efectos:** Ninguno directamente.
*   **Interacciones:** Dirige la navegación de la aplicación a través de las rutas definidas.

### `frontend/src/Header.js`

La cabecera de la aplicación con navegación y contador de libros.

*   **Propósito:** Proporciona la barra de navegación principal de la aplicación, muestra el título del proyecto y un contador del número total de libros en la biblioteca. Incluye un menú de hamburguesa para la navegación móvil.
*   **Estado:**
    *   `menuOpen`: `boolean`, controla la visibilidad del menú de navegación en dispositivos móviles.
    *   `bookCount`: `number`, el número total de libros obtenidos del backend.
    *   `errorMessage`: `string | null`, para mostrar errores si la API falla al obtener el contador.
*   **Props:** Ninguna.
*   **Efectos:**
    *   `useEffect`: Realiza una solicitud `GET` a `${API_URL}/books/count` al montar el componente para obtener el número de libros. Se refresca periódicamente (cada 10 minutos) y también limpia cualquier error anterior.
*   **Interacciones:**
    *   El botón de menú hamburguesa (`&#9776;`) alterna el estado `menuOpen`.
    *   `NavLink`s: Permiten la navegación a las diferentes secciones de la aplicación (`/`, `/upload`, `/etiquetas`, `/herramientas`, `/rag`, etc.). Al hacer clic, cierran el menú en caso de estar abierto.

### `frontend/src/LibraryView.js`

La vista principal para explorar y gestionar la colección de libros.

*   **Propósito:** Muestra una cuadrícula de todos los libros de la biblioteca. Permite a los usuarios buscar, filtrar por autor o categoría, eliminar libros, convertir EPUBs a PDFs, editar los detalles de los libros y abrir/descargar archivos. Implementa un sistema de carga infinita para la visualización.
*   **Estado:**
    *   `books`: `array`, la lista de libros mostrados.
    *   `page`: `number`, el número de la página actual para la paginación de la carga infinita.
    *   `hasMore`: `boolean`, indica si hay más libros disponibles en el backend.
    *   `searchTerm`: `string`, el término de búsqueda actual del usuario.
    *   `debouncedSearchTerm`: `string`, versión con debounce del `searchTerm` para optimizar las llamadas a la API.
    *   `error`: `string`, mensaje de error si la carga de libros falla.
    *   `loading`: `boolean`, indica si se están cargando libros (ya sea la carga inicial o más en el scroll).
    *   `isMobile`: `boolean`, detecta si la vista se está mostrando en un dispositivo móvil.
    *   `editingBook`: `object | null`, almacena el libro que se está editando en el modal.
    *   `convertingId`: `number | null`, ID del libro que se está convirtiendo a PDF, para deshabilitar el botón y mostrar estado.
*   **Props:** Ninguna.
*   **Efectos:**
    *   `useEffect`: Ajusta el estado `isMobile` basándose en el ancho de la ventana.
    *   `useEffect`: Reinicia la lista de libros, la página y el estado `hasMore` cada vez que el `debouncedSearchTerm` o los `searchParams` (filtros de categoría/autor) cambian.
    *   `useEffect`: Función principal para obtener libros. Se ejecuta cuando `page`, `debouncedSearchTerm`, `searchParams` o `hasMore` cambian. Implementa un `IntersectionObserver` para detectar el scroll al final de la lista y cargar más libros. Envía una solicitud `GET` a `${API_URL}/books/` con parámetros de filtrado y paginación.
*   **Interacciones:**
    *   `handleAuthorClick(author)`: Establece los parámetros de búsqueda para filtrar por autor.
    *   `handleCategoryClick(category)`: Establece los parámetros de búsqueda para filtrar por categoría.
    *   `handleDeleteBook(bookId)`: Envía una solicitud `DELETE` a `${API_URL}/books/{bookId}` para eliminar un libro de la base de datos y sus archivos.
    *   `handleConvertToPdf(bookId)`: Envía una solicitud `POST` a `${API_URL}/api/books/{bookId}/convert` para convertir un EPUB a PDF. Añade el nuevo libro PDF a la lista si es exitoso.
    *   `handleEditClick(book)`: Abre el `EditBookModal` con los datos del libro seleccionado.
    *   `handleBookUpdated(updatedBook)`: Callback del modal de edición para actualizar el libro en el estado `books` después de guardar cambios.
    *   `BookCover` (componente interno): Muestra la portada del libro o un placeholder si no hay imagen o si falla la carga.
    *   `BookCard` (componente interno): Renderiza cada libro con su información y botones de acción. Muestra botones específicos para PDF/EPUB (abrir/leer/descargar). El botón de "Convertir a PDF" solo aparece para EPUBs que aún no tienen una versión PDF en la librería.
    *   `EditBookModal`: Se renderiza condicionalmente si `editingBook` no es `null`.

### `frontend/src/EditBookModal.js`

Modal para editar los detalles de un libro.

*   **Propósito:** Proporciona una interfaz modal para que el usuario edite el título y autor de un libro, y opcionalmente suba una nueva imagen de portada.
*   **Estado:**
    *   `title`: `string`, el título actual del libro en el formulario.
    *   `author`: `string`, el autor actual del libro en el formulario.
    *   `coverImage`: `File | null`, el archivo de imagen seleccionado para la nueva portada.
    *   `isSaving`: `boolean`, indica si el formulario está en proceso de guardar.
*   **Props:**
    *   `book`: `object`, el objeto libro cuyos detalles se van a editar.
    *   `onClose`: `function`, callback para cerrar el modal.
    *   `onBookUpdated`: `function`, callback para notificar a la vista padre cuando un libro ha sido actualizado exitosamente.
*   **Efectos:**
    *   `useEffect`: Se ejecuta cuando la prop `book` cambia para inicializar los estados `title` y `author` con los valores del libro.
*   **Interacciones:**
    *   `handleSubmit(e)`: Envía una solicitud `PUT` a `${API_URL}/books/{book.id}` con un `FormData` que contiene el título, autor y la nueva portada (si existe). Si es exitosa, llama a `onBookUpdated` y `onClose`.
    *   Botón "Cancelar": Llama a `onClose`.
    *   Input de tipo `file`: Actualiza el estado `coverImage`.

### `frontend/src/CategoriesView.js`

Vista para explorar las categorías de la biblioteca.

*   **Propósito:** Muestra una lista de todas las categorías únicas de libros disponibles en la biblioteca, permitiendo a los usuarios navegar a la `LibraryView` filtrando por una categoría específica.
*   **Estado:**
    *   `categories`: `array`, lista de cadenas de texto con los nombres de las categorías.
    *   `error`: `string`, mensaje de error si la carga de categorías falla.
    *   `loading`: `boolean`, indica si se están cargando las categorías.
*   **Props:** Ninguna.
*   **Efectos:**
    *   `useEffect`: Realiza una solicitud `GET` a `${API_URL}/categories/` al montar el componente para obtener la lista de categorías.
*   **Interacciones:**
    *   Cada `Link` de categoría: Al hacer clic, navega a la ruta raíz (`/`) añadiendo `?category={nombre_categoria}` a los `searchParams`, lo que activa el filtrado en `LibraryView`.

### `frontend/src/RagView.js`

Interfaz para interactuar con la IA sobre el contenido de los libros.

*   **Propósito:** Permite a los usuarios seleccionar un libro de su biblioteca, indexarlo para RAG (si no lo está ya) y luego interactuar con un chatbot de IA haciendo preguntas sobre su contenido. Ofrece diferentes modos de respuesta de la IA.
*   **Estado:**
    *   `message`: `string`, mensajes informativos para el usuario (estado de indexación, etc.).
    *   `isLoading`: `boolean`, indica si se está esperando una respuesta de la IA.
    *   `bookId`: `string | null`, el ID del libro actualmente indexado y activo para la conversación RAG.
    *   `chatHistory`: `array`, historial de mensajes en el chat (`{sender: 'user' | 'gemini', text: string}`).
    *   `currentQuery`: `string`, la pregunta actual del usuario en el input del chat.
    *   `libraryBooks`: `array`, la lista completa de libros de la biblioteca (para la búsqueda y selección).
    *   `selectedLibraryId`: `string`, el ID del libro seleccionado en la interfaz (no necesariamente el activo en el chat).
    *   `libStatus`: `object`, contiene el estado de indexación RAG del `selectedLibraryId` (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy`: `boolean`, bloquea los botones de indexación/reindexación mientras están en curso.
    *   `refreshing`: `boolean`, indica que se está refrescando el estado RAG del libro seleccionado.
    *   `searchTerm`: `string`, término para buscar libros en la lista desplegable.
    *   `searching`, `searchResults`, `resultsOpen`: Estados para la funcionalidad de búsqueda de libros en la biblioteca.
    *   `mode`: `string`, el modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`).
    *   `selectedBook`: `object | null`, el objeto libro seleccionado de la biblioteca (para mostrar título, autor, etc.).
*   **Props:** Ninguna.
*   **Efectos:**
    *   `useEffect`: Realiza una solicitud `GET` a `${API_URL}/books/` al montar el componente para obtener la lista de libros de la biblioteca.
    *   `useEffect`: Implementa un debounce para el `searchTerm` y realiza una búsqueda de libros por título/autor/categoría cada vez que cambia.
    *   `useEffect`: Se activa cuando `selectedLibraryId` cambia. Llama a `checkLibraryStatus` para obtener el estado de indexación RAG del libro seleccionado.
    *   `useEffect`: Implementa auto-scroll en el historial del chat cuando se añaden nuevos mensajes o mientras se espera una respuesta.
*   **Interacciones:**
    *   Input de búsqueda de libros: Actualiza `searchTerm` y `resultsOpen`. Los resultados de búsqueda se muestran en un `<ul>`.
    *   Clic en un resultado de búsqueda: Establece `selectedLibraryId`, `selectedBook` y rellena el input de búsqueda.
    *   Botones "Comprobar RAG", "Indexar antes de charlar", "Reindexar": Llaman a `checkLibraryStatus` o `indexLibraryBook` para gestionar la indexación RAG del libro seleccionado.
    *   Botón "Chatear": Si el libro seleccionado está indexado, establece `bookId` para activar la sección de chat y reinicia el historial.
    *   `handleQuerySubmit(event)`: Envía la `currentQuery` como una solicitud `POST` a `${API_URL}/rag/query/` con el `bookId` activo y el `mode` de respuesta. La respuesta de la IA se añade a `chatHistory`.
    *   Input de texto del chat: Actualiza `currentQuery` y ajusta dinámicamente su altura.
    *   Radio buttons para "Preferencia de respuesta": Actualizan el estado `mode`.

### `frontend/src/ToolsView.js`

Colección de herramientas adicionales para la biblioteca.

*   **Propósito:** Proporciona una sección para herramientas adicionales, actualmente un convertidor de EPUB a PDF.
*   **Estado:**
    *   `selectedFile`: `File | null`, el archivo EPUB que el usuario ha seleccionado para convertir.
    *   `message`: `string`, mensajes informativos sobre el estado de la conversión.
    *   `isLoading`: `boolean`, indica si la conversión está en curso.
*   **Props:** Ninguna.
*   **Efectos:** Ninguno directamente.
*   **Interacciones:**
    *   `handleFileChange(event)`: Actualiza `selectedFile` cuando el usuario elige un archivo.
    *   `handleDrop(event)`, `handleDragOver(event)`: Implementan la funcionalidad de arrastrar y soltar archivos para seleccionar el EPUB.
    *   `handleConvert()`: Si `selectedFile` es un EPUB, envía una solicitud `POST` a `${API_URL}/tools/convert-epub-to-pdf` con el archivo. Si la conversión es exitosa, el backend devuelve una URL de descarga, y el frontend crea un enlace temporal y simula un clic para iniciar la descarga.

### `frontend/src/ReaderView.js`

Componente para leer libros EPUB en el navegador.

*   **Propósito:** Permite a los usuarios leer libros EPUB directamente en la interfaz web utilizando la librería `react-reader`.
*   **Estado:**
    *   `location`: `string | null`, un identificador (EPUB CFI) que representa la posición actual del lector en el libro.
    *   `epubData`: `ArrayBuffer | null`, el contenido binario del archivo EPUB.
    *   `isLoading`: `boolean`, indica si el libro se está cargando.
    *   `error`: `string`, mensaje de error si el libro no se pudo cargar.
*   **Props:**
    *   `bookId` (obtenido de `useParams`): `string`, el ID del libro EPUB a cargar y leer.
*   **Efectos:**
    *   `useEffect`: Se ejecuta cuando `bookId` cambia. Realiza una solicitud `GET` a `${API_URL}/books/download/{bookId}` para obtener el contenido binario del EPUB. Si es exitoso, almacena el `ArrayBuffer` en `epubData`.
*   **Interacciones:**
    *   `locationChanged(epubcfi)`: Callback de `ReactReader` que se invoca cuando el usuario cambia de página o sección en el EPUB, actualizando el estado `location`.

### `frontend/src/config.js`

Archivo de configuración para la URL de la API.

*   **Propósito:** Define la URL base del backend de la API para que el frontend pueda realizar solicitudes correctamente.
*   **Variables:**
    *   `API_URL`: `string`, toma su valor de la variable de entorno `REACT_APP_API_URL` (definida en el `.env` del frontend) o utiliza `http://localhost:8001` como valor predeterminado.

### `frontend/src/ErrorBoundary.js`

Componente de límite de error para la UI.

*   **Propósito:** Componente de React que captura errores JavaScript en cualquier parte de su árbol de componentes hijo, registra esos errores y muestra una interfaz de usuario de respaldo en lugar de bloquear todo el árbol de componentes.
*   **Estado:**
    *   `hasError`: `boolean`, `true` si un error ha sido capturado.
    *   `error`: `Error | null`, el objeto de error capturado.
*   **Props:**
    *   `children`: Los componentes que este `ErrorBoundary` envuelve.
*   **Métodos del ciclo de vida:**
    *   `static getDerivedStateFromError(error)`: Actualiza el estado para que la próxima renderización muestre la UI de respaldo.
    *   `componentDidCatch(error, info)`: Registra la información del error en la consola.
*   **Interacciones:** Captura y muestra errores de forma pasiva al usuario.

## 5. Flujo de Datos y API

Esta sección describe cómo los datos se mueven a través de la aplicación y resume los endpoints clave del backend.

### Flujo de Carga de un Libro (PDF/EPUB)

1.  **Inicio en Frontend (`UploadView.js`):**
    *   El usuario selecciona uno o varios archivos (PDF o EPUB) mediante el input de archivo o arrastrando y soltando en la zona designada.
    *   Los archivos se añaden a una lista en el estado local, con un estado "pending".
    *   El usuario hace clic en el botón "Subir".

2.  **Solicitud al Backend:**
    *   Por cada archivo "pending", el frontend envía una solicitud `POST` a `/upload-book/`.
    *   El archivo se envía como `FormData` bajo la clave `book_file`.
    *   El estado del archivo en la UI cambia a "uploading".

3.  **Procesamiento en Backend (`main.py` -> `upload_book`):**
    *   **Guardado:** El archivo subido se guarda en el directorio `backend/books/`.
    *   **Detección de duplicados:** Se verifica si ya existe un libro con la misma ruta de archivo en la base de datos.
    *   **Extracción de contenido:** Dependiendo de la extensión (`.pdf` o `.epub`):
        *   `main.process_pdf()` o `main.process_epub()` se encarga de:
            *   Extraer un fragmento de texto de las primeras páginas del libro.
            *   Intentar extraer una imagen de portada y guardarla en `backend/static/covers/`, obteniendo su URL relativa.
    *   **Análisis con IA:**
        *   El texto extraído se pasa a `main.analyze_with_gemini()`.
        *   Este método invoca la API de Google Gemini para obtener el `title`, `author` y `category` del libro en formato JSON.
    *   **Control de Calidad IA:** Si la IA no logra identificar un título y autor confiables ("Desconocido"), el archivo subido se elimina y se retorna un error `HTTPException(422)`.
    *   **Almacenamiento en BD:** Si el análisis es exitoso, `crud.create_book()` se llama para crear un nuevo registro en la tabla `books` con los metadatos (título, autor, categoría, URL de portada, ruta de archivo).
    *   **Indexación RAG (segundo plano):** Se dispara una `BackgroundTasks` (`background_index_book`) para que `rag.process_book_for_rag()` procese el libro para el sistema RAG.

4.  **Indexación RAG (Asíncrona - `rag.py`):**
    *   `rag.process_book_for_rag()`:
        *   Extrae el texto completo del libro (`rag.extract_text()`).
        *   Divide el texto en fragmentos (chunks) utilizando `rag.chunk_text()`.
        *   Para cada chunk, `rag.get_embedding()` se invoca para generar un vector de embedding con el modelo de Google Gemini.
        *   Los chunks de texto y sus embeddings se almacenan en ChromaDB, asociados al `book_id`.

5.  **Respuesta al Frontend:**
    *   El backend envía una respuesta `200 OK` con los datos del nuevo libro (`schemas.Book`).
    *   El frontend actualiza el estado del archivo en la UI a "success" o "error" y muestra un mensaje relevante.
    *   Una vez que todos los archivos han sido procesados, la UI ofrece botones para ir a la biblioteca o subir más libros.

### Flujo de Conversión de EPUB a PDF (desde LibraryView)

1.  **Inicio en Frontend (`LibraryView.js`):**
    *   El usuario hace clic en el botón "PDF" junto a un libro EPUB.
    *   Una comprobación (`convertibilityMap`) asegura que no exista ya un PDF con el mismo nombre base.
    *   Se muestra una confirmación.

2.  **Solicitud al Backend:**
    *   El frontend envía una solicitud `POST` a `/api/books/{book_id}/convert`.
    *   Se marca el `convertingId` en el estado para indicar que la conversión está en curso.

3.  **Procesamiento en Backend (`main.py` -> `convert_book_to_pdf`):**
    *   **Recuperación del EPUB:** Se obtiene la ruta del EPUB original de la base de datos y se lee su contenido binario.
    *   **Conversión:** `utils.convert_epub_bytes_to_pdf_bytes()` se encarga de convertir el contenido binario del EPUB a contenido binario de un PDF.
    *   **Guardado del PDF:** El nuevo archivo PDF se guarda en el directorio `backend/books/`, con un nombre de archivo único si ya existía una colisión.
    *   **Procesamiento de Metadatos y RAG:** Similar al flujo de `upload-book/`:
        *   Se llama a `main.process_pdf()` para extraer texto y portada del PDF recién creado.
        *   `main.analyze_with_gemini()` se usa para extraer metadatos (título, autor, categoría). Si falla, se borra el PDF y se lanza un error.
        *   `crud.create_book()` registra el nuevo libro PDF en la base de datos.
        *   `background_index_book()` se dispara para indexar el PDF en RAG.

4.  **Respuesta al Frontend:**
    *   El backend envía una respuesta `200 OK` con los datos del **nuevo libro PDF** (`schemas.Book`).
    *   El frontend añade el nuevo libro PDF a la lista en `LibraryView` y lo ordena.
    *   Se muestra un mensaje de éxito al usuario.

### Flujo de Consulta RAG

1.  **Preparación en Frontend (`RagView.js`):**
    *   El usuario busca y selecciona un libro de la biblioteca.
    *   Se comprueba el estado RAG del libro (`GET /rag/status/{book_id}`).
    *   Si el libro no está indexado, el usuario lo indexa haciendo clic en "Indexar antes de charlar" (`POST /rag/index/{book_id}`).
    *   El usuario elige un "modo de respuesta" (strict, balanced, open).
    *   Una vez que el libro está indexado y seleccionado para el chat, el usuario escribe una pregunta en el input del chat.

2.  **Solicitud al Backend:**
    *   El frontend envía una solicitud `POST` a `/rag/query/`.
    *   El cuerpo de la solicitud es un objeto `schemas.RagQuery` que contiene `query` (la pregunta del usuario), `book_id` (el ID del libro) y `mode`.
    *   La UI muestra "Esperando respuesta..." en el chat.

3.  **Procesamiento en Backend (`main.py` -> `query_rag_endpoint` -> `rag.query_rag`):**
    *   **Embedding de la consulta:** `rag.get_embedding()` genera un vector de embedding para la `query` del usuario.
    *   **Recuperación de contexto:** ChromaDB (`_collection.query()`) se consulta con el embedding de la consulta y el `book_id` para recuperar los chunks de texto más relevantes del libro.
    *   **Construcción del prompt:** Se construye un prompt de Gemini que incluye:
        *   Las instrucciones de la IA (basadas en el `mode` seleccionado).
        *   Los chunks de texto recuperados como "Contexto del libro".
        *   Metadatos del libro (título, autor, categoría) si están disponibles.
        *   Contexto adicional de la biblioteca (ej. otros libros del mismo autor) si está disponible y el `mode` lo permite.
        *   La pregunta original del usuario.
    *   **Generación de respuesta:** El prompt se envía al modelo de generación de Gemini (`genai.GenerativeModel(GENERATION_MODEL).generate_content_async()`).
    *   **Respuesta al Frontend:** La respuesta generada por Gemini se devuelve.

4.  **Visualización en Frontend:**
    *   La respuesta de la IA se añade al `chatHistory` y se muestra en la interfaz.

### Endpoints Principales de la API

La API del backend está definida en `backend/main.py` y expone los siguientes endpoints principales:

**Gestión de Libros:**
*   `POST /upload-book/`: Sube y procesa un nuevo libro (PDF/EPUB).
*   `GET /books/`: Recupera una lista paginada y filtrada de libros.
*   `GET /books/count`: Obtiene el número total de libros.
*   `GET /books/search/`: Busca libros por título parcial.
*   `GET /categories/`: Obtiene una lista de todas las categorías únicas.
*   `PUT /books/{book_id}`: Actualiza los detalles de un libro existente.
*   `DELETE /books/{book_id}`: Elimina un libro y sus archivos.
*   `DELETE /categories/{category_name}`: Elimina una categoría y todos sus libros.
*   `GET /books/download/{book_id}`: Descarga o abre un archivo de libro.

**Herramientas y Conversión:**
*   `POST /tools/convert-epub-to-pdf`: Convierte un archivo EPUB subido a PDF y ofrece una URL de descarga temporal.
*   `POST /api/books/{book_id}/convert`: Convierte un libro EPUB existente en la biblioteca a PDF, añadiéndolo como un nuevo libro.

**Funcionalidad RAG (IA):**
*   `POST /rag/query/`: Realiza una consulta RAG sobre un libro indexado.
*   `POST /rag/index/{book_id}`: Indexa un libro existente en la base de datos para RAG.
*   `GET /rag/status/{book_id}`: Obtiene el estado de indexación RAG de un libro.
*   `POST /rag/reindex/category/{category_name}`: (Re)indexa todos los libros de una categoría.
*   `POST /rag/reindex/all`: (Re)indexa todos los libros de la biblioteca.
*   `GET /rag/estimate/book/{book_id}`: Estima tokens/chunks y coste de embeddings para un libro.
*   `GET /rag/estimate/category/{category_name}`: Estima para una categoría.
*   `GET /rag/estimate/all`: Estima para toda la biblioteca.

**Archivos Estáticos:**
*   `GET /static/...`: Sirve archivos estáticos (como las portadas de los libros).
*   `GET /temp_books/...`: Sirve archivos temporales (como los PDFs generados por la herramienta de conversión).
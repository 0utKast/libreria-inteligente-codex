# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales (PDF y EPUB).  La aplicación facilita la carga de libros, su organización por categorías y autores, la búsqueda de libros por título o autor, y la descarga de los mismos.  Además, integra un sistema de Recuperación de Información basada en Conocimiento (RAG) que permite al usuario realizar consultas sobre el contenido de sus libros usando un modelo de lenguaje grande (Gemini).

La arquitectura de la aplicación se basa en un frontend desarrollado con React y un backend construido con FastAPI (Python).  La persistencia de datos se realiza mediante una base de datos SQLite. El sistema RAG utiliza ChromaDB para la indexación de embeddings generados por Gemini.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   **`backend/`:** Contiene el código del backend de la aplicación, escrito en Python usando el framework FastAPI.  Incluye subcarpetas para la base de datos (`alembic/`), modelos (`models.py`), rutas (`main.py`), lógica de negocio (`crud.py`), esquemas Pydantic (`schemas.py`), utilidades (`utils.py`), lógica RAG (`rag.py`) y tests (`tests/`).

*   **`frontend/src`:** Contiene el código del frontend de la aplicación, desarrollado en React.  Incluye componentes para la vista principal (`App.js`), la biblioteca (`LibraryView.js`), la carga de libros (`UploadView.js`), las categorías (`CategoriesView.js`), las herramientas (`ToolsView.js`), la vista del lector (`ReaderView.js`) y la interacción con el sistema RAG (`RagView.js`). También incluye un `ErrorBoundary.js` para manejo de errores UI y el archivo de configuración `config.js`.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/main.py`

*   **Propósito:** Define las rutas y la lógica de la API FastAPI.  Gestiona la subida, búsqueda, eliminación y descarga de libros, además de la integración con el sistema RAG y las herramientas.

*   **Funciones/Clases principales:**

    *   `upload_book`: Recibe un archivo de libro (`UploadFile`), lo procesa (extrayendo texto y portada si es posible), lo analiza con Gemini para obtener metadatos, y lo crea en la base de datos mediante `crud.create_book`. Retorna un objeto `schemas.Book`.
    *   `read_books`: Obtiene una lista de libros de la base de datos filtrando opcionalmente por categoría, búsqueda general y autor mediante `crud.get_books`. Retorna una lista de objetos `schemas.Book`.
    *   `get_books_count`: Obtiene el número total de libros en la base de datos utilizando `crud.get_books_count`. Retorna un entero.
    *   `search_books`: Busca libros por un título parcial utilizando `crud.get_books_by_partial_title`. Permite paginación. Retorna una lista de objetos `schemas.Book`.
    *   `read_categories`: Obtiene una lista de categorías únicas de la base de datos utilizando `crud.get_categories`. Retorna una lista de strings.
    *   `delete_single_book`: Elimina un libro de la base de datos y sus archivos asociados utilizando `crud.delete_book`. Limpia los índices RAG asociados. Retorna un diccionario con un mensaje de confirmación.
    *   `delete_category_and_books`: Elimina todos los libros de una categoría dada, incluyendo sus archivos y índices RAG asociados mediante `crud.delete_books_by_category`. Retorna un diccionario con un mensaje de confirmación.
    *   `download_book`: Descarga un libro de la base de datos. Retorna una respuesta `FileResponse`.
    *   `convert_epub_to_pdf`: Convierte un archivo EPUB a PDF usando `weasyprint`. Guarda el PDF generado en una ubicación temporal pública y retorna un `ConversionResponse` con la URL de descarga.
    *   `upload_book_for_rag`: Sube un libro para ser procesado por el sistema RAG, utilizando `rag.process_book_for_rag`. Retorna un `RagUploadResponse`.
    *   `query_rag_endpoint`: Consulta el sistema RAG usando `rag.query_rag`.  Obtiene metadatos y contexto de otros libros del autor de la biblioteca. Retorna un `RagQueryResponse`.
    *   `index_existing_book_for_rag`: Indexa un libro existente en la base de datos en RAG.  Permite reindexar (forzar reindexación). Retorna un diccionario de confirmación.
    *   `rag_status`: Devuelve el estado de indexación RAG para un libro dado, utilizando `rag.get_index_count`.  Retorna un diccionario con el estado.
    *   `rag_reindex_category`: (Re)indexa todos los libros de una categoría específica en RAG.
    *   `rag_reindex_all`: (Re)indexa todos los libros de la biblioteca en RAG.
    *   `estimate_rag_for_book`, `estimate_rag_for_category`, `estimate_rag_for_all`: Estiman el tamaño (tokens) y número de chunks, y coste opcional para indexar un libro, categoría o toda la biblioteca, utilizando `rag.estimate_embeddings_for_file` y `rag.estimate_embeddings_for_files`.


### `backend/crud.py`

*   **Propósito:** Define las funciones CRUD (Create, Read, Update, Delete) para interactuar con la base de datos.

*   **Funciones principales:**  Cada función recibe una sesión de SQLAlchemy (`db: Session`) como primer parámetro y opera sobre la tabla `books`.

    *   `get_book_by_path`: Busca un libro por su `file_path`.
    *   `get_book_by_title`: Busca un libro por su título exacto.
    *   `get_books_by_partial_title`: Busca libros por un título parcial (case-insensitive), con paginación.
    *   `get_books`: Obtiene una lista de libros, con opciones de filtrado.
    *   `get_categories`: Obtiene una lista de categorías únicas.
    *   `create_book`: Crea un nuevo libro en la base de datos.
    *   `delete_book`: Elimina un libro de la base de datos y sus archivos asociados.
    *   `delete_books_by_category`: Elimina todos los libros de una categoría dada.
    *   `get_books_count`: Obtiene el conteo total de libros.


### `backend/database.py`

*   **Propósito:** Configura la conexión a la base de datos SQLite.

*   **Elementos principales:** Define `engine` y `SessionLocal` para interactuar con la base de datos.


### `backend/utils.py`

*   **Propósito:** Contiene funciones utilitarias.

*   **Funciones principales:**

    *   `configure_genai`: Configura la API key de Google Gemini, leyendo de las variables de entorno.


### `backend/models.py`

*   **Propósito:** Define el modelo de datos `Book` para la base de datos.

*   **Clase principal:**

    *   `Book`: Define la estructura de la tabla `books` en la base de datos, con columnas para `id`, `title`, `author`, `category`, `cover_image_url`, y `file_path`.


### `backend/rag.py`

*   **Propósito:** Contiene la lógica para el sistema RAG.

*   **Funciones principales:**

    *   `get_embedding`: Genera un embedding para un texto dado usando la API de embeddings de Gemini. Si `DISABLE_AI` está en el entorno, devuelve un embedding dummy.
    *   `extract_text_from_pdf`: Extrae texto de un archivo PDF usando PyPDF2.
    *   `extract_text_from_epub`: Extrae texto de un archivo EPUB usando ebooklib y BeautifulSoup.
    *   `extract_text`: Función unificada para extraer texto de archivos PDF y EPUB.
    *   `chunk_text`: Divide un texto en chunks más pequeños basados en el conteo de tokens.
    *   `_has_index_for_book`: Verifica si ya existe un índice para un libro en ChromaDB.
    *   `delete_book_from_rag`: Elimina el índice de un libro de ChromaDB.
    *   `get_index_count`: Cuenta los vectores de un libro en ChromaDB.
    *   `has_index`: Devuelve True si un libro está indexado en RAG.
    *   `process_book_for_rag`: Procesa un libro para el sistema RAG (extrae texto, lo divide en chunks, genera embeddings y los guarda en ChromaDB).
    *   `estimate_embeddings_for_file`: Estima el número de tokens y chunks para un archivo.
    *   `estimate_embeddings_for_files`: Estima el número de tokens y chunks para una lista de archivos.
    *   `query_rag`: Consulta el sistema RAG para obtener una respuesta a una pregunta dada, usando un prompt que incluye el contexto del libro, metadatos y contexto opcional de otros libros del autor.


### `backend/schemas.py`

*   **Propósito:** Define los esquemas Pydantic para la serialización y validación de datos.

*   **Clases principales:**

    *   `BookBase`: Esquema base para los datos de un libro.
    *   `Book`: Esquema para los datos de un libro incluyendo el ID.
    *   `ConversionResponse`: Esquema para la respuesta de la conversión EPUB a PDF.
    *   `RagUploadResponse`: Esquema para la respuesta de la subida de libro a RAG.
    *   `RagQuery`: Esquema para la consulta al sistema RAG.
    *   `RagQueryResponse`: Esquema para la respuesta del sistema RAG.


### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

*   **Propósito:** Script Alembic para crear la tabla `books` en la base de datos.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/Header.js`

*   **Propósito:** Componente que representa el encabezado de la aplicación.

*   **Estado:** `menuOpen` (booleano), `bookCount` (entero), `errorMessage` (string).
*   **Efectos:** Obtiene el conteo de libros del backend y actualiza `bookCount`.  Maneja errores.  Refresca el conteo periódicamente.
*   **Interacción con el usuario:** Menú hamburguesa para abrir/cerrar la navegación.
*   **Interacción con el backend:** Obtiene el conteo de libros desde `/books/count`.


### `frontend/src/App.js`

*   **Propósito:** Componente principal de la aplicación, que configura las rutas.


### `frontend/src/ToolsView.js`

*   **Propósito:** Componente que muestra las herramientas disponibles.
*   **Interacción con el usuario:** Permitir subir archivos por input o arrastrarlos a la zona de drop.
*   **Interacción con el backend:** Envia una petición POST a `/tools/convert-epub-to-pdf` para convertir un archivo EPUB a PDF.
*   **Funciones:** `handleFileChange`, `handleDrop`, `handleDragOver`, `handleConvert`.


### `frontend/src/UploadView.js`

*   **Propósito:** Componente para subir archivos de libros.

*   **Estado:** `filesToUpload` (array de objetos), `isUploading` (booleano).
*   **Efectos:** No se utilizan efectos secundarios.
*   **Interacción con el usuario:** Permite seleccionar múltiples archivos (PDF o EPUB) para su subida.
*   **Interacción con el backend:** Envía una petición POST a `/upload-book/` para cada archivo.  Actualiza el estado de cada archivo (`pending`, `uploading`, `success`, `error`).


### `frontend/src/ReaderView.js`

*   **Propósito:** Componente para leer libros EPUB usando la librería ReactReader.

*   **Estado:** `location` (string), `epubData` (arrayBuffer), `isLoading` (booleano), `error` (string).
*   **Efectos:** Obtiene los datos del libro del backend.
*   **Interacción con el usuario:** Permite la navegación dentro del libro EPUB.
*   **Interacción con el backend:** Obtiene el libro desde `/books/download/:bookId`.


### `frontend/src/ErrorBoundary.js`

*   **Propósito:** Componente para capturar errores en la interfaz de usuario.


### `frontend/src/RagView.js`

*   **Propósito:** Componente para interactuar con el sistema RAG.
*   **Interacción con el usuario:** Introducir consultas de texto, seleccionar libro de la biblioteca, elegir modo de respuesta.
*   **Interacción con el backend:** Envía consultas a `/rag/query/` mediante peticiones POST.  Obtiene estado RAG de `/rag/status/:bookId` y realiza peticiones POST a `/rag/index/:bookId` para indexar.
*   **Funciones:** `handleQuerySubmit`, `checkLibraryStatus`, `indexLibraryBook`, `focusChatInput`.
*   **Estado:**  `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.


### `frontend/src/LibraryView.js`

*   **Propósito:** Componente que muestra la lista de libros.

*   **Estado:** `books` (array de objetos), `searchTerm` (string), `error` (string), `loading` (booleano), `isMobile` (booleano).
*   **Efectos:** Obtiene la lista de libros del backend, con filtrado opcional por categoría y búsqueda.  Maneja errores y carga inicial.
*   **Interacción con el usuario:** Permite la búsqueda de libros, visualizar detalle de autores y categorías, y eliminar libros.
*   **Interacción con el backend:** Obtiene los libros desde `/books/`, usando parámetros de consulta (`category`, `search`, `author`). Envía peticiones DELETE a `/books/:bookId` para eliminar libros.
*   **Funciones:** `fetchBooks`, `handleAuthorClick`, `handleCategoryClick`, `handleDeleteBook`.


### `frontend/src/config.js`

*   **Propósito:** Archivo de configuración para la URL de la API.


### `frontend/src/CategoriesView.js`

*   **Propósito:** Componente que muestra la lista de categorías.

*   **Estado:** `categories` (array de strings), `error` (string), `loading` (booleano).
*   **Efectos:** Obtiene la lista de categorías del backend.
*   **Interacción con el usuario:** Navegación a la vista principal con filtro de categoría.
*   **Interacción con el backend:** Obtiene las categorías desde `/categories/`.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro en `UploadView.js`. El frontend envía una petición POST a `/upload-book/` en el backend (`main.py`).  El backend procesa el libro, extrae texto y metadatos (si es posible), y lo guarda en la base de datos.  La respuesta contiene los datos del libro recién creado.

La vista de la biblioteca (`LibraryView.js`) obtiene los libros del backend a través de la ruta `/books/`. Esta ruta soporta parámetros de consulta para la búsqueda y filtrado (categoría, búsqueda general, autor).

Para la descarga de un libro, se utiliza la ruta `/books/download/:bookId`. La ruta `/categories/` proporciona la lista de categorías disponibles.

El sistema RAG permite la indexación de libros mediante las rutas `/rag/upload-book/` (para libros nuevos) y `/rag/index/:bookId` (para libros existentes). Las consultas al sistema RAG se realizan a través de la ruta `/rag/query/`. La ruta `/rag/status/:bookId` proporciona información sobre el estado de indexación de un libro.

**Principales Endpoints de la API:**

*   `/upload-book/` (POST): Sube un nuevo libro.
*   `/books/` (GET): Obtiene una lista de libros (soporta parámetros de búsqueda y filtrado).
*   `/books/count` (GET): Obtiene el número de libros.
*   `/categories/` (GET): Obtiene la lista de categorías.
*   `/books/:bookId` (DELETE): Elimina un libro.
*   `/books/download/:bookId` (GET): Descarga un libro.
*   `/tools/convert-epub-to-pdf` (POST): Convierte un EPUB a PDF.
*   `/rag/upload-book/` (POST): Sube un libro para el sistema RAG.
*   `/rag/query/` (POST): Realiza una consulta al sistema RAG.
*   `/rag/index/:bookId` (POST): Indexa un libro existente en RAG.
*   `/rag/status/:bookId` (GET): Obtiene el estado RAG de un libro.
*   `/rag/reindex/category/:category_name` (POST): Reindexa una categoría en RAG.
*   `/rag/reindex/all` (POST): Reindexa toda la biblioteca en RAG.
*   `/rag/estimate/book/:book_id` (GET): Estimación tokens/chunks y coste opcional para un libro.
*   `/rag/estimate/category/:category_name` (GET): Estimación tokens/chunks y coste opcional para una categoría.
*   `/rag/estimate/all` (GET): Estimación tokens/chunks y coste opcional para toda la biblioteca.


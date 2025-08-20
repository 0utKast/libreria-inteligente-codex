# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales.  La aplicación permite subir libros en formato PDF y EPUB, los analiza utilizando la IA de Google Gemini para extraer metadatos (título, autor, categoría), y los almacena en una base de datos.  Los usuarios pueden buscar libros, ver detalles, y descargarlos.  Adicionalmente, la aplicación integra un sistema RAG (Retrieval Augmented Generation) basado en ChromaDB, permitiendo a los usuarios realizar consultas con la IA sobre el contenido de sus libros.

La arquitectura de la aplicación se basa en un frontend desarrollado en React y un backend construido con FastAPI (Python).  FastAPI se conecta a una base de datos SQLite para el almacenamiento persistente de información sobre los libros.  El sistema RAG utiliza embeddings generados por Google Gemini para indexar el texto de los libros y facilitar la recuperación de información contextual para las consultas de la IA.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales:

*   **backend/:** Contiene el código del backend en Python, utilizando FastAPI.  Este directorio incluye subcarpetas para la base de datos (`alembic/`), modelos (`models.py`), rutas (`main.py`), lógica de CRUD (`crud.py`), esquemas Pydantic (`schemas.py`), utilidades (`utils.py`), y la lógica del sistema RAG (`rag.py`). También incluye un directorio de pruebas (`tests/`).

*   **frontend/:** Contiene el código del frontend desarrollado en React. El directorio `src/` contiene los componentes de la interfaz de usuario, incluyendo el componente principal (`App.js`), vistas para la biblioteca (`LibraryView.js`), subida de libros (`UploadView.js`), categorías (`CategoriesView.js`), herramientas (`ToolsView.js`), lector de EPUB (`ReaderView.js`), vista de conversación con IA (`RagView.js`), manejo de errores (`ErrorBoundary.js`) y el archivo de configuración (`config.js`).


## 3. Análisis Detallado del Backend (Python/FastAPI)

### backend/main.py

**Propósito:** Define las rutas y la lógica principal de la API FastAPI.

**Funciones/Clases Principales:**

*   `analyze_with_gemini(text: str) -> dict:` Envía el texto a Google Gemini para obtener metadatos (título, autor, categoría). Devuelve un diccionario con los metadatos o un diccionario de error.  Maneja excepciones de la API.

*   `process_pdf(file_path: str, static_dir: str) -> dict:` Procesa un archivo PDF, extrayendo texto y la imagen de la portada. Devuelve un diccionario con el texto extraído y la URL de la portada.

*   `process_epub(file_path: str, static_dir: str) -> dict:` Procesa un archivo EPUB extrayendo texto de las primeras páginas y buscando una imagen de portada.  Devuelve un diccionario con texto y URL de la portada o errores HTTP.

*   `upload_book(...)`: Maneja la subida de un libro, procesa el archivo (PDF o EPUB), envía el texto a la IA para análisis, crea un registro de libro en la BD, y devuelve el objeto del libro creado. Maneja la subida de archivos, el análisis con Gemini y la creación de registros en la base de datos. Lanza HTTPException en caso de error.

*   `read_books(...)`: Devuelve una lista de libros de la BD. Permite filtrar por categoría, búsqueda general y autor.

*   `get_books_count(...)`: Devuelve el número de libros en la BD.

*   `search_books(...)`: Busca libros por título parcial (case-insensitive) con paginación.

*   `read_categories(...)`: Devuelve una lista de categorías únicas de la BD.

*   `delete_single_book(...)`: Elimina un libro de la BD por su ID, borrando también sus archivos asociados y de RAG.

*   `delete_category_and_books(...)`: Elimina todos los libros de una categoría, incluyendo sus archivos asociados y de RAG.

*   `download_book(...)`: Permite descargar un libro a través de su ID.

*   `convert_epub_to_pdf(...)`: Convierte un archivo EPUB a PDF usando la librería `weasyprint`. Devuelve un URL para la descarga.

*   `upload_book_for_rag(...)`:  Sube un libro para que sea procesado por el sistema RAG.

*   `query_rag_endpoint(...)`:  Recibe una consulta y la envía al sistema RAG para obtener una respuesta.

*   `index_existing_book_for_rag(...)`:  Indexa en RAG un libro ya existente en la base de datos.

*   `rag_status(...)`: Devuelve el estado del índice RAG para un libro.

*   `rag_reindex_category(...)`: Reindexa todos los libros de una categoría en RAG.

*   `rag_reindex_all(...)`: Reindexa todos los libros en RAG.

*   `estimate_rag_for_book(...)`: Estima tokens/chunks para el indexado en RAG.

*   `estimate_rag_for_category(...)`: Estima tokens/chunks para una categoría en RAG.

*   `estimate_rag_for_all(...)`: Estima tokens/chunks para toda la biblioteca en RAG.


### backend/crud.py

**Propósito:** Define las funciones CRUD (Create, Read, Update, Delete) para interactuar con la base de datos.

**Funciones Principales:**

*   `get_book_by_path(db: Session, file_path: str)`: Obtiene un libro por su ruta de archivo.
*   `get_book_by_title(db: Session, title: str)`: Obtiene un libro por su título.
*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial (case-insensitive), con paginación.
*   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`: Obtiene libros con opciones de filtrado.
*   `get_categories(db: Session) -> list[str]`: Obtiene categorías únicas.
*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea un nuevo libro.
*   `delete_book(db: Session, book_id: int)`: Elimina un libro y sus archivos asociados.
*   `delete_books_by_category(db: Session, category: str)`: Elimina libros de una categoría y sus archivos asociados.
*   `get_books_count(db: Session) -> int`: Cuenta los libros.


### backend/models.py

**Propósito:** Define el modelo de datos `Book` para la base de datos SQLAlchemy.

**Clases Principales:**

*   `Book(Base)`: Define la estructura de la tabla `books` en la base de datos.


### backend/schemas.py

**Propósito:** Define los esquemas Pydantic para la serialización y validación de datos.

**Clases Principales:**

*   `BookBase(BaseModel)`: Esquema base para la creación de libros.
*   `Book(BookBase)`: Esquema para libros, incluyendo el ID.
*   `ConversionResponse(BaseModel)`: Esquema para la respuesta de conversión EPUB a PDF.
*   `RagUploadResponse(BaseModel)`: Esquema para la respuesta de subida a RAG.
*   `RagQuery(BaseModel)`: Esquema para una consulta RAG.
*   `RagQueryResponse(BaseModel)`: Esquema para la respuesta de una consulta RAG.


### backend/rag.py

**Propósito:**  Implementa la lógica del sistema RAG (Retrieval Augmented Generation).

**Funciones Principales:**

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`: Genera un embedding para un texto dado. Utiliza Google Gemini si está configurado, sino, un embedding dummy.
*   `extract_text_from_pdf(file_path: str) -> str`: Extrae texto de un archivo PDF.
*   `extract_text_from_epub(file_path: str) -> str`: Extrae texto de un archivo EPUB.
*   `extract_text(file_path: str) -> str`: Función unificada para la extracción de texto.
*   `chunk_text(text: str, max_tokens: int = 1000) -> list[str]`: Divide un texto en chunks.
*   `_has_index_for_book(book_id: str) -> bool`: Verifica si existe un índice para un libro en ChromaDB.
*   `delete_book_from_rag(book_id: str)`: Elimina el índice de un libro de ChromaDB.
*   `get_index_count(book_id: str) -> int`: Obtiene el número de vectores indexados para un libro.
*   `has_index(book_id: str) -> bool`:  Función de utilidad para saber si un libro está indexado en RAG.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Procesa un libro para RAG: extrae texto, genera chunks y embeddings, y almacena en ChromaDB.
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`: Estima tokens y chunks para un archivo.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`: Estima tokens y chunks para varios archivos.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`: Realiza una consulta al sistema RAG.


### backend/utils.py

**Propósito:**  Funciones de utilidad, incluyendo la configuración de la API Key de Google Generative AI.

**Funciones Principales:**

*   `configure_genai()`: Configura la API Key para Google Generative AI a partir de variables de entorno.


### backend/database.py

**Propósito:**  Configuración de la base de datos SQLAlchemy.


## 4. Análisis Detallado del Frontend (React)

### frontend/src/App.js

**Propósito:** Componente principal de la aplicación React.  Define las rutas de navegación.

**Estado/Propiedades/Efectos:** No tiene estado ni propiedades.  Utiliza `BrowserRouter`, `Routes`, y `Route` para gestionar la navegación entre vistas.


### frontend/src/Header.js

**Propósito:** Componente para el encabezado de la aplicación, incluyendo la navegación.

**Estado:** `menuOpen` (booleano), `bookCount` (entero), `errorMessage` (string).

**Propiedades:** No tiene propiedades.

**Efectos:**  `useEffect` para obtener el conteo de libros del backend, gestionando errores y actualización periódica.

**Interacción con el backend:**  Llamada `fetch` a `/books/count` para obtener el número de libros.


### frontend/src/LibraryView.js

**Propósito:** Visualiza la lista de libros en la biblioteca.

**Estado:** `books` (array de objetos), `searchTerm` (string), `error` (string), `loading` (booleano), `isMobile` (booleano).

**Propiedades:** No tiene propiedades.

**Efectos:** `useEffect` para obtener libros del backend usando `useCallback` para optimizar.  `useDebounce` para evitar peticiones excesivas de búsqueda.

**Interacción con el backend:**  Llamadas `fetch` a `/books/` (con parámetros opcionales de filtrado y búsqueda) y `/books/:bookId` (DELETE) para eliminar libros.


### frontend/src/UploadView.js

**Propósito:** Permite a los usuarios subir libros.

**Estado:** `filesToUpload` (array de objetos), `isUploading` (booleano).

**Propiedades:** No tiene propiedades.

**Efectos:** No tiene efectos secundarios.

**Interacción con el backend:** Llamada `fetch` a `/upload-book/` para subir cada libro.  Actualiza el estado de cada archivo individualmente (pending, uploading, success, error).


### frontend/src/ReaderView.js

**Propósito:** Componente para leer libros EPUB.

**Estado:** `location`, `epubData`, `isLoading`, `error`.

**Propiedades:** `bookId` (obtenido de `useParams`).

**Efectos:** `useEffect` para obtener datos del libro desde `/books/download/:bookId`.

**Interacción con el backend:**  Llamada `fetch` a `/books/download/:bookId` para descargar el libro EPUB.


### frontend/src/RagView.js

**Propósito:**  Permite al usuario interactuar con el sistema RAG.

**Estado:** `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.

**Propiedades:** No tiene propiedades.

**Efectos:** `useEffect` para cargar la lista de libros, gestionar el auto-scroll del chat y realizar búsquedas con debounce.

**Interacción con el backend:**  Llamadas a `/rag/query/`, `/rag/status/:bookId`, `/rag/index/:bookId`, y `/books/` para obtener respuestas de RAG, verificar estado, indexar, y cargar libros respectivamente.


### frontend/src/CategoriesView.js

**Propósito:** Muestra una lista de todas las categorías de libros.

**Estado:** `categories`, `error`, `loading`.

**Propiedades:** No tiene propiedades.

**Efectos:** `useEffect` para obtener las categorías de `/categories/` y actualizar el estado.

**Interacción con el backend:**  Llamada `fetch` a `/categories/`.


### frontend/src/ToolsView.js

**Propósito:**  Proporciona herramientas adicionales, actualmente un convertidor de EPUB a PDF.

**Estado:** `selectedFile`, `message`, `isLoading`.

**Propiedades:** No tiene propiedades.

**Efectos:** No tiene efectos secundarios.

**Interacción con el backend:** Llamada `fetch` a `/tools/convert-epub-to-pdf` para realizar la conversión.


### frontend/src/ErrorBoundary.js

**Propósito:** Componente para el manejo de errores en la interfaz de usuario.


### frontend/src/config.js

**Propósito:**  Archivo de configuración con la URL de la API.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro a través de `UploadView`.  El frontend envía el archivo al endpoint `/upload-book/` del backend.  El backend procesa el archivo, extrae el texto, lo envía a Google Gemini para el análisis, guarda el libro en la base de datos y la ruta del archivo, y devuelve los datos del libro creado. El frontend actualiza su vista con el nuevo libro.

Para la consulta de RAG, el usuario elige un libro en `RagView`, y envía una consulta a través del endpoint `/rag/query/`. El backend procesa la consulta usando el sistema RAG y devuelve una respuesta de texto al frontend, que se añade al historial de chat.

**Principales Endpoints de la API:**

*   `/upload-book/`: POST - Sube un libro.
*   `/books/`: GET - Obtiene una lista de libros (con opciones de filtrado).
*   `/books/count`: GET - Obtiene el número de libros.
*   `/books/search/`: GET - Busca libros por título parcial.
*   `/categories/`: GET - Obtiene las categorías.
*   `/books/:book_id`: DELETE - Elimina un libro.
*   `/books/download/:book_id`: GET - Descarga un libro.
*   `/tools/convert-epub-to-pdf`: POST - Convierte EPUB a PDF.
*   `/rag/upload-book/`: POST - Sube un libro para RAG.
*   `/rag/query/`: POST - Consulta RAG.
*   `/rag/index/:book_id`: POST - Indexa un libro en RAG.
*   `/rag/status/:book_id`: GET - Obtiene estado RAG.
*   `/rag/reindex/category/:category_name`: POST - Reindexa una categoría en RAG.
*   `/rag/reindex/all`: POST - Reindexa toda la biblioteca en RAG.
*   `/rag/estimate/book/:book_id`: GET - Estimación de coste/tokens para un libro.
*   `/rag/estimate/category/:category_name`: GET - Estimación de coste/tokens para una categoría.
*   `/rag/estimate/all`: GET - Estimación de coste/tokens para toda la biblioteca.


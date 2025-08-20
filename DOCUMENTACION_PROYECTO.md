# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales.  La aplicación permite subir libros en formato PDF y EPUB, los analiza utilizando la IA de Google Gemini para extraer metadatos (título, autor, categoría), y los almacena en una base de datos.  Además, incluye funcionalidades de búsqueda, descarga y eliminación de libros, así como un conversador basado en RAG (Retrieval Augmented Generation) que permite hacer preguntas sobre el contenido de los libros indexados.

La arquitectura de la aplicación se basa en un frontend desarrollado con React, un backend construido con FastAPI (Python), y una base de datos SQLite para el almacenamiento persistente de la información de los libros. El procesamiento de lenguaje natural y la generación de respuestas se realiza mediante la API de Google Gemini.  El sistema RAG utiliza ChromaDB para indexar y consultar embeddings de los textos de los libros.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales: `backend/` y `frontend/`.

*   **`backend/`**: Contiene el código del backend de la aplicación, utilizando Python y FastAPI.  Incluye subcarpetas para la base de datos (`alembic/`), modelos (`models.py`), rutas (`main.py`), lógica de acceso a datos (`crud.py`), esquemas Pydantic (`schemas.py`),  utilidades (`utils.py`), la implementación del sistema RAG (`rag.py`) y las pruebas (`tests/`).

*   **`frontend/src`**: Contiene el código fuente del frontend, desarrollado con React.  Cada componente de la interfaz de usuario se encuentra en un archivo `.js` separado, con sus estilos CSS correspondientes.

## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/main.py`

**Propósito:** Define las rutas y la lógica principal de la API FastAPI.  Gestiona la subida de libros, el análisis mediante Gemini, la interacción con la base de datos, y la gestión de la conversión EPUB-PDF.

**Funciones/Clases Principales:**

*   `analyze_with_gemini(text: str) -> dict`: Analiza un texto dado con Google Gemini para extraer título, autor y categoría.  Retorna un diccionario con estos datos.
*   `process_pdf(file_path: str, static_dir: str) -> dict`: Procesa un archivo PDF, extrayendo texto y buscando una imagen de portada. Retorna un diccionario con el texto y la URL de la portada.
*   `process_epub(file_path: str, static_dir: str) -> dict`: Procesa un archivo EPUB, extrayendo texto y buscando una imagen de portada.  Retorna un diccionario con el texto y la URL de la portada.  Incluye manejo de errores para casos donde no se puede extraer texto.
*   `upload_book(...)`: Gestiona la subida de un libro, el análisis con Gemini, y la creación del registro en la base de datos.  Retorna un objeto `schemas.Book`.
*   `read_books(...)`: Obtiene una lista de libros, con opciones de filtrado.  Retorna una lista de objetos `schemas.Book`.
*   `get_books_count(...)`: Obtiene el número total de libros en la base de datos. Retorna un entero.
*   `search_books(...)`: Busca libros por un título parcial, con paginación. Retorna una lista de objetos `schemas.Book`.
*   `read_categories(...)`: Obtiene una lista de todas las categorías únicas. Retorna una lista de strings.
*   `delete_single_book(...)`: Elimina un libro de la base de datos y sus archivos asociados. Retorna un diccionario con un mensaje de confirmación.
*   `delete_category_and_books(...)`: Elimina todos los libros de una categoría específica. Retorna un diccionario con el número de libros eliminados.
*   `download_book(...)`: Permite descargar un libro.  Retorna un `FileResponse` para descargar el libro.
*   `convert_epub_to_pdf(...)`: Convierte un archivo EPUB a PDF. Retorna un objeto `schemas.ConversionResponse` con la URL de descarga.
*   `upload_book_for_rag(...)`: Procesa un libro para indexarlo en RAG.  Retorna un objeto `schemas.RagUploadResponse`.
*   `query_rag_endpoint(...)`: Consulta el sistema RAG.  Retorna un objeto `schemas.RagQueryResponse`.
*   `index_existing_book_for_rag(...)`: Indexa un libro ya existente en la BD en RAG. Retorna un diccionario con información del proceso.
*   `rag_status(...)`: Devuelve si el libro tiene índice RAG y el número de vectores.
*   `rag_reindex_category(...)`: (Re)indexa todos los libros de una categoría en RAG.
*   `rag_reindex_all(...)`: (Re)indexa todos los libros de la biblioteca en RAG.
*   `estimate_rag_for_book(...)`: Estima tokens, chunks y coste (opcional) para un libro.
*   `estimate_rag_for_category(...)`: Estima tokens, chunks y coste (opcional) para una categoría.
*   `estimate_rag_for_all(...)`: Estima tokens, chunks y coste (opcional) para toda la biblioteca.

### `backend/crud.py`

**Propósito:** Define las funciones para interactuar con la base de datos.

**Funciones/Clases Principales:**
* `get_book_by_path(db: Session, file_path: str)`: Obtiene un libro por su ruta de archivo. Retorna un objeto `models.Book` o `None`.
* `get_book_by_title(db: Session, title: str)`: Obtiene un libro por su título. Retorna un objeto `models.Book` o `None`.
* `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial (case-insensitive). Retorna una lista de objetos `models.Book`.
* `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`: Obtiene una lista de libros con opciones de filtrado. Retorna una lista de objetos `models.Book`.
* `get_categories(db: Session) -> list[str]`: Obtiene una lista de todas las categorías únicas. Retorna una lista de strings.
* `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea un nuevo libro en la base de datos. Retorna un objeto `models.Book`.
* `delete_book(db: Session, book_id: int)`: Elimina un libro de la base de datos y sus archivos asociados. Retorna el objeto `models.Book` eliminado o `None`.
* `delete_books_by_category(db: Session, category: str)`: Elimina todos los libros de una categoría y sus archivos. Retorna el número de libros eliminados.
* `get_books_count(db: Session) -> int`: Obtiene el número total de libros. Retorna un entero.

### `backend/models.py`

**Propósito:** Define el modelo de datos `Book` para SQLAlchemy.

**Clases Principales:**

*   `Book`:  Modelo de datos para representar un libro en la base de datos.  Contiene campos para `id`, `title`, `author`, `category`, `cover_image_url` y `file_path`.

### `backend/schemas.py`

**Propósito:** Define los esquemas Pydantic para la serialización y validación de datos.

**Clases Principales:**

*   `BookBase`: Esquema base para un libro.
*   `Book`: Esquema para un libro, incluyendo el ID.
*   `ConversionResponse`: Esquema para la respuesta de la conversión EPUB-PDF.
*   `RagUploadResponse`: Esquema para la respuesta de la subida a RAG.
*   `RagQuery`: Esquema para una consulta RAG.
*   `RagQueryResponse`: Esquema para la respuesta de una consulta RAG.

### `backend/database.py`

**Propósito:** Configura la conexión a la base de datos SQLite.

**Variables/Clases Principales:**

*   `SQLALCHEMY_DATABASE_URL`:  URL de la base de datos.
*   `engine`: Motor de la base de datos SQLAlchemy.
*   `SessionLocal`:  Factory para crear sesiones de la base de datos.
*   `Base`:  Clase base declarativa de SQLAlchemy.

### `backend/utils.py`

**Propósito:**  Funciones utilitarias, incluyendo la configuración de la API Key de Google Gemini.

**Funciones/Clases Principales:**

*   `configure_genai()`: Configura la API Key de Google Gemini a partir del archivo `.env`.


### `backend/rag.py`

**Propósito:** Implementa la lógica del sistema RAG (Retrieval Augmented Generation).

**Funciones/Clases Principales:**

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`: Genera un embedding para un texto dado usando Google Gemini. Retorna la lista de embeddings o una lista de ceros si la IA está deshabilitada.
*   `extract_text_from_pdf(file_path: str) -> str`: Extrae texto de un archivo PDF. Retorna el texto extraído.
*   `extract_text_from_epub(file_path: str) -> str`: Extrae texto de un archivo EPUB. Retorna el texto extraído.
*   `extract_text(file_path: str) -> str`: Función unificada para extraer texto de archivos PDF y EPUB. Retorna el texto extraído.
*   `chunk_text(text: str, max_tokens: int = 1000) -> list[str]`: Divide un texto en chunks más pequeños. Retorna una lista de strings.
*   `_has_index_for_book(book_id: str) -> bool`: Comprueba si un libro ya está indexado en ChromaDB. Retorna un booleano.
*   `delete_book_from_rag(book_id: str)`: Elimina los vectores de un libro de ChromaDB.
*   `get_index_count(book_id: str) -> int`: Obtiene el número de vectores de un libro en ChromaDB. Retorna un entero.
*   `has_index(book_id: str) -> bool`: Comprueba si un libro está indexado en RAG. Retorna un booleano.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Procesa un libro para RAG: extrae texto, lo divide en chunks, genera embeddings y los guarda en ChromaDB.
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`: Estima el número de tokens y chunks para un archivo. Retorna un diccionario con las estimaciones.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`: Estima el número de tokens y chunks para una lista de archivos. Retorna un diccionario con las estimaciones.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`: Consulta el sistema RAG. Retorna la respuesta de la consulta.


### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

**Propósito:** Script de Alembic para crear la tabla `books` en la base de datos.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

**Propósito:** Componente principal de la aplicación React, que define las rutas de navegación.

**Estado, Propiedades, Efectos:** No tiene estado ni propiedades significativas. Define las rutas de la aplicación usando `react-router-dom`.

### `frontend/src/Header.js`

**Propósito:** Componente que representa el encabezado de la aplicación, incluyendo el menú de navegación y el contador de libros.

**Estado:** `menuOpen`, `bookCount`, `errorMessage`.

**Propiedades:** No tiene propiedades.

**Efectos:**  `useEffect` para obtener el contador de libros del backend y actualizarlo periódicamente.

**Interacción con el Backend:**  Realiza una petición `fetch` a `/books/count` para obtener el número de libros.

### `frontend/src/LibraryView.js`

**Propósito:** Muestra la lista de libros de la biblioteca, permitiendo la búsqueda y la eliminación de libros.

**Estado:** `books`, `searchTerm`, `error`, `loading`, `isMobile`.

**Propiedades:** No tiene propiedades.

**Efectos:** `useEffect` para obtener la lista de libros del backend utilizando `useCallback` para optimizar el rendimiento. Utiliza `useDebounce` para optimizar las peticiones de búsqueda.

**Interacción con el Backend:**  Realiza una petición `fetch` a `/books/` para obtener los libros y  a `/books/:bookId` para eliminar libros.

### `frontend/src/UploadView.js`

**Propósito:** Permite a los usuarios subir libros al sistema.

**Estado:** `filesToUpload`, `isUploading`.

**Propiedades:** No tiene propiedades.

**Efectos:** No tiene efectos significativos.

**Interacción con el Backend:** Realiza una petición `fetch` a `/upload-book/` para subir y analizar cada libro.

### `frontend/src/ReaderView.js`

**Propósito:** Muestra un libro EPUB usando `react-reader`.

**Estado:** `location`, `epubData`, `isLoading`, `error`.

**Propiedades:** No tiene propiedades.

**Efectos:** `useEffect` para obtener el libro en formato ArrayBuffer desde el backend.

**Interacción con el Backend:**  Realiza una petición `fetch` a `/books/download/:bookId` para obtener el libro EPUB.

### `frontend/src/ToolsView.js`

**Propósito:** Contiene las herramientas de la aplicación, actualmente solo un conversor EPUB a PDF.

**Estado:** `selectedFile`, `message`, `isLoading`.

**Propiedades:** No tiene propiedades.

**Efectos:** No tiene efectos significativos.

**Interacción con el Backend:** Realiza una petición `fetch` a `/tools/convert-epub-to-pdf` para la conversión de EPUB a PDF.

### `frontend/src/CategoriesView.js`

**Propósito:** Muestra la lista de categorías de libros.

**Estado:** `categories`, `error`, `loading`.

**Propiedades:** No tiene propiedades.

**Efectos:** `useEffect` para obtener la lista de categorías del backend.

**Interacción con el Backend:** Realiza una petición `fetch` a `/categories/` para obtener las categorías.

### `frontend/src/RagView.js`

**Propósito:** Implementa la interfaz de usuario para la interacción con el sistema RAG.

**Estado:** `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.

**Propiedades:** No tiene propiedades.

**Efectos:**  `useEffect` para cargar la lista de libros de la biblioteca, auto-scroll del chat y para comprobar el estado RAG al seleccionar un libro.

**Interacción con el Backend:** Realiza peticiones `fetch` a `/rag/query/`, `/books/`, `/rag/status/:bookId`, y `/rag/index/:bookId`

### `frontend/src/ErrorBoundary.js`

**Propósito:** Componente para gestionar los errores de la interfaz de usuario.


### `frontend/src/config.js`

**Propósito:** Define la URL base de la API.

## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro en `UploadView.js`.  El frontend envía una petición POST a `/upload-book/` en el backend. El backend procesa el archivo, extrae texto usando `process_pdf` o `process_epub`,  utiliza `analyze_with_gemini` para extraer metadatos y guarda la información en la base de datos usando `crud.create_book`. La respuesta JSON contiene el objeto `schemas.Book` creado.

El frontend `LibraryView.js` y `CategoriesView.js` hacen peticiones GET a `/books/` y `/categories/` respectivamente para obtener datos. `LibraryView` también maneja la eliminación de libros mediante una petición DELETE a `/books/:bookId`.  El componente `ReaderView.js` utiliza una petición GET a `/books/download/:bookId` para descargar un libro.  `ToolsView.js` usa una petición POST a `/tools/convert-epub-to-pdf` para convertir libros.

El componente `RagView.js` gestiona la indexación de libros mediante peticiones POST a `/rag/upload-book/` y `/rag/index/:bookId`. Las consultas al modelo RAG se realizan a través de la ruta `/rag/query/` usando peticiones POST. La verificación del estado RAG se hace a través de `/rag/status/:bookId`.

**Endpoints de la API:**

*   **POST `/upload-book/`**: Sube un libro.
*   **GET `/books/`**: Obtiene una lista de libros (con opciones de filtrado).
*   **GET `/books/count`**: Obtiene el número total de libros.
*   **GET `/books/search/`**: Busca libros por un título parcial.
*   **GET `/categories/`**: Obtiene una lista de categorías.
*   **DELETE `/books/:book_id`**: Elimina un libro.
*   **DELETE `/categories/:category_name`**: Elimina una categoría y sus libros.
*   **GET `/books/download/:book_id`**: Descarga un libro.
*   **POST `/tools/convert-epub-to-pdf`**: Convierte EPUB a PDF.
*   **POST `/rag/upload-book/`**: Sube un libro a RAG.
*   **POST `/rag/query/`**: Consulta RAG.
*   **POST `/rag/index/:book_id`**: Indexa un libro en RAG.
*   **GET `/rag/status/:book_id`**: Obtiene el estado RAG de un libro.
*   **POST `/rag/reindex/category/:category_name`**: Reindexa una categoría en RAG.
*   **POST `/rag/reindex/all`**: Reindexa todos los libros en RAG.
*   **GET `/rag/estimate/book/:book_id`**: Estimación de tokens/chunks para un libro.
*   **GET `/rag/estimate/category/:category_name`**: Estimación de tokens/chunks para una categoría.
*   **GET `/rag/estimate/all`**: Estimación de tokens/chunks para toda la biblioteca.


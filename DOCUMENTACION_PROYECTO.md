# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitalmente.  La aplicación ofrece funcionalidades para subir libros (PDF y EPUB), buscar libros por título, autor o categoría, visualizarlos en una biblioteca, convertir EPUB a PDF y una funcionalidad de RAG (Retrieval Augmented Generation) para obtener respuestas a preguntas sobre el contenido de los libros usando un modelo de IA.

La arquitectura de la aplicación se basa en un frontend desarrollado en React, un backend en FastAPI (Python) y una base de datos SQLite. El frontend se encarga de la interfaz de usuario, la interacción con el usuario y la comunicación con el backend mediante API REST. El backend procesa las solicitudes del frontend, interactúa con la base de datos y realiza las tareas de procesamiento de archivos y consulta a la IA. La base de datos almacena la información de los libros, incluyendo metadatos y la ruta de los archivos.  El sistema RAG utiliza ChromaDB para el almacenamiento de embeddings y Google Gemini para la generación de embeddings y respuestas.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   **`backend/`:** Contiene el código del backend de la aplicación, escrito en Python usando el framework FastAPI.  Se estructura de la siguiente manera:
    *   **`alembic/`:**  Contiene las migraciones de la base de datos.
    *   **`database.py`:** Configura la conexión a la base de datos SQLite.
    *   **`crud.py`:** Contiene las funciones CRUD (Create, Read, Update, Delete) para la interacción con la base de datos.
    *   **`main.py`:** Define las rutas y la lógica principal de la API FastAPI.
    *   **`models.py`:** Define el modelo de datos `Book` para la base de datos.
    *   **`rag.py`:** Implementa la funcionalidad de RAG (Retrieval Augmented Generation).
    *   **`schemas.py`:** Define los esquemas Pydantic para la validación de datos.
    *   **`tests/`:** Contiene las pruebas unitarias para el backend.
    *   **`utils.py`:** Funciones auxiliares, incluyendo la configuración de la API key de Google Gemini.
*   **`frontend/src/`:** Contiene el código del frontend de la aplicación, escrito en React.  Se estructura en componentes individuales para cada vista.
    *   **`App.js`:** Componente principal de la aplicación React.
    *   **`CategoriesView.js`:**  Vista para mostrar las categorías de libros.
    *   **`ErrorBoundary.js`:** Componente para manejar errores en la interfaz de usuario.
    *   **`Header.js`:** Componente de cabecera de la aplicación.
    *   **`LibraryView.js`:** Vista principal para mostrar la biblioteca de libros.
    *   **`RagView.js`:** Vista para la interacción con el sistema RAG.
    *   **`ReaderView.js`:** Vista para leer libros EPUB.
    *   **`ToolsView.js`:** Vista para las herramientas de la aplicación.
    *   **`UploadView.js`:** Vista para la subida de nuevos libros.
    *   **`config.js`:** Archivo de configuración para la URL de la API.
*   **`frontend/public/`:** Archivos estáticos del frontend (index.html, etc.).


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/main.py`

**Propósito:** Define las rutas y la lógica principal de la API FastAPI.  Gestiona la subida de libros, la consulta a la base de datos, el análisis con Gemini, la conversión de EPUB a PDF y los endpoints para el RAG.

**Funciones/Clases principales:**

*   `analyze_with_gemini(text: str) -> dict:` Analiza un texto dado usando Google Gemini para extraer el título, autor y categoría del libro. Retorna un diccionario con los resultados.  Maneja excepciones de la API de Gemini.
*   `process_pdf(file_path: str, static_dir: str) -> dict:` Procesa un archivo PDF para extraer texto y obtener una portada. Retorna un diccionario con el texto y la URL de la portada.
*   `process_epub(file_path: str, static_dir: str) -> dict:` Procesa un archivo EPUB para extraer texto y obtener una portada. Retorna un diccionario con el texto y la URL de la portada.  Maneja errores de extracción de texto.
*   `upload_book(...)`: Endpoint FastAPI para subir un libro. Valida el tipo de archivo, procesa el libro usando `process_pdf` o `process_epub`, analiza el texto con `analyze_with_gemini` y crea una nueva entrada en la base de datos mediante `crud.create_book`. Retorna un objeto `schemas.Book`.
*   `read_books(...)`: Endpoint FastAPI para obtener una lista de libros, con opciones de filtrado.
*   `get_books_count(...)`: Endpoint FastAPI para obtener el número total de libros.
*   `search_books(...)`: Endpoint FastAPI para buscar libros por título parcial, con paginación.
*   `read_categories(...)`: Endpoint FastAPI para obtener una lista de todas las categorías.
*   `delete_single_book(...)`: Endpoint FastAPI para eliminar un libro por su ID.
*   `delete_category_and_books(...)`: Endpoint FastAPI para eliminar una categoría y todos sus libros.
*   `download_book(...)`: Endpoint FastAPI para descargar un libro por su ID.
*   `convert_epub_to_pdf(...)`: Endpoint FastAPI para convertir un archivo EPUB a PDF.
*   `upload_book_for_rag(...)`: Endpoint FastAPI para subir un libro y procesarlo para RAG.
*   `query_rag_endpoint(...)`: Endpoint FastAPI para consultar el sistema RAG.
*   `index_existing_book_for_rag(...)`: Endpoint FastAPI para indexar un libro existente en RAG.
*   `rag_status(...)`: Endpoint FastAPI para obtener el estado del índice RAG de un libro.
*   `rag_reindex_category(...)`: Endpoint FastAPI para reindexar todos los libros de una categoría en RAG.
*   `rag_reindex_all(...)`: Endpoint FastAPI para reindexar todos los libros en RAG.
*   `estimate_rag_for_book(...)`: Endpoint FastAPI para estimar el coste y número de embeddings para un libro.
*   `estimate_rag_for_category(...)`: Endpoint FastAPI para estimar el coste y número de embeddings para una categoría.
*   `estimate_rag_for_all(...)`: Endpoint FastAPI para estimar el coste y número de embeddings para todos los libros.


### `backend/crud.py`

**Propósito:** Contiene las funciones CRUD (Create, Read, Update, Delete) para la interacción con la base de datos.

**Funciones principales:** (Documentación abreviada para concisión)

*   `get_book_by_path(db: Session, file_path: str)`: Obtiene un libro por su ruta de archivo.
*   `get_book_by_title(db: Session, title: str)`: Obtiene un libro por su título.
*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial (case-insensitive), con paginación.
*   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`: Obtiene libros con opciones de filtrado.
*   `get_categories(db: Session) -> list[str]` : Obtiene una lista de categorías únicas.
*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea un nuevo libro.
*   `delete_book(db: Session, book_id: int)`: Elimina un libro y sus archivos.
*   `delete_books_by_category(db: Session, category: str)`: Elimina libros de una categoría y sus archivos.
*   `get_books_count(db: Session) -> int`: Cuenta el número de libros.


### `backend/models.py`

**Propósito:** Define el modelo de datos `Book` para la base de datos.

**Clase principal:**

*   `Book(Base)`: Modelo SQLAlchemy que representa un libro.  Contiene atributos para el `id`, `title`, `author`, `category`, `cover_image_url` y `file_path`.


### `backend/rag.py`

**Propósito:** Implementa la funcionalidad de RAG (Retrieval Augmented Generation).

**Funciones principales:** (Documentación abreviada)

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`: Genera un embedding para un texto dado usando Google Gemini.
*   `extract_text_from_pdf(file_path: str) -> str`: Extrae texto de un archivo PDF.
*   `extract_text_from_epub(file_path: str) -> str`: Extrae texto de un archivo EPUB.
*   `extract_text(file_path: str) -> str`: Función unificada para extraer texto de PDF o EPUB.
*   `chunk_text(text: str, max_tokens: int = 1000) -> list[str]`: Divide el texto en chunks.
*   `_has_index_for_book(book_id: str) -> bool`: Comprueba si un libro tiene un índice en ChromaDB.
*   `delete_book_from_rag(book_id: str)`: Elimina el índice RAG de un libro.
*   `get_index_count(book_id: str) -> int`: Obtiene el número de vectores para un libro.
*   `has_index(book_id: str) -> bool`: Función pública para comprobar si un libro tiene índice RAG.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Procesa un libro para RAG: extrae texto, lo divide en chunks, genera embeddings y los almacena en ChromaDB.
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`: Estima el número de tokens y chunks para un archivo.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`: Estimación de tokens y chunks para múltiples archivos.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`: Consulta el sistema RAG.


### `backend/schemas.py`

**Propósito:** Define los esquemas Pydantic para la validación de datos.

**Clases principales:**

*   `BookBase(BaseModel)`: Esquema base para un libro.
*   `Book(BookBase)`: Esquema para un libro incluyendo el ID.
*   `ConversionResponse(BaseModel)`: Esquema para la respuesta de conversión EPUB a PDF.
*   `RagUploadResponse(BaseModel)`: Esquema para la respuesta de subida a RAG.
*   `RagQuery(BaseModel)`: Esquema para la consulta a RAG.
*   `RagQueryResponse(BaseModel)`: Esquema para la respuesta de RAG.


### `backend/utils.py`

**Propósito:** Contiene funciones auxiliares, incluyendo la configuración de la API key de Google Gemini.

**Función principal:**

*   `configure_genai()`: Configura la API key de Google Gemini leyendo la variable de entorno `GOOGLE_API_KEY` o `GEMINI_API_KEY`.  Lanza una excepción si la API key no se encuentra.


### `backend/database.py`

**Propósito:** Configura la conexión a la base de datos SQLite.

**Elementos principales:**

*   `SQLALCHEMY_DATABASE_URL`: Cadena de conexión a la base de datos.
*   `engine`: Objeto `create_engine` de SQLAlchemy.
*   `SessionLocal`:  Factory para crear sesiones SQLAlchemy.
*   `Base`: Clase base de SQLAlchemy.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

**Propósito:** Componente principal de la aplicación React.  Renderiza la cabecera y las rutas de la aplicación.

**Estado:** No tiene estado propio.

**Propiedades:** No tiene propiedades.

**Efectos secundarios:** No tiene efectos secundarios.

**Interacción con el backend:** No tiene interacciones directas con el backend.


### `frontend/src/LibraryView.js`

**Propósito:** Muestra la biblioteca de libros, permitiendo la búsqueda y paginación.

**Estado:**

*   `books`: Array de objetos que representan los libros.
*   `searchTerm`: Término de búsqueda del usuario.
*   `error`: Mensaje de error.
*   `loading`: Indica si se están cargando los datos.

**Propiedades:** No tiene propiedades.

**Efectos secundarios:**  Usa `useEffect` para obtener los libros del backend mediante `fetchBooks`.

**Interacción con el backend:**  Se comunica con el backend a través del endpoint `/books/`, usando parámetros de consulta para la búsqueda y paginación.  También usa un endpoint DELETE para eliminar libros.


### `frontend/src/UploadView.js`

**Propósito:** Permite a los usuarios subir libros (PDF o EPUB).

**Estado:**

*   `filesToUpload`: Array de objetos que representan los archivos a subir. Cada objeto incluye el archivo, el estado de subida y un mensaje.
*   `isUploading`: Booleano que indica si se está subiendo un archivo.

**Propiedades:** No tiene propiedades.

**Efectos secundarios:** No tiene efectos secundarios significativos.

**Interacción con el backend:** Se comunica con el backend a través del endpoint `/upload-book/` para subir cada archivo. Actualiza el estado de cada archivo individualmente.


### `frontend/src/ReaderView.js`

**Propósito:** Permite leer libros EPUB usando `react-reader`.

**Estado:**

*   `location`: Ubicación actual en el libro.
*   `epubData`: Datos del libro EPUB obtenidos del backend.
*   `isLoading`: Indica si se está cargando el libro.
*   `error`: Mensaje de error.

**Propiedades:** No tiene propiedades.

**Efectos secundarios:**  Usa `useEffect` para obtener los datos del libro EPUB del backend.

**Interacción con el backend:** Se comunica con el backend a través del endpoint `/books/download/:bookId` para descargar el archivo EPUB.


### `frontend/src/ToolsView.js`

**Propósito:**  Proporciona herramientas, actualmente un convertidor de EPUB a PDF.

**Estado:**

* `selectedFile`: Archivo EPUB seleccionado por el usuario.
* `message`: Mensaje al usuario (éxito, error, estado de conversión).
* `isLoading`: Indica si la conversión está en proceso.

**Propiedades:** No tiene propiedades.

**Efectos secundarios:** No hay efectos secundarios significativos.

**Interacción con el backend:** Utiliza el endpoint `/tools/convert-epub-to-pdf` para la conversión.


### `frontend/src/CategoriesView.js`

**Propósito:** Muestra una lista de categorías de libros.

**Estado:**

*   `categories`: Array de categorías obtenidas del backend.
*   `error`: Mensaje de error.
*   `loading`: Booleano que indica si se están cargando las categorías.

**Propiedades:** No tiene propiedades.

**Efectos secundarios:** Usa `useEffect` para obtener las categorías del backend mediante `/categories/`.

**Interacción con el backend:** Se comunica con el backend mediante el endpoint `/categories/`.


### `frontend/src/RagView.js`

**Propósito:** Permite al usuario consultar un modelo de IA sobre libros usando RAG.

**Estado:**

*   `message`: Mensajes al usuario.
*   `isLoading`: Indica si se está procesando una consulta.
*   `bookId`: ID del libro seleccionado para la conversación.
*   `chatHistory`: Historial de la conversación.
*   `currentQuery`: Consulta actual del usuario.
*   `libraryBooks`:  Libros disponibles en la biblioteca para seleccionar.
*   `selectedLibraryId`: ID del libro seleccionado de la lista.
*   `libStatus`: Estado del índice RAG del libro seleccionado.
*   `actionsBusy`: Indica si hay alguna acción pesada en ejecución (indexación, etc.)
*   `refreshing`: Indica si se está actualizando el estado de RAG.
*   `searchTerm`: Término de búsqueda para la selección de libro.
*   `searching`: Indica si se está buscando un libro.
*   `searchResults`: Resultados de la búsqueda.
*   `resultsOpen`: Indica si se muestran los resultados de búsqueda.
*   `mode`: Modo de respuesta de RAG (`strict`, `balanced`, `open`).
*   `selectedBook`: Datos del libro seleccionado.

**Propiedades:** No tiene propiedades.

**Efectos secundarios:** Usa varios `useEffect` para gestionar la carga de libros, la búsqueda, el auto-scroll y el estado del índice RAG.

**Interacción con el backend:** Se comunica con el backend a través de los endpoints `/rag/query/`, `/rag/status/:book_id` y `/rag/index/:book_id`.


### `frontend/src/Header.js`

**Propósito:** Componente de cabecera de la aplicación.

**Estado:**

* `menuOpen`: Indica si el menú está abierto.
* `bookCount`: Número de libros en la biblioteca.
* `errorMessage`: Mensaje de error al obtener el contador de libros.

**Propiedades:** No tiene propiedades.

**Efectos secundarios:** Usa `useEffect` para obtener el número de libros del backend (`/books/count`) y actualiza el contador cada minuto.

**Interacción con el backend:** Obtiene el conteo de libros del endpoint `/books/count`.


### `frontend/src/ErrorBoundary.js`

**Propósito:** Componente React para gestionar errores en la UI.  Muestra un mensaje de error si ocurre una excepción en uno de sus componentes hijos.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro a través de `UploadView.js`. Este componente envía el archivo al backend a través del endpoint `/upload-book/`. El backend procesa el archivo (extracción de texto, detección de portada), realiza un análisis con Gemini y guarda la información en la base de datos. La información del libro se retorna al frontend y se actualiza la interfaz.

Para leer el libro EPUB, `LibraryView.js` redirige al usuario a `ReaderView.js`, que obtiene los datos del libro (el contenido del archivo) del backend a través de `/books/download/:bookId` usando `ReactReader`.

La vista `LibraryView.js` obtiene los datos de los libros del endpoint `/books/` con los parámetros de filtrado necesarios.

La vista `CategoriesView.js` obtiene las categorías disponibles del endpoint `/categories/`.

La vista `ToolsView.js` utiliza el endpoint `/tools/convert-epub-to-pdf` para convertir un EPUB a PDF.

La vista `RagView.js` interactúa con los endpoints `/rag/query/` para las consultas al modelo de lenguaje, `/rag/status/:book_id` para comprobar el estado RAG de un libro y `/rag/index/:book_id` para (re)indexar libros.

**Endpoints de la API:**

*   `/upload-book/`: POST - Sube un libro.
*   `/books/`: GET - Obtiene libros (con opciones de filtrado).
*   `/books/count`: GET - Obtiene el número de libros.
*   `/books/search/`: GET - Busca libros por título parcial.
*   `/categories/`: GET - Obtiene categorías.
*   `/books/:book_id`: DELETE - Elimina un libro.
*   `/books/download/:book_id`: GET - Descarga un libro.
*   `/tools/convert-epub-to-pdf`: POST - Convierte EPUB a PDF.
*   `/rag/upload-book/`: POST - Sube un libro para RAG.
*   `/rag/query/`: POST - Consulta RAG.
*   `/rag/index/:book_id`: POST - Indexa un libro en RAG.
*   `/rag/status/:book_id`: GET - Estado del índice RAG.
*   `/rag/reindex/category/:category_name`: POST - Reindexa una categoría en RAG.
*   `/rag/reindex/all`: POST - Reindexa todos los libros en RAG.
*   `/rag/estimate/book/:book_id`: GET - Estimación de coste y número de embeddings para un libro.
*   `/rag/estimate/category/:category_name`: GET - Estimación de coste y número de embeddings para una categoría.
*   `/rag/estimate/all`: GET - Estimación de coste y número de embeddings para todos los libros.


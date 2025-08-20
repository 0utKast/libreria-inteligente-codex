# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales.  La aplicación ofrece funcionalidades de carga de libros (PDF y EPUB), búsqueda, visualización, eliminación y descarga de los mismos, organizados por categorías y autores. Además, integra un sistema de Recuperación de Información basada en Conocimiento (RAG) que permite a los usuarios interactuar mediante texto con el contenido de sus libros mediante una interfaz de chat con una IA.

La aplicación utiliza una arquitectura cliente-servidor: un frontend en React para la interfaz de usuario, un backend en FastAPI (Python) para el procesamiento y la API, y una base de datos SQLite para el almacenamiento persistente de la información de los libros.  El sistema RAG utiliza ChromaDB para indexar los libros y Google Gemini para generar respuestas.

## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   **`backend/`**: Contiene el backend de la aplicación, construido con FastAPI y Python. Incluye:
    *   **`alembic/`**:  Directorio para las migraciones de la base de datos.
    *   **`database.py`**:  Configuración de la base de datos SQLite.
    *   **`crud.py`**:  Lógica de acceso a datos (CRUD) para la base de datos.
    *   **`models.py`**:  Definición del modelo de datos para los libros.
    *   **`rag.py`**:  Lógica del sistema RAG para el procesamiento e indexación de libros y consultas.
    *   **`schemas.py`**:  Definición de los esquemas Pydantic para la serialización y validación de datos.
    *   **`utils.py`**: Funciones utilitarias, incluyendo la configuración de la API de Google Generative AI.
    *   **`main.py`**:  Archivo principal del backend que define las rutas de la API FastAPI.
    *   **`tests/`**:  Directorio para las pruebas unitarias del backend.

*   **`frontend/`**: Contiene el frontend de la aplicación, desarrollado con React.js.  La carpeta `src/` contiene:
    *   **`App.js`**:  Componente principal de la aplicación.
    *   **`CategoriesView.js`**:  Vista para la gestión de categorías.
    *   **`ErrorBoundary.js`**: Componente para el manejo de errores de la UI.
    *   **`Header.js`**: Componente de la cabecera.
    *   **`LibraryView.js`**:  Vista para la visualización de la biblioteca.
    *   **`RagView.js`**:  Vista para la interfaz de conversación con la IA (RAG).
    *   **`ReaderView.js`**:  Vista para la lectura de libros EPUB.
    *   **`ToolsView.js`**:  Vista para las herramientas (convertidor EPUB a PDF).
    *   **`UploadView.js`**: Vista para la carga de libros.
    *   **`config.js`**: Configuracion de la URL de la API.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/database.py`

*   **Propósito:** Define la configuración para conectarse a la base de datos SQLite.

### `backend/models.py`

*   **Propósito:** Define el modelo de datos `Book` para la base de datos.

    *   **Clase `Book`:**
        *   `id` (Integer, primary_key): ID único del libro.
        *   `title` (String, index): Título del libro.
        *   `author` (String, index): Autor del libro.
        *   `category` (String, index): Categoría del libro.
        *   `cover_image_url` (String, nullable=True): URL de la imagen de portada.
        *   `file_path` (String, unique): Ruta al archivo del libro.


### `backend/schemas.py`

*   **Propósito:** Define los esquemas Pydantic para la validación y serialización de datos.

    *   **Clase `BookBase`:** Esquema base para la creación de libros.
        *   `title` (str): Título del libro.
        *   `author` (str): Autor del libro.
        *   `category` (str): Categoría del libro.
        *   `cover_image_url` (str | None, optional): URL de la imagen de portada (opcional).
        *   `file_path` (str): Ruta al archivo del libro.

    *   **Clase `Book`:** Esquema completo para los libros, incluyendo el ID. Hereda de `BookBase`.
        *   `id` (int): ID del libro.

    *   **Clase `ConversionResponse`:** Esquema para la respuesta de la conversión EPUB a PDF.
        *   `download_url` (str): URL de descarga del PDF.

    *   **Clase `RagUploadResponse`:** Esquema para la respuesta de la subida de un libro al sistema RAG.
        *   `book_id` (str): ID del libro en RAG.
        *   `message` (str): Mensaje de estado.

    *   **Clase `RagQuery`:** Esquema para las consultas al sistema RAG.
        *   `query` (str): La consulta del usuario.
        *   `book_id` (str): ID del libro en RAG.
        *   `mode` (str | None, optional): Modo de consulta ('strict', 'balanced', 'open').

    *   **Clase `RagQueryResponse`:** Esquema para la respuesta de las consultas al sistema RAG.
        *   `response` (str): La respuesta de la IA.


### `backend/crud.py`

*   **Propósito:** Contiene la lógica de acceso a datos (CRUD) para la base de datos.

    *   **Función `get_book_by_path(db: Session, file_path: str)`:** Obtiene un libro por su ruta de archivo.
    *   **Función `get_book_by_title(db: Session, title: str)`:** Obtiene un libro por su título.
    *   **Función `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`:** Busca libros por un título parcial (sin distinción de mayúsculas/minúsculas).
    *   **Función `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`:** Obtiene una lista de libros, filtrando opcionalmente por categoría, término de búsqueda y/o autor.
    *   **Función `get_categories(db: Session)`:** Obtiene una lista de todas las categorías únicas.
    *   **Función `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`:** Crea un nuevo libro en la base de datos.
    *   **Función `delete_book(db: Session, book_id: int)`:** Elimina un libro de la base de datos y sus archivos asociados.
    *   **Función `delete_books_by_category(db: Session, category: str)`:** Elimina todos los libros de una categoría y sus archivos asociados.
    *   **Función `get_books_count(db: Session)`:** Obtiene el número total de libros en la base de datos.


### `backend/rag.py`

*   **Propósito:** Implementa la lógica del sistema RAG (Recuperación de Información basada en Conocimiento).

    *   **Función `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`:** Genera una incrustación (embedding) para un texto dado usando Google Gemini.  Si `DISABLE_AI` está en el entorno, devuelve una incrustación dummy.
    *   **Función `extract_text_from_pdf(file_path: str)`:** Extrae texto de un archivo PDF.
    *   **Función `extract_text_from_epub(file_path: str)`:** Extrae texto de un archivo EPUB.
    *   **Función `extract_text(file_path: str)`:** Función unificada para extraer texto de archivos PDF y EPUB.
    *   **Función `chunk_text(text: str, max_tokens: int = 1000)`:** Divide un texto en fragmentos más pequeños basándose en el conteo de tokens.
    *   **Función `_has_index_for_book(book_id: str)`:** Comprueba si existe un índice para un libro en ChromaDB.
    *   **Función `delete_book_from_rag(book_id: str)`:** Elimina los vectores de un libro de ChromaDB.
    *   **Función `get_index_count(book_id: str)`:** Obtiene el número de vectores para un libro en ChromaDB.
    *   **Función `has_index(book_id: str)`:** Devuelve si el libro está indexado en RAG.
    *   **Función `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`:** Procesa un libro para el sistema RAG: extrae texto, lo divide en fragmentos, genera incrustaciones y las almacena en ChromaDB.
    *   **Función `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`:** Estima el número de tokens y fragmentos para un archivo.
    *   **Función `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`:** Estima el número de tokens y fragmentos para una lista de archivos.
    *   **Función `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`:** Realiza una consulta al sistema RAG para obtener una respuesta basada en el contenido de un libro.


### `backend/utils.py`

*   **Propósito:**  Funciones utilitarias, principalmente para configurar la API de Google Generative AI.

    *   **Función `configure_genai()`:** Configura la API de Google Generative AI utilizando la clave API del archivo `.env`.


### `backend/main.py`

*   **Propósito:** Archivo principal del backend, define las rutas de la API FastAPI.

    *   **Función `analyze_with_gemini(text: str)`:** Analiza texto con Gemini para obtener el título, autor y categoría de un libro.
    *   **Función `process_pdf(file_path: str, static_dir: str)`:** Procesa archivos PDF, extrayendo texto e imágenes de portada.
    *   **Función `process_epub(file_path: str, static_dir: str)`:** Procesa archivos EPUB, extrayendo texto e imágenes de portada.
    *   **Ruta `/upload-book/` (POST):** Carga un libro, lo analiza con Gemini y lo guarda en la base de datos.
    *   **Ruta `/books/` (GET):** Devuelve una lista de libros, filtrando opcionalmente por categoría y término de búsqueda.
    *   **Ruta `/books/count` (GET):** Devuelve el número total de libros.
    *   **Ruta `/books/search/` (GET):** Busca libros por un título parcial.
    *   **Ruta `/categories/` (GET):** Devuelve una lista de categorías.
    *   **Ruta `/books/{book_id}` (DELETE):** Elimina un libro.
    *   **Ruta `/categories/{category_name}` (DELETE):** Elimina una categoría y sus libros.
    *   **Ruta `/books/download/{book_id}` (GET):** Permite descargar un libro.
    *   **Ruta `/tools/convert-epub-to-pdf` (POST):** Convierte un archivo EPUB a PDF.
    *   **Ruta `/rag/upload-book/` (POST):** Sube un libro al sistema RAG.
    *   **Ruta `/rag/query/` (POST):** Consulta el sistema RAG.
    *   **Ruta `/rag/index/{book_id}` (POST):** Indexa un libro en RAG.
    *   **Ruta `/rag/status/{book_id}` (GET):** Obtiene el estado del índice RAG de un libro.
    *   **Ruta `/rag/reindex/category/{category_name}` (POST):** Reindexa todos los libros de una categoría en RAG.
    *   **Ruta `/rag/reindex/all` (POST):** Reindexa todos los libros en RAG.
    *   **Ruta `/rag/estimate/book/{book_id}` (GET):** Estima el coste y los tokens de indexar un libro.
    *   **Ruta `/rag/estimate/category/{category_name}` (GET):** Estima el coste y los tokens de indexar una categoría.
    *   **Ruta `/rag/estimate/all` (GET):** Estima el coste y los tokens de indexar la biblioteca completa.



## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

*   **Propósito:** Componente principal de la aplicación, renderiza las diferentes vistas según la ruta.
*   **Estado:** No tiene estado.
*   **Propiedades:** No tiene propiedades.
*   **Efectos secundarios:** No tiene efectos secundarios.
*   **Interacción con el backend:** No interactúa directamente con el backend.


### `frontend/src/Header.js`

*   **Propósito:** Componente de cabecera que muestra el título de la aplicación, un contador de libros y un menú de navegación.
*   **Estado:**
    *   `menuOpen` (boolean): Indica si el menú está abierto o cerrado.
    *   `bookCount` (number): Contador de libros.
    *   `errorMessage` (string): Mensaje de error para el contador de libros.
*   **Propiedades:** No tiene propiedades.
*   **Efectos secundarios:**  Realiza una petición al backend para obtener el número total de libros y actualiza el estado `bookCount`. Refresca el contador periódicamente.
*   **Interacción con el backend:**  Realiza una petición GET a `/books/count` para obtener el contador de libros.


### `frontend/src/LibraryView.js`

*   **Propósito:** Visualiza la lista de libros de la biblioteca.  Permite la búsqueda y filtrado por categoría y autor.  Incluye funcionalidad de eliminación de libros.
*   **Estado:**
    *   `books` (array): Array de objetos con la información de los libros.
    *   `searchTerm` (string): Término de búsqueda actual.
    *   `error` (string): Mensaje de error.
    *   `loading` (boolean): Indica si se está cargando la lista de libros.
    *   `isMobile` (boolean): Indica si el dispositivo es móvil.
*   **Propiedades:** No tiene propiedades.
*   **Efectos secundarios:**  Realiza una petición GET a `/books/` para obtener la lista de libros, incluyendo búsqueda, filtrado y paginación.
*   **Interacción con el backend:** Realiza peticiones GET a `/books/` (con parámetros opcionales) y DELETE a `/books/{book_id}`.


### `frontend/src/UploadView.js`

*   **Propósito:** Permite a los usuarios subir uno o varios archivos de libros (PDF o EPUB) y los envía al backend para su procesamiento.
*   **Estado:**
    *   `filesToUpload` (array): Array de objetos que representan los archivos a subir, cada uno con estado ('pending', 'uploading', 'success', 'error') y mensaje.
    *   `isUploading` (boolean): Indica si se está subiendo un archivo.
*   **Propiedades:** No tiene propiedades.
*   **Efectos secundarios:** No tiene efectos secundarios explícitos.
*   **Interacción con el backend:** Realiza peticiones POST a `/upload-book/`.


### `frontend/src/ReaderView.js`

*   **Propósito:** Permite leer libros EPUB usando la librería `react-reader`.
*   **Estado:**
    *   `location` (object): Ubicación actual en el libro EPUB.
    *   `epubData` (ArrayBuffer): Datos del archivo EPUB.
    *   `isLoading` (boolean): Indica si se está cargando el libro.
    *   `error` (string): Mensaje de error.
*   **Propiedades:** Recibe el `bookId` como parámetro de ruta.
*   **Efectos secundarios:** Realiza una petición GET a `/books/download/{bookId}` para obtener el libro.
*   **Interacción con el backend:** Realiza una petición GET a `/books/download/{bookId}`.


### `frontend/src/ToolsView.js`

*   **Propósito:** Contiene las herramientas de la aplicación, actualmente solo un convertidor de EPUB a PDF.
*   **Estado:**  
    * `selectedFile` (File): Archivo EPUB seleccionado para convertir
    * `message` (string): Mensaje de estado para la conversión
    * `isLoading` (boolean): Indica si la conversión está en progreso
*   **Propiedades:** No tiene propiedades.
*   **Efectos secundarios:** No tiene efectos secundarios explícitos.
*   **Interacción con el backend:** Realiza una petición POST a `/tools/convert-epub-to-pdf`.


### `frontend/src/CategoriesView.js`

*   **Propósito:**  Muestra una lista de todas las categorías de libros disponibles en la base de datos.
*   **Estado:**
    *   `categories` (array): Array de strings con las categorías.
    *   `error` (string): Mensaje de error.
    *   `loading` (boolean): Indica si se está cargando la lista de categorías.
*   **Propiedades:** No tiene propiedades.
*   **Efectos secundarios:**  Realiza una petición GET a `/categories/`.
*   **Interacción con el backend:** Realiza una petición GET a `/categories/`.


### `frontend/src/RagView.js`

*   **Propósito:** Permite a los usuarios realizar consultas al sistema RAG mediante una interfaz de chat.
*   **Estado:**
    *   `message` (string): Mensaje de estado
    *   `isLoading` (boolean): Indica si la consulta esta en progreso
    *   `bookId` (string): El ID del libro seleccionado para la conversación.
    *   `chatHistory` (array): Historial de mensajes del chat
    *   `currentQuery` (string): Consulta actual del usuario.
    *   `libraryBooks` (array): Array con los libros disponibles en la biblioteca para selección.
    *   `selectedLibraryId` (string): ID del libro seleccionado de la biblioteca.
    *   `libStatus` (object):  Estado del índice RAG del libro seleccionado (loading, indexed, error).
    *   `actionsBusy` (boolean): Indica si hay acciones pesadas en progreso.
    *   `refreshing` (boolean): Indica que hay una operación de refresco en curso.
    *   `searchTerm` (string): Término de búsqueda para los libros.
    *   `searching` (boolean): Indica si se está buscando.
    *   `searchResults` (array): Resultados de la búsqueda.
    *   `resultsOpen` (boolean): Indica si la lista de resultados está abierta.
    *   `mode` (string): Modo de respuesta de la IA ('strict', 'balanced', 'open').
    *   `selectedBook` (object): libro seleccionado de la biblioteca.
*   **Propiedades:** No tiene propiedades.
*   **Efectos secundarios:**  Gestiona la búsqueda de libros y realiza varias peticiones al backend (`/books/`, `/rag/status/{book_id}`, `/rag/index/{book_id}`, `/rag/query/`).
*   **Interacción con el backend:**  Realiza peticiones GET a `/books/`, `/rag/status/{book_id}`, POST a `/rag/index/{book_id}` y POST a `/rag/query/`.

### `frontend/src/ErrorBoundary.js`

*   **Propósito:** Componente para capturar y mostrar errores en la interfaz de usuario de React.
*   **Estado:**
    *   `hasError` (boolean): Indica si hay un error.
    *   `error` (Error): Objeto del error capturado.
*   **Propiedades:**  Recibe los componentes hijo como `children`.
*   **Efectos secundarios:** No tiene efectos secundarios explícitos.
*   **Interacción con el backend:** No interactúa directamente con el backend.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un archivo de libro en `UploadView.js`.  El frontend realiza una petición POST a `/upload-book/` en el backend, enviando el archivo. El backend (`main.py`) procesa el archivo, extrayendo el texto y (opcionalmente) la imagen de portada. Luego, utiliza `analyze_with_gemini` para obtener el título, autor y categoría. Finalmente, se crea una entrada en la base de datos a través de `crud.create_book`.  Si la operación es exitosa, el estado del archivo en `UploadView.js` se actualiza a "success".

En `RagView.js`, las consultas del usuario al sistema RAG se realizan mediante una petición POST a `/rag/query/`, incluyendo el ID del libro (que fue previamente indexado) y el modo de consulta. El backend (`rag.py` y `main.py`) recupera las incrustaciones relevantes de ChromaDB, construye una consulta para Gemini y devuelve la respuesta a través de la API.

**Endpoints de la API:**

*   **POST `/upload-book/`**: Sube un libro.
*   **GET `/books/`**: Obtiene una lista de libros (filtrable por categoría y búsqueda).
*   **GET `/books/count`**: Obtiene el número total de libros.
*   **GET `/books/search/`**: Busca libros por título parcial.
*   **GET `/categories/`**: Obtiene la lista de categorías.
*   **DELETE `/books/{book_id}`**: Elimina un libro.
*   **DELETE `/categories/{category_name}`**: Elimina una categoría y sus libros.
*   **GET `/books/download/{book_id}`**: Descarga un libro.
*   **POST `/tools/convert-epub-to-pdf`**: Convierte un EPUB a PDF.
*   **POST `/rag/upload-book/`**: Sube un libro al índice RAG.
*   **POST `/rag/query/`**: Realiza una consulta RAG.
*   **POST `/rag/index/{book_id}`**: Indexa un libro en RAG.
*   **GET `/rag/status/{book_id}`**: Obtiene el estado del índice RAG de un libro.
*   **POST `/rag/reindex/category/{category_name}`**: Reindexa una categoría en RAG.
*   **POST `/rag/reindex/all`**: Reindexa todos los libros en RAG.
*   **GET `/rag/estimate/book/{book_id}`**: Estima el coste de indexar un libro.
*   **GET `/rag/estimate/category/{category_name}`**: Estima el coste de indexar una categoría.
*   **GET `/rag/estimate/all`**: Estima el coste de indexar toda la biblioteca.


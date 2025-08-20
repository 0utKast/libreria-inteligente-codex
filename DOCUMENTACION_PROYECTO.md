# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitalmente.  La aplicación ofrece funcionalidades para subir libros (PDF y EPUB), visualizarlos, buscarlos por título, autor o categoría, convertir EPUB a PDF y, mediante la integración de una IA, realizar consultas sobre el contenido de los libros.

La aplicación tiene una arquitectura cliente-servidor. El frontend está desarrollado en React, ofreciendo una interfaz intuitiva y moderna.  El backend utiliza FastAPI (Python) para manejar las peticiones del frontend, procesar los libros, gestionar la base de datos y comunicarse con la API de Google Gemini para las funcionalidades de IA.  La persistencia de datos se realiza mediante una base de datos SQLite.  La recuperación de información basada en el contenido de los libros se lleva a cabo mediante un sistema RAG (Retrieval Augmented Generation) usando ChromaDB para la indexación y Google Gemini para generar las respuestas.

## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   **`backend/`:** Contiene el código del backend de la aplicación, utilizando FastAPI y Python.  Dentro de esta carpeta se encuentran subcarpetas para la base de datos (`alembic/`), modelos (`models.py`), rutas (`main.py`), lógica de acceso a datos (`crud.py`), esquemas de datos (`schemas.py`), utilidades (`utils.py`), lógica RAG (`rag.py`) y pruebas (`tests/`).

*   **`frontend/src/`:** Contiene el código del frontend, desarrollado con React.  Se incluyen componentes para la visualización de la biblioteca (`LibraryView.js`), subida de libros (`UploadView.js`), gestión de categorías (`CategoriesView.js`), herramientas (`ToolsView.js`), lectura de libros (`ReaderView.js`), interfaz de conversación con la IA (`RagView.js`), encabezado (`Header.js`) y un componente para gestionar errores (`ErrorBoundary.js`).  `index.js` es el punto de entrada de la aplicación React, y `App.js` es el componente principal que enruta las peticiones.  El archivo `config.js` contiene la URL del backend.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/main.py`

*   **Propósito:** Define las rutas y la lógica principal de la API FastAPI.  Gestiona la subida y procesamiento de libros, la consulta de la biblioteca, la gestión de categorías y las herramientas adicionales, así como la integración con el sistema RAG.

*   **Funciones/Clases Principales:**

    *   `upload_book`: Recibe un archivo de libro (UploadFile), lo procesa usando `process_pdf` o `process_epub`, lo analiza con Gemini usando `analyze_with_gemini` y lo crea en la base de datos a través de `crud.create_book`. Devuelve un objeto `schemas.Book`.
    *   `read_books`:  Obtiene una lista de libros de la base de datos usando `crud.get_books`, permitiendo filtrado por categoría, búsqueda general y autor. Devuelve una lista de objetos `schemas.Book`.
    *   `get_books_count`: Obtiene el número total de libros usando `crud.get_books_count`. Devuelve un entero.
    *   `search_books`:  Busca libros por un título parcial usando `crud.get_books_by_partial_title`, con paginación. Devuelve una lista de objetos `schemas.Book`.
    *   `read_categories`: Obtiene una lista de todas las categorías únicas usando `crud.get_categories`. Devuelve una lista de strings.
    *   `delete_single_book`: Elimina un libro de la base de datos y sus archivos asociados usando `crud.delete_book`,  también limpia el índice RAG.  Devuelve un mensaje de confirmación.
    *   `delete_category_and_books`: Elimina todos los libros de una categoría y sus archivos asociados, limpiando los índices RAG. Devuelve un mensaje de confirmación y el número de libros eliminados.
    *   `download_book`: Descarga un libro desde la base de datos usando `FileResponse`. Devuelve una respuesta de archivo.
    *   `convert_epub_to_pdf`: Convierte un archivo EPUB a PDF. Devuelve un JSON con la URL del PDF generado.
    *   `upload_book_for_rag`: Sube un libro para procesarlo con RAG. Devuelve un JSON con el `book_id` y un mensaje de confirmación.
    *   `query_rag_endpoint`: Realiza una consulta al sistema RAG usando `rag.query_rag`. Devuelve un JSON con la respuesta de la IA.
    *   `index_existing_book_for_rag`: Indexa un libro existente en la base de datos para RAG.
    *   `rag_status`: Obtiene el estado de indexación RAG para un libro.
    *   `rag_reindex_category`: Reindexa todos los libros de una categoría en RAG.
    *   `rag_reindex_all`: Reindexa todos los libros en RAG.
    *   `estimate_rag_for_book`, `estimate_rag_for_category`, `estimate_rag_for_all`: Estiman tokens/chunks y coste opcional para el indexado de libros.



### `backend/crud.py`

*   **Propósito:** Define las funciones de acceso a datos (CRUD) para interactuar con la base de datos.

*   **Funciones Principales:**

    *   `get_book_by_path`: Obtiene un libro por su `file_path`. Devuelve un objeto `models.Book` o `None`.
    *   `get_book_by_title`: Obtiene un libro por su título exacto. Devuelve un objeto `models.Book` o `None`.
    *   `get_books_by_partial_title`: Busca libros por un título parcial (case-insensitive), con paginación. Devuelve una lista de objetos `models.Book`.
    *   `get_books`: Obtiene una lista de libros, con opciones de filtrado. Devuelve una lista de objetos `models.Book`.
    *   `get_categories`: Obtiene una lista de todas las categorías únicas. Devuelve una lista de strings.
    *   `create_book`: Crea un nuevo libro en la base de datos. Devuelve el objeto `models.Book` recién creado.
    *   `delete_book`: Elimina un libro de la base de datos y elimina los archivos asociados. Devuelve el objeto `models.Book` eliminado o `None`.
    *   `delete_books_by_category`: Elimina todos los libros de una categoría dada y elimina sus archivos. Devuelve el número de libros eliminados.
    *   `get_books_count`: Obtiene el número total de libros en la base de datos. Devuelve un entero.


### `backend/models.py`

*   **Propósito:** Define el modelo de datos `Book` para la base de datos SQLAlchemy.

*   **Clase Principal:**

    *   `Book`: Representa un libro en la base de datos, con atributos para `id`, `title`, `author`, `category`, `cover_image_url` y `file_path`.


### `backend/rag.py`

*   **Propósito:** Implementa la lógica del sistema RAG para indexar y consultar libros.

*   **Funciones Principales:**

    *   `get_embedding`: Genera un embedding para un texto dado usando la API de Google Gemini o una función dummy si la IA está deshabilitada.  Devuelve una lista de floats.
    *   `extract_text_from_pdf`, `extract_text_from_epub`: Extraen texto de archivos PDF y EPUB, respectivamente. Devuelven un string con el texto extraído.
    *   `extract_text`: Función unificada para la extracción de texto.
    *   `chunk_text`: Divide un texto en chunks más pequeños basados en el conteo de tokens. Devuelve una lista de strings.
    *   `_has_index_for_book`: Verifica si un libro ya está indexado en ChromaDB. Devuelve un booleano.
    *   `delete_book_from_rag`: Elimina los vectores de un libro de ChromaDB.
    *   `get_index_count`: Obtiene el número de vectores indexados para un libro. Devuelve un entero.
    *   `has_index`: Función pública para verificar si un libro está indexado en RAG.
    *   `process_book_for_rag`: Procesa un libro para el sistema RAG: extrae texto, lo divide en chunks, genera embeddings y los guarda en ChromaDB.
    *   `estimate_embeddings_for_file`, `estimate_embeddings_for_files`: Estiman el número de tokens y chunks para uno o varios archivos.
    *   `query_rag`: Realiza una consulta al sistema RAG usando Google Gemini. Devuelve la respuesta de la IA.

### `backend/schemas.py`

*   **Propósito:** Define los modelos Pydantic para la validación y serialización de datos.

*   **Clases Principales:**

    *   `BookBase`: Modelo base para la creación de libros.
    *   `Book`: Modelo completo para los libros, incluyendo el ID.
    *   `ConversionResponse`: Modelo para la respuesta de conversión de EPUB a PDF.
    *   `RagUploadResponse`: Modelo para la respuesta de subida de libro a RAG.
    *   `RagQuery`: Modelo para las consultas al sistema RAG.
    *   `RagQueryResponse`: Modelo para la respuesta de las consultas RAG.

### `backend/database.py`

*   **Propósito:** Configura la conexión a la base de datos SQLite.

### `backend/utils.py`

*   **Propósito:** Contiene funciones utilitarias, incluyendo la configuración de la API Key de Google Gemini.

*   **Funciones Principales:**

    *   `configure_genai`: Configura la API Key de Google Gemini a partir de las variables de entorno `GOOGLE_API_KEY` o `GEMINI_API_KEY`.


### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

*   **Propósito:** Script Alembic para crear la tabla `books` en la base de datos.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

*   **Propósito:** Componente principal de la aplicación React, gestiona las rutas.  No mantiene estado propio.


### `frontend/src/Header.js`

*   **Propósito:** Componente para el encabezado de la aplicación, incluyendo la navegación.

*   **Estado:** `menuOpen`, `bookCount`, `errorMessage`.

*   **Efectos:** Obtiene el conteo de libros del backend y actualiza el estado `bookCount` periódicamente. Maneja errores en la carga del conteo.

*   **Interacción Usuario:** Botón de menú hamburguesa para abrir/cerrar la navegación.  Enlaces a diferentes vistas.


### `frontend/src/LibraryView.js`

*   **Propósito:** Muestra la lista de libros.

*   **Estado:** `books`, `searchTerm`, `error`, `loading`, `isMobile`.

*   **Efectos:**  Carga la lista de libros del backend usando `fetchBooks`, y gestiona el debounce de la búsqueda, además de la detección de dispositivos móviles.

*   **Interacción Usuario:**  Busca libros por título, autor o categoría; elimina libros.  Enlaces para ver libros EPUB en el componente `ReaderView`.


### `frontend/src/UploadView.js`

*   **Propósito:** Permite a los usuarios subir libros al backend.

*   **Estado:** `filesToUpload`, `isUploading`.

*   **Efectos:**  No hay efectos secundarios notables.

*   **Interacción Usuario:**  Permite la selección múltiple de archivos mediante arrastrar y soltar o selección desde el sistema de archivos.  Envía los archivos al backend usando `fetch` y actualiza el estado de cada archivo (pending, uploading, success, error).  Navegación a la vista de biblioteca tras la subida de archivos.


### `frontend/src/ReaderView.js`

*   **Propósito:** Permite leer libros EPUB usando `react-reader`.

*   **Estado:** `location`, `epubData`, `isLoading`, `error`.

*   **Efectos:** Carga el archivo EPUB desde el backend usando `fetch`.

*   **Interacción Usuario:**  Navegación dentro del libro EPUB.


### `frontend/src/ToolsView.js`

*   **Propósito:** Ofrece herramientas para la conversión de EPUB a PDF.

*   **Estado:** `selectedFile`, `message`, `isLoading`.

*   **Efectos:**  No hay efectos secundarios notables.

*   **Interacción Usuario:**  Permite seleccionar un archivo EPUB, convertirlo a PDF llamando al endpoint `/tools/convert-epub-to-pdf` del backend y descarga el archivo resultante.


### `frontend/src/CategoriesView.js`

*   **Propósito:** Muestra una lista de categorías de libros.

*   **Estado:** `categories`, `error`, `loading`.

*   **Efectos:** Obtiene las categorías desde el backend usando `fetch`.

*   **Interacción Usuario:**  Enlaces a la vista de la biblioteca, filtrando por la categoría seleccionada.


### `frontend/src/RagView.js`

*   **Propósito:** Implementa la interfaz de conversación con la IA.

*   **Estado:** `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.

*   **Efectos:**  Carga la lista de libros de la biblioteca, gestiona el debounce de la búsqueda, y actualiza el estado de la conversación.

*   **Interacción Usuario:**  Permite seleccionar un libro para chatear. Envía consultas al backend usando `fetch` y muestra la respuesta de la IA. Permite indexar/reindexar el libro para el sistema RAG.


### `frontend/src/ErrorBoundary.js`

*   **Propósito:** Componente React para gestionar errores dentro de la aplicación.


### `frontend/src/config.js`

*   **Propósito:** Define la URL base de la API del backend.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro en `UploadView.js`.  El frontend envía el archivo al endpoint `/upload-book/` del backend usando `fetch`. El backend procesa el libro (`process_pdf` o `process_epub`), analiza el texto con Gemini (`analyze_with_gemini`) para obtener los metadatos (título, autor, categoría), y guarda la información en la base de datos a través de `crud.create_book`. Luego, el frontend actualiza la lista de libros.

Para consultar la biblioteca, el frontend llama al endpoint `/books/` con parámetros opcionales para filtrar por categoría, búsqueda general o autor. El backend devuelve una lista de libros en formato JSON, que el frontend muestra en `LibraryView.js`.

La conversión de EPUB a PDF se realiza llamando al endpoint `/tools/convert-epub-to-pdf` con el archivo EPUB. El backend procesa la conversión y devuelve la URL del PDF generado, que el frontend descarga.

El sistema RAG se usa para consultar el contenido de los libros. El usuario selecciona un libro y realiza una consulta en `RagView.js`. El frontend envía la consulta al endpoint `/rag/query/` del backend incluyendo el `book_id` y el `mode`. El backend realiza la consulta al sistema RAG utilizando `rag.query_rag` y retorna la respuesta en formato JSON que el frontend muestra.

**Principales Endpoints de la API:**

*   `/upload-book/`: Sube y procesa un libro.  Método POST.
*   `/books/`: Obtiene una lista de libros.  Método GET.  Admite parámetros `category`, `search` y `author`.
*   `/books/count`: Obtiene el conteo de libros. Método GET.
*   `/books/search/`: Busca libros por un título parcial. Método GET.
*   `/categories/`: Obtiene la lista de categorías. Método GET.
*   `/books/{book_id}`: Elimina un libro. Método DELETE.
*   `/tools/convert-epub-to-pdf`: Convierte EPUB a PDF. Método POST.
*   `/rag/upload-book/`: Sube un libro para procesarlo con RAG. Método POST.
*   `/rag/query/`: Consulta al sistema RAG. Método POST.
*   `/rag/index/{book_id}`: Indexa un libro existente en RAG. Método POST.
*   `/rag/status/{book_id}`: Obtiene el estado de indexación RAG. Método GET.
*   `/rag/reindex/category/{category_name}`: Reindexa una categoría. Método POST.
*   `/rag/reindex/all`: Reindexa todos los libros. Método POST.
*   `/books/download/{book_id}`: Descarga un libro. Método GET.


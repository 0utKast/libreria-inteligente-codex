# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitalmente.  La aplicación facilita la carga de libros en formato PDF y EPUB, realiza un análisis automático de metadatos utilizando una IA (Google Gemini), y proporciona una interfaz de usuario intuitiva para visualizar, buscar y gestionar la colección.  La aplicación incluye además una funcionalidad de conversacion con IA (RAG) que permite realizar consultas sobre el contenido de los libros indexados.

La arquitectura de la aplicación se basa en una estructura cliente-servidor:

* **Frontend:** Desarrollado con React.js, proporciona una interfaz de usuario amigable para la interacción con el usuario.
* **Backend:** Desarrollado con FastAPI (Python), maneja la lógica del negocio, el procesamiento de archivos, la interacción con la base de datos y la API.
* **Base de Datos:** Emplea SQLite para almacenar la información de los libros.
* **IA (Google Gemini):** Se utiliza para el análisis automático de metadatos y la generación de respuestas en el sistema RAG.
* **RAG (Retrieval Augmented Generation):** Permite realizar consultas sobre el contenido de los libros utilizando un índice ChromaDB y Google Gemini.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   `backend/`: Contiene el código del backend de la aplicación, escrito en Python utilizando FastAPI.  Incluye:
    *   `alembic/`: Directorio para las migraciones de la base de datos.
    *   `database.py`: Configuración de la base de datos.
    *   `crud.py`: Lógica de acceso a datos (CRUD).
    *   `main.py`: Archivo principal del backend, con la configuración de FastAPI y los endpoints de la API.
    *   `models.py`: Definición del modelo de datos para los libros.
    *   `rag.py`: Lógica para el sistema de recuperación aumentada de generación (RAG).
    *   `schemas.py`: Definición de los esquemas Pydantic para la serialización y validación de datos.
    *   `utils.py`: Funciones auxiliares.
    *   `tests/`: Contiene las pruebas unitarias del backend.


*   `frontend/`: Contiene el código del frontend de la aplicación, escrito en React.js.  Incluye:
    *   `src/`: Directorio con el código fuente del frontend.
    *   `public/`: Archivos estáticos del frontend.
    *   `index.js`: Archivo principal de la aplicación React.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/schemas.py`

**Propósito:** Define los esquemas Pydantic para la serialización y validación de datos.

*   **Clase `BookBase`:** Modelo base para la información de un libro.
    *   `title: str`: Título del libro (requerido).
    *   `author: str`: Autor del libro (requerido).
    *   `category: str`: Categoría del libro (requerido).
    *   `cover_image_url: str | None = None`: URL de la imagen de portada (opcional).
    *   `file_path: str`: Ruta al archivo del libro (requerido).

*   **Clase `Book`:** Modelo completo para un libro, incluyendo el ID. Hereda de `BookBase`.
    *   `id: int`: ID único del libro (requerido).

*   **Clase `ConversionResponse`:**  Respuesta para la conversión de EPUB a PDF.
    *   `download_url: str`: URL de descarga del PDF.

*   **Clase `RagUploadResponse`:** Respuesta para la subida de un libro al sistema RAG.
    *   `book_id: str`: ID del libro en el sistema RAG.
    *   `message: str`: Mensaje de estado.

*   **Clase `RagQuery`:**  Solicitud para una consulta RAG.
    *   `query: str`: Consulta del usuario.
    *   `book_id: str`: ID del libro en el sistema RAG.
    *   `mode: str | None = None`: Modo de consulta ('strict', 'balanced', 'open').

*   **Clase `RagQueryResponse`:** Respuesta para una consulta RAG.
    *   `response: str`: Respuesta generada por la IA.


### `backend/crud.py`

**Propósito:**  Proporciona la lógica de acceso a datos (CRUD) para los libros.

*   `get_book_by_path(db: Session, file_path: str)`: Obtiene un libro por su ruta de archivo. Retorna un objeto `models.Book` o `None`.
*   `get_book_by_title(db: Session, title: str)`: Obtiene un libro por su título exacto. Retorna un objeto `models.Book` o `None`.
*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial (case-insensitive). Retorna una lista de objetos `models.Book`.
*   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`: Obtiene una lista de libros, con opciones de filtrado. Retorna una lista de objetos `models.Book`.
*   `get_categories(db: Session) -> list[str]`: Obtiene una lista de todas las categorías únicas. Retorna una lista de strings.
*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea un nuevo libro en la base de datos. Retorna un objeto `models.Book`.
*   `delete_book(db: Session, book_id: int)`: Elimina un libro de la base de datos por su ID, incluyendo sus archivos asociados. Retorna el objeto `models.Book` eliminado o `None`.
*   `delete_books_by_category(db: Session, category: str)`: Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados. Retorna el número de libros eliminados.
*   `get_books_count(db: Session) -> int`: Obtiene el número total de libros en la base de datos. Retorna un entero.


### `backend/database.py`

**Propósito:** Configura la conexión a la base de datos SQLite.

*   Define `SQLALCHEMY_DATABASE_URL`, `engine` y `SessionLocal`.


### `backend/utils.py`

**Propósito:**  Funciones utilitarias.

*   `configure_genai()`: Configura la API Key de Google Gemini desde el archivo .env.  Lanza una excepción `ValueError` si no se encuentra la API Key.


### `backend/models.py`

**Propósito:** Define el modelo de datos `Book` para la base de datos.

*   **Clase `Book`:**  Representa un libro en la base de datos.
    *   `id`: ID único (entero, clave primaria).
    *   `title`: Título (string).
    *   `author`: Autor (string).
    *   `category`: Categoría (string).
    *   `cover_image_url`: URL de la imagen de portada (string, nullable).
    *   `file_path`: Ruta al archivo del libro (string, unique).


### `backend/rag.py`

**Propósito:** Implementa la lógica para el sistema RAG.

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`: Genera una embedding para el texto dado. Retorna una lista de floats.
*   `extract_text_from_pdf(file_path: str) -> str`: Extrae texto de un archivo PDF. Retorna un string.
*   `extract_text_from_epub(file_path: str) -> str`: Extrae texto de un archivo EPUB. Retorna un string.
*   `extract_text(file_path: str) -> str`: Función unificada para la extracción de texto de PDFs y EPUBs. Retorna un string.
*   `chunk_text(text: str, max_tokens: int = 1000) -> list[str]`: Divide el texto en fragmentos. Retorna una lista de strings.
*   `_has_index_for_book(book_id: str) -> bool`: Comprueba si existe un índice para un libro. Retorna un booleano.
*   `delete_book_from_rag(book_id: str)`: Elimina el índice de un libro.
*   `get_index_count(book_id: str) -> int`:  Obtiene el número de vectores para un libro. Retorna un entero.
*   `has_index(book_id: str) -> bool`: Comprueba si un libro tiene índice RAG. Retorna un booleano.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Procesa un libro para el sistema RAG.
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`: Estima el número de tokens y chunks para un archivo. Retorna un diccionario.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`: Estima el número de tokens y chunks para una lista de archivos. Retorna un diccionario.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`: Realiza una consulta al sistema RAG. Retorna un string.


### `backend/main.py`

**Propósito:** Archivo principal del backend FastAPI.

*   Define la aplicación FastAPI y los endpoints de la API.
    *   `/upload-book/`: Sube un libro.
    *   `/books/`: Obtiene la lista de libros.
    *   `/books/count`: Obtiene el número total de libros.
    *   `/books/search/`: Busca libros por título parcial.
    *   `/categories/`: Obtiene la lista de categorías.
    *   `/books/{book_id}`: Elimina un libro.
    *   `/categories/{category_name}`: Elimina una categoría y sus libros.
    *   `/books/download/{book_id}`: Descarga un libro.
    *   `/tools/convert-epub-to-pdf`: Convierte un EPUB a PDF.
    *   `/rag/upload-book/`: Sube un libro al sistema RAG.
    *   `/rag/query/`: Consulta al sistema RAG.
    *   `/rag/index/{book_id}`: Indexa un libro en RAG.
    *   `/rag/status/{book_id}`: Obtiene el estado de indexado RAG para un libro.
    *   `/rag/reindex/category/{category_name}`: Reindexa libros de una categoría.
    *   `/rag/reindex/all`: Reindexa todos los libros.
    *   `/rag/estimate/book/{book_id}`: Estima el coste y número de embeddings para un libro.
    *   `/rag/estimate/category/{category_name}`: Estima el coste y número de embeddings para una categoría.
    *   `/rag/estimate/all`: Estima el coste y número de embeddings para todos los libros.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/Header.js`

**Propósito:** Componente para el encabezado de la aplicación.

*   **Estado:** `menuOpen`, `bookCount`, `errorMessage`.
*   **Efectos:**  Obtiene el recuento de libros del backend y lo actualiza periódicamente.
*   **Interacción con el usuario:** Botón de menú hamburguesa.
*   **Interacción con el backend:** Llamada a `/books/count` para obtener el número de libros.


### `frontend/src/App.js`

**Propósito:** Componente principal de la aplicación, que gestiona el enrutamiento.


### `frontend/src/ToolsView.js`

**Propósito:** Muestra las herramientas disponibles.

*   **Componente `EpubToPdfConverter`:**  Permite convertir archivos EPUB a PDF.
    *   **Estado:** `selectedFile`, `message`, `isLoading`.
    *   **Interacción con el usuario:**  Selecciona un archivo mediante input o arrastrar y soltar. Botón para iniciar la conversión.
    *   **Interacción con el backend:** Llamada POST a `/tools/convert-epub-to-pdf`.


### `frontend/src/UploadView.js`

**Propósito:** Permite a los usuarios subir libros.

*   **Estado:** `filesToUpload`, `isUploading`.
*   **Efectos:** No se utilizan efectos secundarios (useEffect).
*   **Interacción con el usuario:**  Selecciona uno o varios archivos mediante input o arrastrar y soltar. Botón para iniciar la subida.
*   **Interacción con el backend:** Llamada POST a `/upload-book/` por cada archivo.


### `frontend/src/ReaderView.js`

**Propósito:**  Muestra un libro EPUB utilizando `react-reader`.

*   **Estado:** `location`, `epubData`, `isLoading`, `error`.
*   **Efectos:** Obtiene los datos del libro EPUB del backend.
*   **Interacción con el backend:** Llamada GET a `/books/download/{bookId}`.


### `frontend/src/ErrorBoundary.js`

**Propósito:** Componente para la gestión de errores en la interfaz de usuario.


### `frontend/src/RagView.js`

**Propósito:** Permite al usuario chatear con una IA sobre los libros.

*   **Estado:** `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.
*   **Efectos:** Carga los libros de la biblioteca y gestiona el auto-scroll del chat.  Gestiona la búsqueda de libros.  Comprueba y actualiza el estado del índice RAG.
*   **Interacción con el usuario:**  Campo de texto para la consulta. Botón para enviar.  Selector de modo de respuesta.  Búsqueda de libros.  Acciones para indexar libros.
*   **Interacción con el backend:** Llamada POST a `/rag/query/`, `/rag/status/{selectedLibraryId}`, `/rag/index/{selectedLibraryId}`.


### `frontend/src/LibraryView.js`

**Propósito:** Muestra la lista de libros.

*   **Estado:** `books`, `searchTerm`, `error`, `loading`, `isMobile`.
*   **Efectos:** Obtiene la lista de libros del backend, gestionando la paginación y búsqueda.
*   **Interacción con el usuario:** Campo de texto para búsqueda.  Botones para eliminar libros y abrir/descargar.
*   **Interacción con el backend:** Llamada GET a `/books/`, usando los parámetros `category` y `author`.


### `frontend/src/config.js`

**Propósito:**  Define la URL de la API.


### `frontend/src/CategoriesView.js`

**Propósito:**  Muestra la lista de categorías.

*   **Estado:** `categories`, `error`, `loading`.
*   **Efectos:** Obtiene la lista de categorías del backend.
*   **Interacción con el backend:** Llamada GET a `/categories/`.


## 5. Flujo de Datos y API

1.  **Subida de un libro:** El usuario selecciona un archivo PDF o EPUB en `UploadView.js`.
2.  **Análisis de metadatos (Backend):** El archivo se envía al endpoint `/upload-book/` en `main.py`.  `main.py` llama a `analyze_with_gemini` para obtener metadatos (título, autor, categoría) utilizando Gemini.
3.  **Almacenamiento en la base de datos:** `main.py` llama a `crud.create_book` para almacenar la información del libro en la base de datos.
4.  **Visualización en la biblioteca:** El usuario puede ver los libros en `LibraryView.js`.
5.  **Búsqueda:**  El usuario puede buscar libros mediante título, autor o categoría en  `LibraryView.js`.  `LibraryView.js` hace la llamada al endpoint `/books/`.
6.  **Descarga:** El usuario puede descargar un libro mediante la llamada GET a `/books/download/{book_id}` desde `LibraryView.js`.
7.  **Conversión de EPUB a PDF:** El usuario usa la herramienta de conversión en `ToolsView.js`. El endpoint `/tools/convert-epub-to-pdf` maneja la conversión y la descarga.
8.  **RAG (Conversación con IA):**  El usuario puede seleccionar un libro, indexarlo y conversar con la IA en `RagView.js`. Los endpoints `/rag/upload-book/`, `/rag/query/`, `/rag/index/{book_id}`, y `/rag/status/{book_id}` se utilizan para esta funcionalidad.


**Principales Endpoints de la API:**

*   `/upload-book/` (POST): Sube un libro.
*   `/books/` (GET): Obtiene la lista de libros (con filtros opcionales).
*   `/books/count` (GET): Obtiene el número total de libros.
*   `/books/search/` (GET): Busca libros por título parcial.
*   `/categories/` (GET): Obtiene la lista de categorías.
*   `/books/{book_id}` (DELETE): Elimina un libro.
*   `/categories/{category_name}` (DELETE): Elimina una categoría y sus libros.
*   `/books/download/{book_id}` (GET): Descarga un libro.
*   `/tools/convert-epub-to-pdf` (POST): Convierte un EPUB a PDF.
*   `/rag/upload-book/` (POST): Sube un libro al sistema RAG.
*   `/rag/query/` (POST): Consulta al sistema RAG.
*   `/rag/index/{book_id}` (POST): Indexa un libro en RAG.
*   `/rag/status/{book_id}` (GET): Obtiene el estado de indexado RAG para un libro.
*   `/rag/reindex/category/{category_name}` (POST): Reindexa libros de una categoría.
*   `/rag/reindex/all` (POST): Reindexa todos los libros.
*   `/rag/estimate/book/{book_id}` (GET): Estima el coste y número de embeddings para un libro.
*   `/rag/estimate/category/{category_name}` (GET): Estima el coste y número de embeddings para una categoría.
*   `/rag/estimate/all` (GET): Estima el coste y número de embeddings para todos los libros.


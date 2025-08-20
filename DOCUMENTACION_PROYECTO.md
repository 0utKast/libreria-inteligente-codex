# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitalmente.  La aplicación facilita la subida, organización y búsqueda de libros en formato PDF y EPUB.  Además, integra un sistema de preguntas y respuestas (RAG) basado en la tecnología de Google Generative AI para permitir a los usuarios interactuar con el contenido de sus libros de forma inteligente.

La arquitectura de la aplicación se basa en un frontend desarrollado con React, un backend construido con FastAPI (Python) y una base de datos SQLite para el almacenamiento persistente de la información de los libros.  El sistema RAG utiliza ChromaDB para indexar el contenido de los libros y Gemini para generar respuestas.

## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: el backend (Python) y el frontend (React).

*   **backend/**: Contiene el código del backend de la aplicación, utilizando FastAPI y SQLAlchemy para la interacción con la base de datos.
    *   **alembic/**:  Contiene las migraciones de la base de datos.
    *   **schemas.py**: Define los esquemas Pydantic para la serialización y validación de datos.
    *   **crud.py**: Implementa las funciones CRUD (Create, Read, Update, Delete) para la base de datos.
    *   **database.py**: Configura la conexión a la base de datos SQLite.
    *   **models.py**: Define el modelo de datos SQLAlchemy para la tabla de libros.
    *   **utils.py**: Contiene funciones utilitarias, incluyendo la configuración de la API Key de Google Generative AI.
    *   **rag.py**: Implementa la lógica del sistema RAG (Retrieval Augmented Generation).
    *   **main.py**: El archivo principal del backend, que define las rutas de la API FastAPI.
    *   **tests/**: Contiene las pruebas unitarias para el backend.
*   **frontend/**: Contiene el código del frontend de la aplicación, desarrollado con React.
    *   **src/**: Contiene el código fuente del frontend.
        *   **App.js**: Componente principal de la aplicación.
        *   **Header.js**: Componente de encabezado con navegación.
        *   **LibraryView.js**: Vista principal de la biblioteca.
        *   **UploadView.js**: Vista para subir libros.
        *   **CategoriesView.js**: Vista para mostrar las categorías de los libros.
        *   **ToolsView.js**: Vista para las herramientas (convertidor EPUB a PDF).
        *   **ReaderView.js**: Vista para leer libros EPUB.
        *   **RagView.js**: Vista para interactuar con el sistema RAG.
        *   **ErrorBoundary.js**: Componente para manejo de errores.
        *   **config.js**: Configuración de la URL de la API.
    *   **public/**: Archivos estáticos del frontend.

## 3. Análisis Detallado del Backend (Python/FastAPI)

### backend/schemas.py

Este archivo define los modelos Pydantic para la serialización y validación de datos que se intercambian entre el frontend y el backend.

*   **Clase `BookBase`:** Modelo base para un libro, utilizado para la creación de nuevos libros.
    *   `title: str`: Título del libro (requerido).
    *   `author: str`: Autor del libro (requerido).
    *   `category: str`: Categoría del libro (requerido).
    *   `cover_image_url: str | None = None`: URL de la imagen de portada (opcional).
    *   `file_path: str`: Ruta al archivo del libro (requerido).
*   **Clase `Book`:** Modelo completo para un libro, incluyendo el ID. Hereda de `BookBase`.
    *   `id: int`: ID del libro (requerido).
*   **Clase `ConversionResponse`:** Respuesta para la conversión de EPUB a PDF.
    *   `download_url: str`: URL de descarga del PDF.
*   **Clase `RagUploadResponse`:** Respuesta para la subida de un libro al sistema RAG.
    *   `book_id: str`: ID del libro en el sistema RAG.
    *   `message: str`: Mensaje de estado.
*   **Clase `RagQuery`:**  Solicitud de consulta al sistema RAG.
    *   `query: str`: Consulta del usuario (requerida).
    *   `book_id: str`: ID del libro en el sistema RAG (requerido).
    *   `mode: str | None = None`: Modo de consulta ('strict', 'balanced', 'open') (opcional).
*   **Clase `RagQueryResponse`:** Respuesta de la consulta al sistema RAG.
    *   `response: str`: Respuesta generada por el modelo de lenguaje.


### backend/crud.py

Este archivo contiene las funciones para la interacción con la base de datos.

*   `get_book_by_path(db: Session, file_path: str)`: Obtiene un libro por su ruta de archivo. Retorna un objeto `models.Book` o `None`.
*   `get_book_by_title(db: Session, title: str)`: Obtiene un libro por su título. Retorna un objeto `models.Book` o `None`.
*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial (case-insensitive). Retorna una lista de objetos `models.Book`.
*   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`: Obtiene una lista de libros, con opciones de filtrado.  Retorna una lista de objetos `models.Book`.
*   `get_categories(db: Session) -> list[str]`: Obtiene una lista de todas las categorías únicas. Retorna una lista de strings.
*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea un nuevo libro en la base de datos.  Retorna el objeto `models.Book` creado.
*   `delete_book(db: Session, book_id: int)`: Elimina un libro de la base de datos por su ID, incluyendo sus archivos asociados. Retorna el objeto `models.Book` eliminado o `None`.
*   `delete_books_by_category(db: Session, category: str)`: Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados. Retorna el número de libros eliminados.
*   `get_books_count(db: Session) -> int`: Obtiene el número total de libros en la base de datos. Retorna un entero.


### backend/database.py

Este archivo configura la conexión a la base de datos SQLite.  Define `engine` y `SessionLocal`.

### backend/utils.py

Este archivo contiene funciones utilitarias.

*   `configure_genai()`: Configura la API Key de Google Generative AI leyendo la clave desde un archivo `.env`.  Si no encuentra la clave, lanza una excepción `ValueError`.

### backend/models.py

Este archivo define el modelo de datos SQLAlchemy para la tabla de libros.

*   **Clase `Book`:**  Modelo SQLAlchemy para la tabla `books`.
    *   `id`:  Clave primaria, entero.
    *   `title`: String, indexado.
    *   `author`: String, indexado.
    *   `category`: String, indexado.
    *   `cover_image_url`: String, nullable.
    *   `file_path`: String, único.


### backend/rag.py

Este archivo implementa la lógica del sistema RAG.

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`: Genera una incrustación (embedding) para el texto dado utilizando Google Generative AI o un método dummy si la IA está deshabilitada. Retorna una lista de floats.
*   `extract_text_from_pdf(file_path: str) -> str`: Extrae el texto de un archivo PDF. Retorna un string.
*   `extract_text_from_epub(file_path: str) -> str`: Extrae el texto de un archivo EPUB. Retorna un string.
*   `extract_text(file_path: str) -> str`: Función unificada para la extracción de texto de PDF y EPUB. Retorna un string.
*   `chunk_text(text: str, max_tokens: int = 1000) -> list[str]`: Divide el texto en fragmentos más pequeños. Retorna una lista de strings.
*   `_has_index_for_book(book_id: str) -> bool`:  Comprueba si existe un índice para un libro en ChromaDB. Retorna un booleano.
*   `delete_book_from_rag(book_id: str)`: Elimina los vectores de un libro de ChromaDB.
*   `get_index_count(book_id: str) -> int`: Obtiene el número de vectores para un libro en ChromaDB.  Retorna un entero.
*   `has_index(book_id: str) -> bool`: Comprueba si un libro está indexado en RAG. Retorna un booleano.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Procesa un libro para el sistema RAG: extrae texto, lo divide en fragmentos, genera embeddings y los almacena en ChromaDB.
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`: Estima el número de tokens y fragmentos para un archivo. Retorna un diccionario.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`: Estima el número de tokens y fragmentos para una lista de archivos. Retorna un diccionario.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`: Consulta el sistema RAG. Retorna un string.


### backend/main.py

Este archivo define las rutas de la API FastAPI.

*   `/upload-book/`: Endpoint POST para subir un libro.  Recibe un archivo (`book_file`) y retorna un objeto `schemas.Book`.
*   `/books/`: Endpoint GET para obtener una lista de libros, con opciones de filtrado. Retorna una lista de objetos `schemas.Book`.
*   `/books/count`: Endpoint GET para obtener el número total de libros. Retorna un entero.
*   `/books/search/`: Endpoint GET para buscar libros por título parcial.  Retorna una lista de objetos `schemas.Book`.
*   `/categories/`: Endpoint GET para obtener una lista de categorías. Retorna una lista de strings.
*   `/books/{book_id}`: Endpoint DELETE para eliminar un libro.
*   `/categories/{category_name}`: Endpoint DELETE para eliminar una categoría y sus libros.
*   `/books/download/{book_id}`: Endpoint GET para descargar un libro.
*   `/tools/convert-epub-to-pdf`: Endpoint POST para convertir un EPUB a PDF. Recibe un archivo y retorna un objeto `schemas.ConversionResponse`.
*   `/rag/upload-book/`: Endpoint POST para subir un libro al sistema RAG. Recibe un archivo y retorna un objeto `schemas.RagUploadResponse`.
*   `/rag/query/`: Endpoint POST para consultar el sistema RAG. Recibe un objeto `schemas.RagQuery` y retorna un objeto `schemas.RagQueryResponse`.
*   `/rag/index/{book_id}`: Endpoint POST para indexar un libro existente en RAG.
*   `/rag/status/{book_id}`: Endpoint GET para obtener el estado RAG de un libro.
*   `/rag/reindex/category/{category_name}`: Endpoint POST para reindexar los libros de una categoría en RAG.
*   `/rag/reindex/all`: Endpoint POST para reindexar todos los libros en RAG.
*   `/rag/estimate/book/{book_id}`: Endpoint GET para estimar tokens/chunks para un libro.
*   `/rag/estimate/category/{category_name}`: Endpoint GET para estimar tokens/chunks para una categoría.
*   `/rag/estimate/all`: Endpoint GET para estimar tokens/chunks para todos los libros.


### backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py

Este archivo define la migración para crear la tabla `books` en la base de datos.


## 4. Análisis Detallado del Frontend (React)

### frontend/src/Header.js

Este componente renderiza el encabezado de la aplicación, incluyendo la navegación.  Utiliza `useState` para gestionar el estado del menú y el contador de libros, y `useEffect` para obtener el número de libros del backend.

*   **Estado:** `menuOpen`, `bookCount`, `errorMessage`.
*   **Efectos secundarios:**  Fetch del conteo de libros desde la API `/books/count` con intervalos periódicos.
*   **Interacción con el backend:** Realiza una petición `fetch` a `/books/count` para obtener el número de libros.


### frontend/src/App.js

Este componente renderiza el componente principal de la aplicación utilizando `BrowserRouter`, `Routes`, y `Route` para la navegación.

### frontend/src/ToolsView.js

Este componente renderiza la vista de herramientas.  Actualmente solo incluye un convertidor de EPUB a PDF.  Utiliza `useState` para el estado del archivo seleccionado y la respuesta del backend, `useCallback` para el manejador de drop y `fetch` para la comunicación con el backend.

*   **Estado:** `selectedFile`, `message`, `isLoading`.
*   **Interacción con el backend:** Realiza una petición POST a `/tools/convert-epub-to-pdf` para la conversión.


### frontend/src/UploadView.js

Este componente renderiza la vista para subir libros.  Gestiona el estado de los archivos subidos y la carga. Usa `useState` para el estado de carga y la lista de archivos.

*   **Estado:** `filesToUpload`, `isUploading`.
*   **Interacción con el backend:** Realiza peticiones POST a `/upload-book/` para cada archivo.


### frontend/src/ReaderView.js

Este componente renderiza un visor de libros EPUB. Utiliza `useParams` para obtener el ID del libro desde la URL y `ReactReader` para mostrar el libro.  Hace una petición `fetch` para obtener el archivo.

*   **Estado:** `location`, `epubData`, `isLoading`, `error`.
*   **Interacción con el backend:** Realiza una petición `fetch` a `/books/download/{bookId}` para descargar el libro.


### frontend/src/ErrorBoundary.js

Componente para el manejo de errores en la UI.

### frontend/src/RagView.js

Este componente renderiza la vista para interactuar con el sistema RAG. Gestiona el estado del chat, realiza peticiones al backend y muestra la interfaz para el usuario.

*   **Estado:** `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.
*   **Interacción con el backend:** Realiza peticiones POST a `/rag/query/`, GET a `/rag/status/{selectedLibraryId}` y POST a `/rag/index/{selectedLibraryId}`.
*   **Efectos secundarios:** Carga de la lista de libros de la biblioteca, búsqueda con debounce, y verificación automática del estado RAG del libro seleccionado.


### frontend/src/LibraryView.js

Este componente renderiza la vista principal de la biblioteca.  Permite la búsqueda de libros y muestra una lista de libros. Maneja la eliminación de libros.

*   **Estado:** `books`, `searchTerm`, `error`, `loading`, `isMobile`.
*   **Interacción con el backend:** Realiza peticiones GET a `/books/` para obtener la lista de libros y DELETE a `/books/{bookId}` para eliminar libros.
*   **Efectos secundarios:** Llamada a la función `fetchBooks` cuando se modifica `debouncedSearchTerm` o `searchParams`.
*   **Hook personalizado:** `useDebounce` para la búsqueda con debounce.


### frontend/src/config.js

Este archivo define la URL de la API.


### frontend/src/CategoriesView.js

Este componente renderiza la vista de categorías. Obtiene las categorías del backend y las muestra como enlaces.

*   **Estado:** `categories`, `error`, `loading`.
*   **Interacción con el backend:**  Realiza una petición GET a `/categories/`.



## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro en la vista `UploadView`.  El frontend envía el archivo al backend a través del endpoint `/upload-book/`.  El backend procesa el archivo (extrae texto, obtiene la portada), utiliza Gemini para analizar el texto y extraer metadatos (título, autor, categoría), y finalmente guarda la información en la base de datos.  La información del libro se muestra luego en la vista `LibraryView`.

La vista `LibraryView` obtiene la información de los libros a través de `/books/` (con parámetros opcionales de filtro) y muestra los datos. La vista `CategoriesView` obtiene las categorías únicas de `/categories/`. La vista `ToolsView` utiliza el endpoint `/tools/convert-epub-to-pdf` para convertir archivos. La vista `RagView`  utiliza el endpoint `/rag/upload-book/` para indexar un libro, `/rag/query/` para consultar la IA y `/rag/status/{book_id}` para comprobar el estado del índice.  El visor de libros (`ReaderView`) utiliza el endpoint `/books/download/{book_id}` para descargar el libro.  El encabezado (`Header.js`) utiliza `/books/count` para mostrar el número de libros.

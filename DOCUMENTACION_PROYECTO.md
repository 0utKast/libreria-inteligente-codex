# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitalmente.  Permite subir libros en formato PDF y EPUB, los analiza automáticamente para extraer metadatos (título, autor, categoría) utilizando la IA de Google Gemini, y los almacena en una base de datos. La aplicación ofrece una interfaz de usuario amigable para buscar, visualizar y gestionar los libros, incluyendo la opción de convertir EPUB a PDF y un sistema de preguntas y respuestas basado en el contenido de los libros (RAG).

La aplicación tiene una arquitectura cliente-servidor: un frontend en ReactJS se comunica con un backend en FastAPI (Python) que utiliza SQLAlchemy para interactuar con una base de datos SQLite.  El sistema RAG utiliza ChromaDB para indexar el contenido de los libros y Google Gemini para generar embeddings y respuestas a las consultas de los usuarios.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales:

*   **`backend/`:** Contiene el backend de la aplicación en Python, utilizando el framework FastAPI.  Incluye la lógica de la API, el acceso a la base de datos y el procesamiento de los libros.
*   **`frontend/`:** Contiene el frontend de la aplicación desarrollado con React.  Incluye la interfaz de usuario, la lógica del cliente y la comunicación con el backend.
    *   **`src/`:** Contiene los componentes, estilos y configuración de la aplicación React.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/main.py`

**Propósito:** Define el punto de entrada de la aplicación FastAPI, incluyendo las rutas de la API, la configuración inicial y las funciones de procesamiento de libros y análisis con Gemini.

**Funciones y Clases Principales:**

*   `analyze_with_gemini(text: str) -> dict:` Analiza un texto usando Google Gemini para extraer título, autor y categoría del libro. Retorna un diccionario con estos datos.  Si falla, retorna un diccionario con valores "Error de IA".
*   `process_pdf(file_path: str, static_dir: str) -> dict:` Procesa un archivo PDF extrayendo texto de las primeras 5 páginas y la imagen de la portada (si existe). Retorna un diccionario con el texto y la URL de la portada.
*   `process_epub(file_path: str, static_dir: str) -> dict:` Procesa un archivo EPUB, extrayendo texto y la imagen de la portada si está disponible, incluyendo múltiples métodos de detección de la portada. Retorna un diccionario con el texto extraído y la URL de la portada.
*   `upload_book(...) -> schemas.Book:`  Gestiona la subida de un libro, procesa el archivo (PDF o EPUB), analiza con Gemini y crea una nueva entrada en la base de datos. Retorna el objeto `schemas.Book` creado.
*   `read_books(...) -> List[schemas.Book]:` Obtiene una lista de libros con opciones de filtrado. Retorna una lista de objetos `schemas.Book`.
*   `get_books_count(...) -> int:` Obtiene el número total de libros en la base de datos. Retorna un entero.
*   `search_books(...) -> List[schemas.Book]:` Busca libros por título parcial, con paginación. Retorna una lista de objetos `schemas.Book`.
*   `read_categories(...) -> List[str]:` Obtiene una lista de todas las categorías de libros. Retorna una lista de strings.
*   `delete_single_book(...) -> dict:` Elimina un libro de la base de datos y sus archivos asociados. Limpia el indice RAG asociado. Retorna un diccionario con mensaje de confirmación.
*   `delete_category_and_books(...) -> dict:` Elimina todos los libros de una categoría dada y sus archivos asociados. Limpia los indices RAG asociados. Retorna un diccionario con mensaje de confirmación y cantidad de libros borrados.
*   `download_book(...) -> FileResponse:` Permite la descarga de un libro a través de su ID. Retorna una respuesta con el archivo a descargar.
*   `convert_epub_to_pdf(...) -> schemas.ConversionResponse:` Convierte un archivo EPUB subido a un PDF, genera un archivo temporal y lo devuelve para su descarga. Retorna un objeto `schemas.ConversionResponse` con la URL de descarga.
*   `upload_book_for_rag(...) -> schemas.RagUploadResponse:` Sube un libro para procesarlo con el sistema RAG. Retorna un objeto `schemas.RagUploadResponse`.
*   `query_rag_endpoint(...) -> schemas.RagQueryResponse:` Endpoint para consultar el sistema RAG. Retorna un objeto `schemas.RagQueryResponse`.
*   `index_existing_book_for_rag(...) -> dict:` Indexa un libro existente en la base de datos usando el sistema RAG.  Permite reindexar forzando la eliminación de los embeddings anteriores.
*   `rag_status(...) -> dict:` Consulta el estado RAG de un libro (id).
*   `rag_reindex_category(...) -> dict:` Reindexa todos los libros de una categoria.
*   `rag_reindex_all(...) -> dict:` Reindexa todos los libros.
*   `estimate_rag_for_book(...) -> dict:` Estima el coste de indexación (tokens y chunks) para un libro.
*   `estimate_rag_for_category(...) -> dict:` Estima el coste de indexación (tokens y chunks) para una categoría.
*   `estimate_rag_for_all(...) -> dict:` Estima el coste de indexación (tokens y chunks) para toda la biblioteca.

### `backend/crud.py`

**Propósito:** Define las funciones CRUD (Create, Read, Update, Delete) para la interacción con la base de datos.

**Funciones Principales:**

*   `get_book_by_path(db: Session, file_path: str)`: Obtiene un libro por su ruta de archivo.
*   `get_book_by_title(db: Session, title: str)`: Obtiene un libro por su título.
*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial (case-insensitive), con paginación.
*   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`: Obtiene una lista de libros, con opciones de filtrado.
*   `get_categories(db: Session) -> list[str]:` Obtiene una lista de categorías únicas.
*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea un nuevo libro en la base de datos.
*   `delete_book(db: Session, book_id: int)`: Elimina un libro de la base de datos y sus archivos asociados.
*   `delete_books_by_category(db: Session, category: str)`: Elimina todos los libros de una categoría.
*   `get_books_count(db: Session) -> int:`: Cuenta el número de libros.


### `backend/database.py`

**Propósito:** Configura la conexión a la base de datos SQLite.

**Elementos Principales:**

*   `SQLALCHEMY_DATABASE_URL`: URL de conexión a la base de datos.
*   `engine`: Motor de la base de datos.
*   `SessionLocal`: Fábrica de sesiones SQLAlchemy.
*   `Base`: Clase base para modelos SQLAlchemy.


### `backend/models.py`

**Propósito:** Define el modelo de datos `Book` para SQLAlchemy.

**Clases Principales:**

*   `Book(Base)`: Define la estructura de la tabla `books` en la base de datos.


### `backend/schemas.py`

**Propósito:** Define los modelos Pydantic para la serialización y validación de datos.

**Clases Principales:**

*   `BookBase(BaseModel)`: Modelo base para libros.
*   `Book(BookBase)`: Modelo para libros con ID.
*   `ConversionResponse(BaseModel)`: Respuesta para la conversión EPUB a PDF.
*   `RagUploadResponse(BaseModel)`: Respuesta para la subida de libro a RAG.
*   `RagQuery(BaseModel)`: Modelo para las consultas RAG.
*   `RagQueryResponse(BaseModel)`: Respuesta para las consultas RAG.


### `backend/utils.py`

**Propósito:** Funciones utilitarias, en este caso para configurar la API Key de Google Generative AI.

**Funciones Principales:**

*   `configure_genai()`: Carga la API key de Google Generative AI desde el archivo `.env` y configura el cliente.


### `backend/rag.py`

**Propósito:** Define la lógica del sistema de recuperación de información basada en el contenido del libro (RAG).

**Funciones Principales:**

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`: Genera un embedding para un texto dado usando Google Gemini. Si la IA está deshabilitada, devuelve un embedding dummy.
*   `extract_text_from_pdf(file_path: str) -> str`: Extrae texto de un archivo PDF.
*   `extract_text_from_epub(file_path: str) -> str`: Extrae texto de un archivo EPUB.
*   `extract_text(file_path: str) -> str`: Extrae texto de un archivo (PDF o EPUB).
*   `chunk_text(text: str, max_tokens: int = 1000) -> list[str]`: Divide un texto en fragmentos basados en el conteo de tokens.
*   `_has_index_for_book(book_id: str) -> bool`: Verifica si un libro ya está indexado en ChromaDB.
*   `delete_book_from_rag(book_id: str)`: Elimina los vectores de un libro de ChromaDB.
*   `get_index_count(book_id: str) -> int`: Obtiene el número de vectores de un libro en ChromaDB.
*   `has_index(book_id: str) -> bool`: Indica si un libro está indexado en RAG.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Procesa un libro para el RAG, extrayendo texto, generando embeddings y almacenándolos en ChromaDB.
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`: Estima el número de tokens y fragmentos para un archivo.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`: Estima el número de tokens y fragmentos para una lista de archivos.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`: Consulta el sistema RAG.


### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

**Propósito:** Script Alembic para la creación de la tabla `books` en la base de datos.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

**Propósito:** Componente principal de la aplicación React, que gestiona la navegación entre diferentes vistas.

**Estado, Propiedades, Efectos:** No tiene estado ni propiedades. No hay efectos secundarios.

**Interacción con el Backend:** No interactúa directamente con el backend.


### `frontend/src/Header.js`

**Propósito:** Componente que renderiza el encabezado de la aplicación, incluyendo la navegación.

**Estado:** `menuOpen` (booleano), `bookCount` (entero), `errorMessage` (string).

**Propiedades:** No tiene propiedades.

**Efectos:** Usa `useEffect` para obtener el conteo de libros desde el endpoint `/books/count` del backend y actualizarlo cada minuto.

**Interacción con el Backend:** Realiza una petición `fetch` a `/books/count` para obtener el número de libros.


### `frontend/src/LibraryView.js`

**Propósito:** Muestra la lista de libros de la biblioteca con funcionalidades de búsqueda y paginación.

**Estado:** `books` (array), `searchTerm` (string), `error` (string), `loading` (booleano), `isMobile` (booleano).

**Propiedades:** No tiene propiedades.

**Efectos:** Usa `useEffect` con `fetchBooks` para obtener la lista de libros del backend con opciones de filtrado, búsqueda debounceada y paginación.

**Interacción con el Backend:** Realiza peticiones `fetch` a `/books/` para obtener libros y a `/books/:bookId` para eliminar libros.


### `frontend/src/UploadView.js`

**Propósito:** Permite a los usuarios subir archivos PDF y EPUB.

**Estado:** `filesToUpload` (array), `isUploading` (booleano).

**Propiedades:** No tiene propiedades.

**Efectos:** No usa efectos.

**Interacción con el Backend:** Realiza peticiones `fetch` a `/upload-book/` para subir y procesar cada archivo.


### `frontend/src/ReaderView.js`

**Propósito:** Permite visualizar un libro EPUB en un formato de lectura.

**Estado:** `location` (string), `epubData` (ArrayBuffer), `isLoading` (booleano), `error` (string).

**Propiedades:** `bookId` (string).

**Efectos:** Usa `useEffect` para obtener el archivo EPUB desde el endpoint `/books/download/:bookId` del backend.

**Interacción con el Backend:** Realiza una petición `fetch` a `/books/download/:bookId`.


### `frontend/src/ToolsView.js`

**Propósito:** Ofrece una interfaz para convertir archivos EPUB a PDF.

**Estado:** `selectedFile`, `message`, `isLoading`.

**Propiedades:** Ninguna.

**Efectos:** Ninguno.

**Interacción con el Backend:** Envía una petición POST a `/tools/convert-epub-to-pdf` para realizar la conversión.


### `frontend/src/CategoriesView.js`

**Propósito:** Muestra una lista de categorías de libros.

**Estado:** `categories`, `error`, `loading`.

**Propiedades:** Ninguna.

**Efectos:**  Usa `useEffect` para obtener las categorías del backend con una petición `fetch` a `/categories/`.

**Interacción con el Backend:** Realiza una petición `fetch` a `/categories/`.


### `frontend/src/RagView.js`

**Propósito:**  Proporciona una interfaz para interactuar con el sistema RAG (conversación inteligente sobre libros).

**Estado:**  `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`.

**Propiedades:** Ninguna.

**Efectos:**  Usa `useEffect` para cargar la lista de libros desde `/books`, para gestionar la búsqueda y para actualizar automáticamente el estado RAG del libro seleccionado.

**Interacción con el Backend:**  Realiza peticiones `fetch` a `/rag/query/`, `/rag/status/:bookId`, `/rag/index/:bookId`, y `/books/?search=:searchTerm`.

### `frontend/src/ErrorBoundary.js`

**Propósito:** Componente de gestión de errores para capturar errores en los componentes hijos y mostrar un mensaje de error personalizado.

**Estado:** `hasError`, `error`.

**Propiedades:** `children`.

**Efectos:** Ninguno.

**Interacción con el Backend:** No hay interacción directa con el backend.


### `frontend/src/config.js`

**Propósito:** Define la URL base de la API.


## 5. Flujo de Datos y API

1.  **Subida de Libro (Frontend):** El usuario selecciona o arrastra un archivo (PDF o EPUB) en `UploadView.js`.
2.  **Subida de Libro (Backend):**  `UploadView.js` realiza una petición POST a `/upload-book/` al backend. `main.py` recibe el archivo, lo procesa usando `process_pdf` o `process_epub`, y extrae texto.
3.  **Análisis con Gemini (Backend):** `main.py` llama a `analyze_with_gemini` para obtener el título, autor y categoría del libro.
4.  **Almacenamiento en la Base de Datos (Backend):** `main.py` llama a `crud.create_book` para guardar los datos en la base de datos.
5.  **Visualización de Libros (Frontend):** `LibraryView.js` realiza una petición GET a `/books/` para obtener la lista de libros, mostrando la información en la interfaz de usuario.
6.  **Descarga de Libros (Frontend/Backend):** El usuario hace click en un enlace para descargar. `LibraryView.js` crea el enlace para descargar a través de GET a `/books/download/:bookId`.
7.  **Conversión EPUB a PDF (Frontend/Backend):**  El usuario selecciona un archivo EPUB y clicka en "Convertir". El Frontend envía el archivo vía POST a `/tools/convert-epub-to-pdf`, y el Backend realiza la conversión y retorna una URL de descarga.
8.  **RAG (Frontend/Backend):** El usuario selecciona un libro en `RagView.js`. Para habilitar la charla, hay que indexarlo usando la API `/rag/index/:bookId`. Las consultas se realizan enviando POST a `/rag/query/`. El backend realiza las consultas a ChromaDB y Google Gemini para generar respuestas.

**Endpoints de la API:**

*   `/upload-book/` (POST): Subir y procesar un libro.
*   `/books/` (GET): Obtener una lista de libros.
*   `/books/count` (GET): Obtener el número de libros.
*   `/books/search/` (GET): Buscar libros por título parcial.
*   `/categories/` (GET): Obtener las categorías de libros.
*   `/books/:book_id` (DELETE): Eliminar un libro.
*   `/books/download/:book_id` (GET): Descargar un libro.
*   `/tools/convert-epub-to-pdf` (POST): Convertir un EPUB a PDF.
*   `/rag/upload-book/` (POST): Subir un libro para RAG.
*   `/rag/query/` (POST): Realizar una consulta RAG.
*   `/rag/index/:book_id` (POST): Indexar libro en RAG.
*   `/rag/status/:book_id` (GET): Estado RAG de un libro.
*   `/rag/reindex/category/:category_name` (POST): Reindexar una categoría.
*   `/rag/reindex/all` (POST): Reindexar todos los libros.
*   `/rag/estimate/book/:book_id` (GET): Estimación de coste de RAG para un libro.
*   `/rag/estimate/category/:category_name` (GET): Estimación de coste de RAG para una categoría.
*   `/rag/estimate/all` (GET): Estimación de coste de RAG para toda la biblioteca.


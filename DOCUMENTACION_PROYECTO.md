# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales (PDF y EPUB). La aplicación proporciona funcionalidades para subir libros, buscarlos por título, autor o categoría, descargarlos y leerlos directamente en el navegador. Además, integra un sistema de Recuperación de Información basada en Conocimiento (RAG) para permitir conversaciones inteligentes con los libros usando la IA de Google Gemini.

La arquitectura de la aplicación se basa en un frontend desarrollado con React.js y un backend construido con FastAPI (Python), que utiliza una base de datos SQLite para el almacenamiento persistente de los metadatos de los libros. El sistema RAG se implementa con ChromaDB para el indexado vectorial y la API de Google Gemini para la generación de embeddings y respuestas.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: el backend (Python) y el frontend (React).

*   **backend/**: Contiene el código del backend de la aplicación.
    *   **alembic/**:  Directorio para las migraciones de la base de datos.
    *   **schemas.py**: Define los modelos Pydantic para la serialización y validación de datos.
    *   **crud.py**: Contiene las funciones CRUD (Create, Read, Update, Delete) para interactuar con la base de datos.
    *   **database.py**: Configura la conexión a la base de datos SQLite.
    *   **utils.py**: Funciones utilitarias, incluyendo la configuración de la API Key de Google Gemini.
    *   **models.py**: Define el modelo SQLAlchemy para la tabla de libros en la base de datos.
    *   **rag.py**: Implementa la lógica del sistema RAG, incluyendo la extracción de texto, generación de embeddings y consultas a la base de conocimiento.
    *   **main.py**: El archivo principal del backend, que define las rutas de la API FastAPI.
    *   **tests/**:  Contiene las pruebas unitarias del backend.
*   **frontend/**: Contiene el código del frontend de la aplicación (React).
    *   **src/**: Contiene el código fuente de la aplicación React.
        *   **App.js**: Componente principal de la aplicación.
        *   **Header.js**: Componente para el encabezado de la aplicación.
        *   **LibraryView.js**: Componente para mostrar la lista de libros.
        *   **UploadView.js**: Componente para subir nuevos libros.
        *   **CategoriesView.js**: Componente para mostrar las categorías de libros.
        *   **ToolsView.js**: Componente para las herramientas de la biblioteca (ej: conversor EPUB-PDF).
        *   **RagView.js**: Componente para interactuar con el sistema RAG.
        *   **ReaderView.js**: Componente para la lectura de EPUBs.
        *   **ErrorBoundary.js**: Componente para el manejo de errores en la interfaz de usuario.
        *   **config.js**: Archivo de configuración para la URL de la API.
    *   **public/**:  Archivos estáticos para la aplicación React.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### backend/schemas.py

Este archivo define los modelos Pydantic utilizados para la serialización y validación de datos en la API FastAPI.

*   **Clase `BookBase`**: Modelo base para la información de un libro.
    *   `title: str`: Título del libro (requerido).
    *   `author: str`: Autor del libro (requerido).
    *   `category: str`: Categoría del libro (requerido).
    *   `cover_image_url: str | None = None`: URL de la imagen de portada (opcional).
    *   `file_path: str`: Ruta al archivo del libro (requerido).
*   **Clase `Book`**: Modelo que extiende `BookBase`, añadiendo el ID.
    *   `id: int`: ID único del libro (requerido).
*   **Clase `ConversionResponse`**: Modelo para la respuesta de la conversión EPUB a PDF.
    *   `download_url: str`: URL para descargar el archivo PDF.
*   **Clase `RagUploadResponse`**: Modelo para la respuesta de la carga de un libro para RAG.
    *   `book_id: str`: ID del libro procesado para RAG.
    *   `message: str`: Mensaje de estado.
*   **Clase `RagQuery`**: Modelo para las consultas al sistema RAG.
    *   `query: str`: La consulta del usuario.
    *   `book_id: str`: El ID del libro a consultar.
    *   `mode: str | None = None`: El modo de consulta ('strict', 'balanced', 'open').
*   **Clase `RagQueryResponse`**: Modelo para la respuesta del sistema RAG.
    *   `response: str`: La respuesta generada por la IA.

### backend/crud.py

Este archivo contiene las funciones CRUD para la base de datos.

*   `get_book_by_path(db: Session, file_path: str)`: Obtiene un libro por su ruta de archivo. Retorna un objeto `models.Book` o `None`.
*   `get_book_by_title(db: Session, title: str)`: Obtiene un libro por su título exacto. Retorna un objeto `models.Book` o `None`.
*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial (case-insensitive). Retorna una lista de objetos `models.Book`.
*   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`: Obtiene una lista de libros, con opciones de filtrado. Retorna una lista de objetos `models.Book`.
*   `get_categories(db: Session)`: Obtiene una lista de todas las categorías únicas. Retorna una lista de strings.
*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea un nuevo libro en la base de datos. Retorna el objeto `models.Book` creado.
*   `delete_book(db: Session, book_id: int)`: Elimina un libro de la base de datos por su ID, incluyendo sus archivos asociados. Retorna el objeto `models.Book` eliminado o `None`.
*   `delete_books_by_category(db: Session, category: str)`: Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados. Retorna el número de libros eliminados.
*   `get_books_count(db: Session)`: Obtiene el número total de libros en la base de datos. Retorna un entero.

### backend/database.py

Este archivo configura la conexión a la base de datos SQLite. Define `engine` y `SessionLocal`.

### backend/utils.py

Este archivo contiene funciones utilitarias.

*   `configure_genai()`: Configura la API Key de Google Generative AI desde el archivo `.env`. Lanza `ValueError` si la clave no se encuentra.

### backend/models.py

Este archivo define el modelo SQLAlchemy para la tabla `books`.

*   **Clase `Book`**: Representa un libro en la base de datos.
    *   `id`: ID entero, clave primaria.
    *   `title`: String, título del libro.
    *   `author`: String, autor del libro.
    *   `category`: String, categoría del libro.
    *   `cover_image_url`: String, URL de la imagen de portada (nullable).
    *   `file_path`: String, ruta al archivo del libro (único).


### backend/rag.py

Este archivo implementa la lógica del sistema RAG.

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`: Genera un embedding para el texto dado usando la API de Google Gemini. Retorna una lista de floats.
*   `extract_text_from_pdf(file_path: str)`: Extrae el texto de un archivo PDF. Retorna un string.
*   `extract_text_from_epub(file_path: str)`: Extrae el texto de un archivo EPUB. Retorna un string.
*   `extract_text(file_path: str)`: Función unificada para la extracción de texto de PDF y EPUB. Retorna un string.
*   `chunk_text(text: str, max_tokens: int = 1000)`: Divide el texto en fragmentos más pequeños. Retorna una lista de strings.
*   `_has_index_for_book(book_id: str)`: Comprueba si existe un índice para un libro en ChromaDB. Retorna un booleano.
*   `delete_book_from_rag(book_id: str)`: Elimina los vectores de un libro de ChromaDB.
*   `get_index_count(book_id: str)`: Obtiene el número de vectores de un libro en ChromaDB. Retorna un entero.
*   `has_index(book_id: str)`: Comprueba si un libro está indexado en RAG. Retorna un booleano.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Procesa un libro para RAG: extrae texto, lo divide en fragmentos, genera embeddings y los almacena en ChromaDB.
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000)`: Estima el número de tokens y fragmentos para un archivo. Retorna un diccionario.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000)`: Estima el número de tokens y fragmentos para una lista de archivos. Retorna un diccionario.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`: Consulta el sistema RAG para obtener una respuesta. Retorna un string.


### backend/main.py

Este archivo define las rutas de la API FastAPI.

*   `analyze_with_gemini(text: str)`: Analiza un texto con Google Gemini para obtener el título, autor y categoría.  Retorna un diccionario.
*   `process_pdf(file_path: str, static_dir: str)`: Procesa un archivo PDF para extraer texto e imagen de portada. Retorna un diccionario.
*   `process_epub(file_path: str, static_dir: str)`: Procesa un archivo EPUB para extraer texto e imagen de portada. Retorna un diccionario.
*   `/upload-book/`: Endpoint POST para subir un libro.  Recibe un archivo y retorna un objeto `schemas.Book`.
*   `/books/`: Endpoint GET para obtener una lista de libros, con opciones de filtrado. Retorna una lista de objetos `schemas.Book`.
*   `/books/count`: Endpoint GET para obtener el número total de libros. Retorna un entero.
*   `/books/search/`: Endpoint GET para buscar libros por un título parcial. Retorna una lista de objetos `schemas.Book`.
*   `/categories/`: Endpoint GET para obtener una lista de categorías. Retorna una lista de strings.
*   `/books/{book_id}`: Endpoint DELETE para eliminar un libro por su ID.
*   `/categories/{category_name}`: Endpoint DELETE para eliminar una categoría y sus libros.
*   `/books/download/{book_id}`: Endpoint GET para descargar un libro por su ID.
*   `/tools/convert-epub-to-pdf`: Endpoint POST para convertir un archivo EPUB a PDF. Retorna un objeto `schemas.ConversionResponse`.
*   `/rag/upload-book/`: Endpoint POST para subir un libro para procesarlo con RAG. Retorna un objeto `schemas.RagUploadResponse`.
*   `/rag/query/`: Endpoint POST para consultar el sistema RAG. Recibe un objeto `schemas.RagQuery` y retorna un objeto `schemas.RagQueryResponse`.
*   `/rag/index/{book_id}`: Endpoint POST para indexar un libro en RAG.
*   `/rag/status/{book_id}`: Endpoint GET para obtener el estado RAG de un libro.
*   `/rag/reindex/category/{category_name}`: Endpoint POST para reindexar los libros de una categoría en RAG.
*   `/rag/reindex/all`: Endpoint POST para reindexar todos los libros en RAG.
*   `/rag/estimate/book/{book_id}`: Endpoint GET para obtener una estimación de los tokens y chunks para un libro.
*   `/rag/estimate/category/{category_name}`: Endpoint GET para obtener una estimación de los tokens y chunks para una categoría.
*   `/rag/estimate/all`: Endpoint GET para obtener una estimación de los tokens y chunks para todos los libros.


## 4. Análisis Detallado del Frontend (React)

### frontend/src/Header.js

Este componente renderiza el encabezado de la aplicación, incluyendo un menú de navegación y un contador de libros.

*   **Estado**: `menuOpen` (booleano), `bookCount` (entero), `errorMessage` (string).
*   **Efectos**: Realiza una llamada al backend para obtener el número total de libros (`useEffect`) y actualiza el contador periódicamente.
*   **Interacción con el backend**: Llama a `/books/count` para obtener el número de libros.

### frontend/src/App.js

Este componente es el componente principal de la aplicación React.  Define las rutas de la aplicación usando `react-router-dom`.

### frontend/src/ToolsView.js

Este componente proporciona una interfaz para el conversor EPUB a PDF.

*   **Estado:** `selectedFile`, `message`, `isLoading`.
*   **Interacción con el backend:** Envía una solicitud POST a `/tools/convert-epub-to-pdf` para convertir el archivo.

### frontend/src/UploadView.js

Este componente permite a los usuarios subir libros.

*   **Estado**: `filesToUpload`, `isUploading`.
*   **Efectos secundarios**: Gestiona la subida de varios archivos en paralelo, actualizando el estado de cada uno.
*   **Interacción con el backend**: Llama a `/upload-book/` para subir cada archivo.

### frontend/src/ReaderView.js

Este componente muestra un libro EPUB usando la librería `react-reader`.

*   **Estado**: `location`, `epubData`, `isLoading`, `error`.
*   **Interacción con el backend**: Llama a `/books/download/${bookId}` para obtener el archivo EPUB.

### frontend/src/ErrorBoundary.js

Este componente sirve para manejar errores en la interfaz de usuario.

### frontend/src/RagView.js

Este componente permite a los usuarios interactuar con el sistema RAG.

*   **Estado**: `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`.
*   **Interacción con el backend**: Llama a `/rag/query/`, `/rag/status/{selectedLibraryId}`, y `/rag/index/{selectedLibraryId}`.
*   **Uso de hooks**: `useMemo` para optimizar el cálculo del libro actual, `useRef` para acceder al elemento del chat.
*   **Manejo de errores**: Muestra mensajes de error informativos al usuario en caso de fallo en las interacciones con el backend o el sistema RAG.
*   **Funcionalidades**: Permite buscar libros en la biblioteca, comprobar si están indexados en RAG, indexarlos (o reindexarlos), elegir modo de consulta ('strict', 'balanced', 'open'), y chatear con la IA.
*   **Optimizaciones**: El componente maneja adecuadamente la actualización del chat para auto-scroll, el debounce de la búsqueda, la actualización de estados de procesamiento de manera asíncrona y eficiente, y evita bloqueos innecesarios de la UI.


### frontend/src/LibraryView.js

Este componente muestra la lista de libros de la biblioteca.

*   **Estado**: `books`, `searchParams`, `searchTerm`, `debouncedSearchTerm`, `error`, `loading`, `isMobile`.
*   **Interacción con el backend**: Llama a `/books/` para obtener los libros y a `/books/${bookId}` para eliminar.
*   **Uso de hooks**: `useSearchParams`, `useCallback`, `useDebounce`.
*   **Funcionalidades**: Permite buscar libros por título, autor o categoría (con debounce), y eliminar libros.  Adapta la visualización para dispositivos móviles.



### frontend/src/config.js

Este archivo configura la URL de la API.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un archivo (PDF o EPUB) a través del componente `UploadView.js`. El frontend envía el archivo al backend a través del endpoint `/upload-book/`. El backend:

1.  Guarda el archivo subido.
2.  Procesa el archivo (extracción de texto y portada).
3.  Utiliza Google Gemini para analizar el texto extraído y obtener metadatos (título, autor, categoría).
4.  Guarda la información del libro (incluyendo la ruta del archivo y metadatos) en la base de datos SQLite.
5.  Retorna la información del libro al frontend.

El componente `LibraryView.js` muestra la lista de libros, obteniendo los datos del backend a través del endpoint `/books/`. Los usuarios pueden buscar libros por título, autor o categoría utilizando los parámetros de consulta de la URL.

La lectura de libros EPUB se realiza mediante el componente `ReaderView.js`, que descarga el archivo EPUB desde el endpoint `/books/download/{book_id}`.

El sistema RAG permite conversaciones inteligentes con los libros:

1.  El usuario selecciona un libro en `RagView.js`.
2.  El componente verifica si el libro está indexado en RAG llamando a `/rag/status/{book_id}`. Si no lo está, se puede indexar llamando a `/rag/index/{book_id}`.
3.  El usuario envía consultas al sistema RAG a través del endpoint `/rag/query/`, que utiliza ChromaDB para recuperar fragmentos relevantes y Google Gemini para generar la respuesta.
4.  La respuesta se muestra en el componente `RagView.js`.

El endpoint `/tools/convert-epub-to-pdf` permite la conversión de archivos EPUB a PDF.


**Principales Endpoints de la API:**

*   `/upload-book/` (POST): Subir libro.
*   `/books/` (GET): Obtener libros (filtrado opcional).
*   `/books/count` (GET): Obtener el conteo de libros.
*   `/books/search/` (GET): Buscar libros por título parcial.
*   `/categories/` (GET): Obtener categorías.
*   `/books/{book_id}` (DELETE): Eliminar libro.
*   `/categories/{category_name}` (DELETE): Eliminar categoría.
*   `/books/download/{book_id}` (GET): Descargar libro.
*   `/tools/convert-epub-to-pdf` (POST): Convertir EPUB a PDF.
*   `/rag/upload-book/` (POST): Subir libro para RAG.
*   `/rag/query/` (POST): Consultar RAG.
*   `/rag/index/{book_id}` (POST): Indexar libro en RAG.
*   `/rag/status/{book_id}` (GET): Obtener estado RAG.
*   `/rag/reindex/category/{category_name}` (POST): Reindexar categoría en RAG.
*   `/rag/reindex/all` (POST): Reindexar todos los libros en RAG.
*   `/rag/estimate/book/{book_id}` (GET): Estimar tokens y chunks para un libro.
*   `/rag/estimate/category/{category_name}` (GET): Estimar tokens y chunks para una categoría.
*   `/rag/estimate/all` (GET): Estimar tokens y chunks para todos los libros.


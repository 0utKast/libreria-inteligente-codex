# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros electrónicos.  La aplicación permite subir libros en formatos PDF y EPUB, los cuales son analizados por una IA para extraer metadatos (título, autor, categoría) y luego almacenados en una base de datos. Los usuarios pueden buscar, visualizar, y descargar sus libros. La aplicación también integra un sistema de Recuperación de Información basada en Conocimiento (RAG) que permite a los usuarios realizar consultas sobre el contenido de sus libros usando una interfaz de chat con IA.

La arquitectura de la aplicación se basa en un frontend desarrollado con React, un backend construido con FastAPI (Python), y una base de datos SQLite.  El sistema RAG utiliza ChromaDB para el almacenamiento de embeddings y la API de Google Gemini para la generación de embeddings y respuestas.

## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: el backend (`backend/`) y el frontend (`frontend/`).

*   `backend/`: Contiene el código del backend de la aplicación, incluyendo la API FastAPI, las funciones de acceso a datos, y la lógica de procesamiento de libros.
    *   `alembic/`:  Directorio para las migraciones de la base de datos.
    *   `database.py`:  Configuración de la base de datos SQLite.
    *   `crud.py`:  Funciones CRUD (Create, Read, Update, Delete) para la interacción con la base de datos.
    *   `models.py`:  Definición del modelo de datos `Book`.
    *   `rag.py`:  Implementación del sistema RAG.
    *   `schemas.py`:  Definición de los esquemas Pydantic para la serialización y validación de datos.
    *   `main.py`:  Archivo principal del backend, que define las rutas de la API FastAPI.
    *   `utils.py`: Funciones de utilidad, incluyendo la configuración de la API de Google Gemini.
    *   `tests/`: Contiene las pruebas unitarias del backend.


*   `frontend/src`: Contiene el código fuente del frontend React.
    *   `App.js`: Componente principal de la aplicación.
    *   `Header.js`: Componente para el encabezado de la aplicación.
    *   `LibraryView.js`: Componente para visualizar la biblioteca de libros.
    *   `UploadView.js`: Componente para subir nuevos libros.
    *   `CategoriesView.js`: Componente para visualizar y filtrar libros por categoría.
    *   `ToolsView.js`: Componente para las herramientas de la aplicación (conversor EPUB a PDF).
    *   `ReaderView.js`: Componente para leer libros en formato EPUB.
    *   `RagView.js`: Componente para interactuar con el sistema RAG mediante una interfaz de chat.
    *   `config.js`: Archivo de configuración para la URL de la API.
    *   `ErrorBoundary.js`: Componente para manejar errores en la interfaz.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/main.py`

Propósito: Define las rutas de la API FastAPI para la aplicación.

Funciones/Clases Principales:

*   `upload_book`: Recibe un archivo de libro (PDF o EPUB), lo procesa usando `process_pdf` o `process_epub`, analiza el texto con `analyze_with_gemini`, y crea una nueva entrada en la base de datos usando `crud.create_book`.  Retorna un objeto `schemas.Book`.
*   `read_books`:  Obtiene una lista de libros de la base de datos usando `crud.get_books`, con opciones de filtrado por categoría, búsqueda y autor. Retorna una lista de objetos `schemas.Book`.
*   `get_books_count`: Obtiene el número total de libros en la base de datos usando `crud.get_books_count`. Retorna un entero.
*   `search_books`: Busca libros por un título parcial usando `crud.get_books_by_partial_title`.  Retorna una lista de objetos `schemas.Book`.
*   `read_categories`: Obtiene una lista de todas las categorías únicas de libros de la base de datos usando `crud.get_categories`. Retorna una lista de strings.
*   `delete_single_book`: Elimina un libro de la base de datos y sus archivos asociados usando `crud.delete_book`.  Retorna un diccionario con un mensaje de confirmación.
*   `delete_category_and_books`: Elimina todos los libros de una categoría específica, incluyendo sus archivos, usando `crud.delete_books_by_category`. Retorna un diccionario con un mensaje de confirmación.
*   `download_book`: Descarga un libro desde la base de datos. Retorna una respuesta `FileResponse`.
*   `convert_epub_to_pdf`: Convierte un archivo EPUB a PDF usando la librería `weasyprint`.  Retorna un objeto `schemas.ConversionResponse` con la URL de descarga.
*   `upload_book_for_rag`: Procesa un libro para el sistema RAG usando `rag.process_book_for_rag`.  Retorna un objeto `schemas.RagUploadResponse`.
*   `query_rag_endpoint`: Consulta el sistema RAG usando `rag.query_rag`. Retorna un objeto `schemas.RagQueryResponse`.
*   `index_existing_book_for_rag`: Indexa un libro existente en la base de datos en el sistema RAG.
*   `rag_status`: Obtiene el estado de indexación RAG de un libro.
*   `rag_reindex_category`: Reindexa todos los libros de una categoría en RAG.
*   `rag_reindex_all`: Reindexa todos los libros en RAG.
*   `estimate_rag_for_book`: Estimación de tokens/chunks y coste opcional para un libro.
*   `estimate_rag_for_category`: Estimación de tokens/chunks y coste opcional para una categoría.
*   `estimate_rag_for_all`: Estimación de tokens/chunks y coste opcional para todos los libros.



### `backend/crud.py`

Propósito: Define las funciones CRUD para la interacción con la base de datos.

Funciones Principales:  (Documentadas en el código fuente)


### `backend/models.py`

Propósito: Define el modelo de datos `Book` para la base de datos.

Clases Principales:

*   `Book`:  Representa un libro en la base de datos. Contiene los campos `id`, `title`, `author`, `category`, `cover_image_url`, y `file_path`.


### `backend/rag.py`

Propósito: Implementa la lógica del sistema RAG.

Funciones Principales:  (Documentadas en el código fuente)


### `backend/schemas.py`

Propósito: Define los esquemas Pydantic para la validación y serialización de datos.

Clases Principales: (Documentadas en el código fuente)


### `backend/utils.py`

Propósito: Define funciones de utilidad, incluyendo la configuración de la API de Google.

Funciones Principales:

*   `configure_genai`: Configura la API Key de Google Gemini o Google AI a partir de variables de entorno.


### `backend/database.py`

Propósito: Configura la conexión a la base de datos.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

Propósito: Componente principal de la aplicación, que define las rutas.


### `frontend/src/Header.js`

Propósito: Componente para el encabezado de la aplicación, que incluye un menú de navegación.

Estado:

*   `menuOpen`: Booleano que indica si el menú está abierto.
*   `bookCount`: Número de libros en la biblioteca.
*   `errorMessage`: Mensaje de error al cargar el conteo de libros

Propiedades:  Ninguna.

Efectos Secundarios:  Realiza una petición al servidor para obtener el número de libros y actualiza el contador periódicamente.


### `frontend/src/LibraryView.js`

Propósito: Componente para visualizar y gestionar la biblioteca de libros.

Estado:

*   `books`: Array de objetos que representan los libros.
*   `searchTerm`: Término de búsqueda.
*   `error`: Mensaje de error.
*   `loading`: Indica si se están cargando los datos.
*   `isMobile`: Indica si el dispositivo es móvil.


Propiedades: Ninguna.

Efectos Secundarios:  Realiza una petición al servidor para obtener los libros, con opciones de filtrado.

Interacción con el usuario: Permite buscar libros por título y autor, eliminar libros y navegar a las vistas de lectura.

Interacción con el backend: Realiza peticiones a los endpoints `/books/` y `/books/:bookId` (DELETE).



### `frontend/src/UploadView.js`

Propósito: Componente para subir nuevos libros.

Estado:

*   `filesToUpload`: Array de objetos que representan los archivos a subir.
*   `isUploading`: Booleano que indica si se está subiendo un archivo.

Propiedades: Ninguna

Efectos Secundarios: Maneja la subida y el feedback de los archivos.

Interacción con el usuario: Permite seleccionar y subir archivos.


Interacción con el backend: Realiza peticiones a `/upload-book/`.


### `frontend/src/ToolsView.js`

Propósito: Componente para las herramientas de conversión EPUB a PDF.

Estado:

*   `selectedFile`: Archivo EPUB seleccionado.
*   `message`: Mensaje al usuario.
*   `isLoading`: Indica si está en proceso de conversión.

Propiedades:  Ninguna.

Efectos Secundarios:  Realiza una petición POST a `/tools/convert-epub-to-pdf` para realizar la conversión.


### `frontend/src/ReaderView.js`

Propósito: Componente para leer libros en formato EPUB usando `react-reader`.

Estado:

*   `location`: Ubicación actual en el libro.
*   `epubData`: Datos del libro EPUB.
*   `isLoading`: Indica si el libro se está cargando.
*   `error`: Mensaje de error.

Propiedades: Recibe el `bookId` desde los parámetros de la URL.

Efectos Secundarios:  Realiza una petición a `/books/download/:bookId` para obtener el libro.


### `frontend/src/RagView.js`

Propósito: Componente para interactuar con el sistema RAG mediante una interfaz de chat.

Estado:  (Documentado en el código fuente).

Propiedades: Ninguna.

Efectos Secundarios:  Maneja la interacción con el usuario y las peticiones al backend para las consultas RAG.

Interacción con el usuario:  Permite al usuario enviar consultas y visualizar las respuestas.

Interacción con el backend:  Realiza peticiones a `/rag/query/`, `/rag/status/:book_id`, `/rag/index/:book_id` (POST).


### `frontend/src/CategoriesView.js`

Propósito: Visualizar las categorías de libros.

Estado:
* `categories`: Lista de categorías de libros
* `error`: Mensaje de error
* `loading`: Estado de carga


Propiedades: Ninguna.

Efectos Secundarios: Carga las categorías desde el backend usando `useEffect`.

Interacción con el backend: Solicita datos a través de la URL `/categories/`.


### `frontend/src/ErrorBoundary.js`

Propósito: Componente para capturar y mostrar errores en la interfaz de usuario.

Estado:
* `hasError`: Un booleano que indica si ha ocurrido un error.
* `error`: El objeto de error.



## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario selecciona un archivo de libro en `UploadView.js`.  El frontend envía el archivo al endpoint `/upload-book/` del backend. El backend procesa el archivo, extrae el texto y metadatos con la ayuda de la IA (Gemini) y lo almacena en la base de datos.  `LibraryView.js` muestra la lista de libros desde la base de datos a través del endpoint `/books/`. Los usuarios pueden buscar, descargar, o leer los libros.  `RagView.js` interactúa con el sistema RAG a través de los endpoints `/rag/query/` y `/rag/status/:bookId`.

**Endpoints de la API:**

*   `/upload-book/` (POST): Subir un libro.
*   `/books/` (GET): Obtener una lista de libros (con opciones de filtrado).
*   `/books/count` (GET): Obtener el número total de libros.
*   `/books/search/` (GET): Buscar libros por título parcial.
*   `/categories/` (GET): Obtener una lista de categorías.
*   `/books/:book_id` (DELETE): Eliminar un libro.
*   `/books/download/:book_id` (GET): Descargar un libro.
*   `/tools/convert-epub-to-pdf` (POST): Convertir EPUB a PDF.
*   `/rag/upload-book/` (POST): Subir un libro para RAG.
*   `/rag/query/` (POST): Consultar el sistema RAG.
*   `/rag/index/:book_id` (POST): Indexar un libro en RAG.
*   `/rag/status/:book_id` (GET): Obtener el estado de indexación RAG.
*   `/rag/reindex/category/:category_name` (POST): Reindexar categoría en RAG.
*   `/rag/reindex/all` (POST): Reindexar toda la biblioteca en RAG.
*   `/rag/estimate/book/:book_id` (GET): Estimar coste para un libro.
*   `/rag/estimate/category/:category_name` (GET): Estimar coste para una categoría.
*   `/rag/estimate/all` (GET): Estimar coste para todos los libros.


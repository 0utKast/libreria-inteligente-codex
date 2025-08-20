# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales (PDF y EPUB). La aplicación ofrece funcionalidades para subir libros, buscarlos por título, autor o categoría, descargarlos y leerlos directamente en el navegador.  Además, integra un sistema de Recuperación de Información basada en Conocimiento (RAG) que permite al usuario conversar con una IA sobre el contenido de los libros cargados.

La arquitectura de la aplicación se basa en un frontend desarrollado con React, un backend construido con FastAPI (Python) y una base de datos SQLite para el almacenamiento persistente de información sobre los libros. El sistema RAG utiliza ChromaDB para la indexación de embeddings y la API de Google Gemini para la generación de texto y embeddings.


## 2. Estructura del Proyecto

El proyecto se organiza en dos directorios principales: `backend/` y `frontend/`.

*   **`backend/`:** Contiene el código del backend de la aplicación, incluyendo:
    *   **`alembic/`:**  Directorio para las migraciones de la base de datos.
    *   **`database.py`:** Configuración de la base de datos SQLite.
    *   **`crud.py`:** Lógica de acceso a datos (CRUD) para la base de datos.
    *   **`main.py`:** Archivo principal de la aplicación FastAPI, que define los endpoints de la API.
    *   **`models.py`:** Definición del modelo de datos `Book` para SQLAlchemy.
    *   **`rag.py`:** Lógica para el sistema RAG (Recuperación de Información basada en Conocimiento).
    *   **`schemas.py`:** Definición de los esquemas Pydantic para la serialización/deserialización de datos.
    *   **`tests/`:**  Contiene las pruebas unitarias para el backend.
    *   **`utils.py`:** Funciones de utilidad, incluyendo la configuración de la API Key de Google.
*   **`frontend/src/`:** Contiene el código del frontend de la aplicación React, incluyendo los componentes de la interfaz de usuario.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/main.py`

**Propósito:** Define los endpoints de la API RESTful usando FastAPI.  Gestiona la subida de libros, la búsqueda, la eliminación y la descarga, además de integrar las funcionalidades RAG.

**Funciones/Clases Principales:**

*   **`upload_book`:** Recibe un archivo de libro (PDF o EPUB), lo procesa (extrae texto y portada si es posible), lo analiza con Gemini para obtener metadatos (título, autor, categoría), y lo guarda en la base de datos.  Retorna un objeto `schemas.Book`.
*   **`read_books`:**  Obtiene una lista de libros filtrada opcionalmente por categoría, búsqueda de texto completo y autor. Retorna una lista de objetos `schemas.Book`.
*   **`get_books_count`:**  Obtiene el número total de libros en la base de datos. Retorna un entero.
*   **`search_books`:**  Busca libros por un título parcial (case-insensitive), con opciones de paginación. Retorna una lista de objetos `schemas.Book`.
*   **`read_categories`:** Obtiene una lista de todas las categorías de libros únicas. Retorna una lista de strings.
*   **`delete_single_book`:** Elimina un libro de la base de datos por su ID.  Incluye la eliminación de los archivos asociados. Retorna un diccionario con un mensaje de confirmación.
*   **`delete_category_and_books`:** Elimina todos los libros de una categoría específica y sus archivos asociados. Retorna el número de libros eliminados.
*   **`download_book`:** Permite la descarga de un libro dado su ID. Retorna una respuesta `FileResponse` de FastAPI.
*   **`convert_epub_to_pdf`:** Convierte un archivo EPUB a PDF utilizando WeasyPrint. Retorna un objeto `schemas.ConversionResponse` con la URL del PDF generado.
*   **`upload_book_for_rag`:**  Procesa un libro para que esté disponible en el sistema RAG. Retorna un objeto `schemas.RagUploadResponse`.
*   **`query_rag_endpoint`:**  Punto final para realizar consultas al sistema RAG. Recibe un objeto `schemas.RagQuery` y retorna un objeto `schemas.RagQueryResponse`.
*   **`index_existing_book_for_rag`:** Indexa un libro ya existente en la base de datos en el sistema RAG.
*   **`rag_status`:** Devuelve el estado de indexación RAG para un libro.
*   **`rag_reindex_category`:** Reindexa todos los libros de una categoría en RAG.
*   **`rag_reindex_all`:** Reindexa todos los libros de la biblioteca en RAG.
*   **`estimate_rag_for_book`:** Estima el coste y los tokens/chunks para un libro.
*   **`estimate_rag_for_category`:** Estima el coste y los tokens/chunks para una categoría.
*   **`estimate_rag_for_all`:** Estima el coste y los tokens/chunks para todos los libros.


### `backend/crud.py`

**Propósito:** Contiene la lógica de acceso a datos (CRUD) para la base de datos.

**Funciones Principales:**

*   **`get_book_by_path`:** Obtiene un libro por su ruta de archivo. Retorna un objeto `models.Book` o `None`.
*   **`get_book_by_title`:** Obtiene un libro por su título exacto. Retorna un objeto `models.Book` o `None`.
*   **`get_books_by_partial_title`:** Busca libros por un título parcial (case-insensitive), con opciones de paginación. Retorna una lista de objetos `models.Book`.
*   **`get_books`:** Obtiene una lista de libros, con opciones de filtrado por categoría, búsqueda general y autor. Retorna una lista de objetos `models.Book`.
*   **`get_categories`:** Obtiene una lista de todas las categorías de libros únicas. Retorna una lista de strings.
*   **`create_book`:** Crea un nuevo libro en la base de datos. Retorna el objeto `models.Book` recién creado.
*   **`delete_book`:** Elimina un libro de la base de datos por su ID, incluyendo sus archivos asociados. Retorna el objeto `models.Book` eliminado o `None`.
*   **`delete_books_by_category`:** Elimina todos los libros de una categoría específica, incluyendo sus archivos asociados. Retorna el número de libros eliminados.
*   **`get_books_count`:** Obtiene el número total de libros en la base de datos. Retorna un entero.

### `backend/models.py`

**Propósito:** Define el modelo de datos `Book` para SQLAlchemy.

**Clase Principal:**

*   **`Book`:**  Representa un libro en la base de datos.  Contiene los atributos `id`, `title`, `author`, `category`, `cover_image_url`, y `file_path`.

### `backend/rag.py`

**Propósito:** Implementa la lógica para el sistema RAG.

**Funciones Principales:**

*   **`get_embedding`:** Genera un embedding para un texto dado usando la API de Google Gemini. Retorna una lista de floats.
*   **`extract_text_from_pdf`:** Extrae el texto de un archivo PDF. Retorna un string.
*   **`extract_text_from_epub`:** Extrae el texto de un archivo EPUB. Retorna un string.
*   **`extract_text`:** Función unificada para extraer texto de archivos PDF y EPUB. Retorna un string.
*   **`chunk_text`:** Divide un texto en fragmentos más pequeños basados en el conteo de tokens. Retorna una lista de strings.
*   **`_has_index_for_book`:** Comprueba si existe un índice para un libro en ChromaDB. Retorna un booleano.
*   **`delete_book_from_rag`:** Elimina el índice RAG de un libro.
*   **`get_index_count`:** Obtiene el número de vectores para un libro. Retorna un entero.
*   **`has_index`:** Comprueba si el libro tiene un índice RAG. Retorna un booleano.
*   **`process_book_for_rag`:** Procesa un libro para el sistema RAG (extrae texto, lo fragmenta, genera embeddings y guarda en ChromaDB).
*   **`estimate_embeddings_for_file`:** Estima el conteo de tokens y número de chunks para un archivo. Retorna un diccionario.
*   **`estimate_embeddings_for_files`:** Estima el conteo de tokens y chunks para una lista de archivos. Retorna un diccionario.
*   **`query_rag`:** Realiza una consulta al sistema RAG. Retorna un string con la respuesta.

### `backend/schemas.py`

**Propósito:** Define los esquemas Pydantic para la serialización/deserialización de datos.

**Clases Principales:**

*   **`BookBase`:** Esquema base para la creación de libros.
*   **`Book`:** Esquema para representar un libro, incluyendo el ID.
*   **`ConversionResponse`:** Esquema para la respuesta de conversión EPUB a PDF.
*   **`RagUploadResponse`:** Esquema para la respuesta de carga de libro en RAG.
*   **`RagQuery`:** Esquema para las consultas al sistema RAG.
*   **`RagQueryResponse`:** Esquema para la respuesta de las consultas RAG.

### `backend/database.py`

**Propósito:** Configura la conexión a la base de datos SQLite.


### `backend/utils.py`

**Propósito:** Define funciones de utilidad, como la configuración de la API Key de Google Gemini.

**Funciones Principales:**

*   **`configure_genai`:** Configura la API Key de Google Gemini a partir de las variables de entorno.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

**Propósito:** Componente principal de la aplicación React, que gestiona el enrutamiento.


### `frontend/src/Header.js`

**Propósito:** Componente para el encabezado de la aplicación, incluyendo la navegación y un contador de libros.

**Estado:** `menuOpen`, `bookCount`, `errorMessage`.

**Efectos:**  Obtiene el conteo de libros del backend y actualiza el estado periódicamente.

**Interacción con el backend:**  Realiza una petición `fetch` a `/books/count` para obtener el número de libros.

### `frontend/src/LibraryView.js`

**Propósito:** Componente para mostrar la lista de libros.

**Estado:** `books`, `searchTerm`, `error`, `loading`, `isMobile`.

**Efectos:** Obtiene los libros del backend según los parámetros de búsqueda y actualiza el estado.

**Interacción con el Backend:** Realiza una petición `fetch` a `/books/` con parámetros de búsqueda.  Maneja peticiones `DELETE` a `/books/{bookId}` para eliminar libros.

### `frontend/src/UploadView.js`

**Propósito:** Componente para subir nuevos libros.

**Estado:** `filesToUpload`, `isUploading`.

**Efectos:** Gestiona la subida y el procesamiento de múltiples archivos.

**Interacción con el backend:**  Realiza peticiones `POST` a `/upload-book/` para cada libro. Actualiza el estado de cada libro en la lista según el resultado de la subida.

### `frontend/src/ReaderView.js`

**Propósito:** Componente para leer libros EPUB usando `react-reader`.

**Estado:** `location`, `epubData`, `isLoading`, `error`.

**Efectos:** Obtiene el libro EPUB del backend y lo carga en el lector.

**Interacción con el backend:** Realiza una petición `fetch` a `/books/download/{bookId}` para obtener el libro.

### `frontend/src/ToolsView.js`

**Propósito:** Componente para mostrar herramientas, actualmente solo un convertidor EPUB a PDF.

**Estado:** `selectedFile`, `message`, `isLoading`.

**Interacción con el backend:** Realiza una petición `POST` a `/tools/convert-epub-to-pdf` para convertir el archivo.

### `frontend/src/RagView.js`

**Propósito:** Componente para interactuar con el sistema RAG.

**Estado:** `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.

**Interacción con el backend:**  Realiza peticiones `POST` a `/rag/query/`, `/rag/index/{book_id}` y `GET` a `/rag/status/{book_id}`.  También realiza peticiones `GET` a `/books/` para cargar la biblioteca de libros.


### `frontend/src/CategoriesView.js`

**Propósito:** Componente para mostrar las categorías de libros disponibles.

**Estado:** `categories`, `error`, `loading`.

**Efectos:** Obtiene las categorías del backend y actualiza el estado.

**Interacción con el backend:**  Realiza una petición `fetch` a `/categories/` para obtener las categorías.


### `frontend/src/config.js`

**Propósito:** Configura la URL base de la API.

### `frontend/src/ErrorBoundary.js`

**Propósito:** Componente React para capturar y mostrar errores.



## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro a través de `UploadView.js`.  Este componente realiza una petición POST a `/upload-book/` en el backend. El backend procesa el archivo, lo analiza con Gemini y lo guarda en la base de datos. Los datos del libro se muestran luego en `LibraryView.js` a través de una petición GET a `/books/`. `LibraryView.js` también permite la descarga de libros a través del endpoint `/books/download/{book_id}` y la eliminación mediante `/books/{bookId}`.  Para la interacción con RAG,  `RagView.js` interactúa con `/rag/query/`, `/rag/upload-book/`, `/rag/index/{book_id}`, y `/rag/status/{book_id}`.

**Principales Endpoints de la API:**

*   **POST `/upload-book/`:** Sube un libro y lo añade a la base de datos.
*   **GET `/books/`:** Obtiene una lista de libros (con opciones de filtrado).
*   **GET `/books/count`:** Obtiene el número total de libros.
*   **GET `/books/search/`:** Busca libros por título parcial.
*   **GET `/categories/`:** Obtiene una lista de categorías.
*   **DELETE `/books/{book_id}`:** Elimina un libro.
*   **DELETE `/categories/{category_name}`:** Elimina una categoría y sus libros.
*   **GET `/books/download/{book_id}`:** Descarga un libro.
*   **POST `/tools/convert-epub-to-pdf`:** Convierte un EPUB a PDF.
*   **POST `/rag/upload-book/`:** Procesa un libro para RAG.
*   **POST `/rag/query/`:** Consulta el sistema RAG.
*   **POST `/rag/index/{book_id}`:** Indexa un libro en RAG.
*   **GET `/rag/status/{book_id}`:** Consulta el estado RAG de un libro.
*   **POST `/rag/reindex/category/{category_name}`:** Reindexa una categoría.
*   **POST `/rag/reindex/all`:** Reindexa todos los libros.



# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales.  La aplicación ofrece funcionalidades para subir libros (PDF y EPUB), buscar libros por título, autor o categoría, visualizarlos, y eliminarlos.  Adicionalmente, incluye un conversador inteligente basado en RAG (Retrieval Augmented Generation) que permite interactuar con el contenido de los libros usando un modelo de lenguaje grande.

La arquitectura de la aplicación se basa en un frontend desarrollado con React y un backend construido con FastAPI (Python).  La persistencia de datos se realiza mediante una base de datos SQLite. El RAG utiliza ChromaDB para la indexación y Gemini de Google para la generación de embeddings y respuestas.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales:

*   **backend/:** Contiene el código del backend de la aplicación, escrito en Python usando el framework FastAPI.  Incluye la lógica de la API, el acceso a la base de datos y la funcionalidad de RAG.
*   **frontend/:** Contiene el código del frontend de la aplicación, desarrollado con React.  Se encuentra en la carpeta `src/` e incluye todos los componentes de la interfaz de usuario.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### backend/schemas.py

Este archivo define los modelos Pydantic para la serialización y validación de datos en la API FastAPI.

*   **`BookBase(BaseModel)`:** Modelo base para la información de un libro.
    *   `title: str`: Título del libro (requerido).
    *   `author: str`: Autor del libro (requerido).
    *   `category: str`: Categoría del libro (requerido).
    *   `cover_image_url: str | None = None`: URL de la imagen de portada (opcional).
    *   `file_path: str`: Ruta al archivo del libro (requerido).

*   **`Book(BookBase)`:** Modelo para un libro, incluyendo su ID. Hereda de `BookBase`.
    *   `id: int`: ID del libro (requerido).
    *   `Config.from_attributes = True`: Permite la creación de instancias desde atributos.

*   **`ConversionResponse(BaseModel)`:** Respuesta para la conversión de EPUB a PDF.
    *   `download_url: str`: URL de descarga del PDF generado (requerido).

*   **`RagUploadResponse(BaseModel)`:** Respuesta para la subida de un libro a RAG.
    *   `book_id: str`: ID del libro en RAG (requerido).
    *   `message: str`: Mensaje de estado (requerido).

*   **`RagQuery(BaseModel)`:**  Modelo para las consultas al sistema RAG.
    *   `query: str`: Consulta del usuario (requerido).
    *   `book_id: str`: ID del libro a consultar (requerido).
    *   `mode: str | None = None`: Modo de consulta ('strict', 'balanced', 'open', opcional, por defecto 'balanced').

*   **`RagQueryResponse(BaseModel)`:** Respuesta para las consultas al sistema RAG.
    *   `response: str`: Respuesta generada por el sistema RAG (requerido).


### backend/crud.py

Este archivo contiene las funciones CRUD (Create, Read, Update, Delete) para interactuar con la base de datos.

*   **`get_book_by_path(db: Session, file_path: str)`:** Obtiene un libro por su ruta de archivo. Devuelve un objeto `models.Book` o `None`.
*   **`get_book_by_title(db: Session, title: str)`:** Obtiene un libro por su título exacto. Devuelve un objeto `models.Book` o `None`.
*   **`get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`:** Busca libros por un título parcial (case-insensitive). Devuelve una lista de objetos `models.Book`.
*   **`get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`:** Obtiene una lista de libros con opciones de filtrado. Devuelve una lista de objetos `models.Book`.
*   **`get_categories(db: Session) -> list[str]`:** Obtiene una lista de todas las categorías únicas. Devuelve una lista de strings.
*   **`create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`:** Crea un nuevo libro en la base de datos. Devuelve el objeto `models.Book` creado.
*   **`delete_book(db: Session, book_id: int)`:** Elimina un libro de la base de datos por su ID y sus archivos asociados. Devuelve el objeto `models.Book` eliminado o `None`.
*   **`delete_books_by_category(db: Session, category: str)`:** Elimina todos los libros de una categoría específica y sus archivos asociados. Devuelve el número de libros eliminados.
*   **`get_books_count(db: Session) -> int`:** Obtiene el número total de libros en la base de datos. Devuelve un entero.


### backend/database.py

Este archivo configura la conexión a la base de datos SQLite. Define `engine` y `SessionLocal`.


### backend/utils.py

Este archivo contiene funciones utilitarias, incluyendo la configuración de la API Key de Google Gemini.

*   **`configure_genai()`:** Configura la API Key de Google Gemini a partir de las variables de entorno `GOOGLE_API_KEY` o `GEMINI_API_KEY`. Lanza `ValueError` si ninguna está configurada.


### backend/models.py

Este archivo define el modelo SQLAlchemy para la tabla `books`.

*   **`Book(Base)`:** Modelo SQLAlchemy para la tabla `books`.
    *   `id`: Clave primaria (Integer).
    *   `title`: Título del libro (String).
    *   `author`: Autor del libro (String).
    *   `category`: Categoría del libro (String).
    *   `cover_image_url`: URL de la imagen de portada (String, nullable).
    *   `file_path`: Ruta al archivo del libro (String, unique).


### backend/rag.py

Este archivo implementa la lógica del sistema RAG.

*   **`get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`:** Genera un embedding para el texto dado usando Gemini. Devuelve una lista de floats o una lista vacía si el texto está vacío o la IA está deshabilitada.
*   **`extract_text_from_pdf(file_path: str) -> str`:** Extrae texto de un archivo PDF. Devuelve un string.
*   **`extract_text_from_epub(file_path: str) -> str`:** Extrae texto de un archivo EPUB. Devuelve un string.
*   **`extract_text(file_path: str) -> str`:** Función unificada para extraer texto de archivos PDF y EPUB. Lanza `ValueError` para tipos de archivo no soportados.
*   **`chunk_text(text: str, max_tokens: int = 1000) -> list[str]`:** Divide el texto en fragmentos más pequeños basándose en el conteo de tokens. Devuelve una lista de strings.
*   **`_has_index_for_book(book_id: str) -> bool`:** Verifica si existe un índice para un libro dado en ChromaDB. Devuelve un booleano.
*   **`delete_book_from_rag(book_id: str)`:** Elimina los vectores de un libro de ChromaDB.
*   **`get_index_count(book_id: str) -> int`:** Cuenta el número de vectores para un libro en ChromaDB. Devuelve un entero.
*   **`has_index(book_id: str) -> bool`:** Devuelve `True` si el libro tiene índice en RAG.
*   **`process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`:** Procesa un libro para RAG: extrae texto, lo divide en fragmentos, genera embeddings y los almacena en ChromaDB.
*   **`estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`:** Estima el conteo de tokens y el número de fragmentos para un archivo. Devuelve un diccionario con "tokens" y "chunks".
*   **`estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`:** Estima tokens y chunks para múltiples archivos. Devuelve un diccionario.
*   **`query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`:** Consulta el sistema RAG para obtener respuestas. Devuelve un string.


### backend/main.py

Este archivo define la aplicación FastAPI.  Incluye la configuración de la API, la definición de rutas y las funciones para procesar libros.

*   **`analyze_with_gemini(text: str) -> dict`:** Analiza el texto dado con Gemini para extraer el título, autor y categoría. Devuelve un diccionario.
*   **`process_pdf(file_path: str, static_dir: str) -> dict`:** Procesa un archivo PDF para extraer texto y la imagen de portada. Devuelve un diccionario.
*   **`process_epub(file_path: str, static_dir: str) -> dict`:** Procesa un archivo EPUB para extraer texto y la imagen de portada. Devuelve un diccionario.  Incluye manejo de errores para archivos EPUB con poca información textual.
*   **Las rutas de la API (`/upload-book`, `/books`, `/books/count`, `/books/search`, `/categories`, `/books/{book_id}`, `/categories/{category_name}`, `/books/download/{book_id}`, `/tools/convert-epub-to-pdf`, `/rag/upload-book`, `/rag/query`, `/rag/index/{book_id}`, `/rag/status/{book_id}`, `/rag/reindex/category/{category_name}`, `/rag/reindex/all`, `/rag/estimate/book/{book_id}`, `/rag/estimate/category/{category_name}`, `/rag/estimate/all`)** : Define los endpoints de la API con sus respectivas funciones.


### backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py

Este archivo es parte de Alembic, una herramienta para gestionar las migraciones de la base de datos.


## 4. Análisis Detallado del Frontend (React)

### frontend/src/Header.js

Componente Header de la aplicación. Muestra el título, el número de libros y un menú de navegación.  Utiliza `useEffect` para obtener el número de libros del backend y actualiza la interfaz periódicamente.  Incluye manejo de errores en la carga del contador.


### frontend/src/App.js

Componente principal de la aplicación, que renderiza el Header y las rutas usando `react-router-dom`.


### frontend/src/ToolsView.js

Componente que muestra las herramientas de la aplicación.  Actualmente solo incluye el `EpubToPdfConverter`.

*   **`EpubToPdfConverter`:** Permite convertir archivos EPUB a PDF.  Utiliza un `FormData` para enviar el archivo al backend, maneja el estado de carga (`isLoading`), y muestra mensajes al usuario (`message`).  Mejora la experiencia de usuario al iniciar la descarga del PDF automáticamente.  Incluye manejo de arrastrar y soltar.

### frontend/src/UploadView.js

Componente para subir libros.  Permite seleccionar múltiples archivos (PDF o EPUB) y muestra el estado de la subida para cada archivo.  Maneja el estado de carga (`isUploading`), muestra mensajes de progreso y error, y redirige a la vista de la biblioteca tras completar la subida de todos los archivos. Incluye manejo de arrastrar y soltar.


### frontend/src/ReaderView.js

Componente para leer libros EPUB.  Utiliza la librería `react-reader`. Obtiene los datos del libro desde el backend (`/books/download/{bookId}`) y los renderiza utilizando `ReactReader`.  Incluye manejo de errores de carga.


### frontend/src/ErrorBoundary.js

Componente para capturar errores en la interfaz de usuario.


### frontend/src/RagView.js

Componente para la interfaz de conversación con la IA.  Permite al usuario seleccionar un libro de la biblioteca, comprobar su estado RAG, indexarlo y realizar consultas.  Incluye manejo de estado de carga (`isLoading`), mensajes al usuario (`message`), gestión de historial de chat (`chatHistory`) y selección de modo de consulta (`mode`).  Gestiona el estado del índice RAG mediante `checkLibraryStatus` e `indexLibraryBook`, los cuales controlan el índice RAG (creando o actualizando).  Implementa la búsqueda de libros y muestra los resultados. Permite al usuario cambiar entre los diferentes modos de consulta:  `strict`, `balanced`, y `open`.  Utiliza `useMemo` para optimizar el rendimiento.  Auto-scroll al final de la conversación.


### frontend/src/LibraryView.js

Componente para la visualización de la biblioteca.  Permite buscar libros por título, autor o categoría.  Muestra los libros en una grilla y permite eliminarlos.  Utiliza un `useDebounce` personalizado para optimizar las búsquedas.  Incluye un componente `BookCover` para mostrar la portada de los libros, con un fallback a una imagen genérica si la portada falla.  Maneja el estado de carga (`loading`) y muestra mensajes de error (`error`).  Detecta la pantalla móvil para ajustar la interfaz de usuario y permitir la descarga directa de archivos en móviles.


### frontend/src/config.js

Archivo de configuración con la URL de la API.


### frontend/src/CategoriesView.js

Componente para la visualización de las categorías de los libros.  Obtiene las categorías desde el backend (`/categories/`) y las muestra como enlaces para filtrar la biblioteca.  Incluye manejo de errores y estado de carga.


### frontend/src/index.js

Archivo principal del frontend que renderiza la aplicación.


## 5. Flujo de Datos y API

El flujo de datos comienza con el usuario subiendo un libro (PDF o EPUB) a través de la interfaz de subida (`UploadView`). El frontend envía el archivo al backend a través del endpoint `/upload-book`. El backend procesa el archivo (extrayendo texto y portada), lo analiza con Gemini para determinar el título, autor y categoría, y lo guarda en la base de datos.  Si se selecciona la opción de indexar el libro en RAG, los datos del libro se procesan adicionalmente a través del endpoint `/rag/upload-book`  (o `/rag/index/{book_id}`) para crear un vector semántico que se utiliza para consultas posteriores.

Para visualizar los libros, el frontend realiza una petición al endpoint `/books/` (con parámetros opcionales para filtrar por categoría o autor). El backend retorna los datos de los libros, que el frontend (`LibraryView`) renderiza en la pantalla.  El endpoint `/books/count` se usa para mostrar el número total de libros.  El conversador inteligente (`RagView`) se comunica con el backend mediante el endpoint `/rag/query`. El usuario puede realizar consultas al contenido de los libros indexados en RAG.  La conversión EPUB a PDF se realiza a través del endpoint `/tools/convert-epub-to-pdf`.

**Endpoints de la API:**

*   `/upload-book/`: Sube un libro.
*   `/books/`: Obtiene libros (con filtros).
*   `/books/count`: Obtiene el número de libros.
*   `/books/search/`: Busca libros por título parcial.
*   `/categories/`: Obtiene las categorías.
*   `/books/{book_id}`: Elimina un libro.
*   `/categories/{category_name}`: Elimina libros de una categoría.
*   `/books/download/{book_id}`: Descarga un libro.
*   `/tools/convert-epub-to-pdf`: Convierte un EPUB a PDF.
*   `/rag/upload-book/`: Sube un libro a RAG.
*   `/rag/query/`: Consulta RAG.
*   `/rag/index/{book_id}`: Indexa un libro en RAG.
*   `/rag/status/{book_id}`: Obtiene el estado RAG de un libro.
*   `/rag/reindex/category/{category_name}`: Reindexa una categoría en RAG.
*   `/rag/reindex/all`: Reindexa toda la biblioteca en RAG.
*   `/rag/estimate/book/{book_id}`: Estimación de tokens/chunks/coste para un libro.
*   `/rag/estimate/category/{category_name}`: Estimación de tokens/chunks/coste para una categoría.
*   `/rag/estimate/all`: Estimación de tokens/chunks/coste para toda la biblioteca.


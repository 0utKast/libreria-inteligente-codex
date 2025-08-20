# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitalmente.  La aplicación ofrece funcionalidades para subir libros (PDF y EPUB), buscar libros por título, autor o categoría, leer libros EPUB directamente en el navegador, y consultar información sobre los libros utilizando un sistema de Recuperación de Información basada en Contexto (RAG) con IA.

La arquitectura de la aplicación se basa en un frontend desarrollado con React, un backend con FastAPI (Python) y una base de datos SQLite. El backend proporciona una API RESTful que el frontend consume para gestionar los datos de los libros y las interacciones con la IA.  El RAG se basa en embeddings de Google Gemini y utiliza ChromaDB para la indexación de los documentos.

## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   **`backend/`**: Contiene el código del backend de FastAPI, incluyendo:
    *   **`alembic/`**:  Directorio para las migraciones de la base de datos.
    *   **`database.py`**: Configuración de la base de datos SQLite.
    *   **`crud.py`**: Lógica de acceso a datos (CRUD) para la base de datos.
    *   **`models.py`**: Definición del modelo de datos `Book` para SQLAlchemy.
    *   **`rag.py`**: Lógica para la indexación y consulta del sistema RAG.
    *   **`schemas.py`**: Definición de los esquemas Pydantic para la serialización/deserialización de datos.
    *   **`main.py`**: Archivo principal de la aplicación FastAPI.
    *   **`utils.py`**: Funciones utilitarias.
    *   **`tests/`**:  Contiene las pruebas unitarias del backend.
    *   **`scripts/`**:  Scripts auxiliares, como `generate_tests.py`.

*   **`frontend/src/`**: Contiene el código del frontend React, con componentes para cada vista principal de la aplicación.
    *   Componentes de la interfaz de usuario (UI).
    *   `config.js` para la URL del API.
    *   `index.js` como punto de entrada.
    *   `ErrorBoundary.js` para gestión de errores en la UI.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/main.py`

**Propósito:** Archivo principal de la aplicación FastAPI. Define las rutas y la lógica principal del backend.

```python
# ... (código omitido para brevedad)
```

**Funciones y Clases Principales:**

*   `analyze_with_gemini(text: str) -> dict`: Envía texto a la API de Gemini para extraer metadatos. Retorna un diccionario con título, autor y categoría.
*   `process_pdf(file_path: str, static_dir: str) -> dict`: Procesa un archivo PDF, extrayendo texto y una imagen de portada. Retorna un diccionario con el texto y la URL de la portada.
*   `process_epub(file_path: str, static_dir: str) -> dict`:  Procesa un archivo EPUB, extrayendo texto y una imagen de portada. Retorna un diccionario con el texto y la URL de la portada.
*   `upload_book`: Endpoint para subir un libro.
*   `read_books`: Endpoint para obtener una lista de libros.
*   `get_books_count`: Endpoint para obtener el número total de libros.
*   `search_books`: Endpoint para buscar libros por título parcial.
*   `read_categories`: Endpoint para obtener una lista de categorías.
*   `delete_single_book`: Endpoint para eliminar un libro por su ID.
*   `delete_category_and_books`: Endpoint para eliminar libros de una categoría específica.
*   `download_book`: Endpoint para descargar un libro.
*   `convert_epub_to_pdf`: Endpoint para convertir un EPUB a PDF.
*   `upload_book_for_rag`: Endpoint para procesar un libro para el sistema RAG.
*   `query_rag_endpoint`: Endpoint para realizar una consulta al sistema RAG.
*   `index_existing_book_for_rag`: Endpoint para indexar un libro ya existente.
*   `rag_status`: Endpoint para obtener el estado RAG de un libro.
*   `rag_reindex_category`: Endpoint para reindexar los libros de una categoría.
*   `rag_reindex_all`: Endpoint para reindexar todos los libros.
*   `estimate_rag_for_book`: Endpoint para estimar recursos RAG para un libro.
*   `estimate_rag_for_category`: Endpoint para estimar recursos RAG para una categoría.
*   `estimate_rag_for_all`: Endpoint para estimar recursos RAG para todos los libros.


### `backend/crud.py`

**Propósito:**  Contiene la lógica de acceso a datos (CRUD) para interactuar con la base de datos.

```python
# ... (código omitido para brevedad)
```

**Funciones Principales:**

*   `get_book_by_path(db: Session, file_path: str)`: Obtiene un libro por su ruta de archivo.
*   `get_book_by_title(db: Session, title: str)`: Obtiene un libro por su título.
*   `get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100)`: Busca libros por un título parcial.
*   `get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None)`: Obtiene una lista de libros con opciones de filtrado.
*   `get_categories(db: Session) -> list[str]`: Obtiene una lista de categorías únicas.
*   `create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str)`: Crea un nuevo libro.
*   `delete_book(db: Session, book_id: int)`: Elimina un libro por su ID.
*   `delete_books_by_category(db: Session, category: str)`: Elimina todos los libros de una categoría.
*   `get_books_count(db: Session) -> int`: Obtiene el número total de libros.


### `backend/models.py`

**Propósito:** Define el modelo de datos `Book` para SQLAlchemy.

```python
# ... (código omitido para brevedad)
```

**Clase Principal:**

*   `Book(Base)`: Modelo de datos para representar un libro en la base de datos.


### `backend/rag.py`

**Propósito:** Contiene la lógica para la indexación y consulta del sistema RAG.

```python
# ... (código omitido para brevedad)
```

**Funciones Principales:**

*   `get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT")`: Genera un embedding para un texto dado.
*   `extract_text_from_pdf(file_path: str) -> str`: Extrae texto de un archivo PDF.
*   `extract_text_from_epub(file_path: str) -> str`: Extrae texto de un archivo EPUB.
*   `extract_text(file_path: str) -> str`: Función unificada para extraer texto de archivos PDF o EPUB.
*   `chunk_text(text: str, max_tokens: int = 1000) -> list[str]`: Divide un texto en fragmentos.
*   `_has_index_for_book(book_id: str) -> bool`: Verifica si existe un índice para un libro.
*   `delete_book_from_rag(book_id: str)`: Elimina los vectores de un libro de ChromaDB.
*   `get_index_count(book_id: str) -> int`: Obtiene el número de vectores indexados de un libro.
*   `has_index(book_id: str) -> bool`: Verifica si un libro tiene un índice RAG.
*   `process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False)`: Procesa un libro para el RAG (extracción de texto, creación de embeddings e indexación).
*   `estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict`: Estima el número de tokens y chunks para un archivo.
*   `estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict`: Estima el número de tokens y chunks para múltiples archivos.
*   `query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None)`: Realiza una consulta al sistema RAG.


### `backend/schemas.py`

**Propósito:** Define los esquemas Pydantic para la serialización y deserialización de datos.

```python
# ... (código omitido para brevedad)
```

**Clases Principales:**

*   `BookBase(BaseModel)`: Esquema base para la información de un libro.
*   `Book(BookBase)`: Esquema completo para un libro incluyendo el ID.
*   `ConversionResponse(BaseModel)`: Esquema para la respuesta de conversión de EPUB a PDF.
*   `RagUploadResponse(BaseModel)`: Esquema para la respuesta de subida de libro para RAG.
*   `RagQuery(BaseModel)`: Esquema para la solicitud de consulta RAG.
*   `RagQueryResponse(BaseModel)`: Esquema para la respuesta de consulta RAG.


### `backend/database.py`

**Propósito:** Configuración de la base de datos SQLite.

```python
# ... (código omitido para brevedad)
```

**Variables Principales:**

*   `SQLALCHEMY_DATABASE_URL`: URL de conexión a la base de datos.
*   `engine`: Motor de base de datos SQLAlchemy.
*   `SessionLocal`: Fábrica de sesiones SQLAlchemy.
*   `Base`: Clase base declarativa para SQLAlchemy.


### `backend/utils.py`

**Propósito:** Contiene funciones utilitarias.

```python
# ... (código omitido para brevedad)
```

**Funciones Principales:**

*   `configure_genai()`: Configura la API Key de Google Generative AI.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/App.js`

**Propósito:** Componente principal de la aplicación React.  Define las rutas de navegación.

```jsx
// ... (código omitido para brevedad)
```

**Estado:** No tiene estado propio.

**Propiedades:** No tiene propiedades.


### `frontend/src/LibraryView.js`

**Propósito:** Componente que muestra la lista de libros.

```jsx
// ... (código omitido para brevedad)
```

**Estado:**

*   `books`: Array de objetos que representan los libros.
*   `searchTerm`: Término de búsqueda actual.
*   `error`: Mensaje de error.
*   `loading`: Indicador de carga.
*   `isMobile`: Indica si la pantalla actual es móvil.

**Propiedades:** No tiene propiedades.

**Efectos Secundarios:**  Utiliza `useEffect` para realizar una petición a la API cuando se monta el componente y cuando cambia el término de búsqueda.  Usa `useCallback` para optimizar el proceso de obtener libros de la API.

**Interacción con el usuario:** El usuario puede buscar libros mediante un campo de texto y eliminar libros.


### `frontend/src/UploadView.js`

**Propósito:** Componente que permite a los usuarios subir nuevos libros.

```jsx
// ... (código omitido para brevedad)
```

**Estado:**

*   `filesToUpload`: Array de objetos, cada uno con información sobre un archivo que se va a subir.
*   `isUploading`: Indicador booleano para mostrar que se está subiendo un archivo.

**Propiedades:** No tiene propiedades.

**Efectos Secundarios:** No utiliza efectos secundarios.

**Interacción con el usuario:**  El usuario puede seleccionar archivos arrastrando y soltando o usando un botón. El componente muestra el estado de la subida de cada archivo.


### `frontend/src/ReaderView.js`

**Propósito:** Muestra un libro EPUB utilizando `react-reader`.

```jsx
// ... (código omitido para brevedad)
```

**Estado:**

*   `location`: Objeto con la ubicación actual del lector de EPUB.
*   `epubData`: ArrayBuffer del libro EPUB descargado.
*   `isLoading`: Indicador de carga.
*   `error`: Mensaje de error.


**Propiedades:** No tiene propiedades.

**Efectos Secundarios:** Utiliza `useEffect` para realizar la petición al backend y descargar el libro.

**Interacción con el usuario:** No tiene interacción con el backend, solo presenta el libro.


### `frontend/src/Header.js`

**Propósito:** Componente de encabezado de la aplicación.

```jsx
// ... (código omitido para brevedad)
```

**Estado:**

*   `menuOpen`: Indica si el menú está abierto.
*   `bookCount`: Número de libros en la biblioteca.
*   `errorMessage`: Mensaje de error al obtener el conteo de libros.

**Propiedades:** No tiene propiedades.

**Efectos Secundarios:** Utiliza `useEffect` para obtener el número de libros en la biblioteca con intervalos regulares.

**Interacción con el usuario:** El usuario puede abrir y cerrar el menú de navegación.


### `frontend/src/CategoriesView.js`

**Propósito:** Componente que muestra todas las categorías de libros.

```jsx
// ... (código omitido para brevedad)
```

**Estado:**

*   `categories`: Lista de categorías.
*   `error`: Mensaje de error.
*   `loading`: Indicador de carga.

**Propiedades:** No tiene propiedades.

**Efectos Secundarios:** Usa `useEffect` para obtener las categorías de la API.

**Interacción con el usuario:** El usuario puede navegar a la vista de la biblioteca filtrando por categoría.


### `frontend/src/ToolsView.js`

**Propósito:** Componente que contiene las herramientas de la biblioteca, actualmente solo un convertidor de EPUB a PDF.

```jsx
// ... (código omitido para brevedad)
```

**Estado:**

*   `selectedFile`: Archivo seleccionado por el usuario.
*   `message`: Mensaje informativo o de error.
*   `isLoading`: Indica si se está realizando la conversión.

**Propiedades:** No tiene propiedades.

**Interacción con el usuario:** El usuario puede seleccionar un archivo EPUB y convertirlo a PDF.

### `frontend/src/RagView.js`

**Propósito:** Componente que permite al usuario conversar con la IA sobre un libro.

```jsx
// ... (código omitido para brevedad)
```

**Estado:** (estado simplificado para brevedad)

*   `chatHistory`: Historial de la conversación.
*   `currentQuery`: Consulta actual del usuario.
*   `isLoading`: Indica si se está procesando una consulta.
*   `bookId`: ID del libro seleccionado.
*   `libraryBooks`: Libros disponibles en la biblioteca.
*   `selectedLibraryId`: ID del libro seleccionado en la biblioteca.
*   `libStatus`: Estado del índice RAG del libro seleccionado.
*   `actionsBusy`: Indica si se están realizando acciones largas (indexar).
*   `searchTerm`: Término de búsqueda actual.
*   `searchResults`: Resultados de búsqueda.
*   `resultsOpen`: Indica si se muestran los resultados de búsqueda.
*   `mode`: Modo de respuesta de la IA.


**Propiedades:** No tiene propiedades.


**Efectos Secundarios:** Usa `useEffect` para cargar los libros y gestionar la búsqueda.


**Interacción con el usuario:** El usuario puede seleccionar un libro, indexarlo, formular preguntas y ver las respuestas de la IA.

### `frontend/src/ErrorBoundary.js`

**Propósito:** Componente para gestionar errores de la interfaz de usuario.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro (PDF o EPUB) a través de `UploadView.js`.  Este componente envía una petición POST a `/upload-book/` en el backend.

El backend:

1.  Guarda el archivo.
2.  Procesa el archivo (`process_pdf` o `process_epub`) para extraer texto y una imagen de portada.
3.  Utiliza `analyze_with_gemini` para obtener metadatos del libro a través de la API de Gemini.
4.  Guarda los datos del libro en la base de datos utilizando `crud.create_book`.
5.  Retorna un objeto `Book` al frontend.

`LibraryView.js` realiza peticiones GET a `/books/` para obtener la lista de libros, con opciones de filtrado por categoría y búsqueda.  `/books/count` proporciona el conteo de libros. `/books/download/{book_id}` permite descargar un libro. `/categories/` devuelve la lista de categorías.

Para RAG:

1. `/rag/upload-book/`: Sube un libro para su indexación.
2. `/rag/index/{book_id}`: Indexa un libro ya existente.
3. `/rag/query/`: Consulta la IA utilizando el sistema RAG.
4. `/rag/status/{book_id}`: Devuelve el estado RAG de un libro.
5. `/rag/reindex/category/{category_name}`: Reindexa una categoría de libros.
6. `/rag/reindex/all`: Reindexa todos los libros.
7. `/rag/estimate/book/{book_id}`: Estima el coste y recursos RAG de un libro.
8. `/rag/estimate/category/{category_name}`: Estima el coste y recursos RAG de una categoría.
9. `/rag/estimate/all`: Estima el coste y recursos RAG para todos los libros.
10. `/tools/convert-epub-to-pdf`: Convierte un archivo EPUB a PDF.


El frontend actualiza su estado con los datos recibidos del backend y renderiza la información al usuario. La navegación se maneja mediante `react-router-dom`.

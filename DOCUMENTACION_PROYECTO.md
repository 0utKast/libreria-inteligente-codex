# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros electrónicos (PDF y EPUB).  La aplicación proporciona funcionalidades para subir libros, buscarlos por título, autor o categoría, descargarlos y leerlos directamente en el navegador.  Además, integra un sistema de preguntas y respuestas (RAG) basado en modelos de lenguaje grande de Google Gemini, permitiendo a los usuarios hacer preguntas sobre el contenido de sus libros.

La aplicación se basa en una arquitectura cliente-servidor con un frontend desarrollado en React y un backend en FastAPI (Python).  Los datos se almacenan en una base de datos SQLite.  El sistema RAG utiliza ChromaDB para indexar el contenido de los libros y permitir búsquedas semánticas eficientes.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales:  `backend/` y `frontend/`.

*   **backend/:** Contiene el código del backend en Python, utilizando el framework FastAPI.  Incluye:
    *   `alembic/`:  Directorio para las migraciones de la base de datos.
    *   `database.py`: Configuración de la base de datos SQLite.
    *   `models.py`: Definición del modelo de datos para los libros.
    *   `schemas.py`: Definición de los esquemas Pydantic para la serialización y validación de datos.
    *   `crud.py`: Lógica de acceso a datos (CRUD) para la base de datos.
    *   `utils.py`: Funciones de utilidad, incluyendo la configuración de la API Key de Google Gemini.
    *   `rag.py`: Lógica para el sistema de preguntas y respuestas (RAG).
    *   `main.py`: Archivo principal del backend, definiendo las rutas de la API.
    *   `tests/`:  Directorio con las pruebas unitarias del backend.

*   **frontend/:** Contiene el código del frontend en React.  Incluye:
    *   `src/`: Directorio principal del código fuente del frontend.
        *   Componentes React para la interfaz de usuario.
        *   `config.js`: Configuración de la URL de la API.
        *   `index.js`: Archivo de entrada del frontend.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### backend/main.py

**Propósito:** Define las rutas y la lógica principal de la API FastAPI.

```
# Funciones de IA y Procesamiento ...
@app.post("/upload-book/", response_model=schemas.Book) ...
@app.get("/books/", response_model=List[schemas.Book]) ...
@app.get("/books/count", response_model=int) ...
@app.get("/books/search/", response_model=List[schemas.Book]) ...
@app.get("/categories/", response_model=List[str]) ...
@app.delete("/books/{book_id}") ...
@app.delete("/categories/{category_name}") ...
@app.get("/books/download/{book_id}") ...
@app.post("/tools/convert-epub-to-pdf", response_model=schemas.ConversionResponse) ...
@app.post("/rag/upload-book/", response_model=schemas.RagUploadResponse) ...
@app.post("/rag/query/", response_model=schemas.RagQueryResponse) ...
@app.post("/rag/index/{book_id}") ...
@app.get("/rag/status/{book_id}") ...
@app.post("/rag/reindex/category/{category_name}") ...
@app.post("/rag/reindex/all") ...
@app.get("/rag/estimate/book/{book_id}") ...
@app.get("/rag/estimate/category/{category_name}") ...
@app.get("/rag/estimate/all") ...
```

Cada función (`@app.post`, `@app.get`, `@app.delete`) define un endpoint de la API.  Las funciones manejan las solicitudes, interactúan con la base de datos (`crud.py`) y el sistema RAG (`rag.py`) y devuelven respuestas en formato JSON. Se incluyen funciones auxiliares para el procesamiento de archivos PDF y EPUB.

### backend/crud.py

**Propósito:**  Proporciona las funciones CRUD (Create, Read, Update, Delete) para la interacción con la base de datos.

```python
def get_book_by_path(db: Session, file_path: str): ...
def get_book_by_title(db: Session, title: str): ...
def get_books_by_partial_title(db: Session, title: str, skip: int = 0, limit: int = 100): ...
def get_books(db: Session, category: str | None = None, search: str | None = None, author: str | None = None): ...
def get_categories(db: Session) -> list[str]: ...
def create_book(db: Session, title: str, author: str, category: str, cover_image_url: str, file_path: str): ...
def delete_book(db: Session, book_id: int): ...
def delete_books_by_category(db: Session, category: str): ...
def get_books_count(db: Session) -> int: ...
```

Cada función recibe una sesión de la base de datos (`db: Session`) y parámetros adicionales según la operación. Devuelven objetos `models.Book` o listas de ellos, o un conteo. `delete_book` y `delete_books_by_category`  gestionan la eliminación de archivos asociados.

### backend/models.py

**Propósito:** Define el modelo de datos `Book` para la base de datos.

```python
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    category = Column(String, index=True)
    cover_image_url = Column(String, nullable=True)
    file_path = Column(String, unique=True)
```

Este modelo mapea la tabla `books` en la base de datos. Cada atributo corresponde a una columna de la tabla.

### backend/rag.py

**Propósito:** Implementa la lógica para el sistema de preguntas y respuestas (RAG).

```python
def get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT"): ...
def extract_text_from_pdf(file_path: str) -> str: ...
def extract_text_from_epub(file_path: str) -> str: ...
def extract_text(file_path: str) -> str: ...
def chunk_text(text: str, max_tokens: int = 1000) -> list[str]: ...
def _has_index_for_book(book_id: str) -> bool: ...
def delete_book_from_rag(book_id: str): ...
def get_index_count(book_id: str) -> int: ...
def has_index(book_id: str) -> bool: ...
async def process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False): ...
def estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict: ...
def estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict: ...
async def query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None): ...
```

Incluye funciones para generar embeddings, extraer texto de archivos PDF y EPUB, dividir el texto en fragmentos, gestionar el índice de ChromaDB y realizar consultas al sistema RAG.  `query_rag` interactúa con el modelo de lenguaje grande de Google Gemini.


### backend/schemas.py

**Propósito:** Define los esquemas Pydantic para la validación y serialización de datos.

```python
class BookBase(BaseModel): ...
class Book(BookBase): ...
class ConversionResponse(BaseModel): ...
class RagUploadResponse(BaseModel): ...
class RagQuery(BaseModel): ...
class RagQueryResponse(BaseModel): ...
```

Define clases Pydantic para representar la estructura de los datos de los libros, las respuestas de las conversiones, las respuestas de la subida a RAG, las consultas RAG, y las respuestas RAG.


### backend/database.py

**Propósito:** Configura la conexión a la base de datos SQLite.

Este archivo configura la conexión a la base de datos mediante SQLAlchemy, definiendo el motor de la base de datos y la clase `SessionLocal` para crear sesiones.


### backend/utils.py

**Propósito:** Funciones auxiliares, principalmente la configuración de la API key de Google Generative AI.

Esta función carga las variables de entorno y configura el cliente de Google Generative AI.


## 4. Análisis Detallado del Frontend (React)

### frontend/src/App.js

**Propósito:** Componente principal de la aplicación React.

Este componente define las rutas de navegación utilizando `react-router-dom`. Renderiza el componente `Header` y otros componentes basados en la ruta activa.

### frontend/src/Header.js

**Propósito:** Componente de encabezado de la aplicación.

Muestra el título de la aplicación, el número de libros en la biblioteca (obtenido del backend) y un menú de navegación.  Maneja el estado `menuOpen` para controlar la visibilidad del menú.

### frontend/src/LibraryView.js

**Propósito:** Componente para mostrar la biblioteca de libros.

Este componente muestra una lista de libros de la biblioteca, gestionando la paginación y la búsqueda. Obtiene los datos de libros del backend mediante la API `/books/`. Usa `useSearchParams` para gestionar parámetros de búsqueda y filtrado. El estado incluye los libros, los términos de búsqueda y un estado de carga/error.

### frontend/src/UploadView.js

**Propósito:** Componente para subir libros a la biblioteca.

Permite a los usuarios seleccionar múltiples archivos (PDF y EPUB) y subirlos al backend.  Gestiona el estado de carga de cada archivo y muestra mensajes de progreso/error. El estado incluye una lista de archivos con su estado (pending, uploading, success, error).

### frontend/src/ToolsView.js

**Propósito:** Componente que muestra las herramientas disponibles.

Actualmente, incluye un convertidor de EPUB a PDF que envía una solicitud POST a `/tools/convert-epub-to-pdf`. Gestiona el estado de carga y muestra mensajes de progreso. Se utiliza un estado para el archivo seleccionado y los mensajes que se muestran al usuario.

### frontend/src/ReaderView.js

**Propósito:** Componente para leer libros EPUB.

Permite leer libros EPUB utilizando la librería `react-reader`.  Obtiene el libro del backend mediante la API `/books/download/{bookId}` y lo muestra usando `ReactReader`. Gestiona el estado de carga del libro y muestra un mensaje de error si hay problema.

### frontend/src/RagView.js

**Propósito:** Componente para interactuar con el sistema RAG.

Permite a los usuarios realizar consultas de texto al modelo de lenguaje grande. Obtiene datos de la biblioteca de backend para seleccionar un libro. Gestiona el historial del chat y envía consultas POST a `/rag/query/`.  Gestiona el estado de carga, el historial del chat, la consulta actual, y mensajes de error. Incluye un campo de entrada de texto para la pregunta y un botón para enviar la consulta.

### frontend/src/ErrorBoundary.js

**Propósito:** Componente para gestionar errores en la interfaz de usuario.

Este componente sirve como un envoltorio para capturar errores que puedan ocurrir en los componentes hijo y mostrar un mensaje de error personalizado.


### frontend/src/config.js

**Propósito:** Configuración de la URL de la API.

Este archivo define la URL base de la API backend.


### frontend/src/CategoriesView.js

**Propósito:** Componente para mostrar todas las categorías.

Este componente muestra una lista de categorías, obteniendo los datos del backend mediante la API `/categories/`. Gestiona el estado de carga y muestra mensajes de error.


### frontend/src/index.js

**Propósito:** Archivo de entrada de la aplicación React.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario sube un libro a través de `UploadView.js`. Este componente envía una solicitud POST a `/upload-book/` en el backend.  El backend procesa el archivo (extrae texto, obtiene una portada), utiliza Google Gemini para analizar el texto y extraer metadata y, finalmente, guarda la información en la base de datos y retorna un objeto `schemas.Book`. El `UploadView` actualiza su estado basándose en la respuesta.

Para consultar libros, el frontend usa `LibraryView.js`. Envía peticiones GET a `/books/` con parámetros opcionales (category, search, author).  El backend filtra los datos y devuelve la lista de libros. El frontend renderiza los datos. El detalle de un libro se puede obtener mediante `/books/download/{book_id}`.

El sistema RAG permite realizar consultas al contenido de un libro utilizando los endpoints: `/rag/upload-book/`, `/rag/query/`, `/rag/index/{book_id}`, `/rag/status/{book_id}`, `/rag/reindex/category/{category_name}`, `/rag/reindex/all`, `/rag/estimate/book/{book_id}`, `/rag/estimate/category/{category_name}`, `/rag/estimate/all`.

En resumen, los principales endpoints de la API son:

*   `/upload-book/`: POST - Sube un libro y guarda los metadatos en la base de datos.
*   `/books/`: GET - Obtiene una lista de libros, con opciones de filtrado.
*   `/books/count`: GET - Devuelve el número total de libros.
*   `/books/search/`: GET - Busca libros por un título parcial.
*   `/categories/`: GET - Obtiene una lista de categorías únicas.
*   `/books/{book_id}`: DELETE - Elimina un libro por su ID.
*   `/categories/{category_name}`: DELETE - Elimina una categoría y sus libros.
*   `/books/download/{book_id}`: GET - Descarga un libro por su ID.
*   `/tools/convert-epub-to-pdf`: POST - Convierte un EPUB a PDF.
*   `/rag/upload-book/`: POST - Sube un libro para indexarlo en RAG.
*   `/rag/query/`: POST - Realiza una consulta al sistema RAG.
*   `/rag/index/{book_id}`: POST - (Re)Indexa un libro en RAG.
*   `/rag/status/{book_id}`: GET - Devuelve el estado de indexación RAG de un libro.
*   `/rag/reindex/category/{category_name}`: POST - (Re)indexa todos los libros de una categoría.
*   `/rag/reindex/all`: POST - (Re)indexa todos los libros.
*   `/rag/estimate/book/{book_id}`: GET - Estimación de tokens/chunks y coste para un libro.
*   `/rag/estimate/category/{category_name}`: GET - Estimación de tokens/chunks y coste para una categoría.
*   `/rag/estimate/all`: GET - Estimación de tokens/chunks y coste para todos los libros.


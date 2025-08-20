# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales.  La aplicación permite subir libros en formato PDF y EPUB, los analiza para extraer metadatos (título, autor, categoría) utilizando la IA de Google Gemini, y los almacena en una base de datos.  Además, incluye una funcionalidad de búsqueda y filtrado de libros, y una herramienta para convertir archivos EPUB a PDF.  La aplicación también incorpora un sistema de Recuperación de Información basada en contexto (RAG) para permitir al usuario realizar consultas basadas en el contenido de los libros.

La arquitectura de la aplicación se basa en un frontend desarrollado con React, un backend construido con FastAPI (Python), y una base de datos SQLite. El sistema RAG utiliza ChromaDB para la indexación vectorial y Google Gemini para la generación de embeddings y respuestas.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   **`backend/`**: Contiene el código del backend de la aplicación, utilizando FastAPI y Python.  Esta carpeta se subdivide en:
    *   **`alembic/`**: Contiene las migraciones de la base de datos.
    *   **`schemas.py`**: Define los modelos Pydantic para la serialización y validación de datos.
    *   **`crud.py`**: Implementa las funciones CRUD (Crear, Leer, Actualizar, Eliminar) para interactuar con la base de datos.
    *   **`database.py`**: Configura la conexión a la base de datos SQLite.
    *   **`models.py`**: Define el modelo de datos SQLAlchemy para la tabla `books`.
    *   **`utils.py`**: Contiene funciones utilitarias, incluyendo la configuración de la API Key de Google Gemini.
    *   **`rag.py`**: Implementa la lógica del sistema RAG para indexar y consultar los libros.
    *   **`main.py`**: El punto de entrada de la aplicación FastAPI, definiendo las rutas de la API.
    *   **`tests/`**: Contiene las pruebas unitarias y de integración.

*   **`frontend/src`**: Contiene el código del frontend de la aplicación, utilizando React.  Incluye los componentes para la interfaz de usuario.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/schemas.py`

Este archivo define los modelos Pydantic para la serialización y validación de datos.

```python
class BookBase(BaseModel):
    title: str
    author: str
    category: str
    cover_image_url: str | None = None
    file_path: str

class Book(BookBase):
    id: int

    class Config:
        from_attributes = True

class ConversionResponse(BaseModel):
    download_url: str

class RagUploadResponse(BaseModel):
    book_id: str
    message: str

class RagQuery(BaseModel):
    query: str
    book_id: str
    mode: str | None = None  # 'strict' | 'balanced' | 'open'

class RagQueryResponse(BaseModel):
    response: str
```

### `backend/crud.py`

Este archivo contiene las funciones CRUD para la interacción con la base de datos.

```python
# ... (funciones crud.py)
```

### `backend/database.py`

Este archivo configura la conexión a la base de datos SQLite.

```python
# ... (database.py)
```

### `backend/utils.py`

Este archivo contiene funciones utilitarias, incluyendo la configuración de la API Key.

```python
# ... (utils.py)
```

### `backend/models.py`

Este archivo define el modelo de datos SQLAlchemy para la tabla `books`.

```python
# ... (models.py)
```

### `backend/rag.py`

Este archivo implementa la lógica del sistema RAG.

```python
# ... (rag.py)
```

### `backend/main.py`

Este archivo es el punto de entrada de la aplicación FastAPI, definiendo las rutas y handlers de la API.

```python
# ... (main.py)
```

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

Este archivo define la migración para crear la tabla `books` en la base de datos.

```python
# ... (alembic migration)
```


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/Header.js`

Este componente renderiza el encabezado de la aplicación, incluyendo la navegación.

```javascript
// ... (Header.js)
```

### `frontend/src/App.js`

Este componente es el componente principal de la aplicación React, que renderiza la estructura general y las rutas.

```javascript
// ... (App.js)
```

### `frontend/src/ToolsView.js`

Este componente proporciona una interfaz de usuario para convertir archivos EPUB a PDF.

```javascript
// ... (ToolsView.js)
```

### `frontend/src/UploadView.js`

Este componente permite a los usuarios subir archivos de libros al backend.

```javascript
// ... (UploadView.js)
```

### `frontend/src/ReaderView.js`

Este componente renderiza un visor de libros EPUB usando `react-reader`.

```javascript
// ... (ReaderView.js)
```

### `frontend/src/ErrorBoundary.js`

Este componente maneja los errores que ocurren en los componentes hijos.

```javascript
// ... (ErrorBoundary.js)
```

### `frontend/src/RagView.js`

Este componente proporciona una interfaz de usuario para interactuar con el sistema RAG.

```javascript
// ... (RagView.js)
```

### `frontend/src/LibraryView.js`

Este componente muestra la lista de libros en la biblioteca.

```javascript
// ... (LibraryView.js)
```

### `frontend/src/config.js`

Este archivo contiene la configuración de la URL de la API.

```javascript
// ... (config.js)
```

### `frontend/src/CategoriesView.js`

Este componente muestra una lista de las categorías de libros.

```javascript
// ... (CategoriesView.js)
```

### `frontend/src/index.js`

Este archivo es el punto de entrada de la aplicación React.

```javascript
// ... (index.js)
```


## 5. Flujo de Datos y API

El flujo de datos comienza cuando el usuario selecciona un archivo de libro (PDF o EPUB) en el componente `UploadView`.  El archivo se envía al endpoint `/upload-book/` del backend mediante una solicitud POST.  El backend procesa el archivo, extrae texto, utiliza Google Gemini para extraer metadatos, y guarda el libro en la base de datos y en el sistema de archivos. Luego se devuelve un objeto `Book` al frontend.

El componente `LibraryView` realiza solicitudes GET al endpoint `/books/` para obtener la lista de libros, permitiendo filtrar por categoría o búsqueda de texto parcial.  El endpoint `/books/count` devuelve el número total de libros. El endpoint `/books/download/{book_id}` permite descargar un libro específico.

La funcionalidad de conversión de EPUB a PDF utiliza el endpoint `/tools/convert-epub-to-pdf`.

La interacción con el sistema RAG se realiza a través de los endpoints:

*   `/rag/upload-book/`: Sube un libro para ser indexado en RAG.
*   `/rag/query/`: Realiza una consulta al sistema RAG.
*   `/rag/index/{book_id}`: Indexa un libro existente en la base de datos en RAG.
*   `/rag/status/{book_id}`: Devuelve el estado del índice RAG para un libro determinado.
*   `/rag/reindex/category/{category_name}`: Reindexa todos los libros de una categoría en RAG.
*   `/rag/reindex/all`: Reindexa todos los libros de la biblioteca en RAG.
*   `/rag/estimate/book/{book_id}`: Estimación de tokens/chunks y coste para un libro.
*   `/rag/estimate/category/{category_name}`: Estimación de tokens/chunks y coste para una categoría.
*   `/rag/estimate/all`: Estimación de tokens/chunks y coste para todos los libros.

El frontend actualiza su interfaz de usuario según las respuestas recibidas del backend.

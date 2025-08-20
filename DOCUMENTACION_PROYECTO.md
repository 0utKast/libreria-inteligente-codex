# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales.  La aplicación ofrece funcionalidades para subir libros (PDF y EPUB), visualizarlos en una biblioteca organizada, buscar libros por título, autor o categoría, eliminar libros y convertir archivos EPUB a PDF.  Además, integra una funcionalidad de RAG (Retrieval Augmented Generation) que permite a los usuarios realizar consultas sobre el contenido de sus libros usando un modelo de lenguaje grande, obteniendo respuestas contextualizadas basadas en la información del libro.

La aplicación utiliza una arquitectura cliente-servidor. El frontend está desarrollado con React y se encarga de la interfaz de usuario, la interacción con el usuario y las peticiones a la API. El backend está construido con FastAPI (Python) y se encarga de procesar las peticiones del frontend, interactuar con la base de datos y gestionar la funcionalidad de RAG.  La persistencia de datos se realiza mediante una base de datos SQLite.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   **`backend/`:** Contiene el código del backend de la aplicación, utilizando FastAPI y Python.  Incluye subcarpetas:
    *   **`alembic/`:** Contiene las migraciones de la base de datos.
    *   **`schemas.py`:** Define los modelos Pydantic para la serialización y validación de datos.
    *   **`crud.py`:** Contiene las funciones CRUD (Create, Read, Update, Delete) para la base de datos.
    *   **`database.py`:** Configura la conexión a la base de datos SQLite.
    *   **`models.py`:** Define el modelo de datos SQLAlchemy para la base de datos.
    *   **`utils.py`:** Funciones utilitarias, incluyendo la configuración de la API Key de Google Generative AI.
    *   **`rag.py`:**  Implementa la lógica para el sistema RAG, incluyendo la extracción de texto, generación de embeddings y consultas a la base de conocimiento.
    *   **`main.py`:** El punto de entrada de la aplicación FastAPI.
    *   **`tests/`:** Contiene las pruebas unitarias del backend.
    *   **`tests_curated/`:** Contiene las pruebas de integración y extremo a extremo.


*   **`frontend/src/`:** Contiene el código del frontend de la aplicación, utilizando React.  Incluye los componentes de la interfaz de usuario, la lógica de la aplicación y la gestión de las peticiones a la API.  Algunos componentes relevantes son: `App.js`, `LibraryView.js`, `UploadView.js`, `ToolsView.js`, `RagView.js`, `ReaderView.js`.
*   **`frontend/`:** Contiene el archivo `index.js` y otros archivos de configuración para el frontend.


## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/schemas.py`

Propósito: Define los modelos Pydantic para la serialización y validación de datos.

```python
from pydantic import BaseModel

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

Propósito: Define las funciones CRUD para la interacción con la base de datos.

```python
# Test comment to trigger workflow
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from . import models
import os

# ... (funciones CRUD: get_book_by_path, get_book_by_title, get_books_by_partial_title, get_books, get_categories, create_book, delete_book, delete_books_by_category, get_books_count) ...
```

Cada función realiza una operación CRUD específica sobre la tabla `books` de la base de datos, utilizando SQLAlchemy.  Los parámetros de entrada varían dependiendo de la función, e incluyen objetos `Session` de SQLAlchemy, IDs, títulos, autores, categorías, rutas de archivos, etc.  Los valores de retorno son los libros obtenidos de la base de datos (o `None` si no se encuentran) o el número de libros afectados por una operación de eliminación.


### `backend/database.py`

Propósito: Configura la conexión a la base de datos SQLite.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Usamos una base de datos SQLite que se guardará en la raíz del proyecto
SQLALCHEMY_DATABASE_URL = "sqlite:///../library.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### `backend/utils.py`

Propósito: Funciones utilitarias, incluyendo la configuración de la API Key.

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

def configure_genai():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la API Key. Asegúrate de que GOOGLE_API_KEY o GEMINI_API_KEY estén configuradas en tu archivo .env")
    genai.configure(api_key=api_key)
```

### `backend/models.py`

Propósito: Define el modelo de datos SQLAlchemy para la base de datos.

```python
# Final test comment to trigger workflow
from sqlalchemy import Column, Integer, String
from database import Base

class Book(Base):
    __tablename__ = "books"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    category = Column(String, index=True)
    cover_image_url = Column(String, nullable=True)
    file_path = Column(String, unique=True) # Ruta al archivo original
```

### `backend/rag.py`

Propósito: Implementa la lógica para el sistema RAG.

```python
import os
import google.generativeai as genai
# ... (resto del código: funciones para embedding, extracción de texto, creación de chunks,  indexación y query del RAG con ChromaDB) ...
```

Este archivo contiene funciones para generar embeddings de texto utilizando Google Generative AI, extraer texto de archivos PDF y EPUB, dividir texto en chunks,  indexar esos chunks en una base de conocimiento con embeddings usando ChromaDB y consultar esa base de conocimiento para responder preguntas.


### `backend/main.py`

Propósito: Define las rutas de la API FastAPI.

```python
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Response
# ... (resto del código: definición de las rutas de la API, incluyendo la subida de libros, búsqueda, eliminación, descarga y conversión de EPUB a PDF.  También incluye la lógica de la API del sistema RAG) ...
```

Este archivo es el punto de entrada de la aplicación FastAPI. Define las rutas de la API que manejan las peticiones HTTP del frontend, utilizando los métodos definidos en `crud.py` y `rag.py`.


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/Header.js`

Propósito: Componente que representa el encabezado de la aplicación.

Muestra el logo de la aplicación, un contador de libros (obtenido de la API), un menú de navegación y un botón de menú hamburguesa para dispositivos móviles.

Estado: `menuOpen`, `bookCount`, `errorMessage`.

Efectos secundarios: Realiza una petición a la API para obtener el número total de libros y actualiza el estado `bookCount`.  También realiza un refetch periódico del contador.


### `frontend/src/App.js`

Propósito: Componente principal de la aplicación que contiene el enrutamiento.

Define las rutas para las diferentes vistas de la aplicación, incluyendo: `LibraryView`, `UploadView`, `CategoriesView`, `ToolsView`, `RagView`, `ReaderView`.


### `frontend/src/ToolsView.js`

Propósito: Muestra las herramientas de la aplicación, incluyendo un conversor de EPUB a PDF.

Contiene un componente `EpubToPdfConverter` que permite convertir archivos EPUB a PDF usando la API del backend.  Maneja la selección de archivos, el envío a la API y la gestión de las respuestas, mostrando mensajes de estado al usuario.

Estado: `selectedFile`, `message`, `isLoading`.


### `frontend/src/UploadView.js`

Propósito: Permite a los usuarios subir archivos PDF y EPUB a la aplicación.

Maneja la subida múltiple de archivos, mostrando el estado de subida (pendiente, subiendo, éxito, error) para cada archivo.  Realiza peticiones POST a la API `/upload-book/` para cada archivo subido.

Estado: `filesToUpload`, `isUploading`.


### `frontend/src/ReaderView.js`

Propósito: Muestra un visor de libros EPUB.

Utiliza la librería `react-reader` para mostrar el contenido de los libros.  Obtiene el libro desde el backend mediante una petición GET.

Estado: `location`, `epubData`, `isLoading`, `error`.


### `frontend/src/ErrorBoundary.js`

Propósito: Componente para manejar errores en los componentes hijos.

Captura los errores que se producen en los componentes hijos y muestra un mensaje de error al usuario.


### `frontend/src/RagView.js`

Propósito: Permite al usuario chatear con un modelo de lenguaje grande para obtener información sobre un libro.

Selecciona un libro de la biblioteca, lo indexa para el RAG si no está indexado, permite al usuario hacer preguntas sobre ese libro y muestra la respuesta del modelo de lenguaje.

Estado: `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.


### `frontend/src/LibraryView.js`

Propósito: Muestra la lista de libros de la biblioteca.

Permite buscar libros por título, autor o categoría, y eliminar libros.  Realiza peticiones GET a la API `/books/` para obtener la lista de libros, con opciones de filtrado.

Estado: `books`, `searchParams`, `searchTerm`, `error`, `loading`, `isMobile`.


### `frontend/src/config.js`

Propósito: Define la URL base de la API.


### `frontend/src/CategoriesView.js`

Propósito: Muestra una lista de las categorías de libros disponibles.

Realiza peticiones GET a la API para obtener la lista de categorías.

Estado: `categories`, `error`, `loading`.



## 5. Flujo de Datos y API

El flujo de datos comienza cuando un usuario sube un libro (PDF o EPUB) a través del componente `UploadView` del frontend. El frontend envía una petición POST a la API `/upload-book/` del backend. El backend procesa el archivo, extrae el texto y metadatos utilizando `fitz` (para PDF) o `ebooklib` (para EPUB), y utiliza un modelo de lenguaje (Gemini) para inferir el título, autor y categoría.  A continuación, guarda la información del libro y la ruta del archivo en la base de datos.

El frontend utiliza las APIs `/books/`, `/books/count`, `/books/search/`, `/categories/` y `/books/download/{book_id}` para mostrar la lista de libros, el número total de libros, los resultados de búsqueda, las categorías, y descargar los archivos.

La funcionalidad de RAG utiliza las siguientes APIs:

*   `/rag/upload-book/`: Sube un libro para indexación en el sistema RAG.
*   `/rag/query/`: Consulta el sistema RAG para obtener respuestas a preguntas sobre un libro específico.
*   `/rag/index/{book_id}`: Indexa un libro existente.
*   `/rag/reindex/category/{category_name}`: Reindexa todos los libros de una categoría específica.
*   `/rag/reindex/all`: Reindexa todos los libros.
*   `/rag/status/{book_id}`: Obtiene el estado de indexación de un libro en el RAG.
*   `/rag/estimate/book/{book_id}`: Estima el coste y el número de tokens y chunks del libro para RAG.
*   `/rag/estimate/category/{category_name}`: Estimación para una categoría.
*   `/rag/estimate/all`: Estimación para toda la biblioteca.


La API `/tools/convert-epub-to-pdf` permite la conversión de un archivo EPUB a PDF.  El backend utiliza `weasyprint` para realizar la conversión y devuelve la URL del PDF temporal.

El frontend realiza las peticiones correspondientes a cada API, procesa las respuestas y actualiza la interfaz de usuario.

# DOCUMENTACION_PROYECTO.md

## 1. Descripción General del Proyecto

"Mi Librería Inteligente" es una aplicación web que permite a los usuarios gestionar su colección de libros digitales.  La aplicación ofrece funcionalidades para subir libros en formato PDF y EPUB,  buscar libros por título, autor o categoría,  visualizar la biblioteca, y eliminar libros.  Además, incluye una herramienta para convertir archivos EPUB a PDF y una interfaz de chat basada en Retrieval Augmented Generation (RAG) que permite a los usuarios hacer preguntas sobre el contenido de sus libros utilizando un modelo de lenguaje grande (LLM).

La arquitectura de la aplicación se basa en un frontend desarrollado con React, un backend implementado con FastAPI (Python) y una base de datos SQLite para el almacenamiento persistente de la información de los libros.  El componente RAG utiliza ChromaDB para la indexación de vectores y la API de Gemini de Google para la generación de embeddings y respuestas.


## 2. Estructura del Proyecto

El proyecto se divide en dos partes principales: `backend/` y `frontend/`.

*   **`backend/`:** Contiene el código del backend de la aplicación, utilizando FastAPI y Python.  Se subdivide en:
    *   `alembic/` :  Directorio para las migraciones de la base de datos.
    *   `database.py`:  Configuración de la base de datos SQLite.
    *   `crud.py`:  Lógica de acceso a datos (CRUD).
    *   `models.py`:  Definición del modelo de datos (ORM).
    *   `rag.py`:  Lógica para el sistema RAG.
    *   `schemas.py`:  Definición de los esquemas Pydantic para la serialización y validación de datos.
    *   `main.py`:  Aplicación FastAPI principal.
    *   `utils.py`:  Funciones utilitarias.
    *   `tests/`:  Conjunto de pruebas unitarias.

*   **`frontend/src/`:** Contiene el código del frontend de la aplicación, desarrollado con React. Se subdivide en:
    *   `App.js`: Componente principal de la aplicación.
    *   `Header.js`: Componente de encabezado de la aplicación.
    *   `LibraryView.js`: Vista de la biblioteca de libros.
    *   `UploadView.js`: Vista para subir libros.
    *   `CategoriesView.js`: Vista para mostrar y filtrar por categorías.
    *   `ToolsView.js`: Vista con herramientas (convertidor EPUB a PDF).
    *   `ReaderView.js`: Vista para leer libros EPUB.
    *   `RagView.js`: Vista para interactuar con el sistema RAG.
    *   `config.js`:  Configuración del frontend (URL de la API).
    *   `index.js`:  Archivo de entrada de la aplicación React.

## 3. Análisis Detallado del Backend (Python/FastAPI)

### `backend/schemas.py`

Propósito: Define los esquemas de datos Pydantic para la serialización y validación de datos.

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

Propósito: Contiene la lógica de acceso a datos (CRUD) para la base de datos.

```python
# Test comment to trigger workflow
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import models
import os

# ... (resto de las funciones)
```

Cada función realiza una operación CRUD (Create, Read, Update, Delete) sobre la tabla `books`.  Las funciones `get_book_by_path`, `get_book_by_title`, `get_books_by_partial_title`, y `get_books` leen datos de la base de datos con diferentes criterios de filtro.  `create_book` crea un nuevo libro, `delete_book` elimina un libro por su ID, `delete_books_by_category` elimina todos los libros de una categoría dada, y `get_books_count` devuelve el número total de libros.  Todas las funciones de eliminación manejan también la eliminación de los archivos asociados a los libros.


### `backend/database.py`

Propósito: Configura la conexión a la base de datos SQLite.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ... (resto del código)
```

### `backend/utils.py`

Propósito: Contiene funciones utilitarias, en este caso, la configuración de la API Key de Google Gemini.


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

Propósito: Define el modelo de datos SQLAlchemy para la tabla `books`.

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
from dotenv import load_dotenv
import chromadb
# ... (resto del código)
```

Las funciones de este archivo se encargan de la indexación y consulta del sistema RAG, usando ChromaDB para el almacenamiento vectorial. Las funciones `get_embedding` y `chunk_text` gestionan la generación de embeddings y la fragmentación del texto respectivamente. `extract_text_from_pdf` y `extract_text_from_epub` son funciones para la extracción del texto de los archivos PDF y EPUB. `process_book_for_rag` es crucial para generar vectores y añadirlos a ChromaDB. `has_index`, `_has_index_for_book`, `delete_book_from_rag` y `get_index_count` son funciones utilitarias para la gestión del índice. Finalmente, `query_rag` realiza la consulta al sistema RAG con diferentes modos de respuesta.


### `backend/main.py`

Propósito: Define la aplicación FastAPI principal.

```python
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
# ... (resto del código)
```

Este archivo contiene la configuración de la aplicación FastAPI, incluyendo la configuración CORS y el manejo de rutas. Contiene los endpoints de la API para: subir libros (`/upload-book/`), obtener libros (`/books/`), obtener el conteo de libros (`/books/count`), buscar libros (`/books/search/`), obtener categorías (`/categories/`), eliminar libros (`/books/{book_id}` y `/categories/{category_name}`), descargar libros (`/books/download/{book_id}`), convertir EPUB a PDF (`/tools/convert-epub-to-pdf`), y las rutas relacionadas con RAG (`/rag/upload-book/`, `/rag/query/`, `/rag/index/{book_id}`, `/rag/status/{book_id}`, `/rag/reindex/category/{category_name}`, `/rag/reindex/all`, `/rag/estimate/book/{book_id}`, `/rag/estimate/category/{category_name}`, `/rag/estimate/all`).


## 4. Análisis Detallado del Frontend (React)

### `frontend/src/Header.js`

Propósito: Componente de encabezado de la aplicación. Muestra el título, el número de libros y un menú de navegación.

Estado: `menuOpen`, `bookCount`, `errorMessage`.
Propiedades: Ninguna.
Efectos secundarios: Se utiliza `useEffect` para obtener el número de libros desde el backend y actualizarlo periódicamente.

Interacción con el backend: Realiza una petición `fetch` a `/books/count` para obtener el número de libros.


### `frontend/src/App.js`

Propósito: Componente principal de la aplicación, configura las rutas de navegación.


Estado: Ninguno.
Propiedades: Ninguna.
Efectos secundarios: Ninguno.

Interacción con el backend: Ninguna directa, la interacción se realiza a través de los componentes hijo.


### `frontend/src/ToolsView.js`

Propósito:  Contiene el convertidor EPUB a PDF.

Estado: `selectedFile`, `message`, `isLoading`.
Propiedades: Ninguna.
Efectos secundarios: Ninguno.

Interacción con el backend:  Envía una petición `fetch` POST a `/tools/convert-epub-to-pdf` para convertir el archivo.  Maneja la respuesta JSON para iniciar la descarga.


### `frontend/src/UploadView.js`

Propósito:  Vista para subir nuevos libros a la base de datos.

Estado: `filesToUpload`, `isUploading`.
Propiedades: Ninguna.
Efectos secundarios: Ninguno.

Interacción con el backend: Envía una petición `fetch` POST a `/upload-book/` por cada archivo para subir los libros al backend. Actualiza el estado para mostrar el progreso de la subida y los mensajes de éxito o error.


### `frontend/src/ReaderView.js`

Propósito:  Vista para leer libros EPUB.

Estado: `location`, `epubData`, `isLoading`, `error`.
Propiedades: `bookId` (vía `useParams`).
Efectos secundarios: Se usa `useEffect` para obtener el libro (`/books/download/{bookId}`) del backend en formato `ArrayBuffer`.

Interacción con el backend: Realiza una petición `fetch` a `/books/download/{bookId}` para descargar el archivo EPUB.


### `frontend/src/RagView.js`

Propósito: Vista para la interacción con el sistema RAG.

Estado: `message`, `isLoading`, `bookId`, `chatHistory`, `currentQuery`, `libraryBooks`, `selectedLibraryId`, `libStatus`, `actionsBusy`, `refreshing`, `searchTerm`, `searching`, `searchResults`, `resultsOpen`, `mode`, `selectedBook`.
Propiedades: Ninguna.
Efectos secundarios: Se usan varios `useEffect` para: cargar la lista de libros, manejar la búsqueda de libros, y para mantener el enfoque en el input del chat.


Interacción con el backend: Envía peticiones `fetch` POST a `/rag/query/` para enviar las consultas, y a `/rag/index/{book_id}` y `/rag/status/{book_id}` para gestionar el índice RAG.


### `frontend/src/LibraryView.js`

Propósito: Vista para mostrar la biblioteca de libros.

Estado: `books`, `searchTerm`, `error`, `loading`, `isMobile`.
Propiedades: Ninguna.
Efectos secundarios: Utiliza `useEffect` y `useCallback` para gestionar la carga de la lista de libros en función de los parámetros de búsqueda (`category`, `author`).  Utiliza `useDebounce` para retrasar la búsqueda.

Interacción con el backend: Realiza una petición `fetch` a `/books/` para obtener la lista de libros, y una petición `fetch` DELETE a `/books/{bookId}` para eliminar un libro.


### `frontend/src/CategoriesView.js`

Propósito: Vista para mostrar todas las categorías disponibles.

Estado: `categories`, `error`, `loading`.
Propiedades: Ninguna.
Efectos secundarios: Utiliza `useEffect` para obtener las categorías desde el backend.

Interacción con el backend: Realiza una petición `fetch` a `/categories/` para obtener la lista de categorías.


### `frontend/src/config.js`

Propósito: Define la URL base de la API.


## 5. Flujo de Datos y API

El flujo de datos comienza cuando un usuario sube un libro (PDF o EPUB) a través de `UploadView.js`.  El frontend envía el archivo al backend a través de una petición POST a `/upload-book/`. El backend procesa el archivo (extrayendo texto y una imagen de portada si es posible), utiliza Gemini para inferir el título, autor y categoría, y guarda la información en la base de datos.  Luego, el frontend recibe una respuesta JSON que confirma la subida y actualiza la interfaz de usuario.

La vista `LibraryView.js` permite ver, buscar y eliminar libros.  Las peticiones a `/books/`, `/books/search/`, y `/books/{bookId}` (DELETE) gestionan la visualización y modificación de la colección. `/categories/` proporciona la lista de categorías para filtrado.  `/books/download/{bookId}` sirve para descargar un libro específico.

El componente `RagView.js` interactua con el sistema RAG. El usuario selecciona un libro o lo carga, y una vez indexado en RAG, realiza consultas POST a `/rag/query/` para obtener respuestas. Las funciones RAG en el backend (en `rag.py`) se encargan de la indexación (almacenamiento de embeddings vectoriales en ChromaDB) y la búsqueda de información relevante en la base de datos vectorial para responder a las preguntas.  `/rag/index/{book_id}` y `/rag/status/{book_id}` gestionan el estado del índice. `/tools/convert-epub-to-pdf` gestiona la conversión de EPUB a PDF, devolviendo una URL para descargar el PDF generado.

**Resumen de los Endpoints de la API:**

*   `/upload-book/`: POST - Sube un libro.
*   `/books/`: GET - Obtiene una lista de libros (filtrado opcional por categoría, búsqueda o autor).
*   `/books/count`: GET - Obtiene el número total de libros.
*   `/books/search/`: GET - Busca libros por título parcial.
*   `/categories/`: GET - Obtiene una lista de categorías.
*   `/books/{book_id}`: DELETE - Elimina un libro.
*   `/categories/{category_name}`: DELETE - Elimina una categoría y sus libros.
*   `/books/download/{book_id}`: GET - Descarga un libro.
*   `/tools/convert-epub-to-pdf`: POST - Convierte un EPUB a PDF.
*   `/rag/upload-book/`: POST - Sube un libro para indexarlo en RAG.
*   `/rag/query/`: POST - Realiza una consulta al sistema RAG.
*   `/rag/index/{book_id}`: POST - Indexa un libro en RAG.
*   `/rag/status/{book_id}`: GET - Obtiene el estado del índice RAG para un libro.
*   `/rag/reindex/category/{category_name}`: POST - Reindexa todos los libros de una categoría en RAG.
*   `/rag/reindex/all`: POST - Reindexa todos los libros en RAG.
*   `/rag/estimate/book/{book_id}`: GET - Estima tokens/chunks y coste opcional para un libro.
*   `/rag/estimate/category/{category_name}`: GET - Estima tokens/chunks y coste opcional para una categoría.
*   `/rag/estimate/all`: GET - Estima tokens/chunks y coste opcional para todos los libros.


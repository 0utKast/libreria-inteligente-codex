# Documentación del Proyecto: Mi Librería Inteligente

"Mi Librería Inteligente" es una aplicación web moderna diseñada para gestionar, explorar y interactuar con tu colección de libros digitales. Combina una interfaz de usuario intuitiva con potentes capacidades de inteligencia artificial para organizar automáticamente los libros y permitir a los usuarios conversar con su contenido.

## 1. Descripción General del Proyecto

Mi Librería Inteligente permite a los usuarios subir libros en formato PDF y EPUB, extrayendo automáticamente metadatos como título, autor y categoría mediante el uso de modelos de lenguaje grandes (LLMs) de Google Gemini. La aplicación ofrece una biblioteca con funciones de búsqueda, filtrado y paginación. Además, incluye herramientas para la conversión de EPUB a PDF y una funcionalidad avanzada de Recuperación Aumentada por Generación (RAG) que permite a los usuarios hacer preguntas directamente sobre el contenido de los libros y recibir respuestas contextualizadas generadas por IA.

### Arquitectura General

La aplicación sigue una arquitectura cliente-servidor, dividida en dos componentes principales:

*   **Frontend (React):** Desarrollado con React, proporciona la interfaz de usuario. Permite a los usuarios interactuar con la biblioteca, subir libros, ver categorías, leer EPUBs directamente en el navegador, usar herramientas de conversión y chatear con los libros a través de la interfaz RAG.
*   **Backend (FastAPI):** Construido con Python y el framework FastAPI, actúa como la API RESTful para el frontend. Gestiona la lógica de negocio, la interacción con la base de datos, el procesamiento de archivos, la integración con los servicios de IA de Google Gemini y la persistencia del índice RAG con ChromaDB.
*   **Base de Datos (SQLite):** Utiliza SQLAlchemy como ORM para interactuar con una base de datos SQLite (`library.db`), que almacena los metadatos de los libros.
*   **Inteligencia Artificial (Google Gemini):** Se utiliza para la extracción automática de metadatos de los libros y para la generación de respuestas en el sistema RAG.
*   **Almacenamiento de Archivos:** Los archivos de libros (PDFs y EPUBs) y las portadas generadas se almacenan directamente en el sistema de archivos del servidor.
*   **Vector Database (ChromaDB):** Utilizado para almacenar y gestionar los embeddings (representaciones vectoriales) de los fragmentos de texto de los libros, permitiendo la búsqueda semántica eficiente para el sistema RAG.

## 2. Estructura del Proyecto

El proyecto está organizado en dos directorios principales, `backend` y `frontend`, junto con otras carpetas para persistencia de datos y archivos estáticos.

```
.
├── backend/                  # Código del servidor (FastAPI, Python)
│   ├── alembic/              # Migraciones de base de datos (SQLAlchemy Alembic)
│   │   └── versions/         # Scripts de migración
│   ├── tests/                # Pruebas unitarias y de integración del backend
│   ├── tests_curated/        # Pruebas curadas (preexistentes) del backend
│   ├── __init__.py           # Archivo de inicialización de paquete Python
│   ├── crud.py               # Operaciones CRUD para la base de datos
│   ├── database.py           # Configuración de la base de datos
│   ├── main.py               # Aplicación principal FastAPI, endpoints de la API
│   ├── models.py             # Modelos de SQLAlchemy ORM
│   ├── rag.py                # Lógica para Retrieval Augmented Generation (RAG)
│   ├── schemas.py            # Modelos Pydantic para validación de datos
│   └── utils.py              # Funciones de utilidad diversas
├── frontend/                 # Código del cliente (React)
│   ├── public/               # Archivos públicos para el frontend
│   └── src/                  # Código fuente de los componentes React
│       ├── App.css           # Estilos globales de la aplicación
│       ├── App.js            # Componente principal de React
│       ├── CategoriesView.css
│       ├── CategoriesView.js # Vista de categorías
│       ├── config.js         # Configuración de la URL de la API
│       ├── EditBookModal.css
│       ├── EditBookModal.js  # Modal para editar detalles del libro
│       ├── ErrorBoundary.js  # Componente para manejo de errores de UI
│       ├── Header.css
│       ├── Header.js         # Componente de encabezado y navegación
│       ├── index.css
│       ├── index.js          # Punto de entrada de la aplicación React
│       ├── LibraryView.css
│       ├── LibraryView.js    # Vista principal de la biblioteca
│       ├── RagView.css
│       ├── RagView.js        # Vista para interacción RAG
│       ├── ReaderView.css
│       ├── ReaderView.js     # Vista para leer libros EPUB
│       ├── reportWebVitals.js
│       ├── ToolsView.css
│       ├── ToolsView.js      # Vista de herramientas (ej. conversor EPUB a PDF)
│       └── UploadView.css
│       └── UploadView.js     # Vista para subir libros
├── .env                      # Variables de entorno (API Keys, etc.)
├── library.db                # Base de datos SQLite (generada)
├── books/                    # Directorio para almacenar los archivos de los libros
├── static/                   # Archivos estáticos
│   └── covers/               # Directorio para almacenar las portadas de los libros
├── temp_books/               # Directorio para archivos temporales (ej. PDFs convertidos para descarga)
├── rag_index/                # Directorio para la persistencia de ChromaDB
├── README.md                 # Archivo README del proyecto
└── requirements.txt          # Dependencias de Python
```

## 3. Análisis Detallado del Backend (Python/FastAPI)

El backend de la aplicación está construido con FastAPI y Python, y gestiona toda la lógica del servidor, la interacción con la base de datos y los servicios de IA.

### `backend/main.py`

*   **Propósito:** Este es el corazón de la API FastAPI. Define todos los endpoints HTTP, orquesta las llamadas a otras capas (CRUD, utilidades, RAG, modelos de IA) y maneja el procesamiento de archivos subidos.

*   **Clases/Funciones Principales:**
    *   `save_optimized_image(pix_or_bytes, target_path, is_pixmap)`:
        *   **Lógica:** Guarda una imagen optimizada (redimensionada y comprimida) en un `target_path`. Puede recibir un `fitz.Pixmap` (de PDF) o bytes de imagen (de EPUB). Redimensiona a un ancho máximo de 400px y guarda como JPEG con calidad 80.
        *   **Parámetros:**
            *   `pix_or_bytes`: Objeto `fitz.Pixmap` o `bytes` de la imagen.
            *   `target_path`: Ruta completa donde guardar la imagen.
            *   `is_pixmap`: Booleano, `True` si `pix_or_bytes` es un `Pixmap`.
        *   **Retorna:** `None`.
    *   `get_safe_path(db_path)`:
        *   **Lógica:** Convierte una ruta de archivo almacenada en la base de datos (que puede ser relativa o absoluta) a una ruta absoluta segura en el sistema de archivos.
        *   **Parámetros:** `db_path` (str): Ruta del archivo como está en la BD.
        *   **Retorna:** `str`: Ruta absoluta.
    *   `get_relative_path(abs_path)`:
        *   **Lógica:** Convierte una ruta absoluta del sistema de archivos a una ruta relativa al directorio `backend`.
        *   **Parámetros:** `abs_path` (str): Ruta absoluta del archivo.
        *   **Retorna:** `str`: Ruta relativa.
    *   `analyze_with_gemini(text)`:
        *   **Lógica:** Envía un fragmento de texto a un modelo Gemini (configurable, por defecto `gemini-2.5-flash`) para extraer el título, autor y categoría del libro. Devuelve un diccionario JSON. Incluye lógica de depuración y manejo de errores.
        *   **Parámetros:** `text` (str): Texto a analizar.
        *   **Retorna:** `dict`: Diccionario con `title`, `author`, `category` o mensajes de error.
    *   `process_pdf(file_path, covers_dir_fs, covers_url_prefix)`:
        *   **Lógica:** Extrae texto de las primeras páginas de un PDF usando `fitz` y busca una imagen de portada dentro del PDF. Guarda la portada optimizada.
        *   **Parámetros:**
            *   `file_path` (str): Ruta del archivo PDF.
            *   `covers_dir_fs` (str): Directorio del sistema de archivos para guardar portadas.
            *   `covers_url_prefix` (str): Prefijo URL para las portadas.
        *   **Retorna:** `dict`: Diccionario con el texto extraído y la URL de la imagen de portada.
    *   `process_epub(file_path, covers_dir_fs, covers_url_prefix)`:
        *   **Lógica:** Extrae texto de un EPUB usando `ebooklib` y `BeautifulSoup`. Busca imágenes de portada siguiendo varias estrategias (metadatos, nombre de archivo). Guarda la portada optimizada.
        *   **Parámetros:**
            *   `file_path` (str): Ruta del archivo EPUB.
            *   `covers_dir_fs` (str): Directorio del sistema de archivos para guardar portadas.
            *   `covers_url_prefix` (str): Prefijo URL para las portadas.
        *   **Retorna:** `dict`: Diccionario con el texto extraído y la URL de la imagen de portada.
    *   `get_db()`:
        *   **Lógica:** Función de dependencia de FastAPI que proporciona una sesión de base de datos SQLAlchemy para cada solicitud.
        *   **Retorna:** `Session`: Sesión de base de datos.
    *   **Endpoints de la API:**
        *   `POST /api/books/{book_id}/convert`: Convierte un EPUB existente en la librería a PDF, lo añade como un nuevo libro y devuelve los metadatos del nuevo PDF.
        *   `POST /tools/convert-epub-to-pdf`: Convierte un EPUB subido a PDF y devuelve una URL temporal para su descarga.
        *   `POST /upload-book/`: Sube un archivo de libro (PDF/EPUB), lo procesa (texto, portada, IA para metadatos) y lo añade a la base de datos.
        *   `GET /books/`: Obtiene una lista paginada de libros, con opciones de filtrado por categoría, búsqueda general o autor.
        *   `PUT /books/{book_id}`: Actualiza los detalles de un libro existente (título, autor, portada).
        *   `GET /books/count`: Retorna el número total de libros en la biblioteca.
        *   `GET /books/search/`: Busca libros por título parcial.
        *   `GET /categories/`: Retorna una lista de todas las categorías de libros únicas.
        *   `DELETE /books/{book_id}`: Elimina un libro por su ID, incluyendo sus archivos asociados y, si existe, su índice RAG.
        *   `DELETE /categories/{category_name}`: Elimina todos los libros de una categoría y sus índices RAG.
        *   `GET /books/download/{book_id}`: Permite la descarga o visualización en línea de un archivo de libro.
        *   `POST /rag/upload-book/` (Deprecated/Unused): Subía un libro temporal para RAG. La nueva UI usa `/rag/index/{book_id}`.
        *   `POST /rag/query/`: Envía una consulta a la IA RAG sobre un libro específico, con modos de respuesta (strict, balanced, open).
        *   `POST /rag/index/{book_id}`: Indexa un libro existente en la base de datos para RAG. Puede forzar la reindexación.
        *   `GET /rag/status/{book_id}`: Retorna el estado de indexación RAG para un libro.
        *   `POST /rag/reindex/category/{category_name}`: Reindexa todos los libros de una categoría.
        *   `POST /rag/reindex/all`: Reindexa todos los libros de la biblioteca.
        *   `GET /rag/estimate/book/{book_id}`: Estima el costo y el número de chunks para indexar un libro.
        *   `GET /rag/estimate/category/{category_name}`: Estima el costo para una categoría.
        *   `GET /rag/estimate/all`: Estima el costo para toda la biblioteca.

### `backend/crud.py`

*   **Propósito:** Proporciona funciones de operaciones CRUD (Crear, Leer, Actualizar, Borrar) para el modelo `Book` en la base de datos, interactuando con SQLAlchemy. También maneja la eliminación de archivos físicos asociados a los libros.

*   **Funciones Principales:**
    *   `get_abs_path(db_path)`: Convierte una ruta relativa almacenada en BD a una absoluta en el sistema de archivos.
    *   `get_book(db, book_id)`: Obtiene un libro por su ID.
    *   `get_book_by_path(db, file_path)`: Obtiene un libro por su ruta de archivo.
    *   `get_book_by_title(db, title)`: Obtiene un libro por su título exacto.
    *   `get_books_by_partial_title(db, title, skip, limit)`: Busca libros por título parcial.
    *   `get_books(db, category, search, author, skip, limit)`: Obtiene una lista paginada y filtrada de libros.
    *   `get_categories(db)`: Obtiene una lista de todas las categorías únicas.
    *   `create_book(db, title, author, category, cover_image_url, file_path)`: Crea un nuevo registro de libro.
    *   `delete_book(db, book_id)`: Elimina un libro y sus archivos asociados (libro y portada).
    *   `delete_books_by_category(db, category)`: Elimina todos los libros de una categoría y sus archivos asociados.
    *   `get_books_count(db)`: Obtiene el recuento total de libros.
    *   `update_book(db, book_id, title, author, cover_image_url)`: Actualiza los metadatos de un libro.

### `backend/models.py`

*   **Propósito:** Define el esquema de la tabla `books` en la base de datos utilizando el ORM SQLAlchemy.

*   **Clases Principales:**
    *   `Book(Base)`:
        *   **Tabla:** `"books"`
        *   **Columnas:**
            *   `id`: `Integer`, clave primaria, índice.
            *   `title`: `String`, índice.
            *   `author`: `String`, índice.
            *   `category`: `String`, índice.
            *   `cover_image_url`: `String`, URL de la portada, puede ser nulo.
            *   `file_path`: `String`, ruta al archivo del libro, única.
        *   `__table_args__ = {'extend_existing': True}`: Permite que la tabla se redefina si ya existe, útil para algunos entornos de desarrollo o tests.

### `backend/database.py`

*   **Propósito:** Configura la conexión a la base de datos y proporciona las herramientas para interactuar con ella utilizando SQLAlchemy.

*   **Variables/Funciones Principales:**
    *   `_base_dir`, `_db_path`: Definición de la ruta absoluta para el archivo `library.db` (en la raíz del proyecto).
    *   `SQLALCHEMY_DATABASE_URL`: URL de conexión a la base de datos SQLite.
    *   `engine`: Objeto de motor SQLAlchemy para la conexión. `connect_args={"check_same_thread": False}` es necesario para SQLite con FastAPI en modo de un solo hilo.
    *   `SessionLocal`: Constructor de sesiones de base de datos.
    *   `Base`: La clase base declarativa de SQLAlchemy a partir de la cual se heredan los modelos ORM.

### `backend/utils.py`

*   **Propósito:** Contiene funciones de utilidad generales que no encajan directamente en CRUD, modelos o RAG, incluyendo la configuración de la IA, manipulación de archivos y la compleja conversión de EPUB a PDF.

*   **Funciones Principales:**
    *   `configure_genai()`: Carga la clave API de Google Gemini desde las variables de entorno (`.env`) y configura el SDK de `google.generativeai`.
    *   `get_gemini_model(model_name)`: Obtiene una instancia del modelo Gemini especificado.
    *   `generate_text_from_prompt(prompt, model_name)`: Genera texto utilizando un prompt y el modelo Gemini.
    *   `get_file_extension(filename)`: Extrae la extensión de un nombre de archivo.
    *   `is_allowed_file(filename, allowed_extensions)`: Comprueba si un archivo tiene una extensión permitida.
    *   `convert_epub_bytes_to_pdf_bytes(epub_content)`:
        *   **Lógica:** Esta es una función compleja que realiza la conversión de EPUB (en bytes) a PDF (en bytes). Implica:
            1.  Descomprimir el EPUB a un directorio temporal.
            2.  Localizar el archivo `.opf` (manifiesto del EPUB).
            3.  Analizar el `.opf` con `BeautifulSoup` para encontrar la estructura del libro (capítulos, CSS, portada).
            4.  Construir un conjunto de documentos HTML y CSS (usando `weasyprint.HTML` y `weasyprint.CSS`).
            5.  Renderizar y unir estos documentos en un único archivo PDF en memoria.
        *   **Parámetros:** `epub_content` (bytes): Contenido binario del archivo EPUB.
        *   **Retorna:** `bytes`: Contenido binario del PDF resultante.

### `backend/schemas.py`

*   **Propósito:** Define los modelos de datos de Pydantic utilizados para la validación de entrada y la serialización/deserialización de salida en los endpoints de la API.

*   **Modelos Principales:**
    *   `BookBase`: Esquema base para un libro (título, autor, categoría, URL de portada, ruta de archivo).
    *   `Book(BookBase)`: Extiende `BookBase` añadiendo el `id` del libro. `Config.from_attributes = True` permite mapeo de atributos de modelos ORM.
    *   `ConversionResponse`: Respuesta para la conversión de EPUB a PDF, contiene una `download_url`.
    *   `RagUploadResponse`: Respuesta para la carga de libros para RAG (aunque este endpoint ya no se usa directamente para la subida inicial de libros).
    *   `RagQuery`: Esquema para las consultas RAG (query, book_id, mode).
    *   `RagQueryResponse`: Respuesta de una consulta RAG (el texto de la respuesta).

### `backend/rag.py`

*   **Propósito:** Implementa la lógica de Retrieval Augmented Generation (RAG), permitiendo la interacción conversacional con el contenido de los libros. Utiliza embeddings de Gemini y ChromaDB para la recuperación de información.

*   **Funciones Principales:**
    *   `_ensure_init()`: Inicializa el cliente de ChromaDB (persistente en `./rag_index`) y configura el SDK de Gemini si la IA está habilitada.
    *   `get_embedding(text, task_type)`: Genera embeddings de texto utilizando el modelo de embedding de Gemini (`models/text-embedding-004` por defecto). Incluye un mock para cuando la IA está deshabilitada.
    *   `extract_text_from_pdf(file_path)`: Extrae texto de un archivo PDF usando `PyPDF2`.
    *   `extract_text_from_epub(file_path)`: Extrae texto de un archivo EPUB usando `ebooklib` y `BeautifulSoup`.
    *   `extract_text(file_path)`: Unifica la extracción de texto para PDF y EPUB.
    *   `chunk_text(text, max_tokens)`: Divide un texto largo en fragmentos más pequeños, optimizando el tamaño según un número máximo de tokens (utiliza `tiktoken` para estimación).
    *   `_has_index_for_book(book_id)`: Comprueba si un libro ya tiene vectores indexados en ChromaDB.
    *   `delete_book_from_rag(book_id)`: Elimina todos los vectores de un libro de ChromaDB.
    *   `get_index_count(book_id)`: Retorna el número de vectores almacenados para un libro.
    *   `has_index(book_id)`: Función pública para verificar la existencia del índice RAG.
    *   `process_book_for_rag(file_path, book_id, force_reindex)`:
        *   **Lógica:** Función central para indexar un libro en RAG. Extrae el texto, lo divide en chunks, genera embeddings para cada chunk y los almacena en ChromaDB junto con metadatos. Permite la reindexación forzada.
        *   **Parámetros:**
            *   `file_path` (str): Ruta del archivo del libro.
            *   `book_id` (str): ID del libro (normalmente el ID de la BD).
            *   `force_reindex` (bool): Si es `True`, borra el índice existente antes de volver a indexar.
    *   `estimate_embeddings_for_file(file_path, max_tokens)`: Estima la cantidad de tokens y chunks que un archivo generaría para la indexación.
    *   `estimate_embeddings_for_files(file_paths, max_tokens)`: Realiza la estimación para múltiples archivos.
    *   `query_rag(query, book_id, mode, metadata, library)`:
        *   **Lógica:** Procesa una consulta RAG. Genera un embedding para la consulta, busca los chunks más relevantes en ChromaDB para el `book_id` dado, construye un prompt enriquecido con el contexto recuperado y metadatos del libro/biblioteca, y luego envía este prompt al modelo de generación de Gemini para obtener la respuesta.
        *   **Parámetros:**
            *   `query` (str): La pregunta del usuario.
            *   `book_id` (str): ID del libro sobre el que se pregunta.
            *   `mode` (str): Estrategia de respuesta de la IA (`strict`, `balanced`, `open`).
            *   `metadata` (dict, opcional): Metadatos adicionales del libro (título, autor, categoría).
            *   `library` (dict, opcional): Contexto de la biblioteca (ej. otras obras del autor).
        *   **Retorna:** `str`: La respuesta generada por la IA.

### `backend/alembic/versions/1a2b3c4d5e6f_create_books_table.py`

*   **Propósito:** Este es un script de migración de la base de datos generado por Alembic. Define los pasos para crear la tabla `books` y sus índices.

*   **Funciones Principales:**
    *   `upgrade()`: Crea la tabla `books` con las columnas e índices definidos en `models.py`. Establece `id` como clave primaria y `file_path` como único.
    *   `downgrade()`: Elimina la tabla `books` y sus índices.

### `backend/tests/` y `backend/tests_curated/`

*   **Propósito:** Estos directorios contienen las pruebas unitarias y de integración para el backend. Aseguran que las funciones y endpoints de la API funcionan como se espera, cubriendo casos de éxito, error y comportamiento de los mocks. Los tests `_curated` son un conjunto inicial o de referencia, mientras que los tests en `backend/tests` son adiciones o expansiones.

## 4. Análisis Detallado del Frontend (React)

El frontend está desarrollado con React y ofrece una interfaz de usuario interactiva y dinámica.

### `frontend/src/App.js`

*   **Propósito:** El componente raíz de la aplicación React. Configura el enrutamiento de la aplicación (`BrowserRouter` y `Routes`) y renderiza la estructura básica de la página (encabezado y contenido principal).

*   **Estado/Propiedades:** No mantiene estado directamente.
*   **Efectos:** Renderiza la `Header` y, según la ruta, el componente de vista correspondiente (`LibraryView`, `UploadView`, etc.).
*   **Interacciones:** Maneja la navegación de alto nivel entre las diferentes secciones de la aplicación.

### `frontend/src/Header.js`

*   **Propósito:** Componente de encabezado que incluye el título de la aplicación, el recuento total de libros y la barra de navegación.

*   **Estado:**
    *   `menuOpen` (boolean): Controla la visibilidad del menú de navegación en pantallas pequeñas.
    *   `bookCount` (number): El número total de libros en la biblioteca.
    *   `errorMessage` (string | null): Mensaje de error si falla la carga del recuento de libros.
*   **Propiedades:** Ninguna.
*   **Efectos:**
    *   `useEffect`: Realiza una solicitud al endpoint `/books/count` del backend al montar el componente para obtener el número total de libros. También configura un intervalo para refrescar el recuento cada 10 minutos.
*   **Interacciones:**
    *   Botón "hamburguesa" para alternar `menuOpen`.
    *   Los `NavLink`s permiten la navegación a diferentes vistas y cierran el menú al hacer clic.

### `frontend/src/LibraryView.js`

*   **Propósito:** La vista principal que muestra la colección de libros en la biblioteca, con funcionalidades de búsqueda, filtrado por autor/categoría, paginación con "infinite scroll" y opciones de acción sobre cada libro.

*   **Estado:**
    *   `books` (array): Lista de objetos de libros mostrados.
    *   `page` (number): Número de página actual para la carga de libros.
    *   `hasMore` (boolean): Indica si hay más libros para cargar.
    *   `searchTerm` (string): Término de búsqueda introducido por el usuario.
    *   `debouncedSearchTerm` (string): Versión "debounced" de `searchTerm` para evitar llamadas excesivas a la API.
    *   `error` (string): Mensaje de error de carga de libros.
    *   `loading` (boolean): Indica si los libros se están cargando actualmente.
    *   `isMobile` (boolean): Indica si la vista actual es móvil.
    *   `editingBook` (object | null): El libro que se está editando en el modal.
    *   `convertingId` (number | null): El ID del libro que se está convirtiendo a PDF.
*   **Propiedades:** Ninguna.
*   **Efectos:**
    *   `useEffect` (redimensionamiento): Detecta el tamaño de la ventana para establecer `isMobile`.
    *   `useEffect` (reset de búsqueda/filtros): Reinicia el estado de `books`, `page` y `hasMore` cuando cambian los parámetros de búsqueda o filtros.
    *   `useEffect` (carga de libros): Se activa cuando `page`, `debouncedSearchTerm` o `searchParams` cambian para fetchear libros del backend (`GET /books/`). Implementa la lógica de paginación y carga infinita.
*   **Interacciones:**
    *   `handleAuthorClick`, `handleCategoryClick`: Actualizan los parámetros de la URL para filtrar libros.
    *   `handleDeleteBook`: Llama a la API `DELETE /books/{book_id}`.
    *   `handleConvertToPdf`: Llama a la API `POST /api/books/{book_id}/convert` para convertir EPUB a PDF.
    *   `handleEditClick`: Abre el `EditBookModal` para el libro seleccionado.
    *   `BookCover` (componente interno): Muestra la portada del libro o un fallback genérico.
    *   `BookCard` (componente interno): Renderiza los detalles de un libro y sus acciones (abrir/descargar, convertir, editar, eliminar).
    *   `useDebounce` (hook): Utilidad para retrasar la ejecución de la búsqueda.
    *   `lastBookElementRef` (callback para `IntersectionObserver`): Implementa la lógica de "infinite scroll".
    *   `convertibilityMap` (memoizado): Determina si un libro EPUB puede ser convertido a PDF sin crear un duplicado basado en `file_path`.

### `frontend/src/EditBookModal.js`

*   **Propósito:** Un modal para que el usuario pueda editar el título, autor y la imagen de portada de un libro.

*   **Estado:**
    *   `title` (string): Título del libro, editable.
    *   `author` (string): Autor del libro, editable.
    *   `coverImage` (File | null): Archivo de imagen para la nueva portada.
    *   `isSaving` (boolean): Indica si la operación de guardado está en curso.
*   **Propiedades:**
    *   `book` (object): El objeto del libro a editar.
    *   `onClose` (function): Función para cerrar el modal.
    *   `onBookUpdated` (function): Callback que se ejecuta con el libro actualizado tras un guardado exitoso.
*   **Efectos:**
    *   `useEffect`: Inicializa los estados `title` y `author` con los valores del libro pasado por `props`.
*   **Interacciones:**
    *   `handleSubmit`: Envía los datos actualizados al backend (`PUT /books/{book_id}`) como `FormData`.
    *   `handleFileChange`: Captura el archivo de la nueva portada.
    *   Botones para "Cancelar" y "Guardar Cambios".

### `frontend/src/UploadView.js`

*   **Propósito:** Proporciona una interfaz para que los usuarios suban uno o varios archivos de libros (PDF o EPUB) a la biblioteca.

*   **Estado:**
    *   `filesToUpload` (array): Lista de objetos que representan los archivos seleccionados, cada uno con su `file`, `status` y `message`.
    *   `isUploading` (boolean): Indica si hay archivos subiéndose actualmente.
*   **Propiedades:** Ninguna.
*   **Efectos:** Ninguno.
*   **Interacciones:**
    *   `handleFileChange`: Agrega archivos seleccionados a la lista `filesToUpload`.
    *   `handleDrop`, `handleDragOver`: Implementan la funcionalidad de arrastrar y soltar archivos.
    *   `handleUpload`: Itera sobre `filesToUpload` y envía cada archivo al endpoint `POST /upload-book/` del backend. Actualiza el estado (`status` y `message`) de cada archivo.
    *   `handleReset`: Limpia la lista de archivos y el input del formulario.
    *   Después de la carga, ofrece opciones para "Ir a la Biblioteca" o "Añadir más libros".

### `frontend/src/CategoriesView.js`

*   **Propósito:** Muestra todas las categorías de libros disponibles en la biblioteca como enlaces cliqueables.

*   **Estado:**
    *   `categories` (array): Lista de cadenas de texto con los nombres de las categorías.
    *   `error` (string): Mensaje de error si falla la carga de categorías.
    *   `loading` (boolean): Indica si las categorías se están cargando.
*   **Propiedades:** Ninguna.
*   **Efectos:**
    *   `useEffect`: Realiza una solicitud al endpoint `GET /categories/` del backend al montar el componente para obtener la lista de categorías.
*   **Interacciones:**
    *   Cada categoría se muestra como un `Link` que lleva al `LibraryView`, filtrando los libros por la categoría seleccionada.

### `frontend/src/ToolsView.js`

*   **Propósito:** Ofrece herramientas adicionales para la gestión de libros. Actualmente, solo incluye un convertidor de EPUB a PDF.

*   **Componentes Principales:**
    *   `EpubToPdfConverter`:
        *   **Estado:** `selectedFile`, `message`, `isLoading`.
        *   **Propiedades:** Ninguna.
        *   **Efectos:** Ninguno.
        *   **Interacciones:**
            *   `handleFileChange`: Captura el archivo EPUB seleccionado.
            *   `handleDrop`, `handleDragOver`: Soporte para arrastrar y soltar archivos.
            *   `handleConvert`: Envía el archivo EPUB al endpoint `POST /tools/convert-epub-to-pdf` del backend. Si la conversión es exitosa, se activa una descarga automática del PDF resultante.

### `frontend/src/ReaderView.js`

*   **Propósito:** Componente para la lectura de libros en formato EPUB directamente en el navegador.

*   **Estado:**
    *   `location` (string | null): La ubicación actual dentro del EPUB (CFIs de EPUB) para mantener el progreso de lectura.
    *   `epubData` (ArrayBuffer | null): Los datos binarios del archivo EPUB cargado.
    *   `isLoading` (boolean): Indica si el libro se está cargando.
    *   `error` (string): Mensaje de error si el libro no se puede cargar.
*   **Propiedades:**
    *   `bookId` (string): Obtenido de los parámetros de la URL (`useParams`).
*   **Efectos:**
    *   `useEffect`: Realiza una solicitud al endpoint `GET /books/download/{bookId}` del backend al montar el componente para obtener el contenido del EPUB como `ArrayBuffer`.
*   **Interacciones:**
    *   Utiliza la biblioteca `react-reader` para renderizar el contenido EPUB y gestionar la navegación y el progreso de lectura.

### `frontend/src/RagView.js`

*   **Propósito:** Proporciona una interfaz para interactuar con la funcionalidad de Retrieval Augmented Generation (RAG). Los usuarios pueden seleccionar un libro, indexarlo y luego hacerle preguntas, recibiendo respuestas generadas por IA.

*   **Estado:**
    *   `message` (string): Mensajes informativos para el usuario.
    *   `isLoading` (boolean): Indica si se está esperando una respuesta de la IA.
    *   `bookId` (string | null): ID del libro actualmente seleccionado para la conversación RAG.
    *   `chatHistory` (array): Array de objetos `{sender: 'user'|'gemini', text: string}` que representa la conversación.
    *   `currentQuery` (string): El texto de la pregunta actual del usuario.
    *   `libraryBooks` (array): Lista de todos los libros en la biblioteca para seleccionar.
    *   `selectedLibraryId` (string): ID del libro seleccionado en el buscador de la biblioteca.
    *   `libStatus` (object): Contiene el estado de indexación RAG del libro seleccionado (`loading`, `indexed`, `vector_count`, `error`).
    *   `actionsBusy` (boolean): Bloquea acciones pesadas (indexación) durante su ejecución.
    *   `refreshing` (boolean): Indica si se está refrescando el estado RAG.
    *   `searchTerm` (string): Término de búsqueda para encontrar libros en la biblioteca.
    *   `searchResults` (array): Resultados de la búsqueda de libros.
    *   `resultsOpen` (boolean): Controla la visibilidad de los resultados de búsqueda.
    *   `mode` (string): Modo de respuesta de la IA (`'strict'`, `'balanced'`, `'open'`).
    *   `selectedBook` (object | null): El objeto libro completo del libro seleccionado.
*   **Propiedades:** Ninguna.
*   **Efectos:**
    *   `useEffect` (autoscroll): Desplaza el chat al final cuando el historial o el estado de carga cambian.
    *   `useEffect` (carga de libros): Carga la lista completa de libros de la biblioteca al montar.
    *   `useEffect` (búsqueda de libros): Debounces `searchTerm` y busca libros en la API `/books/`.
    *   `useEffect` (estado RAG): Se activa cuando `selectedLibraryId` cambia para llamar a `checkLibraryStatus` y obtener el estado de indexación del libro.
*   **Interacciones:**
    *   **Buscador de libros:** Permite buscar y seleccionar un libro de la biblioteca.
    *   **Botones de acción:** "Comprobar RAG", "Indexar antes de charlar", "Reindexar", "Chatear". Llaman a los endpoints `GET /rag/status/{book_id}` y `POST /rag/index/{book_id}`.
    *   **Selector de modo:** Botones de radio para elegir el modo de respuesta de la IA.
    *   **Formulario de chat:**
        *   `handleQuerySubmit`: Envía la pregunta del usuario al endpoint `POST /rag/query/` del backend.
        *   `textarea`: Entrada de texto para la pregunta del usuario, auto-ajustable.
    *   Muestra el historial de chat con mensajes del usuario y de Gemini.

### `frontend/src/config.js`

*   **Propósito:** Define la URL base del backend de la API, permitiendo una fácil configuración para diferentes entornos (desarrollo, producción).

*   **Variable Principal:**
    *   `API_URL`: Utiliza la variable de entorno `REACT_APP_API_URL` si está definida, de lo contrario, por defecto es `http://localhost:8001`.

### Otros Archivos Frontend

*   `frontend/src/ErrorBoundary.js`: Un componente React `ErrorBoundary` estándar para capturar errores de JavaScript en la interfaz de usuario y mostrarlos, evitando que la aplicación falle completamente.
*   `frontend/src/index.js`: El punto de entrada principal de la aplicación React. Renderiza el componente `App` dentro de `React.StrictMode`.
*   `.css` files: Cada componente de vista tiene un archivo `.css` asociado para sus estilos específicos, manteniendo la modularidad del diseño.

## 5. Flujo de Datos y API

Este apartado describe cómo fluyen los datos a través de la aplicación y resume los principales endpoints de la API.

### Flujos de Datos Clave

1.  **Carga de un Libro:**
    *   **Frontend (`UploadView`):** El usuario selecciona o arrastra archivos PDF/EPUB.
    *   **Backend (`main.py` - `POST /upload-book/`):**
        *   El archivo se guarda en `backend/books/`.
        *   Se llama a `process_pdf` o `process_epub` para extraer texto y portada. La portada se guarda en `backend/static/covers/`.
        *   El texto extraído se envía a `analyze_with_gemini` para obtener título, autor y categoría.
        *   Si la IA identifica metadatos, se llama a `crud.create_book` para guardar los metadatos y las rutas de archivo en la base de datos (`library.db`).
        *   Si falla el análisis o la subida, se elimina el archivo subido del disco.
    *   **Base de Datos (`crud.py`, `models.py`, `database.py`):** Los metadatos del libro se persisten.

2.  **Visualización de la Biblioteca:**
    *   **Frontend (`LibraryView`):** Realiza una solicitud a `GET /books/` con parámetros de paginación, búsqueda o filtrado.
    *   **Backend (`main.py` - `GET /books/`):**
        *   Llama a `crud.get_books` con los filtros y la paginación.
        *   `crud.get_books` consulta la base de datos (`library.db`) para obtener los metadatos de los libros.
    *   **Frontend:** Muestra la lista de libros, incluyendo las portadas (cargadas desde `/static/covers/`) y permite interactuar con ellos.

3.  **Conversión de EPUB a PDF:**
    *   **Frontend (`LibraryView` o `ToolsView`):**
        *   Desde `LibraryView`: El usuario hace clic en "Convertir a PDF" para un EPUB existente (`POST /api/books/{book_id}/convert`).
        *   Desde `ToolsView`: El usuario sube un archivo EPUB para conversión temporal (`POST /tools/convert-epub-to-pdf`).
    *   **Backend (`main.py`):**
        *   Para `POST /api/books/{book_id}/convert`: Recupera el EPUB original del disco, lo convierte a PDF usando `utils.convert_epub_bytes_to_pdf_bytes`. El PDF resultante se guarda en `backend/books/`, se procesa con `process_pdf` y `analyze_with_gemini`, y se añade como un nuevo libro a la base de datos.
        *   Para `POST /tools/convert-epub-to-pdf`: El EPUB subido se convierte a PDF usando `utils.convert_epub_bytes_to_pdf_bytes`. El PDF resultante se guarda temporalmente en `backend/temp_books/` y se devuelve una URL para su descarga directa.
    *   **Frontend:** Muestra un mensaje de éxito/error y, en el caso de `ToolsView`, inicia la descarga del PDF.

4.  **Interacción RAG (Chat con Libros):**
    *   **Frontend (`RagView`):** El usuario selecciona un libro de la biblioteca.
    *   **Backend (`main.py` - `GET /rag/status/{book_id}`):** Se comprueba si el libro ya está indexado.
    *   **Frontend:** Si no está indexado, el usuario hace clic en "Indexar".
    *   **Backend (`main.py` - `POST /rag/index/{book_id}`):**
        *   Recupera el archivo del libro.
        *   Llama a `rag.process_book_for_rag` para:
            *   Extraer texto (`rag.extract_text`).
            *   Dividir en chunks (`rag.chunk_text`).
            *   Generar embeddings para cada chunk (`rag.get_embedding`).
            *   Almacenar embeddings y chunks en ChromaDB (directorio `rag_index/`).
    *   **Frontend (`RagView`):** El usuario introduce una pregunta.
    *   **Backend (`main.py` - `POST /rag/query/`):**
        *   Recupera metadatos del libro de la BD.
        *   Llama a `rag.query_rag` con la pregunta del usuario, el ID del libro y el modo de respuesta.
        *   `rag.query_rag`:
            *   Genera un embedding para la pregunta.
            *   Consulta ChromaDB para recuperar los chunks más relevantes del libro.
            *   Construye un prompt enriquecido con la pregunta, los chunks recuperados, metadatos del libro y contexto de la biblioteca.
            *   Envía el prompt a un modelo de generación de Gemini para obtener la respuesta.
    *   **Frontend:** Muestra la respuesta de la IA en el historial de chat.

### Resumen de Endpoints de la API Backend (FastAPI)

Aquí se listan los principales endpoints definidos en `backend/main.py`:

| Método | Ruta                                    | Descripción                                                                                               | Request Body (ej.)                                        | Response (ej.)                                            |
| :----- | :-------------------------------------- | :-------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------- | :-------------------------------------------------------- |
| `POST` | `/upload-book/`                         | Sube un archivo de libro (PDF/EPUB), lo analiza con IA y lo añade a la biblioteca.                        | `book_file: UploadFile`                                   | `schemas.Book`                                            |
| `GET`  | `/books/`                               | Obtiene una lista paginada de libros, con filtros opcionales (categoría, búsqueda, autor).               | `None`                                                    | `List[schemas.Book]`                                      |
| `PUT`  | `/books/{book_id}`                      | Actualiza los detalles (título, autor, portada) de un libro existente.                                    | `title: str`, `author: str`, `cover_image: UploadFile`    | `schemas.Book`                                            |
| `GET`  | `/books/count`                          | Retorna el número total de libros en la biblioteca.                                                       | `None`                                                    | `int`                                                     |
| `GET`  | `/books/search/`                        | Busca libros por un título parcial.                                                                       | `title: str` (query param)                                | `List[schemas.Book]`                                      |
| `GET`  | `/categories/`                          | Retorna una lista de todas las categorías únicas de libros.                                               | `None`                                                    | `List[str]`                                               |
| `DELETE`| `/books/{book_id}`                     | Elimina un libro específico por su ID, incluyendo archivos asociados y el índice RAG.                    | `None`                                                    | `{"message": "Libro eliminado..."}`                       |
| `DELETE`| `/categories/{category_name}`          | Elimina todos los libros de una categoría, incluyendo archivos asociados y sus índices RAG.              | `None`                                                    | `{"message": "Categoría eliminada..."}`                   |
| `GET`  | `/books/download/{book_id}`             | Permite descargar o visualizar el archivo de un libro por su ID.                                         | `None`                                                    | `FileResponse` (PDF o EPUB)                               |
| `POST` | `/api/books/{book_id}/convert`          | Convierte un EPUB existente en la biblioteca a PDF y lo añade como un nuevo libro.                       | `None`                                                    | `schemas.Book`                                            |
| `POST` | `/tools/convert-epub-to-pdf`            | Convierte un archivo EPUB subido a PDF y devuelve una URL para su descarga temporal.                      | `file: UploadFile`                                        | `{"download_url": "/temp_books/..."}`                     |
| `POST` | `/rag/index/{book_id}`                  | Indexa un libro existente en la base de datos para el sistema RAG.                                       | `force: bool` (query param)                               | `{"message": "Libro indexado...", "book_id": "...", "force": "..."}` |
| `GET`  | `/rag/status/{book_id}`                 | Retorna el estado de indexación RAG para un libro específico.                                             | `None`                                                    | `{"book_id": "...", "indexed": true/false, "vector_count": 0}` |
| `POST` | `/rag/query/`                           | Envía una consulta a la IA RAG sobre el contenido de un libro.                                            | `schemas.RagQuery` (query, book_id, mode)                 | `schemas.RagQueryResponse` (response)                     |
| `POST` | `/rag/reindex/category/{category_name}` | (Re)indexa todos los libros de una categoría específica en RAG.                                          | `force: bool` (query param)                               | `{"category": "...", "processed": ..., "failed": [...]}` |
| `POST` | `/rag/reindex/all`                      | (Re)indexa todos los libros de la biblioteca en RAG.                                                     | `force: bool` (query param)                               | `{"processed": ..., "failed": [...], "total": ...}`      |
| `GET`  | `/rag/estimate/book/{book_id}`          | Estima la cantidad de tokens y chunks para indexar un libro, con un coste opcional.                      | `per1k: float`, `max_tokens: int` (query params)          | `{"book_id": "...", "tokens": ..., "chunks": ..., "estimated_cost": ...}` |
| `GET`  | `/rag/estimate/category/{category_name}`| Estima la cantidad de tokens y chunks para indexar todos los libros de una categoría.                    | `per1k: float`, `max_tokens: int` (query params)          | `{"category": "...", "tokens": ..., "chunks": ..., "files": ..., "estimated_cost": ...}` |
| `GET`  | `/rag/estimate/all`                     | Estima la cantidad de tokens y chunks para indexar todos los libros de la biblioteca.                    | `per1k: float`, `max_tokens: int` (query params)          | `{"tokens": ..., "chunks": ..., "files": ..., "estimated_cost": ...}` |
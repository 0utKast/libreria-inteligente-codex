from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import shutil
import os
from pathlib import Path
import asyncio
import io
from dotenv import load_dotenv
import json
from typing import List, Optional
from PIL import Image

from . import crud, models, database, schemas, utils
import uuid # For generating unique book IDs

# --- Configuración Inicial ---
base_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_dir.parent / '.env')

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
AI_ENABLED = bool(API_KEY)
if AI_ENABLED:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
models.Base.metadata.create_all(bind=database.engine)

# --- Utilidades de Imagen ---
def save_optimized_image(pix_or_bytes, target_path, is_pixmap=True):
    """Guarda una imagen optimizada (redimensionada y comprimida)."""
    if is_pixmap:
        # pix_or_bytes es un fitz.Pixmap
        img = Image.frombytes("RGB", [pix_or_bytes.width, pix_or_bytes.height], pix_or_bytes.samples)
    else:
        # pix_or_bytes es un objeto bytes (de EPUB)
        img = Image.open(io.BytesIO(pix_or_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

    # Redimensionar si es muy grande (máximo 400px de ancho para portadas)
    MAX_WIDTH = 400
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / float(img.width)
        new_height = int(float(img.height) * ratio)
        img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
    
    # Guardar como JPEG con calidad optimizada
    img.save(target_path, "JPEG", quality=80, optimize=True)

# --- Utilidades de Ruta ---
def get_safe_path(db_path: str) -> str:
    """Resuelve una ruta de la base de datos a una ruta absoluta en tiempo de ejecución."""
    if not db_path:
        return db_path
    if os.path.isabs(db_path):
        return db_path
    # Asumimos que las rutas relativas en la BD son relativas a la carpeta 'backend'
    return os.path.abspath(os.path.join(str(base_dir), db_path))

def get_relative_path(abs_path: str) -> str:
    """Convierte una ruta absoluta a una relativa al directorio 'backend'."""
    try:
        rel = os.path.relpath(abs_path, base_dir)
        return rel.replace("\\", "/")
    except ValueError:
        return abs_path

# --- Funciones de IA y Procesamiento ---
async def analyze_with_gemini(text: str) -> dict:
    if os.getenv("DISABLE_AI") == "1" or not AI_ENABLED:
        return {"title": "Desconocido", "author": "Desconocido", "category": "Desconocido"}
    import google.generativeai as genai
    # Permite configurar el modelo por variable de entorno; por defecto 2.5 (sin alias -latest)
    model_name = os.getenv("GEMINI_MODEL_MAIN", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name)
    prompt = f"""
    Eres un bibliotecario experto. Analiza el siguiente texto extraído de las primeras páginas de un libro.
    Tu tarea es identificar el título, el autor y la categoría principal del libro.
    Devuelve ÚNICAMENTE un objeto JSON con las claves "title", "author" y "category".
    Si no puedes determinar un valor, usa "Desconocido".
    Ejemplo: {{'title': 'El nombre del viento', 'author': 'Patrick Rothfuss', 'category': 'Fantasía'}}
    Texto a analizar: --- {text[:4000]} ---
    """
    try:
        response = await model.generate_content_async(prompt)
        if os.getenv("DEBUG_GEMINI") == "1":
            print(f"DEBUG: Gemini raw response: {response.text}")
        match = response.text.strip()
        if match.startswith("```json"):
            match = match[7:]
        if match.endswith("```"):
            match = match[:-3]
        return json.loads(match.strip())
    except Exception as e:
        print(f"Error al analizar con Gemini: {e}")
        if 'response' in locals() and os.getenv("DEBUG_GEMINI") == "1":
            print(f"DEBUG: Gemini raw response on error: {response.text}")
        return {"title": "Error de IA", "author": "Error de IA", "category": "Error de IA"}

def process_pdf(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict:
    import fitz
    text = utils.extract_text_from_pdf(file_path, max_pages=5)
    doc = fitz.open(file_path)
    cover_path = None
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.width > 300 and pix.height > 300:
                cover_filename = f"cover_{os.path.basename(file_path)}.jpg"
                cover_full_path = os.path.join(covers_dir_fs, cover_filename)
                save_optimized_image(pix, cover_full_path, is_pixmap=True)
                cover_path = f"{covers_url_prefix}/{cover_filename}"
                break
        if cover_path:
            break
    return {"text": text, "cover_image_url": cover_path}

def process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict:
    """ Lógica de procesamiento de EPUB muy mejorada con fallbacks para la portada. """
    text = utils.extract_text_from_epub(file_path, max_chars=4500)
    
    import ebooklib
    from ebooklib import epub
    book = epub.read_epub(file_path)
    
    if len(text.strip()) < 100:
        raise HTTPException(status_code=422, detail="No se pudo extraer suficiente texto del EPUB para su análisis.")

    cover_path = None
    cover_item = None

    # Intento 1: Buscar la portada oficial en metadatos
    cover_items = list(book.get_items_of_type(ebooklib.ITEM_COVER))
    if cover_items:
        cover_item = cover_items[0]
    
    # Intento 2: Si no hay portada oficial, buscar por nombre de archivo "cover"
    if not cover_item:
        for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
            if 'cover' in item.get_name().lower():
                cover_item = item
                break

    # Si encontramos una portada por cualquiera de los métodos
    if cover_item:
        cover_filename = f"cover_{os.path.basename(file_path)}_{cover_item.get_name()}".replace('/', '_').replace('\\', '_')
        if not cover_filename.lower().endswith(('.jpg', '.jpeg')):
            cover_filename = os.path.splitext(cover_filename)[0] + ".jpg"
        cover_full_path = os.path.join(covers_dir_fs, cover_filename)
        save_optimized_image(cover_item.get_content(), cover_full_path, is_pixmap=False)
        cover_path = f"{covers_url_prefix}/{cover_filename}"

    return {"text": text, "cover_image_url": cover_path}

# --- Configuración de la App FastAPI ---
# Test comment
app = FastAPI(title="Mi Librería Inteligente Codex", version="0.4.0-alpha")

# Rutas robustas basadas en este archivo
STATIC_DIR_FS = (base_dir / "static").resolve()
STATIC_COVERS_DIR_FS = (STATIC_DIR_FS / "covers").resolve()
TEMP_BOOKS_DIR_FS = (base_dir / "temp_books").resolve()
BOOKS_DIR_FS = (base_dir / "books").resolve()

STATIC_COVERS_URL_PREFIX = "static/covers"

os.makedirs(STATIC_COVERS_DIR_FS, exist_ok=True)
os.makedirs(TEMP_BOOKS_DIR_FS, exist_ok=True)
os.makedirs(BOOKS_DIR_FS, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR_FS)), name="static")

# Cache headers for static files (covers and others)
@app.middleware("http")
async def add_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        # Cache for 1 day
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

app.mount("/temp_books", StaticFiles(directory=str(TEMP_BOOKS_DIR_FS)), name="temp_books")
raw_origins = os.getenv("ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
allow_origins = [o.strip() for o in raw_origins if o.strip()]

# Permitir orígenes de redes privadas sin necesidad de fijar IPs, soportando HTTP y HTTPS,
# y una lista configurable de puertos de frontend.
ports_csv = os.getenv("FRONTEND_PORTS", "3000,3001,5173,8080")
ports = [p.strip() for p in ports_csv.split(",") if p.strip()]
ports_pattern = "|".join(ports) if ports else r"\d+"
default_origin_regex = rf"^https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+):({ports_pattern})$"
allow_origin_regex = os.getenv("ALLOW_ORIGIN_REGEX", default_origin_regex)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Rutas de la API ---

async def background_index_book(book_id: int, file_path: str):
    """Tarea en segundo plano para indexar un libro en RAG."""
    try:
        from . import rag
        await rag.process_book_for_rag(file_path, str(book_id))
    except Exception as e:
        print(f"Error en indexación de fondo para book_id={book_id}: {e}")

async def background_convert_and_index(book_id: int, original_path: str, db_session_factory):
    """Tarea compleja en segundo plano: convertir, analizar e indexar."""
    # Nota: Aquí necesitaríamos manejar nuestra propia sesión si quisiéramos actualizar la BD
    # Pero para simplificar en esta fase, nos enfocaremos en la indexación RAG automática.
    pass

@app.post("/api/books/{book_id}/convert", response_model=schemas.Book)
async def convert_book_to_pdf(book_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Convierte un libro EPUB existente a PDF y lo añade a la biblioteca como un nuevo libro.
    """
    # 1. Obtener el libro original
    original_book = crud.get_book(db, book_id=book_id)
    if not original_book:
        raise HTTPException(status_code=404, detail="Libro original no encontrado.")

    # 2. Validar que es un EPUB
    if not original_book.file_path.lower().endswith('.epub'):
        raise HTTPException(status_code=400, detail="La conversión solo es posible para libros en formato EPUB.")

    # 3. Leer el contenido del archivo EPUB
    abs_epub_path = get_safe_path(original_book.file_path)
    try:
        with open(abs_epub_path, "rb") as f:
            epub_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo EPUB no encontrado en el disco.")

    # 4. Convertir a PDF (Esto sigue siendo una tarea pesada, pero la mantenemos aquí para devolver el libro)
    # En una versión futura podríamos devolver 202 Accepted y notificar por WebSocket.
    try:
        pdf_bytes = await asyncio.to_thread(utils.convert_epub_bytes_to_pdf_bytes, epub_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la conversión a PDF: {e}")

    # 5. Guardar el nuevo archivo PDF
    base_filename = os.path.splitext(os.path.basename(original_book.file_path))[0]
    new_filename = f"{base_filename}.pdf"
    new_filepath_abs = os.path.join(str(BOOKS_DIR_FS), new_filename)

    # Asegurarse de que el nombre de archivo no exista ya
    counter = 1
    while os.path.exists(new_filepath_abs):
        new_filename = f"{base_filename}_{counter}.pdf"
        new_filepath_abs = os.path.join(str(BOOKS_DIR_FS), new_filename)
        counter += 1
    
    with open(new_filepath_abs, "wb") as f:
        f.write(pdf_bytes)

    # 6. Procesar el nuevo PDF para añadirlo a la biblioteca (lógica de /upload-book)
    try:
        book_data = process_pdf(new_filepath_abs, str(STATIC_COVERS_DIR_FS), STATIC_COVERS_URL_PREFIX)
        gemini_result = await analyze_with_gemini(book_data["text"])

        title = gemini_result.get("title", "Desconocido")
        author = gemini_result.get("author", "Desconocido")

        if title == "Desconocido" and author == "Desconocido":
            os.remove(new_filepath_abs)
            raise HTTPException(status_code=422, detail="La IA no pudo identificar metadatos del PDF convertido.")

        new_book = crud.create_book(
            db=db,
            title=title,
            author=author,
            category=gemini_result.get("category", original_book.category), # Usar categoría original como fallback
            cover_image_url=book_data.get("cover_image_url"),
            file_path=get_relative_path(new_filepath_abs)
        )
        
        # Disparar indexación RAG en segundo plano
        background_tasks.add_task(background_index_book, new_book.id, new_filepath_abs)
        
        return new_book
    except Exception as e:
        # Si algo falla, limpiar el PDF creado
        if os.path.exists(new_filepath_abs):
            os.remove(new_filepath_abs)
        # Re-lanzar la excepción para que FastAPI la maneje
        raise HTTPException(status_code=500, detail=f"Error al procesar el nuevo PDF: {e}")


@app.post("/tools/convert-epub-to-pdf")
async def convert_epub_to_pdf_tool(file: UploadFile = File(...)):
    """
    Convierte un archivo EPUB subido a PDF y devuelve un enlace de descarga temporal.
    """
    if not file.filename.lower().endswith('.epub'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un EPUB.")

    try:
        epub_content = await file.read()
        pdf_bytes = await asyncio.to_thread(utils.convert_epub_bytes_to_pdf_bytes, epub_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la conversión: {e}")

    # Guardar el PDF en un directorio temporal
    base_filename = os.path.splitext(file.filename)[0]
    # Usar un UUID para evitar colisiones y añadir seguridad
    unique_id = uuid.uuid4()
    new_filename = f"{base_filename}_{unique_id}.pdf"
    temp_pdf_path = os.path.join(str(TEMP_BOOKS_DIR_FS), new_filename)

    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_bytes)

    # Devolver la URL para descargar el archivo
    download_url = f"/temp_books/{new_filename}"
    return {"download_url": download_url}


@app.post("/upload-book/", response_model=schemas.Book)
async def upload_book(background_tasks: BackgroundTasks, db: Session = Depends(get_db), book_file: UploadFile = File(...)):
    books_dir = str(BOOKS_DIR_FS)
    safe_name = os.path.basename(book_file.filename)
    file_path_abs = os.path.abspath(os.path.join(books_dir, safe_name))

    if crud.get_book_by_path(db, file_path_abs) or crud.get_book_by_path(db, get_relative_path(file_path_abs)):
        raise HTTPException(status_code=409, detail="Este libro ya ha sido añadido.")

    with open(file_path_abs, "wb") as buffer:
        shutil.copyfileobj(book_file.file, buffer)

    file_ext = os.path.splitext(book_file.filename)[1].lower()
    try:
        if file_ext == ".pdf":
            book_data = process_pdf(file_path_abs, str(STATIC_COVERS_DIR_FS), STATIC_COVERS_URL_PREFIX)
        elif file_ext == ".epub":
            book_data = process_epub(file_path_abs, str(STATIC_COVERS_DIR_FS), STATIC_COVERS_URL_PREFIX)
        else:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado.")
    except HTTPException as e:
        os.remove(file_path_abs) # Limpiar el archivo subido si el procesamiento falla
        raise e

    gemini_result = await analyze_with_gemini(book_data["text"])
    
    # --- Puerta de Calidad ---
    title = gemini_result.get("title", "Desconocido")
    author = gemini_result.get("author", "Desconocido")

    if title == "Desconocido" and author == "Desconocido":
        os.remove(file_path_abs) # Borrar el archivo que no se pudo analizar
        raise HTTPException(status_code=422, detail="La IA no pudo identificar el título ni el autor del libro. No se ha añadido.")

    new_book = crud.create_book(
        db=db, 
        title=title, 
        author=author, 
        category=gemini_result.get("category", "Desconocido"), 
        cover_image_url=book_data.get("cover_image_url"), 
        file_path=get_relative_path(file_path_abs)
    )

    # Disparar indexación RAG en segundo plano
    background_tasks.add_task(background_index_book, new_book.id, file_path_abs)

    return new_book

@app.get("/api/books/search/semantic", response_model=List[schemas.Book])
async def semantic_search(q: str, db: Session = Depends(get_db)):
    """Busca libros usando similitud semántica (IA) a través de RAG."""
    if not AI_ENABLED:
        raise HTTPException(status_code=400, detail="La búsqueda semántica requiere que la IA esté habilitada.")
    
    try:
        from . import rag
        semantic_results = await rag.query_semantic_books(q)
        
        # Obtener los objetos Book completos de la DB
        books_map = {}
        for res in semantic_results:
            book = crud.get_book(db, book_id=res["book_id"])
            if book:
                books_map[book.id] = book
        
        # Mantener el orden de relevancia devuelto por RAG
        ordered_books = []
        for res in semantic_results:
            if res["book_id"] in books_map:
                ordered_books.append(books_map[res["book_id"]])
                
        return ordered_books
    except Exception as e:
        print(f"Error en búsqueda semántica: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/books/", response_model=List[schemas.Book])
def read_books(category: str | None = None, search: str | None = None, author: str | None = None, db: Session = Depends(get_db), skip: int = 0, limit: int = 20):
    return crud.get_books(db, category=category, search=search, author=author, skip=skip, limit=limit)

@app.put("/books/{book_id}", response_model=schemas.Book)
async def update_book_details(
    book_id: int,
    db: Session = Depends(get_db),
    title: str = Form(...),
    author: str = Form(...),
    cover_image: Optional[UploadFile] = File(None)
):
    """
    Actualiza los detalles de un libro, incluyendo título, autor y portada.
    """
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    new_cover_path = db_book.cover_image_url

    if cover_image:
        # Hay una nueva imagen, hay que guardarla
        if db_book.cover_image_url:
            old_cover_full_path = STATIC_DIR_FS / db_book.cover_image_url
            if os.path.exists(old_cover_full_path):
                os.remove(old_cover_full_path)

        # Generar un nombre de archivo único para la nueva portada
        file_ext = Path(cover_image.filename).suffix
        new_cover_filename = f"cover_{book_id}_{uuid.uuid4()}{file_ext}"
        new_cover_full_path = STATIC_COVERS_DIR_FS / new_cover_filename
        
        with open(new_cover_full_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        
        new_cover_path = f"{STATIC_COVERS_URL_PREFIX}/{new_cover_filename}"

    updated_book = crud.update_book(
        db=db,
        book_id=book_id,
        title=title,
        author=author,
        cover_image_url=new_cover_path
    )

    if not updated_book:
        # Esto no debería ocurrir si la comprobación inicial pasó, pero por si acaso
        raise HTTPException(status_code=404, detail="Libro no encontrado al intentar actualizar")

    return updated_book

@app.get("/books/count", response_model=int)
def get_books_count(db: Session = Depends(get_db)):
    """Obtiene el número total de libros en la biblioteca."""
    return crud.get_books_count(db)

@app.get("/books/search/", response_model=List[schemas.Book])
def search_books(title: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Busca libros por un título parcial, con opciones de paginación."""
    books = crud.get_books_by_partial_title(db, title=title, skip=skip, limit=limit)
    return books

@app.get("/categories/", response_model=List[str])
def read_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@app.delete("/books/{book_id}")
def delete_single_book(book_id: int, db: Session = Depends(get_db)):
    # Limpiar índices RAG asociados al libro (usamos el ID de BD como book_id en RAG)
    try:
        from . import rag
        rag.delete_book_from_rag(str(book_id))
    except Exception as e:
        print(f"Advertencia: fallo al limpiar RAG para book_id={book_id}: {e}")
    book = crud.delete_book(db, book_id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    return {"message": f"Libro '{book.title}' eliminado con éxito."}

@app.delete("/categories/{category_name}")
def delete_category_and_books(category_name: str, db: Session = Depends(get_db)):
    # Obtener IDs antes de borrar para limpiar RAG
    ids = [str(row.id) for row in db.query(models.Book).filter(models.Book.category == category_name).all()]
    deleted_count = crud.delete_books_by_category(db, category=category_name)
    for bid in ids:
        try:
            rag.delete_book_from_rag(bid)
        except Exception as e:
            print(f"Advertencia: fallo al limpiar RAG para book_id={bid}: {e}")
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Categoría '{category_name}' no encontrada o ya está vacía.")
    return {"message": f"Categoría '{category_name}' y sus {deleted_count} libros han sido eliminados."}

@app.get("/books/download/{book_id}")
def download_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    
    abs_file_path = get_safe_path(book.file_path)
    if not os.path.exists(abs_file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el disco.")

    file_ext = os.path.splitext(abs_file_path)[1].lower()
    filename = os.path.basename(abs_file_path)
    
    if file_ext == ".pdf":
        return FileResponse(
            path=abs_file_path,
            filename=filename,
            media_type='application/pdf',
            content_disposition_type='inline'
        )
    else: # Para EPUB y otros tipos de archivo
        return FileResponse(
            path=abs_file_path,
            filename=filename,
            media_type='application/epub+zip',
            content_disposition_type='attachment'
        )

@app.post("/rag/upload-book/", response_model=schemas.RagUploadResponse)
async def upload_book_for_rag(file: UploadFile = File(...)):
    book_id = str(uuid.uuid4())
    file_location = os.path.join(str(TEMP_BOOKS_DIR_FS), f"{book_id}_{file.filename}")
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    try:
        from . import rag
        await rag.process_book_for_rag(file_location, book_id)
        return {"book_id": book_id, "message": "Libro procesado para RAG exitosamente."}
    except Exception as e:
        os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Error al procesar el libro para RAG: {e}")

@app.post("/rag/query/", response_model=schemas.RagQueryResponse)
async def query_rag_endpoint(query_data: schemas.RagQuery, db: Session = Depends(get_db)):
    try:
        mode = query_data.mode or "balanced"
        # Metadatos del libro
        book = db.query(models.Book).filter(models.Book.id == int(query_data.book_id)).first()
        metadata = None
        library_ctx = None
        if book:
            metadata = {"title": book.title, "author": book.author, "category": book.category}
            if mode != "strict":
                # Otras obras del mismo autor en la biblioteca
                others = [b.title for b in db.query(models.Book).filter(models.Book.author == book.author, models.Book.id != book.id).limit(50).all()]
                library_ctx = {"author_other_books": others}
        response_text = await rag.query_rag(query_data.query, query_data.book_id, mode=mode, metadata=metadata, library=library_ctx)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar RAG: {e}")


@app.post("/rag/index/{book_id}")
async def index_existing_book_for_rag(book_id: int, force: bool = False, db: Session = Depends(get_db)):
    """Indexa en RAG un libro ya existente en BD usando su file_path.

    Usa el ID de BD como book_id en RAG. Si `force` es True, reindexa (borra y vuelve a indexar).
    """
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    
    abs_file_path = get_safe_path(book.file_path)
    if not os.path.exists(abs_file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el disco.")
    try:
        from . import rag
        await rag.process_book_for_rag(abs_file_path, str(book.id), force_reindex=force)
        return {"message": "Libro indexado en RAG", "book_id": str(book.id), "force": force}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al indexar en RAG: {e}")


@app.get("/rag/status/{book_id}")
def rag_status(book_id: int):
    """Devuelve si el libro tiene índice RAG y el número de vectores."""
    try:
        from . import rag
        count = rag.get_index_count(str(book_id))
        return {"book_id": str(book_id), "indexed": count > 0, "vector_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estado RAG: {e}")


@app.get("/rag/stats")
async def get_rag_stats():
    """Obtiene estadísticas del índice RAG."""
    try:
        from . import rag
        rag._ensure_init()
        count = rag._collection.count()
        return {"total_documents": count}
    except Exception as e:
        return {"total_documents": 0, "error": str(e)}

@app.post("/rag/reindex/category/{category_name}")
async def rag_reindex_category(category_name: str, force: bool = True, db: Session = Depends(get_db)):
    """(Re)indexa todos los libros de una categoría en RAG."""
    books = db.query(models.Book).filter(models.Book.category == category_name).all()
    if not books:
        raise HTTPException(status_code=404, detail=f"Categoría '{category_name}' no encontrada o sin libros.")
    processed, failed = 0, []
    for b in books:
        try:
            from . import rag
            abs_file_path = get_safe_path(b.file_path)
            await rag.process_book_for_rag(abs_file_path, str(b.id), force_reindex=force)
            processed += 1
        except Exception as e:
            failed.append({"book_id": b.id, "error": str(e)})
    return {"category": category_name, "processed": processed, "failed": failed, "force": force}


async def background_reindex_all(force: bool, db_session: Session):
    """Tarea en segundo plano para reindexar toda la biblioteca."""
    books = db_session.query(models.Book).all()
    from . import rag
    for b in books:
        try:
            abs_file_path = get_safe_path(b.file_path)
            await rag.process_book_for_rag(abs_file_path, str(b.id), force_reindex=force)
        except Exception as e:
            print(f"RAG: Fallo al reindexar libro {b.id}: {e}")

@app.post("/rag/reindex/all")
async def rag_reindex_all(background_tasks: BackgroundTasks, force: bool = True, db: Session = Depends(get_db)):
    """(Re)indexa todos los libros de la biblioteca en RAG (en segundo plano)."""
    # Necesitamos una sesión de DB que no se cierre al terminar la petición
    # Pero FastAPI.BackgroundTasks maneja bien la inyección si pasamos el objeto
    background_tasks.add_task(background_reindex_all, force, db)
    return {"message": "Iniciado proceso de reindexado masivo en segundo plano.", "total_books": db.query(models.Book).count()}


@app.get("/rag/estimate/book/{book_id}")
def estimate_rag_for_book(book_id: int, per1k: float | None = None, max_tokens: int = 1000, db: Session = Depends(get_db)):
    """Estimación de tokens/chunks y coste opcional para un libro."""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    try:
        from . import rag
        abs_file_path = get_safe_path(book.file_path)
        est = rag.estimate_embeddings_for_file(abs_file_path, max_tokens=max_tokens)
        cost = (est["tokens"] / 1000.0) * per1k if per1k else None
        return {"book_id": str(book.id), **est, "per1k": per1k, "estimated_cost": cost}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en estimación: {e}")


@app.get("/rag/estimate/category/{category_name}")
def estimate_rag_for_category(category_name: str, per1k: float | None = None, max_tokens: int = 1000, db: Session = Depends(get_db)):
    books = db.query(models.Book).filter(models.Book.category == category_name).all()
    if not books:
        raise HTTPException(status_code=404, detail=f"Categoría '{category_name}' no encontrada o sin libros.")
    try:
        file_paths = [get_safe_path(b.file_path) for b in books]
        from . import rag
        est = rag.estimate_embeddings_for_files(file_paths, max_tokens=max_tokens)
        cost = (est["tokens"] / 1000.0) * per1k if per1k else None
        return {"category": category_name, **est, "per1k": per1k, "estimated_cost": cost}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en estimación: {e}")


@app.get("/rag/estimate/all")
def estimate_rag_for_all(per1k: float | None = None, max_tokens: int = 1000, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    if not books:
        return {"tokens": 0, "chunks": 0, "files": 0, "per1k": per1k, "estimated_cost": 0}
    try:
        file_paths = [get_safe_path(b.file_path) for b in books]
        from . import rag
        est = rag.estimate_embeddings_for_files(file_paths, max_tokens=max_tokens)
        cost = (est["tokens"] / 1000.0) * per1k if per1k else None
        return {**est, "per1k": per1k, "estimated_cost": cost}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en estimación: {e}")

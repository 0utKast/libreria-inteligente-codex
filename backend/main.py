from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import shutil
import os
from pathlib import Path
import io
import fitz
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import json
from typing import List, Optional

from . import crud, models, database, schemas
from . import rag  # Import the new RAG module
import uuid # For generating unique book IDs

# --- Configuración Inicial ---
base_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_dir.parent / '.env')

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
AI_ENABLED = bool(API_KEY)
if AI_ENABLED:
    genai.configure(api_key=API_KEY)
models.Base.metadata.create_all(bind=database.engine)

# --- Funciones de IA y Procesamiento ---
async def analyze_with_gemini(text: str) -> dict:
    if os.getenv("DISABLE_AI") == "1" or not AI_ENABLED:
        return {"title": "Desconocido", "author": "Desconocido", "category": "Desconocido"}
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
    doc = fitz.open(file_path)
    text = ""
    for i in range(min(len(doc), 5)):
        text += doc.load_page(i).get_text("text", sort=True)
    cover_path = None
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.width > 300 and pix.height > 300:
                cover_filename = f"cover_{os.path.basename(file_path)}.png"
                cover_full_path = os.path.join(covers_dir_fs, cover_filename)
                pix.save(cover_full_path)
                cover_path = f"{covers_url_prefix}/{cover_filename}"
                break
        if cover_path:
            break
    return {"text": text, "cover_image_url": cover_path}

def process_epub(file_path: str, covers_dir_fs: str, covers_url_prefix: str) -> dict:
    """ Lógica de procesamiento de EPUB muy mejorada con fallbacks para la portada. """
    book = epub.read_epub(file_path)
    text = ""
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        text += soup.get_text(separator=' ') + "\n"
        if len(text) > 4500:
            break
    
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
        cover_full_path = os.path.join(covers_dir_fs, cover_filename)
        with open(cover_full_path, 'wb') as f:
            f.write(cover_item.get_content())
        cover_path = f"{covers_url_prefix}/{cover_filename}"

    return {"text": text, "cover_image_url": cover_path}

# --- Configuración de la App FastAPI ---
# Test comment
app = FastAPI()

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
app.mount("/temp_books", StaticFiles(directory=str(TEMP_BOOKS_DIR_FS)), name="temp_books")
raw_origins = os.getenv("ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
allow_origins = [o.strip() for o in raw_origins if o.strip()]

# Permitir orígenes de redes privadas sin necesidad de fijar IPs, soportando HTTP y HTTPS,
# y una lista configurable de puertos de frontend.
ports_csv = os.getenv("FRONTEND_PORTS", "3000,5173,8080")
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

@app.post("/upload-book/", response_model=schemas.Book)
async def upload_book(db: Session = Depends(get_db), book_file: UploadFile = File(...)):
    books_dir = str(BOOKS_DIR_FS)
    safe_name = os.path.basename(book_file.filename)
    file_path = os.path.abspath(os.path.join(books_dir, safe_name))

    if crud.get_book_by_path(db, file_path):
        raise HTTPException(status_code=409, detail="Este libro ya ha sido añadido.")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(book_file.file, buffer)

    file_ext = os.path.splitext(book_file.filename)[1].lower()
    try:
        if file_ext == ".pdf":
            book_data = process_pdf(file_path, str(STATIC_COVERS_DIR_FS), STATIC_COVERS_URL_PREFIX)
        elif file_ext == ".epub":
            book_data = process_epub(file_path, str(STATIC_COVERS_DIR_FS), STATIC_COVERS_URL_PREFIX)
        else:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado.")
    except HTTPException as e:
        os.remove(file_path) # Limpiar el archivo subido si el procesamiento falla
        raise e

    gemini_result = await analyze_with_gemini(book_data["text"])
    
    # --- Puerta de Calidad ---
    title = gemini_result.get("title", "Desconocido")
    author = gemini_result.get("author", "Desconocido")

    if title == "Desconocido" and author == "Desconocido":
        os.remove(file_path) # Borrar el archivo que no se pudo analizar
        raise HTTPException(status_code=422, detail="La IA no pudo identificar el título ni el autor del libro. No se ha añadido.")

    return crud.create_book(
        db=db, 
        title=title, 
        author=author, 
        category=gemini_result.get("category", "Desconocido"), 
        cover_image_url=book_data.get("cover_image_url"), 
        file_path=file_path
    )

@app.get("/books/", response_model=List[schemas.Book])
def read_books(category: str | None = None, search: str | None = None, author: str | None = None, db: Session = Depends(get_db)):
    return crud.get_books(db, category=category, search=search, author=author)

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
    if not os.path.exists(book.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el disco.")

    file_ext = os.path.splitext(book.file_path)[1].lower()
    filename = os.path.basename(book.file_path)
    
    if file_ext == ".pdf":
        return FileResponse(
            path=book.file_path,
            filename=filename,
            media_type='application/pdf',
            content_disposition_type='inline'
        )
    else: # Para EPUB y otros tipos de archivo
        return FileResponse(
            path=book.file_path,
            filename=filename,
            media_type='application/epub+zip',
            content_disposition_type='attachment'
        )

@app.post("/tools/convert-epub-to-pdf", response_model=schemas.ConversionResponse)
async def convert_epub_to_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith('.epub'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un EPUB.")

    epub_content = await file.read()

    try:
        import tempfile
        import zipfile
        import pathlib
        from weasyprint import HTML, CSS
        from bs4 import BeautifulSoup
        import uuid

        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Extraer el EPUB a una carpeta temporal
            with zipfile.ZipFile(io.BytesIO(epub_content), 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # 2. Encontrar el archivo .opf (el "manifiesto" del libro)
            opf_path = next(pathlib.Path(temp_dir).rglob('*.opf'), None)
            if not opf_path:
                raise Exception("No se pudo encontrar el archivo .opf en el EPUB.")
            content_root = opf_path.parent

            # 3. Leer y analizar el manifiesto .opf en modo binario para autodetectar codificación
            with open(opf_path, 'rb') as f:
                opf_soup = BeautifulSoup(f, 'lxml-xml')

            # 4. Crear una página de portada si se encuentra
            html_docs = []
            cover_meta = opf_soup.find('meta', {'name': 'cover'})
            if cover_meta:
                cover_id = cover_meta.get('content')
                cover_item = opf_soup.find('item', {'id': cover_id})
                if cover_item:
                    cover_href = cover_item.get('href')
                    cover_path = content_root / cover_href
                    if cover_path.exists():
                        cover_html_string = f"<html><body style='text-align: center; margin: 0; padding: 0;'><img src='{cover_path.as_uri()}' style='width: 100%; height: 100%; object-fit: contain;'/></body></html>"
                        html_docs.append(HTML(string=cover_html_string))

            # 5. Encontrar y leer todos los archivos CSS
            stylesheets = []
            css_items = opf_soup.find_all('item', {'media-type': 'text/css'})
            for css_item in css_items:
                css_href = css_item.get('href')
                if css_href:
                    css_path = content_root / css_href
                    if css_path.exists():
                        stylesheets.append(CSS(filename=css_path))

            # 6. Encontrar el orden de lectura (spine) y añadir los capítulos
            spine_ids = [item.get('idref') for item in opf_soup.find('spine').find_all('itemref')]
            html_paths_map = {item['id']: item['href'] for item in opf_soup.find_all('item', {'media-type': 'application/xhtml+xml'})}
            
            for chapter_id in spine_ids:
                href = html_paths_map.get(chapter_id)
                if href:
                    chapter_path = content_root / href
                    if chapter_path.exists():
                        # LA SOLUCIÓN: Pasar filename y encoding directamente a WeasyPrint
                        html_docs.append(HTML(filename=chapter_path, encoding='utf-8'))

            if not html_docs:
                raise Exception("No se encontró contenido HTML en el EPUB.")

            # 7. Renderizar y unir todos los documentos
            first_doc = html_docs[0].render(stylesheets= stylesheets)
            all_pages = [p for doc in html_docs[1:] for p in doc.render(stylesheets= stylesheets).pages]
            
            pdf_bytes_io = io.BytesIO()
            first_doc.copy(all_pages).write_pdf(target=pdf_bytes_io)
            pdf_bytes = pdf_bytes_io.getvalue()

        # Guardar el PDF en la carpeta temporal pública
        pdf_filename = f"{uuid.uuid4()}.pdf"
        public_pdf_path = os.path.join(str(TEMP_BOOKS_DIR_FS), pdf_filename)
        with open(public_pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        # Devolver la URL de descarga en un JSON
        return {"download_url": f"/temp_books/{pdf_filename}"}
    except Exception as e:
        error_message = f"Error durante la conversión: {type(e).__name__}: {e}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)

@app.post("/rag/upload-book/", response_model=schemas.RagUploadResponse)
async def upload_book_for_rag(file: UploadFile = File(...)):
    book_id = str(uuid.uuid4())
    file_location = os.path.join(str(TEMP_BOOKS_DIR_FS), f"{book_id}_{file.filename}")
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    try:
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
    if not os.path.exists(book.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el disco.")
    try:
        await rag.process_book_for_rag(book.file_path, str(book.id), force_reindex=force)
        return {"message": "Libro indexado en RAG", "book_id": str(book.id), "force": force}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al indexar en RAG: {e}")


@app.get("/rag/status/{book_id}")
def rag_status(book_id: int):
    """Devuelve si el libro tiene índice RAG y el número de vectores."""
    try:
        count = rag.get_index_count(str(book_id))
        return {"book_id": str(book_id), "indexed": count > 0, "vector_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estado RAG: {e}")


@app.post("/rag/reindex/category/{category_name}")
async def rag_reindex_category(category_name: str, force: bool = True, db: Session = Depends(get_db)):
    """(Re)indexa todos los libros de una categoría en RAG."""
    books = db.query(models.Book).filter(models.Book.category == category_name).all()
    if not books:
        raise HTTPException(status_code=404, detail=f"Categoría '{category_name}' no encontrada o sin libros.")
    processed, failed = 0, []
    for b in books:
        try:
            await rag.process_book_for_rag(b.file_path, str(b.id), force_reindex=force)
            processed += 1
        except Exception as e:
            failed.append({"book_id": b.id, "error": str(e)})
    return {"category": category_name, "processed": processed, "failed": failed, "force": force}


@app.post("/rag/reindex/all")
async def rag_reindex_all(force: bool = True, db: Session = Depends(get_db)):
    """(Re)indexa todos los libros de la biblioteca en RAG."""
    books = db.query(models.Book).all()
    processed, failed = 0, []
    for b in books:
        try:
            await rag.process_book_for_rag(b.file_path, str(b.id), force_reindex=force)
            processed += 1
        except Exception as e:
            failed.append({"book_id": b.id, "error": str(e)})
    return {"processed": processed, "failed": failed, "total": len(books), "force": force}


@app.get("/rag/estimate/book/{book_id}")
def estimate_rag_for_book(book_id: int, per1k: float | None = None, max_tokens: int = 1000, db: Session = Depends(get_db)):
    """Estimación de tokens/chunks y coste opcional para un libro."""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    try:
        est = rag.estimate_embeddings_for_file(book.file_path, max_tokens=max_tokens)
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
        file_paths = [b.file_path for b in books]
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
        file_paths = [b.file_path for b in books]
        est = rag.estimate_embeddings_for_files(file_paths, max_tokens=max_tokens)
        cost = (est["tokens"] / 1000.0) * per1k if per1k else None
        return {**est, "per1k": per1k, "estimated_cost": cost}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en estimación: {e}")

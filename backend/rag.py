import os
import google.generativeai as genai
from dotenv import load_dotenv
import chromadb
from PyPDF2 import PdfReader
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import tiktoken
import math

# Lazy environment loading and clients
_initialized = False
_collection = None
_ai_enabled = False

# Modelos configurables por entorno; por defecto 2.5 para generación
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
GENERATION_MODEL = os.getenv("GEMINI_GENERATION_MODEL", "models/gemini-2.5-flash")

def _ensure_init():
    global _initialized, _collection, _ai_enabled
    if _initialized:
        return
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    # Do not configure genai if AI is disabled for tests
    if os.getenv("DISABLE_AI") == "1":
        _ai_enabled = False
    else:
        _ai_enabled = bool(api_key)
        if _ai_enabled:
            genai.configure(api_key=api_key)
    # Persist Chroma index to disk
    client = chromadb.PersistentClient(path=str(os.getenv("CHROMA_PATH", "./rag_index")))
    _collection = client.get_or_create_collection(name="book_rag_collection")
    _initialized = True

def get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT"):
    """Generates an embedding for the given text."""
    _ensure_init()
    if not text.strip():
        return []  # empty
    if os.getenv("DISABLE_AI") == "1" or not _ai_enabled:
        # Simple deterministic dummy embedding (not for production)
        return [0.0] * 10
    return genai.embed_content(model=EMBEDDING_MODEL, content=text, task_type=task_type)["embedding"]

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return ""
    return text

def extract_text_from_epub(file_path: str) -> str:
    """Extracts text from an EPUB file."""
    text_content = []
    try:
        book = ebooklib.epub.read_epub(file_path)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text_content.append(soup.get_text())
    except Exception as e:
        print(f"Error extracting text from EPUB {file_path}: {e}")
        return ""
    return "\n".join(text_content)

def extract_text(file_path: str) -> str:
    """Unified text extraction for supported types."""
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    if file_path.lower().endswith(".epub"):
        return extract_text_from_epub(file_path)
    raise ValueError("Unsupported file type. Only PDF and EPUB are supported.")

def chunk_text(text: str, max_tokens: int = 1000) -> list[str]:
    """Chunks text into smaller pieces based on token count."""
    if not text.strip():
        return []
    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo") # Using a common tokenizer for token counting
    tokens = tokenizer.encode(text)
    chunks = []
    current_chunk_tokens = []
    for token in tokens:
        current_chunk_tokens.append(token)
        if len(current_chunk_tokens) >= max_tokens:
            chunks.append(tokenizer.decode(current_chunk_tokens))
            current_chunk_tokens = []
    if current_chunk_tokens:
        chunks.append(tokenizer.decode(current_chunk_tokens))
    return chunks

def _has_index_for_book(book_id: str) -> bool:
    """Returns True if the collection already has vectors for the given book_id."""
    _ensure_init()
    try:
        res = _collection.get(where={"book_id": book_id}, limit=1)
        return bool(res and res.get("ids"))
    except Exception as e:
        print(f"RAG: error checking index for {book_id}: {e}")
        return False

def delete_book_from_rag(book_id: str):
    """Deletes all vectors for a book_id from ChromaDB (no-op if none)."""
    _ensure_init()
    try:
        _collection.delete(where={"book_id": book_id})
    except Exception as e:
        print(f"RAG: error deleting index for {book_id}: {e}")

def get_index_count(book_id: str) -> int:
    """Returns number of vectors stored for a given book_id."""
    _ensure_init()
    try:
        res = _collection.get(where={"book_id": book_id}, include=[])
        return len(res.get("ids", [])) if res else 0
    except Exception as e:
        print(f"RAG: error counting index for {book_id}: {e}")
        return 0

def has_index(book_id: str) -> bool:
    """Public helper to know if a book has index in RAG."""
    return get_index_count(book_id) > 0

async def process_book_for_rag(file_path: str, book_id: str, force_reindex: bool = False):
    """Extracts text, chunks it, generates embeddings, and stores in ChromaDB.

    If force_reindex is True, deletes any existing vectors for book_id first.
    Skips if already indexed and force_reindex is False.
    """
    _ensure_init()
    if force_reindex:
        delete_book_from_rag(book_id)
    else:
        if _has_index_for_book(book_id):
            print(f"RAG: book_id {book_id} already indexed; skipping.")
            return
    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".epub"):
        text = extract_text_from_epub(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and EPUB are supported.")

    if not text.strip():
        raise ValueError("Could not extract text from the book.")

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Could not chunk text from the book.")

    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk) # No await here
        if embedding:  # Only add if embedding is not empty
            _collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"book_id": book_id, "chunk_index": i}],
                ids=[f"{book_id}_chunk_{i}"]
            )
    print(f"Processed {len(chunks)} chunks for book ID: {book_id}")

def estimate_embeddings_for_file(file_path: str, max_tokens: int = 1000) -> dict:
    """Estimate token count and number of chunks for a file using the same tokenizer and chunk size.

    Note: Uses tiktoken (gpt-3.5-turbo) as an approximation to Gemini tokenization.
    """
    text = extract_text(file_path)
    if not text.strip():
        return {"tokens": 0, "chunks": 0}
    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    total_tokens = len(tokenizer.encode(text))
    chunks = math.ceil(total_tokens / max_tokens) if max_tokens > 0 else 0
    return {"tokens": total_tokens, "chunks": chunks}

def estimate_embeddings_for_files(file_paths: list[str], max_tokens: int = 1000) -> dict:
    total_tokens = 0
    total_chunks = 0
    counted = 0
    for p in file_paths:
        try:
            est = estimate_embeddings_for_file(p, max_tokens=max_tokens)
            total_tokens += est["tokens"]
            total_chunks += est["chunks"]
            counted += 1
        except Exception as e:
            print(f"RAG: estimation failed for {p}: {e}")
    return {"tokens": total_tokens, "chunks": total_chunks, "files": counted}

async def query_rag(query: str, book_id: str, mode: str = "balanced", metadata: dict | None = None, library: dict | None = None):
    """Queries the RAG system for answers based on the book content.

    mode:
      - strict: Solo libro. Si falta en el contexto, indícalo.
      - balanced: Prioriza libro, complementa con conocimiento general si falta, señalando lo que no viene del libro.
      - open: Integra libro y conocimiento general libremente, priorizando el libro.

    metadata: opcional, ejemplo {title, author, category}
    library: opcional, ejemplo {author_other_books: [..]}
    """
    _ensure_init()
    query_embedding = get_embedding(query, task_type="RETRIEVAL_QUERY") # No await here
    if not query_embedding:
        return "I cannot process an empty query."

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=5, # Retrieve top 5 relevant chunks
        where={"book_id": book_id}
    )

    relevant_chunks = [doc for doc in results['documents'][0]]
    context = "\n\n".join(relevant_chunks)

    meta_text = ""
    if metadata:
        t = metadata.get("title") or "?"
        a = metadata.get("author") or "?"
        c = metadata.get("category") or "?"
        meta_text = f"Titulo: {t}\nAutor: {a}\nCategoria: {c}"
    lib_text = ""
    if library and library.get("author_other_books"):
        other = ", ".join(str(x) for x in library["author_other_books"][:20])
        lib_text = f"Otras obras del mismo autor (en tu biblioteca): {other}"

    if mode not in ("strict", "balanced", "open"):
        mode = "balanced"

    guidance = {
        "strict": (
            "Responde UNICAMENTE con el contenido del Contexto. Si la respuesta no consta en el Contexto, indícalo brevemente ('No consta en el libro')."
        ),
        "balanced": (
            "Prioriza el Contexto. Si falta información, puedes complementarla con tus conocimientos generales. Señala con 'Nota:' aquello que NO provenga del Contexto del libro."
        ),
        "open": (
            "Integra libremente tus conocimientos generales con el Contexto, dejando claro qué parte viene del libro cuando corresponda."
        )
    }[mode]

    prompt = f"""Eres un asistente útil que responde preguntas.
{guidance}
Responde siempre en español.

Contexto del libro:
{context}

Metadatos del libro:
{meta_text}

Contexto de biblioteca (opcional):
{lib_text}

Pregunta: {query}
Respuesta:"""

    if os.getenv("DISABLE_AI") == "1" or not _ai_enabled:
        return "[IA deshabilitada] Resumen no disponible. Contexto recuperado:\n" + context[:500]
    model = genai.GenerativeModel(GENERATION_MODEL)
    response = model.generate_content(prompt)  # No await here
    return response.text

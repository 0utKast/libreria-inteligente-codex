import os
import google.generativeai as genai
from dotenv import load_dotenv
import chromadb
from PyPDF2 import PdfReader
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import tiktoken

# Lazy environment loading and clients
_initialized = False
_collection = None
_ai_enabled = False

EMBEDDING_MODEL = "models/text-embedding-004"
GENERATION_MODEL = "models/gemini-1.5-flash"

def _ensure_init():
    global _initialized, _collection, _ai_enabled
    if _initialized:
        return
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
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

async def process_book_for_rag(file_path: str, book_id: str):
    """Extracts text, chunks it, generates embeddings, and stores in ChromaDB."""
    _ensure_init()
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

async def query_rag(query: str, book_id: str):
    """Queries the RAG system for answers based on the book content."""
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

    prompt = f"""Eres un asistente útil que responde preguntas.
Prioriza la información del Contexto proporcionado para responder a la pregunta.
Si la información en el Contexto no es suficiente para responder la pregunta, utiliza tus conocimientos generales.
Responde siempre en español.

Contexto:
{context}

Pregunta: {query}
Respuesta:"""

    if os.getenv("DISABLE_AI") == "1" or not _ai_enabled:
        return "[IA deshabilitada] Resumen no disponible. Contexto recuperado:\n" + context[:500]
    model = genai.GenerativeModel(GENERATION_MODEL)
    response = model.generate_content(prompt)  # No await here
    return response.text


from backend.schemas import Book, BookBase, ConversionResponse, RagUploadResponse, RagQuery, RagQueryResponse


def test_bookbase_valid_creation():
    b = BookBase(title="T", author="A", category="C", file_path="/tmp/file")
    assert b.title == "T" and b.author == "A" and b.category == "C"


def test_book_valid_creation():
    b = Book(id=1, title="T", author="A", category="C", file_path="/tmp/file")
    assert b.id == 1 and b.title == "T"


def test_conversion_and_rag_models():
    conv = ConversionResponse(download_url="/temp_books/x.pdf")
    assert conv.download_url.endswith(".pdf")

    up = RagUploadResponse(book_id="abc", message="ok")
    assert up.book_id == "abc" and up.message == "ok"

    q = RagQuery(query="Hola", book_id="123", mode="balanced")
    assert q.mode in ("balanced", "strict", "open")

    res = RagQueryResponse(response="texto")
    assert isinstance(res.response, str)


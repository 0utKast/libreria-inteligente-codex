import pytest
from backend.schemas import Book, BookBase, ConversionResponse, RagUploadResponse, RagQuery, RagQueryResponse
from typing import Union
from pydantic import ValidationError


def test_bookbase_valid_creation():
    b = BookBase(title="T", author="A", category="C", file_path="/tmp/file")
    assert b.title == "T" and b.author == "A" and b.category == "C" and b.file_path == "/tmp/file"

def test_bookbase_empty_creation():
    with pytest.raises(ValidationError):
        BookBase()

def test_bookbase_invalid_creation():
    with pytest.raises(ValidationError):
        BookBase(title=123, author="A", category="C", file_path="/tmp/file")
    with pytest.raises(ValidationError):
        BookBase(title="T", author=123, category="C", file_path="/tmp/file")
    with pytest.raises(ValidationError):
        BookBase(title="T", author="A", category=123, file_path="/tmp/file")
    with pytest.raises(ValidationError):
        BookBase(title="T", author="A", category="C", file_path=123)
    with pytest.raises(ValidationError):
        BookBase(title="", author="A", category="C", file_path="/tmp/file")
    with pytest.raises(ValidationError):
        BookBase(title="T", author="", category="C", file_path="/tmp/file")
    with pytest.raises(ValidationError):
        BookBase(title="T", author="A", category="", file_path="/tmp/file")
    with pytest.raises(ValidationError):
        BookBase(title="T", author="A", category="C", file_path="")


def test_book_valid_creation():
    b = Book(id=1, title="T", author="A", category="C", file_path="/tmp/file")
    assert b.id == 1 and b.title == "T" and b.author == "A" and b.category == "C" and b.file_path == "/tmp/file"

def test_book_invalid_creation():
    with pytest.raises(ValidationError):
        Book(id="abc", title="T", author="A", category="C", file_path="/tmp/file")
    with pytest.raises(ValidationError):
        Book(id=1, title=123, author="A", category="C", file_path="/tmp/file")
    with pytest.raises(ValidationError):
        Book(id=1, title="T", author=123, category="C", file_path="/tmp/file")
    with pytest.raises(ValidationError):
        Book(id=1, title="T", author="A", category=123, file_path="/tmp/file")
    with pytest.raises(ValidationError):
        Book(id=1, title="T", author="A", category="C", file_path=123)


def test_conversion_and_rag_models():
    conv = ConversionResponse(download_url="/temp_books/x.pdf")
    assert conv.download_url.endswith(".pdf")

    up = RagUploadResponse(book_id="abc", message="ok")
    assert up.book_id == "abc" and up.message == "ok"

    q = RagQuery(query="Hola", book_id="123", mode="balanced")
    assert q.mode in ("balanced", "strict", "open")

    res = RagQueryResponse(response="texto")
    assert isinstance(res.response, str)

    with pytest.raises(ValidationError):
        RagQuery(query=123, book_id="123", mode="balanced")
    with pytest.raises(ValidationError):
        RagQuery(query="Hola", book_id=123, mode="balanced")
    with pytest.raises(ValidationError):
        RagQuery(query="Hola", book_id="123", mode="invalid_mode")
    with pytest.raises(ValidationError):
        RagUploadResponse(book_id=123, message="ok")
    with pytest.raises(ValidationError):
        ConversionResponse(download_url=123)
    with pytest.raises(ValidationError):
        RagQueryResponse(response=123)
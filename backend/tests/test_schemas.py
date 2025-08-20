import pytest
from backend.schemas import Book, BookBase, ConversionResponse, RagUploadResponse, RagQuery, RagQueryResponse

def test_book_creation():
    book = Book(id=1, title="Test Book", author="Test Author", category="Test Category", cover_image_url="test.jpg", file_path="path/to/file")
    assert book.id == 1
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.category == "Test Category"
    assert book.cover_image_url == "test.jpg"
    assert book.file_path == "path/to/file"

def test_book_creation_missing_cover_image():
    book = Book(id=1, title="Test Book", author="Test Author", category="Test Category", file_path="path/to/file")
    assert book.cover_image_url is None

def test_bookbase_creation():
    book_base = BookBase(title="Test Book", author="Test Author", category="Test Category", file_path="path/to/file")
    assert book_base.title == "Test Book"
    assert book_base.author == "Test Author"
    assert book_base.category == "Test Category"
    assert book_base.file_path == "path/to/file"

def test_bookbase_missing_fields():
    with pytest.raises(ValueError):
        BookBase(author="Test Author", category="Test Category", file_path="path/to/file")

def test_conversion_response():
    response = ConversionResponse(download_url="http://test.com/download")
    assert response.download_url == "http://test.com/download"

def test_ragupload_response():
    response = RagUploadResponse(book_id="123", message="Book uploaded successfully")
    assert response.book_id == "123"
    assert response.message == "Book uploaded successfully"

def test_ragquery():
    query = RagQuery(query="Test query", book_id="456", mode="strict")
    assert query.query == "Test query"
    assert query.book_id == "456"
    assert query.mode == "strict"

def test_ragquery_no_mode():
    query = RagQuery(query="Test query", book_id="456")
    assert query.mode is None

def test_ragqueryresponse():
    response = RagQueryResponse(response="Test response")
    assert response.response == "Test response"

def test_book_invalid_title():
    with pytest.raises(ValueError):
        Book(id=1, title="", author="Test Author", category="Test Category", file_path="path/to/file")

def test_book_invalid_author():
    with pytest.raises(ValueError):
        Book(id=1, title="Test Book", author="", category="Test Category", file_path="path/to/file")

def test_book_invalid_category():
    with pytest.raises(ValueError):
        Book(id=1, title="Test Book", author="Test Author", category="", file_path="path/to/file")

def test_book_invalid_filepath():
    with pytest.raises(ValueError):
        Book(id=1, title="Test Book", author="Test Author", category="Test Category", file_path="")

def test_ragquery_invalid_query():
    with pytest.raises(ValueError):
        RagQuery(query="", book_id="456")

def test_ragquery_invalid_book_id():
    with pytest.raises(ValueError):
        RagQuery(query="Test query", book_id="")

def test_ragquery_invalid_mode():
    with pytest.raises(ValueError):
        RagQuery(query="Test query", book_id="456", mode="invalid_mode")
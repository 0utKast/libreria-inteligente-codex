import pytest
import os
from unittest.mock import patch, MagicMock
from backend.rag import (
    get_embedding,
    extract_text_from_pdf,
    extract_text_from_epub,
    extract_text,
    chunk_text,
    _has_index_for_book,
    delete_book_from_rag,
    get_index_count,
    has_index,
    process_book_for_rag,
    estimate_embeddings_for_file,
    estimate_embeddings_for_files,
    query_rag,
)


# Mock external dependencies
@patch("backend.rag.genai")
@patch("backend.rag.load_dotenv")
@patch("backend.rag.chromadb")
def test_get_embedding_with_ai(mock_chromadb, mock_load_dotenv, mock_genai):
    mock_genai.embed_content.return_value = {"embedding": [0.1, 0.2]}
    os.environ["GOOGLE_API_KEY"] = "test_api_key"
    embedding = get_embedding("test text")
    assert embedding == [0.1, 0.2]

@patch("backend.rag.genai")
@patch("backend.rag.load_dotenv")
@patch("backend.rag.chromadb")
def test_get_embedding_without_ai(mock_chromadb, mock_load_dotenv, mock_genai):
    os.environ["DISABLE_AI"] = "1"
    embedding = get_embedding("test text")
    assert embedding == [0.0] * 10
    del os.environ["DISABLE_AI"]


@patch("backend.rag.PdfReader")
def test_extract_text_from_pdf(mock_pdf_reader):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "test text"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader
    text = extract_text_from_pdf("test.pdf")
    assert text == "test text"

@patch("backend.rag.BeautifulSoup")
@patch("backend.rag.ebooklib.epub.read_epub")
def test_extract_text_from_epub(mock_read_epub, mock_beautifulsoup):
    mock_item = MagicMock()
    mock_item.get_type.return_value = "ITEM_DOCUMENT"
    mock_item.get_content.return_value = "<html><body>test text</body></html>"
    mock_book = MagicMock()
    mock_book.get_items.return_value = [mock_item]
    mock_read_epub.return_value = mock_book
    mock_soup = MagicMock()
    mock_soup.get_text.return_value = "test text"
    mock_beautifulsoup.return_value = mock_soup
    text = extract_text_from_epub("test.epub")
    assert text == "test text"

def test_extract_text_unsupported_type():
    with pytest.raises(ValueError):
        extract_text("test.txt")

def test_chunk_text():
    text = "This is a test text." * 100
    chunks = chunk_text(text, max_tokens=10)
    assert len(chunks) > 1

def test_chunk_text_empty():
    assert chunk_text("") == []

@patch("backend.rag._collection")
def test_has_index_for_book(mock_collection):
    mock_collection.get.return_value = {"ids": ["id1"]}
    assert _has_index_for_book("test_book_id")
    mock_collection.get.return_value = {"ids": []}
    assert not _has_index_for_book("test_book_id")
    mock_collection.get.side_effect = Exception("Test Exception")
    assert not _has_index_for_book("test_book_id")


@patch("backend.rag._collection")
def test_delete_book_from_rag(mock_collection):
    delete_book_from_rag("test_book_id")
    mock_collection.delete.assert_called_once_with(where={"book_id": "test_book_id"})
    mock_collection.delete.side_effect = Exception("Test Exception")
    delete_book_from_rag("test_book_id")


@patch("backend.rag._collection")
def test_get_index_count(mock_collection):
    mock_collection.get.return_value = {"ids": ["id1", "id2"]}
    assert get_index_count("test_book_id") == 2
    mock_collection.get.return_value = {"ids": []}
    assert get_index_count("test_book_id") == 0
    mock_collection.get.side_effect = Exception("Test Exception")
    assert get_index_count("test_book_id") == 0


@patch("backend.rag._collection")
@patch("backend.rag.get_embedding")
def test_process_book_for_rag(mock_get_embedding, mock_collection):
    mock_get_embedding.return_value = [0.1, 0.2]
    mock_collection.add = MagicMock()
    process_book_for_rag("test.pdf", "test_book_id")
    mock_collection.add.assert_called()

@patch("backend.rag.extract_text")
def test_estimate_embeddings_for_file(mock_extract_text):
    mock_extract_text.return_value = "test text"
    result = estimate_embeddings_for_file("test.pdf")
    assert result["tokens"] > 0
    assert result["chunks"] > 0
    mock_extract_text.return_value = ""
    result = estimate_embeddings_for_file("test.pdf")
    assert result["tokens"] == 0
    assert result["chunks"] == 0

@patch("backend.rag.estimate_embeddings_for_file")
def test_estimate_embeddings_for_files(mock_estimate_embeddings_for_file):
    mock_estimate_embeddings_for_file.side_effect = [{"tokens": 100, "chunks": 1}, {"tokens": 200, "chunks": 2}]
    result = estimate_embeddings_for_files(["file1.pdf", "file2.pdf"])
    assert result["tokens"] == 300
    assert result["chunks"] == 3
    assert result["files"] == 2
    mock_estimate_embeddings_for_file.side_effect = Exception("Test Exception")
    result = estimate_embeddings_for_files(["file1.pdf"])
    assert result["files"] == 0


@patch("backend.rag._collection")
@patch("backend.rag.get_embedding")
@patch("backend.rag.genai.GenerativeModel")
def test_query_rag(mock_gen_model, mock_get_embedding, mock_collection):
    mock_get_embedding.return_value = [0.1, 0.2]
    mock_collection.query.return_value = {"documents": [["doc1", "doc2"]]}
    mock_model = MagicMock()
    mock_model.generate_content.return_value = MagicMock(text="test response")
    mock_gen_model.return_value = mock_model
    response = query_rag("test query", "test_book_id")
    assert "test response" in response
    os.environ["DISABLE_AI"] = "1"
    response = query_rag("test query", "test_book_id")
    assert "[IA deshabilitada]" in response
    del os.environ["DISABLE_AI"]
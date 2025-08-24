from fastapi.testclient import TestClient
import pytest
import types
from unittest.mock import patch

from backend import main as app_module


client = TestClient(app_module.app)


def test_books_count_endpoint_success():
    with patch.object(app_module.crud, "get_books_count", return_value=42) as mock_get_books_count:
        r = client.get("/books/count")
        assert r.status_code == 200
        assert r.json() == 42
        mock_get_books_count.assert_called_once()


def test_books_count_endpoint_failure():
    with patch.object(app_module.crud, "get_books_count", side_effect=Exception("Database error")):
        r = client.get("/books/count")
        assert r.status_code == 500


def test_books_list_endpoint_success():
    with patch.object(app_module.crud, "get_books", return_value=[]) as mock_get_books:
        r = client.get("/books/")
        assert r.status_code == 200
        assert r.json() == []
        mock_get_books.assert_called_once_with(None, None, None, None)


def test_books_list_endpoint_with_parameters():
    mock_data = [{"title": "Book 1"}]
    with patch.object(app_module.crud, "get_books", return_value=mock_data) as mock_get_books:
        r = client.get("/books/?category=test&search=query&author=author")
        assert r.status_code == 200
        assert r.json() == mock_data
        mock_get_books.assert_called_once_with(None, "test", "query", "author")


def test_books_list_endpoint_failure():
    with patch.object(app_module.crud, "get_books", side_effect=Exception("Database error")):
        r = client.get("/books/")
        assert r.status_code == 500


def test_rag_status_endpoint_success():
    with patch.object(app_module.rag, "get_index_count", return_value=0) as mock_get_index_count:
        r = client.get("/rag/status/1")
        assert r.status_code == 200
        data = r.json()
        assert data["book_id"] == "1" and data["indexed"] is False
        mock_get_index_count.assert_called_once_with("1")


def test_rag_status_endpoint_failure():
    with patch.object(app_module.rag, "get_index_count", side_effect=Exception("Index error")):
        r = client.get("/rag/status/1")
        assert r.status_code == 500


def test_rag_status_endpoint_invalid_book_id():
    with patch.object(app_module.rag, "get_index_count", return_value=0):
        r = client.get("/rag/status/abc")
        assert r.status_code == 422 # or 500 depending on your error handling


@pytest.mark.asyncio
async def test_rag_query_endpoint_success():
    async def fake_query_rag(query, book_id, mode="balanced", metadata=None, library=None):
        return "ok"

    with patch.object(app_module.rag, "query_rag", new=fake_query_rag) as mock_query_rag:
        payload = {"query": "hola", "book_id": "1", "mode": "strict"}
        r = client.post("/rag/query/", json=payload)
        assert r.status_code == 200
        assert r.json() == {"response": "ok"}
        await mock_query_rag.assert_called_once_with("hola", "1", "strict")


@pytest.mark.asyncio
async def test_rag_query_endpoint_failure():
    async def fake_query_rag(query, book_id, mode="balanced", metadata=None, library=None):
        raise Exception("RAG query error")

    with patch.object(app_module.rag, "query_rag", new=fake_query_rag):
        payload = {"query": "hola", "book_id": "1", "mode": "strict"}
        r = client.post("/rag/query/", json=payload)
        assert r.status_code == 500


@pytest.mark.asyncio
async def test_rag_query_endpoint_missing_parameters():
    async def fake_query_rag(query, book_id, mode="balanced", metadata=None, library=None):
        return "ok"

    with patch.object(app_module.rag, "query_rag", new=fake_query_rag):
        payload = {"query": "hola"}
        r = client.post("/rag/query/", json=payload)
        assert r.status_code == 422 # or 500 depending on your error handling
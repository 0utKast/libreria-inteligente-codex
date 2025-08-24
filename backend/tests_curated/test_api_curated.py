from fastapi.testclient import TestClient


from backend import main as app_module


client = TestClient(app_module.app)


def test_books_count_endpoint(monkeypatch):
    monkeypatch.setattr(app_module.crud, "get_books_count", lambda db: 42)
    r = client.get("/books/count")
    assert r.status_code == 200
    assert r.json() == 42


def test_books_list_endpoint(monkeypatch):
    monkeypatch.setattr(app_module.crud, "get_books", lambda db, category=None, search=None, author=None: [])
    r = client.get("/books/")
    assert r.status_code == 200
    assert r.json() == []


def test_rag_status_endpoint(monkeypatch):
    monkeypatch.setattr(app_module.rag, "get_index_count", lambda book_id: 0)
    r = client.get("/rag/status/1")
    assert r.status_code == 200
    data = r.json()
    assert data["book_id"] == "1" and data["indexed"] is False


def test_rag_query_endpoint(monkeypatch):
    async def fake_query_rag(query, book_id, mode="balanced", metadata=None, library=None):
        return "ok"

    monkeypatch.setattr(app_module.rag, "query_rag", fake_query_rag)
    payload = {"query": "hola", "book_id": "1", "mode": "strict"}
    r = client.post("/rag/query/", json=payload)
    assert r.status_code == 200
    assert r.json() == {"response": "ok"}


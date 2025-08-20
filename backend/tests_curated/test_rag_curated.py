import os

from backend import rag


def test_get_embedding_disabled_ai(monkeypatch):
    monkeypatch.setenv("DISABLE_AI", "1")
    emb = rag.get_embedding("hola")
    assert isinstance(emb, list) and len(emb) == 10


def test_has_index_false_for_random_id(monkeypatch, tmp_path):
    # Use a temporary Chroma path to isolate CI runs
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "rag_index"))
    assert rag.has_index("nonexistent-book") is False


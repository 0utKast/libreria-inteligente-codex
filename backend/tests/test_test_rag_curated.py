import os
import pytest
from unittest.mock import patch, Mock

from backend import rag


def test_get_embedding_disabled_ai_empty_string():
    with patch.dict(os.environ, {"DISABLE_AI": "1"}):
        emb = rag.get_embedding("")
        assert isinstance(emb, list) and len(emb) == 10

def test_get_embedding_disabled_ai_none():
    with patch.dict(os.environ, {"DISABLE_AI": "1"}):
        emb = rag.get_embedding(None)
        assert isinstance(emb, list) and len(emb) == 10

def test_get_embedding_enabled_ai(monkeypatch):
    monkeypatch.delenv("DISABLE_AI", raising=False)
    with patch('backend.rag.openai.Embedding.create', return_value=Mock(data=[1]*10)):
        emb = rag.get_embedding("hola")
        assert isinstance(emb, list) and len(emb) == 10

def test_get_embedding_enabled_ai_error(monkeypatch):
    monkeypatch.delenv("DISABLE_AI", raising=False)
    with patch('backend.rag.openai.Embedding.create', side_effect=Exception("API Error")):
        with pytest.raises(Exception) as e:
            rag.get_embedding("hola")
        assert "API Error" in str(e.value)


def test_has_index_true(monkeypatch, tmp_path):
    index_path = tmp_path / "rag_index"
    index_path.mkdir()
    (index_path / "some_file.bin").touch()
    monkeypatch.setenv("CHROMA_PATH", str(index_path))
    assert rag.has_index("some_id") is True

def test_has_index_false_empty_path(monkeypatch, tmp_path):
    index_path = tmp_path / "rag_index"
    index_path.mkdir()
    monkeypatch.setenv("CHROMA_PATH", str(index_path))
    assert rag.has_index("some_id") is False


def test_has_index_path_error(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "nonexistent_dir"))
    assert rag.has_index("some_id") is False

def test_has_index_none_path(monkeypatch):
    monkeypatch.delenv("CHROMA_PATH", raising=False)
    with pytest.raises(FileNotFoundError):
      rag.has_index("some_id")

def test_has_index_invalid_id():
    with pytest.raises(TypeError):
        rag.has_index(123)

def test_has_index_empty_id():
    with pytest.raises(ValueError):
        rag.has_index("")
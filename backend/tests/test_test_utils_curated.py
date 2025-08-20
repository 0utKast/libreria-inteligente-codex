import os
import pytest

from unittest.mock import patch, MagicMock

from backend import utils


def test_configure_genai_raises_without_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        utils.configure_genai()


def test_configure_genai_with_gemini_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    with patch('backend.utils.genai.configure') as mock_configure:
        utils.configure_genai()
        mock_configure.assert_called_once_with(api_key="k")


def test_configure_genai_with_google_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "g")
    with patch('backend.utils.genai.configure') as mock_configure:
        utils.configure_genai()
        mock_configure.assert_called_once_with(api_key="g")


def test_configure_genai_with_both_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_API_KEY", "g")
    with patch('backend.utils.genai.configure') as mock_configure:
        utils.configure_genai()
        mock_configure.assert_called_once_with(api_key="k")


def test_configure_genai_with_empty_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    with pytest.raises(ValueError):
        utils.configure_genai()


def test_configure_genai_with_invalid_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "  ")
    monkeypatch.setenv("GOOGLE_API_KEY", "   ")
    with pytest.raises(ValueError):
        utils.configure_genai()

def test_configure_genai_with_None_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", None)
    monkeypatch.setenv("GOOGLE_API_KEY", None)
    with pytest.raises(ValueError):
        utils.configure_genai()

@patch('backend.utils.genai.configure')
def test_configure_genai_exception_handling(mock_configure):
    mock_configure.side_effect = Exception("API error")
    with pytest.raises(Exception) as e:
        utils.configure_genai()
    assert str(e.value) == "API error"
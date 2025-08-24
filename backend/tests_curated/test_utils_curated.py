
import pytest

from backend import utils


def test_configure_genai_raises_without_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        utils.configure_genai()


def test_configure_genai_with_gemini_key(monkeypatch):
    called = {"configured": False}

    def fake_configure(api_key=None):
        if api_key == "k":
            called["configured"] = True

    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_API_KEY", "")

    # Patch genai.configure in utils module
    import backend.utils as u
    u.genai.configure = fake_configure  # type: ignore

    utils.configure_genai()
    assert called["configured"] is True


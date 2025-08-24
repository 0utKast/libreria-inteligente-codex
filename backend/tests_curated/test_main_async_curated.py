import importlib

import pytest


@pytest.mark.asyncio
async def test_analyze_with_gemini_success(monkeypatch):
    # Preparar entorno para que AI_ENABLED sea True al importar el módulo
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("DISABLE_AI", "0")

    import backend.main as main
    importlib.reload(main)

    class FakeModel:
        def __init__(self, *_args, **_kwargs):
            pass

        async def generate_content_async(self, prompt):
            class R:
                text = '{"title": "Titulo", "author": "Autor", "category": "Cat"}'

            return R()

    # Parchear la clase del SDK
    main.genai.GenerativeModel = FakeModel  # type: ignore

    res = await main.analyze_with_gemini("texto")
    assert res == {"title": "Titulo", "author": "Autor", "category": "Cat"}


@pytest.mark.asyncio
async def test_analyze_with_gemini_error_path(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("DISABLE_AI", "0")

    import backend.main as main
    importlib.reload(main)

    class FakeModel:
        def __init__(self, *_args, **_kwargs):
            pass

        async def generate_content_async(self, prompt):  # noqa: D401
            raise RuntimeError("boom")

    main.genai.GenerativeModel = FakeModel  # type: ignore

    res = await main.analyze_with_gemini("texto")
    assert res == {
        "title": "Error de IA",
        "author": "Error de IA",
        "category": "Error de IA",
    }

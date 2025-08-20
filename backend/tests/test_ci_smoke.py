def test_ci_smoke_imports():
    # Import a few modules to ensure they load in CI
    import backend.schemas as schemas  # noqa: F401
    import backend.rag as rag  # noqa: F401
    assert True

def test_ci_true():
    assert 1 + 1 == 2


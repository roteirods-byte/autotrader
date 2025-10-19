def test_imports():
    import ops.db, ops.models, engine.signals  # noqa: F401
    assert True

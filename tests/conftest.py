import pytest

from app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A test client for an app that uses a temporary database."""
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()

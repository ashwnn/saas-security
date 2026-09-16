import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def load_app(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_health(tmp_path, monkeypatch):
    client = load_app(tmp_path, monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_normal_customer_lookup(tmp_path, monkeypatch):
    client = load_app(tmp_path, monkeypatch)
    response = client.get("/invoices?customer=acme")
    assert response.status_code == 200
    assert {row["customer"] for row in response.get_json()} == {"acme"}

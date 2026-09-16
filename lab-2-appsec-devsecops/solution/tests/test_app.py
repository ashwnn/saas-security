import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def load_app(tmp_path, monkeypatch, admin_token=None):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    if admin_token is None:
        monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    else:
        monkeypatch.setenv("ADMIN_TOKEN", admin_token)
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_health(tmp_path, monkeypatch):
    client = load_app(tmp_path, monkeypatch)
    assert client.get("/health").get_json() == {"status": "ok"}


def test_normal_customer_lookup(tmp_path, monkeypatch):
    client = load_app(tmp_path, monkeypatch)
    rows = client.get("/invoices?customer=acme").get_json()
    assert len(rows) == 2
    assert {row["customer"] for row in rows} == {"acme"}


def test_injection_does_not_cross_customer_boundary(tmp_path, monkeypatch):
    client = load_app(tmp_path, monkeypatch)
    response = client.get("/invoices", query_string={"customer": "' OR 1=1 --"})
    assert response.status_code == 200
    assert response.get_json() == []


def test_admin_export_fails_closed_without_secret(tmp_path, monkeypatch):
    client = load_app(tmp_path, monkeypatch)
    response = client.get("/admin/export", headers={"X-API-Key": "anything"})
    assert response.status_code == 401
    assert response.get_json() == {"error": "unauthorized"}


def test_admin_export_rejects_invalid_secret(tmp_path, monkeypatch):
    client = load_app(tmp_path, monkeypatch, admin_token="correct-horse-battery-staple")
    response = client.get("/admin/export", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
    assert "correct-horse" not in response.get_data(as_text=True)

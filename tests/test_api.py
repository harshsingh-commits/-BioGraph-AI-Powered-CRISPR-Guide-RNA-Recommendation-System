import os

os.environ["BIOGRAPH_JWT_SECRET"] = "test-secret"
os.environ["BIOGRAPH_ALLOW_DEV_USERS"] = "true"

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def token(username="researcher", password="researcher"):
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_auth_and_role_protection():
    assert client.get("/health").status_code == 200
    assert client.post("/evaluate", json={"predictions": [], "labels": []}).status_code == 401
    assert (
        client.post(
            "/evaluate",
            json={"predictions": [], "labels": []},
            headers={"Authorization": f"Bearer {token()}"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/evaluate",
            json={"predictions": [], "labels": []},
            headers={"Authorization": f"Bearer {token('reviewer', 'reviewer')}"},
        ).status_code
        == 200
    )


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "biograph_analysis_total" in response.text

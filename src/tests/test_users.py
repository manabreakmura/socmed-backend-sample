from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_users():
    response = client.get("/api/v1/users")
    assert response.status_code == 401

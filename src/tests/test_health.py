from src.config.settings import settings


def test_startup(client):
    response = client.get("/")
    assert hasattr(response, "status_code")


def test_cors(client):
    for URL in settings.FRONTEND_URL.split(","):
        response = client.options("/docs", headers={"Origin": URL})
        assert response.headers.get("access-control-allow-origin") == URL


def test_debug(client):
    response = client.get("/docs")
    if settings.DEBUG:
        assert response.status_code == 200

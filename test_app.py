from fastapi.testclient import TestClient
from main import app


def test_get_users():
    client = TestClient(app)
    response = client.get("/user/")
    assert response.status_code == 200


def test_fix_posts():
    client = TestClient(app)
    response = client.get("/posts/fix/")
    assert response.status_code == 200



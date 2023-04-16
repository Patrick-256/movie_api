from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_line():
    response = client.get("/lines/50")
    assert response.status_code == 200

    with open("test/lines/50.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)
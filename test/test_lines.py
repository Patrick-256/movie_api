from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_line():
    response = client.get("/lines/50")
    assert response.status_code == 200

    with open("test/lines/50.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_list_line_filter():
    response = client.get("/lines/?spoken_by=Patrick&line_text=miss&offset=1")
    assert response.status_code == 200

    with open("test/lines/lines-spoken_by=Patrick&line_text=miss&offset=1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_movie_lines():
    response = client.get("movie_lines/?movie_title=the%20hudsucker%20proxy&limit=10&offset=10")
    assert response.status_code == 200

    with open("test/lines/movie_lines-movie_title=the%20hudsucker%20proxy&limit=10&offset=10.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)
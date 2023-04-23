from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

# def test_add_conversation():
#     client.post(
#         "/movies/525/conversations",
#         headers={},
#         json={
#             "character_1_id": 7770,
#             "character_2_id": 7761,
#             "lines": [
#                 {
#                 "character_id": 7770,
#                 "line_text": "Hello Southpark!"
#                 }
#             ]
#         })
    
#     response = client.get("/lines/?spoken_by=Patrick&line_text=miss&offset=1")
#     assert response.status_code == 200

#     with open("test/lines/lines-spoken_by=Patrick&line_text=miss&offset=1.json", encoding="utf-8") as f:
#         assert response.json() == json.load(f)
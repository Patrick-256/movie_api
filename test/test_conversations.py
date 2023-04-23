from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

#change the unique number each time test cases need to be run
uniqueNumber = "3"

def test_add_conversation():
    client.post(
        "/movies/525/conversations",
        headers={},
        json={
            "character_1_id": 7770,
            "character_2_id": 7761,
            "lines": [
                {
                "character_id": 7770,
                "line_text": "Hello Southpark! this is for convoTestcase15"
                },
                {
                "character_id": 7761,
                "line_text": "What the hell is convoTestcase15"
                }
            ]
        })
    
    response = client.get("/lines/?line_text=convoTestcase15")
    assert response.status_code == 200
    # theJSONresponse = response.json()
    # print(theJSONresponse)
    # for line in theJSONresponse:
    #     del line["line_id"]
    # print(theJSONresponse)
    
    # assert theJSONresponse == [
    #     {
    #     "spoken_by": "KYLE",
    #     "movie": "south park: bigger longer & uncut",
    #     "spoken_to": "STAN",
    #     "line_text": "Hello Southpark! this is for convoTestcase14",
    #     },
    #     {
    #     "spoken_by": "STAN",
    #     "movie": "south park: bigger longer & uncut",
    #     "spoken_to": "KYLE",
    #     "line_text": "What the hell is convoTestcase14",
    #     },
    # ] 

def test_add_conversation1():
    client.post(
        "/movies/267/conversations",
        headers={},
        json={
            "character_1_id": 4020,
            "character_2_id": 4029,
            "lines": [
                {
                "character_id": 4020,
                "line_text": "hey hows that assignment going?"
                },
                {
                "character_id": 4029,
                "line_text": "going alright, ive only attempted to set up the test cases 17 times"
                }
            ]
        })
    
    response = client.get("/lines/?line_text=attempted to set up the test cases 17 times")
    assert response.status_code == 200
    assert response.json != []
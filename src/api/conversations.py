from fastapi import APIRouter
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime


# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """

    # TODO: Remove the following two lines. This is just a placeholder to show
    # how you could implement persistent storage.

    # print(conversation)
    response = {"my placeholder response"}

    return response

    # #Step 1: ensure that both characters are part of the movie
    # if db.characters[conversation["character_1_id"]][1] == movie_id and db.characters[conversation["character_2_id"]][1] == movie_id and conversation["character_1_id"] != conversation["character_2_id"]:
    #     #both characters are in the movie
    #     print("both characters are in the movie")
    #     response = {"my placeholder response"}

    #     #Step 2: go through the lines and check that the speakers match the characters provided
    # else:
    #     raise HTTPException(status_code=404, detail="One or more characters not found in the referenced movie")

    # return response

from fastapi import APIRouter, HTTPException
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

# def addConversationToCSV():



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
    response = {"my null response ._."}

    #Step 1: ensure that both characters are part of the movie
    if db.characters[conversation.character_1_id][1] == movie_id and db.characters[conversation.character_2_id][1] == movie_id and conversation.character_1_id != conversation.character_2_id:
        #both characters are in the movie
        print("both characters are in the movie")
        response = {"made it to step 1 :D"}

        print(conversation)

        #Step 2: go through the lines and check that the speakers match the characters provided
        # for line in conversation.lines:
        #     if conversation.lines[line].character_id != conversation.character_1_id and conversation.lines[line].character_id != conversation.character_2_id:
        #         raise HTTPException(status_code=404, detail="step 2 failure: a line is spoken by a character not in the conversation")
        
        for index, line in enumerate(conversation.lines):
            if line.character_id != conversation.character_1_id and line.character_id != conversation.character_2_id:
                raise HTTPException(status_code=400, detail="step 2 failure:a line is spoken by a character not in the conversation")
        
        #Step 3: add the conversation to the database
        response = {"made it to step 3 :D"}

        #break out into lines and conversations
        #determine highest convo ID
        
        #Test writing to movie_conversations_log.csv
        print(db.logs)
        db.logs.append({'post_call_time': '2023-04-21 14:44:31', 'movie_id_added_to': 525})
        print(db.logs)

        db.upload_new_log()


    else:
        raise HTTPException(status_code=404, detail="One or more characters not found in the referenced movie")

    return response
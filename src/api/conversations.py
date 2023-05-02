from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlalchemy
from sqlalchemy import create_engine


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

    print(conversation)

    

    #Step 1: Query the database to make sure the characters are in the movie
    if conversation.character_1_id != conversation.character_2_id:
        character1_query = (
            sqlalchemy.select(
                db.characters.c.character_id,
                db.characters.c.movie_id
            )
            .where(db.characters.c.character_id == conversation.character_1_id)
        )
        character2_query = (
            sqlalchemy.select(
                db.characters.c.character_id,
                db.characters.c.movie_id
            )
            .where(db.characters.c.character_id == conversation.character_2_id)
        )

        with db.engine.connect() as conn:
            character1_result = conn.execute(character1_query)
            character1 = character1_result.fetchone()
            character2_result = conn.execute(character2_query)
            character2 = character2_result.fetchone()

            if character1 is None or character2 is None:
                return {"one of the characters not found!"}

            if character1.movie_id != movie_id:
                return {"character1 is not in this movie!"}
            if character2.movie_id != movie_id:
                return {"character2 is not in this movie!"}
    else:
        return {"convesation character ids 1 and 2 are the same! -_-"}
    
    
    #Step 2: check that each line in the conversation is spoken by the provided characters
    for line in conversation.lines:
        if line.character_id != conversation.character_1_id and line.character_id != conversation.character_2_id:
            raise HTTPException(status_code=400, detail="step 2 failure:a line is spoken by a character not in the conversation")

    
    #Step 3: Add this conversation to the database
    #Step 3-1: Find out what conversation ID to assign
    lastConvoId_query = sqlalchemy.select(db.conversations.c.conversation_id).order_by(sqlalchemy.desc(db.conversations.c.conversation_id))

    with db.engine.connect() as conn:
        lastConvoId_result = conn.execute(lastConvoId_query)
        
        lastConvoId = lastConvoId_result.fetchone()
        # print("the last convo is is:")
        # print(lastConvoId.c.conversation_id)
        # return {"lastConvoId":lastConvoId.conversation_id}
    
    #Step 3-2: Add the new conversation to the conversation table
    insert_statment = sqlalchemy.insert(db.conversations).values(
        conversation_id = lastConvoId[0]+1,
        character1_id = conversation.character_1_id,
        character2_id = conversation.character_2_id,
        movie_id = movie_id
    )
    with db.engine.begin() as conn:
        addConvoResult = conn.execute(insert_statment)
        print(addConvoResult)

    #Step 3-3: Add the lines to the lines database
    lastLineId_query = sqlalchemy.select(db.lines.c.line_id).order_by(sqlalchemy.desc(db.lines.c.line_id))
    with db.engine.connect() as conn:
        lastLineId_result = conn.execute(lastLineId_query)
        lastLineId = lastLineId_result.fetchone()

    for i in range(len(conversation.lines)):
        lines_insert_stmt = sqlalchemy.insert(db.lines).values(
            line_id = lastLineId[0]+1+i,
            character_id = conversation.lines[i].character_id,
            movie_id = movie_id,
            conversation_id = lastConvoId[0]+1,
            line_sort = i,
            line_text = conversation.lines[i].line_text
        )
        with db.engine.begin() as conn:
            addLineResult = conn.execute(lines_insert_stmt)
            print(addLineResult)
    return {"Added conversation and lines to database!"}
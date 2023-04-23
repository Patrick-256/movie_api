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
        
        #Step 3-1: Add log entry to movie_conversations_log.csv file
        # get the current date and time
        now = datetime.now()

        # format the date and time as a string
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        print(db.logs)
        db.logs.append({'post_call_time': date_time_str, 'movie_id_added_to': 525})
        print(db.logs)

        db.upload_new_log()

        #Step 3-2: Add conversation to conversations.csv file
        #find out what number to give conversation id
        last_convo_key = list(db.conversations.keys())[-1]
        db.conversationsCSV.append({"conversation_id":last_convo_key+1, "character1_id":conversation.character_1_id, "character2_id":conversation.character_2_id, "movie_id":movie_id})

        key = last_convo_key+1
        values = [conversation.character_1_id,conversation.character_2_id,movie_id]
        db.conversations[key] = values

        db.upload_new_conversation()

        #Step 3-3 Add the lines to the lines.csv file
        last_line_key = list(db.lines.keys())[-1]
        for i in range(len(conversation.lines)):
            db.linesCSV.append({"line_id":last_line_key+1+i, "character_id":conversation.lines[i].character_id, "movie_id":movie_id, "conversation_id":last_convo_key+1, "line_sort":i+1, "line_text":conversation.lines[i].line_text})

            #Also add the lines to the dictionary the other endpoints use
            key = last_line_key+1+i
            values = [conversation.lines[i].character_id,movie_id,last_convo_key+1,i+1,conversation.lines[i].line_text]
            db.lines[key] = values
        db.upload_new_lines()
        db.buildVerboseLines()

        response = last_convo_key+1

    else:
        raise HTTPException(status_code=404, detail="One or more characters not found in the referenced movie")

    return response
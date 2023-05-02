from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import sqlalchemy

router = APIRouter()

@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """

    characters_Query = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name.label("character"),
            db.characters.c.movie_id,
            db.characters.c.gender,
            # db.characters.c.age,
            db.movies.c.title.label("movie"),
        )  
        .select_from(
            db.characters
            .join(db.movies, db.characters.c.movie_id == db.movies.c.movie_id)
        ) 
        .where(db.characters.c.character_id == id)
    )

    top_conversations_Query = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name.label("character"),
            db.characters.c.gender,
            sqlalchemy.func.count(db.lines.c.conversation_id).label("num_lines_convoID")
        )
        .select_from(
            db.conversations
            .join(db.lines, db.conversations.c.conversation_id == db.lines.c.conversation_id)
            .join(db.characters, db.lines.c.character_id == db.characters.c.character_id)
        )
        .where(
            sqlalchemy.or_(
                db.conversations.c.character1_id == id,
                db.conversations.c.character2_id == id
            )
        )
        .group_by(db.conversations.c.conversation_id, db.characters.c.character_id, db.characters.c.name)
        .order_by(sqlalchemy.desc("num_lines_convoID"))
        .limit(5)
    )

    top1_conversations_query = (
        sqlalchemy.select(
            db.conversations.c.conversation_id,
            db.conversations.c.character1_id,
            db.conversations.c.character2_id,
            db.characters.c.name.label("character1_name"),
            db.characters.c.name.label("character2_name"),
            sqlalchemy.func.count(db.lines.c.conversation_id).label("num_lines_convoID")
        )   
        .select_from(
            db.conversations
            .join(db.lines, db.conversations.c.conversation_id == db.lines.c.conversation_id)
            .join(db.characters, db.lines.c.character_id == db.characters.c.character_id)
        )
        .where(
            sqlalchemy.or_(
                db.conversations.c.character1_id == id,
                db.conversations.c.character2_id == id
            )
        )
        .group_by(db.conversations.c.conversation_id, db.characters.c.character_id, db.characters.c.name)
        .order_by(sqlalchemy.desc("num_lines_convoID"))
    )

    with db.engine.connect() as conn:
        char_result = conn.execute(characters_Query)
        char = char_result.fetchone()

        convo_result = conn.execute(top_conversations_Query)
        top_convos = []
        for row in convo_result:
            top_convos.append({
                "character_id":row.character_id,
                "character":row.character,
                "gender":row.gender,
                "number_of_lines_together":row.num_lines_convoID,
            })
        convo1_result = conn.execute(top1_conversations_query)
        top1_convos = []
        char_convos = {
                "character_id": None,
                "character": "placeholder",
                "gender": "placeholder",
                "number_of_lines_together": 0
            }
        for row in convo1_result:
            
            # char_convos = {
            #     "conversation_id":row.conversation_id,
            #     "character1_id":row.character1_id,
            #     "character2_id":row.character2_id,
            #     "character1_name":row.character1_name,
            #     "character2_name":row.character2_name,
            #     "num_lines_convoID":row.num_lines_convoID,
            # }

            #find out what character was talked to
            characterTalkedToId = None
            if row.character1_id == id:
                characterTalkedToId = row.character2_id
            else:
                characterTalkedToId = row.character1_id

            if char_convos["character_id"] == characterTalkedToId:
                char_convos["number_of_lines_together"] += row.num_lines_convoID
            elif char_convos["character_id"] is None:
                char_convos["character_id"] = characterTalkedToId
                char_convos["number_of_lines_together"] = row.num_lines_convoID
            else:
                top1_convos.append(char_convos)
                char_convos["character_id"] = characterTalkedToId
                char_convos["number_of_lines_together"] = row.num_lines_convoID


        if char is None:
            raise HTTPException(status_code=404, detail="character not found.")
        
        res_json = {
            "character_id": char.character_id ,
            "character": char.character,
            "movie": char.movie,
            "gender": char.gender,
            #"top_conversations":top_convos,
            "top1_convos":top1_convos,
        }
    return res_json



class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"



@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    if sort is character_sort_options.character:
        order_by = db.characters.c.name
    elif sort is character_sort_options.movie:
        order_by = db.movies.c.title
    elif sort is character_sort_options.number_of_lines:
        order_by = sqlalchemy.desc("num_lines")
    else:
        assert False

    characters_query = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name.label("character"),
            db.characters.c.movie_id,
            db.movies.c.title.label("movie"),
            sqlalchemy.func.count(db.lines.c.character_id == db.characters.c.character_id).label("num_lines")
        )
        .select_from(db.characters.join(db.lines).join(db.movies))
        .limit(limit)
        .offset(offset)
        .group_by(db.characters.c.character_id, db.characters.c.name, db.movies.c.title)
        .order_by(order_by, db.characters.c.name)
    )

    # filter only if name parameter is passed
    if name != "":
        characters_query = characters_query.where(db.characters.c.name.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(characters_query)
        res_json = []
        for row in result:
            res_json.append({
                "character_id": row.character_id,
                "character": row.character,
                # "movie_id":row.movie_id,
                "movie": row.movie,
                "number_of_lines": row.num_lines
            })
        return res_json
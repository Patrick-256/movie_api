from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
import sqlalchemy
from sqlalchemy import outerjoin

router = APIRouter()

@router.get("/lines/{id}", tags=["lines"])
def get_line(id: int):
    """
    This endpoint returns a single line by its identifier. For each line
    it returns:
    * `line`: the internal id of the character. Can be used to query the
      `/line/{line_id}` endpoint.
    * `spoken_by`: The name of the character who spoke the line.
    * `movie`: The movie the line is from.
    * `spoken_to`: The name of the character who the line was spoken to.
    * `line_text`: The content of the line
    """

    line_Query = (
        sqlalchemy.select(
            db.lines.c.line_id,
            db.lines.c.character_id,
            db.lines.c.movie_id,
            db.lines.c.conversation_id,
            db.lines.c.line_text,
            db.movies.c.title.label("movie"),
            db.characters.c.name.label("spoken_by"),
            db.conversations.c.character1_id.label("convo_char1"),
            db.conversations.c.character2_id.label("convo_char2"),
            
        )
        .select_from(
            db.lines
            .join(db.characters, db.lines.c.character_id == db.characters.c.character_id)
            .join(db.movies, db.lines.c.movie_id == db.movies.c.movie_id)
            .join(db.conversations, db.lines.c.conversation_id == db.conversations.c.conversation_id)
        )
        .where(db.lines.c.line_id == id)
    )



    with db.engine.connect() as conn:
        line_result = conn.execute(line_Query)
        line = line_result.fetchone()

        spoken_to_character_id = None
        #determine the character spoken_to id
        if line.character_id == line.convo_char1:
            spoken_to_character_id = line.convo_char2
        else:
            spoken_to_character_id = line.convo_char1

        spoken_to_character_Query = (
            sqlalchemy.select(
                db.characters.c.name
            )
            .where(db.characters.c.character_id == spoken_to_character_id)
        )
        spoken_to_char_result = conn.execute(spoken_to_character_Query)
        spoken_to_char = spoken_to_char_result.fetchone()

        if line is None:
            raise HTTPException(status_code=404, detail="line not found.")
        
        res_json = {
            "line_id": line.line_id,
            # "char_id": line.character_id,
            "spoken_by": line.spoken_by,
            "movie": line.movie,
            # "spoken_to?_1": line.convo_char1,
            # "spoken_to?_2": line.convo_char2,
            "spoken_to": spoken_to_char.name,
            "line_text": line.line_text,
        }

        return res_json

class line_sort_options(str, Enum):
    spoken_by = "spoken_by"
    movie = "movie"
    line_text = "line_text"

@router.get("/lines/", tags=["lines"])
def list_lines(
    spoken_by: str = "",
    line_text: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: line_sort_options = line_sort_options.spoken_by,
):
    """
    This endpoint returns a list of lines. For each line
    it returns:
    * `line`: the internal id of the character. Can be used to query the
      `/line/{line_id}` endpoint.
    * `spoken_by`: The name of the character who spoke the line.
    * `movie`: The movie the line is from.
    * `spoken_to`: The name of the character who the line was spoken to.
    * `line_text`: The content of the line

    You can filter for lines whose chararacter's spoken by's name contains a string by using the
    `spoken_by` query parameter.
    You can also filter for lines whose contents contains a string by using the
    `line_contains` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `spoken_by` - Sort by spoken by character's name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `line_text` - Sort by line text alphabetically.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    if sort is line_sort_options.spoken_by:
        order_by = (db.lines.c.character_id == db.characters.c.character_id)
    elif sort is line_sort_options.movie:
        order_by = (db.movies.c.movie_id == db.lines.c.movie_id)
    elif sort is line_sort_options.line_text:
        order_by = db.lines.c.line_text
    else:
        assert False

    lines_Query = (
        sqlalchemy.select(
            db.lines.c.line_id,
            db.lines.c.character_id,
            db.lines.c.movie_id,
            db.lines.c.conversation_id,
            db.lines.c.line_text,
            db.movies.c.title.label("movie"),
            db.characters.c.name.label("spoken_by"),
            db.conversations.c.character1_id.label("convo_char1"),
            db.conversations.c.character2_id.label("convo_char2"),  
        )
        .select_from(db.lines
            .join(db.characters, db.lines.c.character_id == db.characters.c.character_id)
            .join(db.movies, db.lines.c.movie_id == db.movies.c.movie_id)
            .join(db.conversations, db.lines.c.conversation_id == db.conversations.c.conversation_id)
        )
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.movies.c.movie_id)
    )

    # filter based on line content
    if line_text != "":
        lines_Query = lines_Query.where(db.lines.c.line_text.ilike(f"%{line_text}%"))

    if spoken_by != "":
        lines_Query = lines_Query.where(db.characters.c.name.ilike(f"%{spoken_by}%"))

    

    with db.engine.connect() as conn:
        lines_result = conn.execute(lines_Query)

        if lines_result.rowcount == 0:
            raise HTTPException(status_code=404, detail="no lines not found.")

        res_json = []

        for row in lines_result:
            spoken_to_character_id = None
            #determine the character spoken_to id
            if row.character_id == row.convo_char1:
                spoken_to_character_id = row.convo_char2
            else:
                spoken_to_character_id = row.convo_char1

            spoken_to_character_Query = (
                sqlalchemy.select(
                    db.characters.c.name
                )
                .where(db.characters.c.character_id == spoken_to_character_id)
            )
            spoken_to_char_result = conn.execute(spoken_to_character_Query)
            spoken_to_char = spoken_to_char_result.fetchone()

            res_json.append({
                "line_id": row.line_id,
                # "char_id": line.character_id,
                "spoken_by": row.spoken_by,
                "movie": row.movie,
                # "spoken_to?_1": line.convo_char1,
                # "spoken_to?_2": line.convo_char2,
                "spoken_to": spoken_to_char.name,
                "line_text": row.line_text,
            })

        return res_json

@router.get("/movie_lines/", tags=["lines"])
def list_lines(
    movie_title:str,
    limit: int = 50,
    offset: int = 0
):
    """
    This endpoint returns a list of lines from a given movie. For each line
    it returns:
    * `line_id`: the internal id of the character. Can be used to query the
      `/line/{line_id}` endpoint.
    * `spoken_by`: The name of the character who spoke the line.
    * `movie`: The movie the line is from.
    * `spoken_to`: The name of the character who the line was spoken to.
    * `line_text`: The content of the line

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    lines_Query = (
        sqlalchemy.select(
            db.lines.c.line_id,
            db.lines.c.character_id,
            db.lines.c.movie_id,
            db.lines.c.conversation_id,
            db.lines.c.line_text,
            db.movies.c.title.label("movie"),
            db.characters.c.name.label("spoken_by"),
            db.conversations.c.character1_id.label("convo_char1"),
            db.conversations.c.character2_id.label("convo_char2"),   
        )
        .select_from(
            db.lines
            .join(db.characters, db.lines.c.character_id == db.characters.c.character_id)
            .join(db.movies, db.lines.c.movie_id == db.movies.c.movie_id)
            .join(db.conversations, db.lines.c.conversation_id == db.conversations.c.conversation_id)
        )
        .limit(limit)
        .offset(offset)
        .order_by(db.lines.c.line_id)
    )

    # filter based on movie title
    if movie_title != "":
        lines_Query = lines_Query.where(db.movies.c.title.ilike(f"%{movie_title}%"))
    
    with db.engine.connect() as conn:
        lines_result = conn.execute(lines_Query)

        if lines_result.rowcount == 0:
            raise HTTPException(status_code=404, detail="no lines not found.")

        res_json = []

        for row in lines_result:
            spoken_to_character_id = None
            #determine the character spoken_to id
            if row.character_id == row.convo_char1:
                spoken_to_character_id = row.convo_char2
            else:
                spoken_to_character_id = row.convo_char1

            spoken_to_character_Query = (
                sqlalchemy.select(
                    db.characters.c.name
                )
                .where(db.characters.c.character_id == spoken_to_character_id)
            )
            spoken_to_char_result = conn.execute(spoken_to_character_Query)
            spoken_to_char = spoken_to_char_result.fetchone()

            res_json.append({
                "line_id": row.line_id,
                # "char_id": line.character_id,
                "spoken_by": row.spoken_by,
                "movie": row.movie,
                # "spoken_to?_1": line.convo_char1,
                # "spoken_to?_2": line.convo_char2,
                "spoken_to": spoken_to_char.name,
                "line_text": row.line_text,
            })

        return res_json

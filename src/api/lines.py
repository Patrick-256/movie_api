from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

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

    line = None
    line = db.verbosLines.get(int(id))
    if line is not None:
        return line

    if line is None:
        raise HTTPException(status_code=404, detail="line not found.")

    return line
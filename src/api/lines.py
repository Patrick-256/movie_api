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

    #step 1: do the sorting
    sortedLines = {}
    if sort == "spoken_by":
        sortedLines = {k: v for k, v in sorted(db.verbosLines.items(), key=lambda item: item[1]["spoken_by"])}
    if sort == "movie":
        sortedLines = {k: v for k, v in sorted(db.verbosLines.items(), key=lambda item: item[1]["movie"])}
    if sort == "line_text":
        sortedLines = {k: v for k, v in sorted(db.verbosLines.items(), key=lambda item: item[1]["line_text"])}

    #step 2: do the picking
    jsonResults =  []

    if spoken_by == "":
        if line_text == "":
            #list out the first 50 lines
            for line in sortedLines:
                if offset > 0:
                    offset -= 1
                else:
                    if limit > 0:
                        jsonResults.append(sortedLines[line])
                        limit -= 1
                    else: break
        else:
            for line in sortedLines:
                if line_text in sortedLines[line]["line_text"]:
                    if offset > 0:
                        offset -= 1
                    else:
                        if limit > 0:
                            jsonResults.append(sortedLines[line])
                            limit -= 1
                        else: break
    else: #looking for a line spoken by a particular character
        if line_text == "":
            for line in sortedLines:
                if spoken_by.upper() in sortedLines[line]["spoken_by"]: 
                    if offset > 0:
                        offset -= 1
                    else:
                        if limit > 0:
                            jsonResults.append(sortedLines[line])
                            limit -= 1
                        else: break
        else:
            for line in sortedLines:
                if spoken_by.upper() in sortedLines[line]["spoken_by"]:
                    if line_text in sortedLines[line]["line_text"]: 
                        if offset > 0:
                            offset -= 1
                        else:
                            if limit > 0:
                                jsonResults.append(sortedLines[line])
                                limit -= 1
                            else: break

    return jsonResults
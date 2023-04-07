from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()

def getNumLinesOfConvo(id: str):
    #returns how many lines a certain conversation is
    numLines = 0

    for line in db.lines:
        if line["conversation_id"] == id:
            numLines += 1
    
    return numLines


def getMovieTitle(id: str):
    for movie in db.movies:
        if movie["movie_id"] == id:
            print("movie found")
            return movie["title"]
    print("movie not found :(")
    return None

def getCharacterGender(character):
    if character["gender"] == "M":
        return "M"
    if character["gender"] == "F":
        return "F"
    return None

def getMostLines(id: str):
    highConvoCount = 0
    mostTalkedId = None
    currentConvoCount = 0
    currentTalkedId = None

    for convo in db.conversations:
        if convo["character1_id"] == id:
            if convo["character2_id"] == currentTalkedId:
                currentConvoCount += getNumLinesOfConvo(convo["conversation_id"])
            else:
                currentTalkedId = convo["character2_id"]
                currentConvoCount = getNumLinesOfConvo(convo["conversation_id"])

            if currentConvoCount > highConvoCount:
                highConvoCount = currentConvoCount
                mostTalkedId = currentTalkedId

        if convo["character2_id"] == id:
            if convo["character1_id"] == currentTalkedId:
                currentConvoCount += getNumLinesOfConvo(convo["conversation_id"])
            else:
                currentTalkedId = convo["character1_id"]
                currentConvoCount = getNumLinesOfConvo(convo["conversation_id"])

            if currentConvoCount > highConvoCount:
                highConvoCount = currentConvoCount
                mostTalkedId = currentTalkedId

    json = None
    
    for character in db.characters:
          if character["character_id"] == mostTalkedId:
              print("most talked to character found")
              json = [{
                "character_id":mostTalkedId,
                "character":character["name"],
                "gender":getCharacterGender(character),
                "number_of_lines_together":highConvoCount
              }]

    return json



@router.get("/characters/{id}", tags=["characters"])
def get_character(id: str):
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

    json = None

    for character in db.characters:
        if character["character_id"] == id:
            print("character found")
            json = {
              "character_id":id,
              "character":character["name"],
              "movie":getMovieTitle(character["movie_id"]),
              "gender":getCharacterGender(character),
              "top_conversations":getMostLines(id)
            }

    if json is None:
        raise HTTPException(status_code=404, detail="character not found.")

    return json


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
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

    jsonArray = []

    x = 0
    for x in range(50):
        jsonArray = get_character(x)
    return jsonArray

from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()

def getTotalNumLinesOfConvo(id: str):
    #returns how many lines a certain conversation is
    numLines = 0

    for line in db.lines:
        if db.lines[line][2] == id:
            numLines += 1
    
    return numLines

def getMovieTitle(id: int):
    movie = db.movies.get(id)      
    return movie[0]

def getCharacterGender(value):
    if value == "M":
        return "M"
    if value == "F":
        return "F"
    return None

def getMostLines(id: int):
    characterIDsAlreadyConsidered = []
    topCharacterLines = []

    for convo in db.conversations:

        if db.conversations[convo][0] == id or db.conversations[convo][1] == id:
            #found a convo with our character, find out who they talked to
            charTalkedToId = None
            if db.conversations[convo][0] == id:
                charTalkedToId = db.conversations[convo][1]
            else:
                charTalkedToId = db.conversations[convo][0]

            characterIDsAlreadyConsidered.insert(0,charTalkedToId)
            topCharacterLines.insert(0,getTotalNumLinesOfConvo(convo))

    #aggregate the arrays
    characterIds_agg = [-1]
    charLines_agg = [-1]

    for i in range(len(characterIDsAlreadyConsidered)):
        idFound = False
        for k in range(len(characterIds_agg)):
            if characterIds_agg[k] == characterIDsAlreadyConsidered[i]:
                charLines_agg[k] += topCharacterLines[i]
                idFound = True

        if idFound == False:
            characterIds_agg.insert(0,characterIDsAlreadyConsidered[i])
            charLines_agg.insert(0,topCharacterLines[i])

    # print("original id array:   ",characterIDsAlreadyConsidered)
    # print("aggregated id array: ",characterIds_agg)
    # print("original line array:   ",topCharacterLines)
    # print("aggregated line array: ",charLines_agg)

    #sort arrays based on line count
    sortingDone = False
    numOfSwaps = 0

    while sortingDone == False: 
        for i in range(len(charLines_agg)-1):
            if charLines_agg[i] < charLines_agg[i+1]:
                #print("swapping")
                #perform swap on both characterline counts and character ID arrays
                numOfSwaps += 1
                temp = charLines_agg[i]
                temp2 = characterIds_agg[i]

                charLines_agg[i] = charLines_agg[i+1]
                charLines_agg[i+1] = temp
                characterIds_agg[i] = characterIds_agg[i+1]
                characterIds_agg[i+1] = temp2
        if numOfSwaps == 0:
            sortingDone = True
        numOfSwaps = 0


    json = [] 
    for i in range(len(characterIds_agg)-1):      
        characterConvo = {
            "character_id":int(characterIds_agg[i]),
            "character":db.characters[characterIds_agg[i]][0],
            "gender":getCharacterGender(db.characters[characterIds_agg[i]][2]),
            "number_of_lines_together":int(charLines_agg[i])
        }
        json.append(characterConvo)

    return json



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

    json = None


    character = db.characters.get(int(id))
    #print("character found")
    if character is not None:
        json = {
            "character_id":int(id),
            "character":character[0],
            "movie":getMovieTitle(character[1]),
            "gender":getCharacterGender(character[2]),
            "top_conversations":getMostLines(int(id))
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
    

    #step 0: prepare the characters to be sorted by calculating their lines
    charactersWithLines = {}
    for character in db.characters:
        key = character
        simpleChar = {
            "character_id":character,
            "character":db.characters[character][0],
            "movie":getMovieTitle(db.characters[character][1]),
            "number_of_lines": 0
        }
        charactersWithLines[key] = simpleChar
    
    # print(charactersWithLines)

    for line in db.lines:
        charactersWithLines[db.lines[line][0]]["number_of_lines"] += 1

    # print(charactersWithLines)

    #Step 1: do the sorting
    sortedCharacters = {}
    if sort == "character":
        sortedCharacters = {k: v for k, v in sorted(charactersWithLines.items(), key=lambda item: item[1]["character"])}
    if sort == "movie":
        sortedCharacters = {k: v for k, v in sorted(charactersWithLines.items(), key=lambda item: item[1]["movie"])}
    if sort == "number_of_lines":
        sortedCharacters = {k: v for k, v in sorted(charactersWithLines.items(), key=lambda item: item[1]["number_of_lines"], reverse=True)}


    #Step 2: do the picking
    jsonResults =  []

    if name == "":
        #list out the first 50 characters
        for character in sortedCharacters:
            if offset > 0:
                offset -= 1
            else:
                if limit > 0:
                    jsonResults.append(sortedCharacters[character])
                    limit -= 1
                else: break
    else:
        for character in sortedCharacters:
            if offset > 0:
                offset -= 1
            else:
                if limit > 0:
                    if name.upper() in sortedCharacters[character]["character"]:            
                        jsonResults.append(sortedCharacters[character])
                        limit -= 1
                else: break

    return jsonResults

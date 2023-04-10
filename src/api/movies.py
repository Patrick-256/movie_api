from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()

def getNumLinesOfConvo(convo_id: str,character_id: str):
    #returns how many lines a certain conversation is
    numLines = 0

    for line in db.lines:
        if line["conversation_id"] == convo_id and line["character_id"] == character_id:
            numLines += 1
    
    return numLines

def getCharacterName(id: str):
    for character in db.characters:
        if character["character_id"] == id:
            return character["name"]
    return None

def getTop5charactersFromMovie(id: str):
    #look at convos for the given movie id
    #keep track of the top 5 character ids with the most occurences
    characterIds = [-1]
    characterLineCounts = [-1]

    for convo in db.conversations:
        if convo["movie_id"] == id:
            #characters are in the movie      
            #increment currentCharacter if this character is the same
            if characterIds[0] == convo["character1_id"]:
                characterLineCounts[0] += getNumLinesOfConvo(convo["conversation_id"],convo["character1_id"])
            else:
                characterIds.insert(0,convo["character1_id"])
                characterLineCounts.insert(0, getNumLinesOfConvo(convo["conversation_id"],convo["character1_id"]))

    for convo in db.conversations:
        if convo["movie_id"] == id:
            #characters are in the movie      
            #increment currentCharacter if this character is the same
            if characterIds[0] == convo["character2_id"]:
                characterLineCounts[0] += getNumLinesOfConvo(convo["conversation_id"],convo["character1_id"])
            else:
                characterIds.insert(0,convo["character2_id"])
                characterLineCounts.insert(0, getNumLinesOfConvo(convo["conversation_id"],convo["character1_id"]))

    #aggregate same characters
    characterIds_agg = [-1]
    characterLineCounts_agg = [-1]

    print(characterIds)
    print(characterLineCounts)
    for i in range(len(characterIds)):
        #check if its already in agg array
        idFound = False
        for k in range(len(characterIds_agg)):
            if characterIds_agg[k] == characterIds[i]:  
                characterLineCounts_agg[k] += characterLineCounts[i]
                idFound = True

        if idFound == False:
            characterIds_agg.insert(0,characterIds[i])
            characterLineCounts_agg.insert(0,characterLineCounts[i])
        # print(characterIds_agg)
        # print(characterLineCounts_agg)

    print("done aggregating")
    print(characterIds_agg)
    print(characterLineCounts_agg)
    #sort them
    sortComplete = False
    numOfSwaps = 0

    while sortComplete == False:
        numOfSwaps = 0
        for i in range(len(characterLineCounts_agg)-1):
            if characterLineCounts_agg[i] < characterLineCounts_agg[i+1]:
                #swap them
                numOfSwaps += 1

                temp1 = characterLineCounts_agg[i]
                characterLineCounts_agg[i] = characterLineCounts_agg[i+1]
                characterLineCounts_agg[i+1] = temp1
                
                temp2 = characterIds_agg[i]
                characterIds_agg[i] = characterIds_agg[i+1]
                characterIds_agg[i+1] = temp2
        
        if numOfSwaps == 0: sortComplete = True


    json = []
    for i in range(5):
        if characterIds_agg[i] == -1: return json
        character = {
            "character_id":characterIds_agg[i],
            "character":getCharacterName(characterIds_agg[i]),
            "num_lines":characterLineCounts_agg[i]
        }
        json.append(character)
    return json



# include top 3 actors by number of lines
@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: str):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """
    json = None

    for movie in db.movies:
        if movie["movie_id"] == movie_id:
            print("movie found")
            json = {
                "movie_id":movie_id,
                "title":movie["title"],
                "top_characters":getTop5charactersFromMovie(movie_id)
            }

    

    if json is None:
        raise HTTPException(status_code=404, detail="movie not found.")

    return json


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    json = None

    return json

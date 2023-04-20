from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query

router = APIRouter()


def getCharacterName(id: int):
    name = db.characters[id][0]
    if name is not None:
        return name
    return None

def getTop5charactersFromMovie(movie_id: int):
    #look at convos for the given movie id
    #keep track of the top 5 character ids with the most occurences
    characterIds = [-1]
    characterLineCounts = [-1]

    for line in db.lines:
        if db.lines[line][1] == movie_id:
            characterIds.append(db.lines[line][0])
            characterLineCounts.append(1)

    #aggregate same characters
    characterIds_agg = [-1]
    characterLineCounts_agg = [-1]

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
        # #print(characterIds_agg)
        # #print(characterLineCounts_agg)

    # print("done aggregating")
    # print(characterIds_agg)
    # print(characterLineCounts_agg)
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
            "character_id":int(characterIds_agg[i]),
            "character":getCharacterName(characterIds_agg[i]),
            "num_lines":characterLineCounts_agg[i]
        }
        json.append(character)
    return json



# include top 3 actors by number of lines
@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: int):
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
    movie = db.movies.get(int(movie_id))

    if movie is not None:
        # print("the movie: ",movie)
        json = {
            "movie_id":int(movie_id),
            "title":movie[0],
            "top_characters":getTop5charactersFromMovie(int(movie_id))
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
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
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
    #step 0: set up movie dictionary
    simpleMovies = {}
    for movie in db.movies:
        key = movie
        simpleMovie = {
            "movie_id":movie,
            "movie_title":db.movies[movie][0],
            "year":db.movies[movie][1],
            "imdb_rating":db.movies[movie][2],
            "imdb_votes":db.movies[movie][3],
        }
        simpleMovies[key] = simpleMovie

    #step 1: do the sorting
    sortedMovies = {}
    if sort == "movie_title":
        sortedMovies = {k: v for k, v in sorted(simpleMovies.items(), key=lambda item: item[1]["movie_title"])}
    if sort == "year":
        sortedMovies = {k: v for k, v in sorted(simpleMovies.items(), key=lambda item: item[1]["year"])}
    if sort == "rating":
        sortedMovies = {k: v for k, v in sorted(simpleMovies.items(), key=lambda item: item[1]["imdb_rating"], reverse=True)}

    # print(sortedMovies)

    #step 2: do the picking
    jsonResults = []

    if name == "":
        #no name provided
        for movie in sortedMovies:
            if offset > 0:
                offset -= 1
            else:
                if limit > 0:
                    jsonResults.append(sortedMovies[movie])
                    limit -= 1
    else:
        for movie in sortedMovies:
            if name.lower() in sortedMovies[movie]["movie_title"]:
                if offset > 0:
                    offset -= 1
                else:
                    if limit > 0:
                        jsonResults.append(sortedMovies[movie])
                        limit -= 1

    return jsonResults


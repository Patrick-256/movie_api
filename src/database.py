import csv
from src.datatypes import Character, Movie, Conversation, Line
import os
import io
from supabase import Client, create_client
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

# Reading in the log file from the supabase bucket
log_csv = (
    supabase.storage.from_("movie-api")
    .download("movie_conversations_log.csv")
    .decode("utf-8")
)

logs = []
for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
    logs.append(row)


# Writing to the log file and uploading to the supabase bucket
def upload_new_log():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["post_call_time", "movie_id_added_to"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(logs)
    supabase.storage.from_("movie-api").upload(
        "movie_conversations_log.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )


# END PLACEHOLDER CODE


def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None


movies = {}
with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        key = int(row["movie_id"])
        values = [row["title"],row["year"],float(row["imdb_rating"]),int(row["imdb_votes"]),row["raw_script_url"]]
        movies[key] = values
    
    
characters = {}
with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        key = int(row["character_id"])
        values = [row["name"],int(row["movie_id"]),row["gender"],row["age"]]
        characters[key] = values
    
    #print(characters[10])

conversations = {}
with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        key = int(row["conversation_id"])
        values = [int(row["character1_id"]),int(row["character2_id"]),int(row["movie_id"])]
        conversations[key] = values
    
    #print(conversations)

lines = {}
with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        key = int(row["line_id"])
        values = [int(row["character_id"]),int(row["movie_id"]),int(row["conversation_id"]),row["line_sort"],row["line_text"]]
        lines[key] = values

#build lines
def findSpokenTo(spokenBy_id:int,conversation_id):
    char1 = conversations[conversation_id][0]
    char2 = conversations[conversation_id][1]

    spokenToChar_id = char1
    if spokenToChar_id == spokenBy_id:
        spokenToChar_id = char2
    return spokenToChar_id

verbosLines = {}
for line in lines:
    key = line
    verbosLine = {
        "line_id":line,
        "spoken_by":characters[lines[line][0]][0],
        "movie":movies[lines[line][1]][0],
        "spoken_to":characters[findSpokenTo(lines[line][0],lines[line][2])][0],
        "line_text":lines[line][4],
    }
    verbosLines[key] = verbosLine

# print("hello")
# print(verbosLines[50])
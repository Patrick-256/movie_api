import csv

# TODO: You will want to replace all of the code below. It is just to show you
# an example of reading the CSV files where you will get the data to complete
# the assignment.

print("reading movies")

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    movies = {}
    for row in csv_reader:
        key = int(row["movie_id"])
        values = [row["title"],row["year"],row["imdb_rating"],row["imdb_votes"],row["raw_script_url"]]
        movies[key] = values
    

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    characters = {}
    for row in csv_reader:
        key = int(row["character_id"])
        values = [row["name"],int(row["movie_id"]),row["gender"],row["age"]]
        characters[key] = values
    
    #print(characters[10])

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    conversations = {}
    for row in csv_reader:
        key = int(row["conversation_id"])
        values = [int(row["character1_id"]),int(row["character2_id"]),int(row["movie_id"])]
        conversations[key] = values
    
    #print(conversations)

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    lines = {}
    for row in csv_reader:
        key = int(row["line_id"])
        values = [int(row["character_id"]),int(row["movie_id"]),int(row["conversation_id"]),row["line_sort"],row["line_text"]]
        lines[key] = values

from sqlalchemy import create_engine
import os
import dotenv
import sqlalchemy

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"


print(database_connection_url())
# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())

# Create a single connection to the database. Later we will discuss pooling connections.
conn = engine.connect()

from sqlalchemy import MetaData, Table, Column, Integer, String, Float

# metadata = MetaData()

metadata_obj = sqlalchemy.MetaData()
movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=engine)
characters = sqlalchemy.Table("characters", metadata_obj, autoload_with=engine)
conversations = sqlalchemy.Table("conversations", metadata_obj, autoload_with=engine)
lines = sqlalchemy.Table("lines", metadata_obj, autoload_with=engine)

# movies = Table(
#     "movies",
#     metadata,
#     Column("movie_id", Integer, primary_key=True),
#     Column("title", String),
#     Column("year", Integer),
#     Column("imdb_rating", Float),
#     Column("imdb_votes", Integer),
# )

# characters = Table(
#     "characters",
#     metadata,
#     Column("character_id", Integer, primary_key=True),
#     Column("name", String),
#     Column("movie_id", Integer),
#     Column("gender", String),
#     Column("age", Integer),
# )

# conversations = Table(
#     "conversations",
#     metadata,
#     Column("conversation_id", Integer, primary_key=True),
#     Column("character1_id", Integer),
#     Column("character2_id", Integer),
#     Column("movie_id", Integer),
# )

# lines = Table(
#     "lines",
#     metadata,
#     Column("line_id", Integer, primary_key=True),
#     Column("character_id", Integer),
#     Column("movie_id", Integer),
#     Column("conversation_id", Integer),
#     Column("line_sort", Integer),
#     Column("line_text", String),
# )



# Access the "title" column of the "movies" table using db.movies.c.title
db = {
    "movies": movies,
    "characters":characters,
    "conversations":conversations,
    "lines":lines,
}
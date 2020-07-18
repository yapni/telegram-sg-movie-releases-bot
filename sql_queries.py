"""
SQL queries strings
"""

# Craete movies table
CREATE_MOVIES_TABLE = 'CREATE TABLE IF NOT EXISTS movies ( \
    imdb_id varchar(20) PRIMARY KEY, \
    title text, \
    year varchar(10), \
    imdb_link text, \
    release_date date, \
    run_time varchar(10), \
    genre text, \
    director text, \
    writer text, \
    actors text, \
    plot text, \
    language text, \
    country text, \
    poster_link text \
);'

# Insert a movie object in the movies table
INSERT_MOVIE = 'INSERT INTO movies (imdb_id, title, year, imdb_link, release_date, run_time, genre, director, \
                                    writer, actors, plot, language, country, poster_link) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'

# Update a movie object in the movies table
UPDATE_MOVIE = 'UPDATE movies \
                SET title=%s, year=%s, imdb_link=%s, release_date=%s, run_time=%s, genre=%s, director=%s, \
                    writer=%s, actors=%s, plot=%s, language=%s, country=%s, poster_link=%s \
                WHERE imdb_id=%s;'

# Check if a movie exists in the movies table using its imdb_id
CHECK_MOVIE_EXISTS = 'SELECT 1 FROM movies WHERE imdb_id=%s;'

# Get movies
GET_MOVIES = 'SELECT * FROM movies;'

# Get movies based on title (case-insensitive)
GET_MOVIES_BY_TITLE = 'SELECT * FROM movies WHERE LOWER(title)=LOWER(%s);'

# Delete a movie object from the movies table
DELETE_MOVIE = 'DELETE FROM movies WHERE imdb_id=%s;'

# Create users table
CREATE_USERS_TABLE = 'CREATE TABLE IF NOT EXISTS users ( \
    chat_id integer PRIMARY KEY, \
    first_name varchar(50), \
    username varchar(50) \
);'

# Insert a user object in the users table
INSERT_USER = 'INSERT INTO users (chat_id, first_name, username) \
                VALUES (%s, %s, %s) \
                ON CONFLICT DO NOTHING;'

# Get users
GET_USERS = 'SELECT * FROM users;'

# Delete a user object from the movies table
DELETE_USER = 'DELETE FROM users WHERE chat_id=%s;'
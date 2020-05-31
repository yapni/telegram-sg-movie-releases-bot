"""
Deals with database stuff for the bot
"""

from movie import Movie
from user import User
import logging
import psycopg2
import sql_queries as queries
import unidecode

LOGGER = logging.getLogger()

class DatabaseManager:

    def __init__(self, db_name, user, port, host, password=''):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.port = port
        self.host = host
        self.connection = None
        self.cursor = None
    
    def connect_db(self, with_pwd):
        '''
        Attempts to connect to the database.
        Returns a connection object if success, exit if fail.

        @param with_pwd: If True, connect to db with a password. Else, connect to db without password.
        '''
        try:
            if with_pwd:
                LOGGER.info("Connecting to the database {} at {} (port {}) as user {} (with password)"
                        .format(self.db_name, self.host, self.port, self.user))
                self.connection = psycopg2.connect(
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port,
                    database=self.db_name
                )
            else:
                self.connection = psycopg2.connect(
                    user=self.user,
                    host=self.host,
                    port=self.port,
                    database=self.db_name
                )
            self.cursor = self.connection.cursor()
        except Exception as e:
            LOGGER.error("Failed to connect to the database!")
            print(e)
        return self.connection
    
    def create_tables(self):
        '''
        Create all the required tables (movies, users) in this db.
        '''
        self.create_movies_table()
        self.create_users_table()
    
    def create_movies_table(self):
        '''
        Create movies table in the db if it does not exists.
        '''
        self.cursor.execute(queries.CREATE_MOVIES_TABLE)
        self.connection.commit()
    
    def create_users_table(self):
        '''
        Create users table in the db if it does not exists.
        '''
        self.cursor.execute(queries.CREATE_USERS_TABLE)
        self.connection.commit()
    
    def insert_user(self, user):
        '''
        Insert a user object into the users table. If user already exists, do nothing.
        Returns 1 if user is inserted into the db, 0 if user already exists in the db.
        '''
        self.cursor.execute(queries.INSERT_USER, (user.chat_id, user.username))
        row_count = self.cursor.rowcount
        self.connection.commit()
        return row_count
    
    def get_users(self):
        '''
        Return users in the database as a list of User objects
        '''
        self.cursor.execute(queries.GET_USERS)
        rows = self.cursor.fetchall()
        users = [User(row[0], row[1]) for row in rows]
        return users
    
    def delete_user(self, user):
        '''
        Remove a user object from the users table.
        Returns 1 if the user is removed, 0 if user does not exists in the db.
        '''
        self.cursor.execute(queries.DELETE_USER, (user.chat_id,))
        row_count = self.cursor.rowcount
        self.connection.commit()
        return row_count
    
    def upsert_movie(self, movie):
        '''
        Insert or update a movie object into the movies table
        '''
        self.__encode_movie(movie)
        self.cursor.execute(queries.CHECK_MOVIE_EXISTS, (movie.imdb_id,))
        if self.cursor.fetchone(): # Movie exists, update values instead
            self.cursor.execute(queries.UPDATE_MOVIE, (
                        movie.title, movie.year, movie.imdb_link, movie.release_date, movie.run_time, movie.genre, 
                        movie.director, movie.writer, movie.actors, movie.plot, movie.language, movie.country, 
                        movie.poster_link, movie.imdb_id
            ))
        else: # Movie does not exists, insert into table
            self.cursor.execute(queries.INSERT_MOVIE, (
                        movie.imdb_id, movie.title, movie.year, movie.imdb_link, movie.release_date, movie.run_time, movie.genre, 
                        movie.director, movie.writer, movie.actors, movie.plot, movie.language, movie.country, movie.poster_link
            ))
        
        self.connection.commit()
    
    def get_movies(self):
        '''
        Returns movies in the database as a list of Movie objects
        '''
        self.cursor.execute(queries.GET_MOVIES)
        movies = [Movie(row[1], row[2], row[3], row[0], row[4], row[5], row[6], row[7], row[8], row[9], row[10], 
                        row[11], row[12], row[13]) for row in self.cursor.fetchall()]
        return movies
    
    def get_movies_by_title(self, title):
        '''
        Returns movies in the database that matches the given title as a list of Movie objects.
        Title is case-insensitive.
        '''
        self.cursor.execute(queries.GET_MOVIES_BY_TITLE, (title, ))
        movies = [Movie(row[1], row[2], row[3], row[0], row[4], row[5], row[6], row[7], row[8], row[9], row[10], 
                        row[11], row[12], row[13]) for row in self.cursor.fetchall()]
        return movies
    
    def delete_movie(self, movie):
        '''
        Delete a movie object from the movies table.
        Returns 1 if the movie is removed, 0 if the movie does not exists in the db.
        '''
        self.cursor.execute(queries.DELETE_MOVIE, (movie.imdb_id,))
        row_count = self.cursor.rowcount
        self.connection.commit()
        return row_count

    def __encode_movie(self, movie):
        '''
        Encode a movie object by taking Unicode data and represent it in ASCII characters
        for relevant attributes in the movie object.
        This is to bypass any encoding issues we may encounter using pycopg2.
        '''
        # TODO: deal with unicode encodings properly
        movie.title = unidecode.unidecode(movie.title)
        movie.genre = unidecode.unidecode(movie.genre)
        movie.director = unidecode.unidecode(movie.director)
        movie.writer = unidecode.unidecode(movie.writer)
        movie.actors = unidecode.unidecode(movie.actors)
        movie.plot = unidecode.unidecode(movie.plot)
        movie.language = unidecode.unidecode(movie.language)
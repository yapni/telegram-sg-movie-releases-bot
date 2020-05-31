"""
Fetches movie releases from IMDB
"""

from bs4 import BeautifulSoup
from movie import Movie
import datetime
import json
import os
import requests

class Releases:

    def __init__(self):
        self.movie_releases = [] # List of Movie objects fetched

    def fetch_releases(self):
        '''
        Fetches the movie releases and populate the movie_releases list.
        '''
        self.movie_releases = self.get_imdb_movie_releases()
        self.get_movie_details(self.movie_releases)

        return self.movie_releases
    
    def get_movie_details(self, movies):
        '''
        Populate the movie details in the list of movies through the OMDb API.
        The movie details are found using its imdb_id.
        '''
        # Get OMDb API key
        try:
            api_key = os.environ['OMDB_API_KEY']
        except KeyError:
            raise KeyError('OMDb API key not found! Ensure that your OMDb API key is in the "OMDB_API_KEY" environment variable!')

        omdb_url_by_id = 'http://www.omdbapi.com/?i={}&apikey=' + api_key

        # Get the movie details through OMDb API (search by IMDB id)
        for movie in movies:
            response = requests.get(omdb_url_by_id.format(movie.imdb_id))
            full_details = json.loads(response.text)
            if full_details['Response'] == 'True':
                movie.run_time = full_details['Runtime']
                movie.genre = full_details['Genre']
                movie.director = full_details['Director']
                movie.writer = full_details['Writer']
                movie.actors = full_details['Actors']
                movie.plot = full_details['Plot']
                movie.language = full_details['Language']
                movie.country = full_details['Country']
                movie.poster_link = full_details['Poster']

    def get_imdb_movie_releases(self):
        '''
        Retrieves upcoming movie releases from the IMDB page.
        Returns a list of Movie objects with populated "title", "year", "release_date", "imdb_id" and "imdb_link" values.
        '''
        imdb_movie_releases_link = 'https://www.imdb.com/calendar/?region=sg'
        movies = []

        # Fetch IMDB page
        response = requests.get(imdb_movie_releases_link)
        page = response.content

        # Parse the page and get movie releases info
        soup = BeautifulSoup(page, 'html.parser')
        main_div = soup.find(id='main')
        release_dates_h4 = main_div.find_all('h4')
        for release_date_element in release_dates_h4:
            release_date = self.__imdb_date_to_datetime(release_date_element.text)
            titles_li = release_date_element.find_next('ul').find_all('li')
            for title_element in titles_li:
                title, year = title_element.text.strip().strip('\n').rsplit(' ', 1)
                year = year.strip('(').strip(')')
                imdb_link = title_element.a['href']
                imdb_id = imdb_link.split('/')[2]
                movies.append(Movie(title=title, year=year, imdb_link=imdb_link, imdb_id=imdb_id, release_date=release_date))
        
        return movies
    
    def __imdb_date_to_datetime(self, imdb_date):
        ''' 
        Returns a datetime object converted from an IMDB date (e.g. '31 January 2020').
        '''
        month_name_to_number = {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'August': 8,
            'September': 9,
            'October': 10,
            'November': 11,
            'December': 12
        }
        day, month_name, year = imdb_date.split(' ')
        date = datetime.datetime(int(year), month_name_to_number[month_name], int(day))
        return date
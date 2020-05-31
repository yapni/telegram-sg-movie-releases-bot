"""
Contains details of a movie
"""

class Movie:
    def __init__(self, title='', year='', imdb_link='', imdb_id='', release_date=None, run_time='', genre='', \
                    director='', writer='', actors='', plot='', language='', country='', poster_link=''):
        self.title = title
        self.year = year
        self.imdb_link = imdb_link
        self.imdb_id = imdb_id
        self.release_date = release_date # datetime object
        self.run_time = run_time
        self.genre = genre
        self.director = director
        self.writer = writer
        self.actors = actors
        self.plot = plot
        self.language = language
        self.country = country
        self.poster_link = poster_link
    
    def __str__(self):
        return "\n".join([
            "Title: " + self.title,
            "Year: " + self.year,
            "IMDB Link: " + self.imdb_link,
            "IMDB ID: " + self.imdb_id,
            "Release Date: " + self.release_date.strftime("%d %B %Y"),
            "Run Time: " + self.run_time,
            "Genre: " + self.genre,
            "Director: " + self.director,
            "Writer: " + self.writer,
            "Actors: " + self.actors,
            "Plot: " + self.plot,
            "Language: " + self.language,
            "Country: " + self.country,
            "Poster Link: " + self.poster_link
        ])
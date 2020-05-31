# Telegram Bot: Singapore Movie Releases

This bot notifies users of movie releases in Singapore.

This bot is currently deployed using Heroku's free plan. Add the bot to your telegram: http://t.me/sgmoviereleases_bot

The list of movies are scrapped from [IMDB's website](https://www.imdb.com/calendar/?region=sg) while the details of each movie are obtained using [OMDb's API](https://www.omdbapi.com/).

The bot checks for upcoming movie releases and updates the database every midnight. The bot also checks if there are new movie releases every morning and notifies users if so. The list of movies and users suscribed to the bot are maintained using PostgreSQL (using pycopg2 as a Python interface).

## Requirements
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): For web scrapping
* [psycopg2](https://www.psycopg.org/docs/): For interfacing with PostgreSQL
* [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot): Python wrapper for [Telegram API](https://core.telegram.org/bots/api)
* [pytz](https://pythonhosted.org/pytz/): For timezone definitions
* [requests](https://requests.readthedocs.io/en/master/): For HTTP requests
* [Unidecode](https://github.com/takluyver/Unidecode): To deal with non-ascii characters

To install the requirements, simply use the command:
```shell
$ pip install -r requirements.txt
```

## Usage
1. Register your bot and obtain an authorization token via [BotFather](https://core.telegram.org/bots/#6-botfather)
2. Set the environment variables required in your shell:
   - `TOKEN`: Authorization token obtained from BotFather
   - `OMDB_API_KEY`: [OMDb API key](https://www.omdbapi.com/apikey.aspx)
   - `MODE`: Set to "dev" for development mode (running locally) or "prod" to production mode (Heroku deployment)
   - `DB_NAME`: Database name
   - `DB_HOST`: Database host address
   - `DB_PORT`: Connection port number of the database
   - `DB_USER`: Username used to authenticate to the database
   - `DATABASE_URL`: Database URL of the PostgreSQL addon on Heroku (refer to [this](https://devcenter.heroku.com/articles/heroku-postgresql)). Required if running in production mode.
   - `PORT` : Port number to listen for the web hook. Required if running in production mode. Set to 8443 by default.
   - `HEROKU_APP_NAME`: Heroku app name. Required if running in production mode.

   > Note: If you are running in 'dev' mode, you must set DB_NAME, DB_HOST, DB_PORT and DB_USER to connect to the database.
   > DATABASE_URL is only required for Heroku deployments.
3. Run the main script:
```shell
$ python3 main.py 
```
4. Add the bot to a Telegram group. Enter "/help" and follow the instructions given by the bot.
"""
A telegram bot that notifies users of movie releases in Singapore.

Author: Yap Ni
"""

from database import DatabaseManager
from releases import Releases
from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Updater
from user import User
import datetime
import logging
import os
import pytz
import requests
import sql_queries as queries
import sys

# Fetch required variables
TOKEN = os.getenv('TELEGRAM_SG_MOVIE_RELEASE_BOT_TOKEN') # Authentication token for this bot
MODE = os.getenv('TELEGRAM_SG_MOVIE_RELEASE_BOT_MODE') # Development ('dev') mode or production mode ('prod')
DATABASE_NAME = os.getenv('TELEGRAM_SG_MOVIE_RELEASE_BOT_DB') # Database name
DATABASE_USER = os.getenv('TELEGRAM_SG_MOVIE_RELEASE_BOT_DB_USER') # Database user
DATABASE_PORT = os.getenv('TELEGRAM_SG_MOVIE_RELEASE_BOT_DB_PORT') # Database port
DATABASE_HOST = os.getenv('TELEGRAM_SG_MOVIE_RELEASE_BOT_DB_HOST') # Database host

# Database stuff
DB_MGR = DatabaseManager(DATABASE_NAME, DATABASE_USER, DATABASE_PORT, DATABASE_HOST)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOGGER = logging.getLogger()

def start(update, context):
    '''
    Callback function for /start command.
    Adds new users to the db so that they can receive update msgs from bot.
    '''
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    # Add new user to DB
    user = User(chat_id, username)
    success_add = DB_MGR.insert_user(user)

    if success_add: # User added to db
        LOGGER.info("New user: " + str(user))
        msg = "Welcome to @sgmovierelease_bot! This bot notifies you when a movie is released in Singapore and " \
            "lets you know all upcoming movie releases! To view the list of commands, type /help.\n\n" \
            " Note: The upcoming movie releases are currated from IMDB's website and are hence not exhaustive."
        context.bot.send_message(chat_id=chat_id, text=msg)
    else: # User already in db
        msg = "You have already started the bot. To view the list of commands, type /help."
        context.bot.send_message(chat_id=chat_id, text=msg)

def stop(update, context):
    '''
    Callback function for /stop command.
    Removes users from the db so that they can no longer receive update msgs from bot.
    '''
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    user = User(chat_id, username)
    success_del = DB_MGR.delete_user(user)

    if success_del: # User exists in db and successfully removed
        LOGGER.info("Removed user: " + str(user))
        msg = "You have chose to stop receiving movie release updates from the bot. " \
            "However, you can still view the list of upcoming movie releases using the bot (see /help).\n\n" \
            "If you changed your mind and wish to receive movie release updates from the bot again, " \
            "type /start."
        context.bot.send_message(chat_id=chat_id, text=msg)
    else:
        msg = "You are already not receiving movie release updates from the bot. " \
                "To receive movie release updates from the bot, type /start."
        context.bot.send_message(chat_id=chat_id, text=msg)

def update(update, context):
    '''
    Callback function for /update command.
    '''
    chat_id = update.effective_chat.id

    updating_msg = "⏳ Updating the database...."
    context.bot.send_message(chat_id=chat_id, text=updating_msg)

    if update_db(None): # Success
        updated_msg = "🟢 Database successfully updated!"
        context.bot.send_message(chat_id=chat_id, text=updated_msg)
    else:
        failed_msg = "🔴 Failed to update database"
        context.bot.send_message(chat_id=chat_id, text=failed_msg)

def listall(update, context):
    '''
    Callback function for /list command.
    Lists all the movies in the db.
    '''
    chat_id = update.effective_chat.id

    # Get movies and sort by release date
    movies = DB_MGR.get_movies()
    movies.sort(key=lambda movie: movie.release_date)

    # Craft movies list text
    movies_list_msg = ""
    prev_date = None
    for movie in movies:
        if movie.release_date != prev_date:
            prev_date = movie.release_date
            movies_list_msg = movies_list_msg + movie.release_date.strftime("\n<b>%d %B %Y</b>\n")
        movies_list_msg = movies_list_msg + "🎬 " + movie.title + "\n"
    
    msg = "Here are the upcoming movie releases in Singapore. To view a movie's information, " \
            "type /info followed by the full name of the movie.\n" + movies_list_msg

    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)

def info(update, context):
    '''
    Callback function for /info command.
    Shows the full information of a movie. 
    The query string must match the movie title exactly (not case sensitive).
    '''
    chat_id = update.effective_chat.id
    query_str = ' '.join(context.args)

    movies = DB_MGR.get_movies_by_title(query_str)

    if not movies or len(movies) != 1: # Movie not found
        msg = "Sorry, we can't find the movie you are looking for ☹ " \
                "Please ensure that you type the <u>full title</u> of the movie (case-insensitive). " \
                "If you are unsure of the full title, type /listall and copy and paste the movie title.\n\n" \
                "❗ Note that we are only able to provide information of upcoming movies in our database " \
                "(i.e. everything that is listed in /listall)."
        context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)
        return

    # Craft movie description text
    target_movie = movies[0]
    google_query_str = target_movie.title.split(' ')
    google_query_str.append(target_movie.year)
    google_link = "https://www.google.com/search?q={}".format('+'.join(google_query_str))
    msg = "🎬" + target_movie.title + " (" + target_movie.year + ")\n\n" + \
                    "↘ <b>Release Date</b>\n" + target_movie.release_date.strftime("%d %B %Y") + "\n\n" + \
                    "↘ <b>Plot</b>\n" + target_movie.plot + "\n\n" + \
                    "↘ <b>Run Time</b>\n" + target_movie.run_time + "\n\n" + \
                    "↘ <b>Genre</b>\n" + target_movie.genre + "\n\n" + \
                    "↘ <b>Actors</b>\n" + target_movie.actors + "\n\n" + \
                    "↘ <b>Director</b>\n" + target_movie.director + "\n\n" + \
                    "↘ <b>Writer</b>\n" + target_movie.writer + "\n\n" + \
                    "↘ <b>Language</b>\n" + target_movie.language + "\n\n" + \
                    "↘ <b>Country</b>\n" + target_movie.country + "\n\n" + \
                    "↘ <b>IMDB Link</b>\n" + "https://www.imdb.com" + target_movie.imdb_link + "\n\n" + \
                    "Not enough information? <a href=\'" + google_link + "\'>🔎 Google it! </a>"

    # Check if poster exists or if the poster link is valid
    has_poster = False
    if target_movie.poster_link:
        resp = requests.get(target_movie.poster_link)
        if resp.status_code == 200 or resp.status_code == 304:
            has_poster = True

    if has_poster: # Send poster with caption if there is a poster
        context.bot.send_photo(chat_id=chat_id, photo=target_movie.poster_link, caption=msg, parse_mode=ParseMode.HTML)
    else:
        context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)

def help(update, context):
    '''
    Callback function for /help command.
    '''
    chat_id = update.effective_chat.id

    msg = "ℹ This bots updates you on upcoming movie releases in Singapore. " \
            "If you wish to be notified whenever there is a new movie released, be sure to type /start. " \
            "If you no longer wish to be notified, type /stop.\n\n" \
            "List of commands:\n" \
            "/start: Receive notifications whenever there is a new movie released.\n" \
            "/stop: Stop receiving notifcations from the bot.\n" \
            "/listall: List all upcoming movie releases in Singapore.\n" \
            "/info <movie>: See information about a movie. "\
                "You must ensure that <movie> must be the full title of the movie (case-insensitive).\n" \
            "/update: Update the database of movie releases. The database will be automatically updated every midnight. " \
                "However, you can also update the database manually using this command.\n" \
            "/help: Show this menu"
    
    context.bot.send_message(chat_id=chat_id, text=msg)
        
def update_db(context: CallbackContext):
    '''
    Fetches movie releases and update the database. Returns True if success.
    Assumes that the associated DB is already connected and there is already a movies table.
    '''
    LOGGER.info("Fetching movies from IMDB...")
    releases = Releases()
    movies = releases.fetch_releases()

    LOGGER.info("Updating movies database...")

    # Insert movies into db
    for movie in movies:
        DB_MGR.upsert_movie(movie)
    
    # Remove movies that are expired from the db
    movies_in_db = DB_MGR.get_movies()
    date_today = datetime.date.today()
    for movie in movies_in_db:
        if date_today > movie.release_date:
            DB_MGR.delete_movie(movie)
    
    return True

def notify_user(context: CallbackContext):
    '''
    Checks if there is a new release on this particular day. If yes, notify user.
    '''
    LOGGER.info("Checking movie releases today...")

    # Get new releases today
    movies = DB_MGR.get_movies()
    date_today = datetime.date.today()
    movies_released = [] # List of movies released today
    for movie in movies:
       if date_today == movie.release_date:
           movies_released.append(movie)
    
    # Craft movie descriptions
    google_link_template = "https://www.google.com/search?q={}"
    full_imdb_link_template = "https://www.imdb.com{}"
    movie_desc_template = "🎬 <b>{}</b>\n" \
                            "➡️ <a href=\"{}\">IMDB Link</a>\n" \
                            "➡️ <a href=\"{}\">Search on Google</a>"
    movies_text = ""
    for movie in movies_released:
        query_str = movie.title.split(' ')
        query_str.append(movie.year)
        google_link = google_link_template.format('+'.join(query_str))
        full_imdb_link = full_imdb_link_template.format(movie.imdb_link)
        movie_desc = movie_desc_template.format(movie.title, full_imdb_link, google_link)
        movies_text = movies_text + movie_desc + "\n\n"
    
    help_text_template = "To see the full information of the movie, " \
                            "type '/info' followed by the full title of the movie (e.g. /info {})"

    # Notify users
    users = DB_MGR.get_users()
    for user in users:
        if movies_released:
            help_text = help_text_template.format(movies_released[0].title)
            main_text = "☀ Good morning {}! Here are the movie releases in Singapore today:\n\n{}{}" \
                        .format(user.username, movies_text, help_text)
            context.bot.send_message(chat_id=user.chat_id, text=main_text, parse_mode=ParseMode.HTML)
        else:
            main_text = "☀ Good morning {}! Unfortunately, there are no movie releases in Singapore today. " \
                        "You can still check out upcoming releases by typing /listall." \
                        .format(user.username)
            context.bot.send_message(chat_id=user.chat_id, text=main_text, parse_mode=ParseMode.HTML)
    
    LOGGER.info("Notified users on today's releases")

def wake(context: CallbackContext):
    '''
    Do useless stuff to keep bot alive.
    '''
    LOGGER.info("Keeping the bot awake with a cup of coffee...")

def main():
    # Initialise database and update the movies table
    DB_MGR.connect_db()
    DB_MGR.create_tables()
    update_db(None)

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register periodic tasks
    job_queue = updater.job_queue
    timezone = pytz.timezone('Asia/Singapore')
    job_queue.run_once(update_db, datetime.time(hour=0, minute=0, second=0, tzinfo=timezone)) # Every midnight
    job_queue.run_once(notify_user, datetime.time(hour=8, minute=0, second=0, tzinfo=timezone)) # Every 8am
    job_queue.run_repeating(wake, datetime.timedelta(minutes=20)) # Wake bot every 20 mins

    # Register callback functions
    # /start
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    # /stop
    stop_handler = CommandHandler('stop', stop)
    dispatcher.add_handler(stop_handler)
    # /update
    update_handler = CommandHandler('update', update)
    dispatcher.add_handler(update_handler)
    # /listall
    listall_handler = CommandHandler('listall', listall)
    dispatcher.add_handler(listall_handler)
    # /info
    info_handler = CommandHandler('info', info)
    dispatcher.add_handler(info_handler)
    # /help
    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    # Start the bot
    if MODE == 'dev':
        # Use polling (i.e. getUpdates API method) if in development mode
        LOGGER.info("Starting bot in development mode...")
        updater.start_polling()
    elif MODE == 'prod':
        # Use webhooks if in production mode
        LOGGER.info("Starting bot in production mode...")
        updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
        updater.bot.set_webhook('https://{}.herokuapp.com/{}'.format(HEROKU_APP_NAME, TOKEN))
        LOGGER.info("Webhook set at https://{}.herokuapp.com/<token>".format(HEROKU_APP_NAME))
        updater.idle()
    else:
        LOGGER.error("Invalid TELEGRAM_SG_MOVIE_RELEASE_BOT_MODE value! Should be 'dev' or 'prod'.")
        sys.exit(1)

if __name__ == '__main__':
    main()
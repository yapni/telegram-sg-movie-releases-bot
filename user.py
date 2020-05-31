"""
Represents a user that is subcribed to the bot
"""

class User:
    def __init__(self, chat_id, username):
        self.chat_id = chat_id
        self.username = username
    
    def __str__(self):
        return "(" + str(self.chat_id) + ", " + self.username + ")"
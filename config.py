import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') # Set your bot token in environment variables
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# URLs
DICTIONARY_URL = "https://www.dictionary.com/browse/{word}"

# Response Templates
HELP_MESSAGE = """
📚 Dictionary Bot Commands:
!define <word> - Get the definition, examples, and etymology of a word
!dict_help - Show this help message

Example: !define example
"""

ERROR_MESSAGE = "❌ Sorry, I couldn't find the definition for '{word}'. Please check the spelling and try again."
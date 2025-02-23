import discord
from discord.ext import commands
import asyncio
import logging
from dictionary_scraper import DictionaryScraper
from utils import format_dictionary_response
from config import DISCORD_TOKEN, COMMAND_PREFIX, HELP_MESSAGE, ERROR_MESSAGE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot with command prefix and required intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
dictionary = DictionaryScraper()

@bot.event
async def on_ready():
    """Event handler when bot is ready"""
    logger.info(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="!define commands"
    ))

@bot.command(name='define')
async def define(ctx, word: str):
    """
    Command to get word definition
    Usage: !define <word>
    """
    logger.info(f"Received define command for word: {word}")
    async with ctx.typing():
        # Get word information
        word_info = dictionary.get_word_info(word)

        if word_info:
            # Format and send response
            embed = format_dictionary_response(word, word_info)
            await ctx.send(embed=embed)
            logger.info(f"Successfully sent definition for word: {word}")
        else:
            # Send error message
            await ctx.send(ERROR_MESSAGE.format(word=word))
            logger.warning(f"Could not find definition for word: {word}")

@bot.command(name='dict_help')
async def dictionary_help(ctx):
    """Shows dictionary bot help message"""
    logger.info("Received help command")
    await ctx.send(HELP_MESSAGE)

@define.error
async def define_error(ctx, error):
    """Error handler for define command"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a word to define. Usage: !define <word>")
        logger.error("Missing word argument in define command")
    else:
        await ctx.send("An error occurred while processing your request. Please try again later.")
        logger.error(f"Unexpected error in define command: {str(error)}")

def run_bot():
    """Runs the Discord bot"""
    if not DISCORD_TOKEN:
        logger.error("Discord token not found in environment variables")
        return

    logger.info("Starting Discord bot...")
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run_bot()
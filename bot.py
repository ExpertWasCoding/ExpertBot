import discord
from discord.ext import commands
from bot_token import token_bot

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

# Load cogs
initial_extensions = ['cogs.server', 'cogs.game']

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

# Load bot token and start the bot
bot.run(token_bot)

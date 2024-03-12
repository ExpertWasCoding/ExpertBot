import discord
from discord.ext import commands
from bot_token import token_bot


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)


@bot.command()
async def start(ctx, nplayers):
    await ctx.send(f'Game started with {nplayers} players')


@bot.command()
async def ping(ctx, arg):
    await ctx.send(arg)

bot.run(token_bot)

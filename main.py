import discord
from discord.ext import commands
from bot_token import token_bot
import asyncio
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)


server_data = {}

try:
    with open('server_data.json', 'r') as f:
        server_data = json.load(f)
except FileNotFoundError:
    server_data = server_data


def save_server_data():
    with open('server_data.json', 'w') as f:
        json.dump(server_data, f)


@bot.event
async def on_guild_join(guild):
    server_data[guild.id] = {'IsRunning': False}
    print(guild.id)
    save_server_data()


@bot.event
async def on_guild_remove(guild):
    del server_data[guild.id]


@bot.command()
async def id(ctx):
    await ctx.send(ctx.guild.id)


@bot.command()
async def start(ctx, nplayers):
    server_id = ctx.guild.id
    print(server_id)
    IsRunning = server_data.get(server_id, {}).get('IsRunning', False)

    if IsRunning:
        await ctx.send("already running lil bro")
        return
    nplayers = int(nplayers)
    if nplayers > 9:
        await ctx.send(f'number of players {nplayers}, is too large, the max number of players is 9')
        return
    elif nplayers < 2:
        await ctx.send("not enough players")
        return
    elif nplayers == 2:
        await ctx.send(f"Game started but the recommended number of players is greater than {nplayers}")
        IsRunning = True
    else:
        await ctx.send(f'Game started with {nplayers} players, {ctx.author.mention} type ">play" to join.')
    server_data[server_id]['IsRunning'] = True

    def check(msg, mentioned=None):
        if msg.author == ctx.author and msg.content.lower() == '>play':
            server_data[server_id]['IsRunning'] = True
    try:
        await bot.wait_for('message', timeout=60, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timeout. Not enough players.')
    else:
        await ctx.send(f'{ctx.author.mention} joined the game!')


@bot.command()
async def userping(ctx, arg):
    await ctx.send("dwiajo")


bot.run(token_bot)

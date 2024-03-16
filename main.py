import discord
from discord.ext import commands
from bot_token import token_bot
import asyncio
import pymongo


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["server_data"]
collection = db["servers"]
server_data = {}


for document in collection.find():
    server_id = document["server_id"]
    is_running = document["IsRunning"]
    server_data[server_id] = {"IsRunning": is_running}


@bot.event
async def on_guild_join(guild):
    server_data[guild.id] = {"IsRunning": False}
    data = {"server_id": guild.id, "IsRunning": False}
    collection.insert_one(data)


@bot.event
async def on_guild_remove(guild):
    collection.delete_one({"server_id": guild.id})
    del server_data[guild.id]


@bot.command()
async def id(ctx):
    await ctx.send(ctx.guild.id)


@bot.command()
async def start(ctx, nplayers):
    server_id = ctx.guild.id
    IsRunning = server_data.get(server_id, {}).get("IsRunning", False)
    if IsRunning:
        await ctx.send("already running lil bro")
        return
    nplayers = int(nplayers)
    if nplayers > 9:
        await ctx.send(
            f"number of players {nplayers}, is too large"
            "the max number of players is 9"
        )
        return
    elif nplayers < 2:
        await ctx.send("not enough players")
        return
    elif nplayers == 2:
        await ctx.send(
            f"Game started but the recommended number of players is"
            f" greater than {nplayers}"
        )
    else:
        await ctx.send(f"game started with {nplayers} players")
    players = []
    server_data[server_id]["IsRunning"] = True

    def check_message(message):
        return message.guild == ctx.guild and message.content == "play"

    while len(players) < nplayers:
        try:
            message = await bot.wait_for("message", check=check_message, timeout=60)
            if message.author.mention in players:
                await ctx.send(
                    f"this nigga {message.author.mention}" "is already there"
                )
            else:
                players.append(message.author.mention)
                await ctx.send(
                    f"{message.author} has joined the game,"
                    f" total players are {players}"
                )
        except asyncio.TimeoutError:
            ctx.send("timed out")
            break


@bot.command()
async def userping(ctx):
    await ctx.send(ctx.author.mention)
    return


@bot.command()
async def mentioned(ctx, arg):
    await ctx.send(f"{ctx.author.mention} mentioned {arg}")


bot.run(token_bot)

import discord
from discord.ext import commands
from bot_token import token_bot
import asyncio
import pymongo
import random as rand

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["server_data"]
collection = db["servers"]
server_data = {}
server_deck = {}

for document in collection.find():
    server_id = document["server_id"]
    is_running = document["IsRunning"]
    server_data[server_id] = {"IsRunning": is_running}


def two_random_numbers():
    list_of_two_rand_nums = []
    for i in range(2):
        two_nums = rand.randint(0, 53)
        list_of_two_rand_nums.append(two_nums)
    return list_of_two_rand_nums


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
            await ctx.send("timed out")
            break
    server_deck[ctx.guild.id] = create_deck()
    players_with_cards = {}
    for player in players:
        random_indices = two_random_numbers()
        cards = [server_deck[ctx.guild.id][index] for index in random_indices]
        players_with_cards[player] = cards
    await ctx.send(players_with_cards)


def create_deck():
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    values = [
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "Jack",
        "Queen",
        "King",
        "Ace",
    ]
    deck = []
    for suit in suits:
        for value in values:
            card = f"{value} of {suit}"
            deck.append(card)
    return deck


@bot.command()
async def userping(ctx):
    await ctx.send(ctx.author.mention)
    return


@bot.command()
async def mentioned(ctx, arg):
    await ctx.send(f"{ctx.author.mention} mentioned {arg}")


bot.run(token_bot)

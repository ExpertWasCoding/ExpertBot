import random as rand
import pymongo
import asyncio
from bot_token import token_bot
from discord.ext import commands
import discord
import utils


# rand comment for future
# max players exceeded warning on "play"
# index range error handle
# add the 12-4 thingy

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


async def check_player_count(ctx, nplayers):
    if nplayers is None:
        await ctx.send('Please specify the number of players. Example: ">start 2"')
        return False

    nplayers = int(nplayers)
    if nplayers > 9:
        await ctx.send(
            f"Number of players {nplayers} is too large. The maximum number of players is 9."
        )
        return False
    elif nplayers < 2:
        await ctx.send("Not enough players. The minimum number of players is 2.")
        return False
    elif nplayers == 2:
        await ctx.send(
            f"Game started but the recommended number of players is greater than {nplayers}."
        )
    return True


@bot.command()
async def start(ctx, nplayers=None):
    if nplayers is None:
        await ctx.send('please specify the number of players example -> ">start 2"')
        return

    server_id = ctx.guild.id

    IsRunning = server_data.get(server_id, {}).get("IsRunning", False)
    if IsRunning:
        await ctx.send("already running lil bro")
        return

    nplayers = int(nplayers)
    if await check_player_count(ctx, nplayers):
        await ctx.send("starting")
    else:
        return

    players = []
    player_id = []
    player_with_ids = {}
    server_data[server_id]["IsRunning"] = True

    def check_message(message):
        return message.guild == ctx.guild and message.content == "play"

    while len(players) < nplayers:
        try:
            message = await bot.wait_for("message", check=check_message, timeout=60)
            if message.author.mention in players:
                await ctx.send(f"{message.author.mention}" "is already there")
            else:
                players.append(message.author.mention)
                player_id.append(message.author)
                player_with_ids[message.author.mention] = message.author
                await ctx.send(
                    f"{message.author} has joined the game,"
                    f" total players are {players}"
                )
                try:
                    await message.author.send("you are playing")
                except discord.errors.Forbidden:
                    await ctx.send("DM's not open")
                    break
        except asyncio.TimeoutError:
            await ctx.send("timed out")
            break
    server_deck[ctx.guild.id] = utils.create_deck()
    players_with_cards = {}
    for player in players:
        random_indices = utils.random_numbers(2)
        cards = [server_deck[ctx.guild.id][index] for index in random_indices]
        players_with_cards[player] = cards
    for player in players:
        await player_with_ids[player].send(
            f"your cards are {players_with_cards[player]}"
        )

    for cards in players_with_cards.values():
        for card in cards:
            server_deck[ctx.guild.id].remove(card)
    # await ctx.send(len(server_deck[ctx.guild.id]))


@bot.command()
async def userping(ctx):
    await ctx.send(ctx.author.mention)
    return


@bot.command()
async def dmme(ctx, arg):
    await ctx.send(f"dm'ed {ctx.author.mention} {arg}")
    await ctx.author.send(f"{arg}")


@bot.command()
async def mentioned(ctx, arg):
    await ctx.send(f"{ctx.author.mention} mentioned {arg}")


@bot.command()
async def dm_user(ctx, user_mention: discord.Member, *, message: str):
    # Check if the user has permissions to send DMs
    if not user_mention.dm_channel:
        await user_mention.create_dm()

    # Send the message
    await user_mention.send(message)
    await ctx.send(f"Message sent to {user_mention.mention}")


bot.run(token_bot)

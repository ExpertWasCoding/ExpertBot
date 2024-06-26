import pymongo
import asyncio
from discord.ext import commands
import discord
import utils
from dotenv import load_dotenv
import os

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
    if await utils.check_player_count(ctx, nplayers):
        await ctx.send("starting")
    else:
        return

    players = []
    player_id = []
    server_bar = {}
    server_bar[ctx.guild.id] = 0
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
                await ctx.send(f"{message.author} has joined the game")
                try:
                    await message.author.send("you are playing")
                except discord.errors.Forbidden:
                    await ctx.send("DM's not open")
                    break
        except asyncio.TimeoutError:
            await ctx.send("timed out")
            server_data[server_id]["IsRunning"] = True
            break
    await ctx.send(f"players playing are {players}")
    server_deck[ctx.guild.id] = utils.create_deck()
    players_with_cards = {}
    players_money_on_table = {}
    players_with_money = {}
    players_with_points = {}
    player_with_status = {}
    table = {"cards": [], "money": 0}
    for player in players:
        random_indices = utils.random_numbers(2)
        cards = []
        for index in random_indices:
            cards.append(server_deck[ctx.guild.id][index])
            del server_deck[ctx.guild.id][index]
        player_with_status[player] = False
        players_with_cards[player] = cards
        players_with_points[player] = 0
        players_money_on_table[player] = 0
        players_with_money[player] = 1000
    for player in players:
        await player_with_ids[player].send(
            f"your cards are {players_with_cards[player]} and money is {players_with_money[player]}"
        )

    table["cards_on_table"] = []
    await start_game_loop(
        ctx,
        players,
        player_with_ids,
        players_with_cards,
        players_with_money,
        table,
        player_with_status,
        players_with_points,
        players_money_on_table,
        server_bar,
    )


async def start_game_loop(
    ctx,
    players,
    player_with_ids,
    players_with_cards,
    players_with_money,
    table,
    player_with_status,
    players_with_points,
    players_money_on_table,
    server_bar,
):
    current_player_index = 0
    global game_over
    game_over = False
    turn_number = 0
    while not game_over:
        if turn_number == len(players):
            random_two = utils.random_numbers(2, 53 - (len(players) * 2))
            for index in random_two:
                table["cards_on_table"].append(
                    server_deck[ctx.guild.id][index])
                del server_deck[ctx.guild.id][index]
            await ctx.send(f"{table['cards_on_table']} are now on table")
        elif turn_number == len(players) * 2:
            random_one = utils.random_numbers(1, 51 - (len(players) * 2))
            table["cards_on_table"].append(
                server_deck[ctx.guild.id][random_one])
            del server_deck[ctx.guild.id][random_one]
        elif turn_number == len(players) * 3:
            random_one = utils.random_numbers(1, 50 - (len(players) * 2))
            table["cards_on_table"].append(
                server_deck[ctx.guild.id][random_one])
            del server_deck[ctx.guild.id][random_one]
        elif turn_number == len(players) * 4:
            random_one = utils.random_numbers(1, 49 - (len(players) * 2))
            table["cards_on_table"].append(
                server_deck[ctx.guild.id][random_one])
            del server_deck[ctx.guild.id][random_one]
        elif turn_number == len(players) * 5:
            random_one = utils.random_numbers(1, 48 - (len(players) * 2))
            table["cards_on_table"].append(
                server_deck[ctx.guild.id][random_one])
            del server_deck[ctx.guild.id][random_one]

        current_player = players[current_player_index]

        await ctx.send(f"{player_with_ids[current_player]} It's your turn.")

        await player_with_ids[current_player].send(
            f"Your cards are {players_with_cards[current_player]} "
            f"and your money is {players_with_money[current_player]}"
        )

        action = await get_player_action(ctx, current_player)
        await process_player_action(
            ctx,
            action,
            current_player,
            players_with_money,
            table,
            player_with_status,
            players_money_on_table,
            server_bar,
        )
        players_ready_to_end = []
        for player in players:
            if player_with_status[player] == "folded":
                continue
            else:
                players_ready_to_end.append(player)

        all_players_ready = all(
            player_with_status[player] for player in players_ready_to_end
        )
        if all_players_ready or turn_number == len(players) * 5:
            for player in players_ready_to_end:
                await game_over_check(
                    ctx,
                    player,
                    players_with_money,
                    player_with_status,
                    players_with_cards,
                    table,
                    players_with_points,
                    players_money_on_table,
                )
            won_player = max(players_with_points, key=players_with_points.get)
            await ctx.send(f"{won_player} has won the game")
            break

        turn_number += 1
        current_player_index = (current_player_index + 1) % len(players)


async def get_player_action(ctx, current_player):
    def check(message):
        return message.author.mention == current_player

    try:
        message = await bot.wait_for("message", check=check, timeout=60)
        message = message.content
        splitted_message = message.split(" ")
        if splitted_message[0] == "fold":
            await ctx.send("player folded")
            return "fold"
        elif splitted_message[0] == "call":
            try:
                return [splitted_message[0], splitted_message[1]]
            except ValueError:
                await ctx.send(
                    f"{current_player.mention} is not a number, pls try again"
                )
                await get_player_action(ctx, current_player)
        elif splitted_message[0] == "raise":
            try:
                await ctx.send(f"raised raised {int(splitted_message[1])}")
                return [splitted_message[0], splitted_message[1]]
            except ValueError:
                await ctx.send("not a number pls try again.")
                await get_player_action(ctx, current_player)
        else:
            await get_player_action(ctx, current_player)
    except asyncio.TimeoutError:
        await ctx.send(f"{current_player.mention} took too long to make a move.")
        return


async def game_over_check(
    ctx,
    player,
    players_with_money,
    player_with_status,
    player_with_cards,
    table,
    players_with_points,
    players_money_on_table,
):
    list_cards = []
    for card in table["cards_on_table"]:
        list_cards.append(card)
    for card in player_with_cards[player]:
        list_cards.append(card)

    points = utils.score_calculate(list_cards)
    players_with_points[player] = points
    won_player = max(players_with_points, key=players_with_points.get)
    players_with_money[won_player] += table["money"]
    table["money"] = 0


async def process_player_action(
    ctx,
    action,
    current_player,
    player_with_money,
    table,
    player_with_status,
    player_money_on_table,
    server_bar,
):
    if not player_with_status[current_player]:
        if isinstance(action, list):
            if action[0] == "call":
                if player_with_money[current_player] >= int(action[1]):
                    player_with_money[current_player] -= int(action[1])
                    player_money_on_table[current_player] += int(action[1])
                    table["money"] += int(action[1])
                    player_with_status[current_player] = True
                else:
                    await ctx.send("Not enough money")
            elif action[0] == "raise":
                if (
                    player_with_money[current_player] >= int(action[1])
                    and int(action[1]) > server_bar[ctx.guild.id]
                ):
                    player_with_status[current_player] = True
                    player_with_money[current_player] -= int(action[1])
                    table["money"] += int(action[1])
                else:
                    await ctx.send("Not enough money")
    elif player_with_status[current_player]:
        await ctx.send(f"{current_player} is folded")
    elif isinstance(action, str):
        if action == "fold":
            player_with_status[current_player] = "folded"
            await ctx.send("player folded successfully")
    else:
        await ctx.send("Some random error occured")


@bot.command()
async def userping(ctx):
    await ctx.send(ctx.author.mention)
    return


@bot.command()
async def dmme(ctx, arg):
    await ctx.send(f"dm'ed {ctx.author.mention} {arg}")
    await ctx.author.send(f"{arg}")


@bot.command()
async def debug(ctx):
    await ctx.send(f"{ctx.author}")


@bot.command()
async def mentioned(ctx, arg):
    await ctx.send(f"{ctx.author.mention} mentioned {arg}")


@bot.command()
async def dm_user(ctx, user_mention: discord.Member, *, message: str):
    if not user_mention.dm_channel:
        await user_mention.create_dm()

    await user_mention.send(message)
    await ctx.send(f"Message sent to {user_mention.mention}")


@bot.command()
async def stop_game(ctx):
    global game_over
    server_id = ctx.guild.id
    IsRunning = server_data.get(server_id, {}).get("IsRunning", False)

    if not IsRunning:
        await ctx.send("No game is currently running.")
        return
    game_over = True
    server_data[server_id]["IsRunning"] = False
    server_deck[ctx.guild.id] = []

    await ctx.send("Game stopped.")


load_dotenv()
token_bot = os.getenv("token_bot")
bot.run(token_bot)

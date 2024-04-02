import pymongo
import asyncio
from bot_token import token_bot
from discord.ext import commands
import discord
import utils

# adding a debugger decorator??
# max players exceeded warning on "play"
# index range error handle
# add the 12-4 thingy
# add a stop command
# should have used hash tables fuck
# can't commit today cuz of high fever
# ^^
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
            server_data[server_id]["IsRunning"] = True
            break
    server_deck[ctx.guild.id] = utils.create_deck()
    players_with_cards = {}
    players_with_money = {}
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
        players_with_money[player] = 1000
    for player in players:
        await player_with_ids[player].send(
            f"your cards are {players_with_cards[player]} and money is {players_with_money[player]}"
        )

    for cards in players_with_cards.values():
        for card in cards:
            if card in server_deck[ctx.guild.id]:
                server_deck[ctx.guild.id].remove(card)
                table["cards"].append(card)
            else:
                await ctx.send(f"{card} not found")
    table["cards_on_table"] = []
    await start_game_loop(
        ctx,
        players,
        player_with_ids,
        players_with_cards,
        players_with_money,
        table,
        player_with_status,
    )
    # await ctx.send(len(server_deck[ctx.guild.id]))


async def start_game_loop(
    ctx,
    players,
    player_with_ids,
    players_with_cards,
    players_with_money,
    table,
    player_with_status,
):
    current_player_index = 0
    game_over = False
    turn_number = 0
    # continue here
    while not game_over:
        if turn_number == len(players):
            random_two = utils.random_numbers(2, 53 - (len(players) * 2))
            for index in random_two:
                table["cards_on_table"].append(
                    server_deck[ctx.guild.id][index])
                del server_deck[ctx.guild.id][index]
            await ctx.send(f"{table['cards_on_table']} are now on table")

        current_player = players[current_player_index]

        # Notify the current player that it's their turn
        await ctx.send(f"{player_with_ids[current_player]} It's your turn.")

        # Show the player their cards and current money
        await player_with_ids[current_player].send(
            f"Your cards are {players_with_cards[current_player]} and your money is {players_with_money[current_player]}"
        )

        # Wait for the player's action (like fold, call, raise, etc.)
        action = await get_player_action(ctx, current_player)
        await ctx.send(f"{action}")
        await process_player_action(
            ctx, action, current_player, players_with_money, table, player_with_status
        )
        all_players_ready = all(
            player_with_status[player] for player in players)
        if all_players_ready:
            for player in players:
                await ctx.send("ending the game")
                await game_over_check(
                    ctx,
                    player,
                    players_with_money,
                    player_with_status,
                    players_with_cards,
                )
            break
            # add logic to check if all player_with_status[player] == True

        # Check if the game is over or move to the next player's turn
        turn_number += 1
        current_player_index = (current_player_index + 1) % len(players)
        # game_over = check_game_over_condition()


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
                await ctx.send(f"called for {int(splitted_message[1])}")
                return [splitted_message[0], splitted_message[1]]
            except ValueError:
                await ctx.send(
                    f"{current_player.mention} is not a number, pls try again"
                )
                await get_player_action(ctx, current_player)
        elif splitted_message[0] == "raise":
            try:
                await ctx.send(f"raised for {int(splitted_message[1])}")
                return [splitted_message[0], splitted_message[1]]
            except ValueError:
                await ctx.send(
                    f"{current_player.mention} is not a number, pls try again"
                )
                await get_player_action(ctx, current_player)

    except asyncio.TimeoutError:
        await ctx.send(f"{current_player.mention} took too long to make a move.")
        return


async def game_over_check(
    ctx, player, players_with_money, player_with_status, player_with_cards
):
    pass


async def process_player_action(
    ctx, action, current_player, player_with_money, table, player_with_status
):
    if player_with_status[current_player] == False:
        if isinstance(action, list):
            if action[0] == "call":
                if player_with_money[current_player] >= int(action[1]):
                    player_with_money[current_player] -= int(action[1])
                    table["money"] += int(action[1])
                    player_with_status[current_player] = True
                else:
                    await ctx.send("Not enough money")
            elif action[0] == "raise":
                if player_with_money[current_player] >= int(action[1]):
                    player_with_money[current_player] -= int(action[1])
                    table["money"] += int(action[1])
                else:
                    await ctx.send("Not enough money")
    elif player_with_status[current_player]:
        await ctx.send(f"{current_player} is folded")
    elif isinstance(action, str):
        if action == "fold":
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
    # Check if the user has permissions to send DMs
    if not user_mention.dm_channel:
        await user_mention.create_dm()

    # Send the message
    await user_mention.send(message)
    await ctx.send(f"Message sent to {user_mention.mention}")


@bot.command()
async def stop_game(ctx):
    pass


# logic to stop game

bot.run(token_bot)

# Code below is written by chatgpt, do not pay attention it is for reference during card permutation
#
# from collections import Counter
#
#
# # Function to check for a straight
# def has_straight(hand_values):
#     return max(hand_values) - min(hand_values) == 4 and len(set(hand_values)) == 5
#
#
# # Function to check for a flush
# def has_flush(hand_suits):
#     return len(set(hand_suits)) == 1
#
#
# # Function to check the hand and determine the best possible hand
# def check_hand(cards):
#     values = {
#         "2": 2,
#         "3": 3,
#         "4": 4,
#         "5": 5,
#         "6": 6,
#         "7": 7,
#         "8": 8,
#         "9": 9,
#         "T": 10,
#         "J": 11,
#         "Q": 12,
#         "K": 13,
#         "A": 14,
#     }
#     suits = [card[1] for card in cards]
#     hand_values = [values[card[0]] for card in cards]
#     hand_values.sort()
#
#     # Check for straight flush, straight, and flush
#     if has_flush(suits) and has_straight(hand_values):
#         return "Straight Flush"
#     elif has_flush(suits):
#         return "Flush"
#     elif has_straight(hand_values):
#         return "Straight"
#
#     # Check for four of a kind
#     if 4 in Counter(hand_values).values():
#         return "Four of a Kind"
#
#     # Check for full house
#     if set(Counter(hand_values).values()) == {2, 3}:
#         return "Full House"
#
#     # Check for three of a kind
#     if 3 in Counter(hand_values).values():
#         return "Three of a Kind"
#
#     # Check for two pairs
#     if list(Counter(hand_values).values()).count(2) == 2:
#         return "Two Pair"
#
#     # Check for one pair
#     if 2 in Counter(hand_values).values():
#         return "One Pair"
#
#     # Otherwise, the best hand is high card
#     return "High Card"

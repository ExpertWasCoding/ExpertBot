import random as rand


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


def random_numbers(n, _range=53):
    list_of_rand_nums = []
    for i in range(n):
        nums = rand.randint(0, _range)
        _range -= 1
        list_of_rand_nums.append(nums)
    return list_of_rand_nums


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

#idk how this is working
def score_calculate(list_of_cards):
    player_points = 0

    card_values = {
        "Ace": 14,
        "King": 13,
        "Queen": 12,
        "Jack": 11,
        "10": 10,
        "9": 9,
        "8": 8,
        "7": 7,
        "6": 6,
        "5": 5,
        "4": 4,
        "3": 3,
        "2": 2,
    }

    rank_counts = {}
    for card in list_of_cards:
        value = card.split()[0]
        rank_counts[value] = rank_counts.get(value, 0) + 1

    for value, count in rank_counts.items():
        if count == 4:
            player_points += 100  # Four of a kind
        elif count == 3:
            player_points += 50  # Three of a kind
        elif count == 2:
            player_points += 20  # One pair
        player_points += card_values[value] * count

    return player_points


def debugger(func):
    def debugger_func(*args, **kwargs):
        print("starting debugger")
        print(f"running {debugger_func.__name__} with args {args}, {kwargs}")
        print("function ended")
        return func(*args, **kwargs)

    return debugger_func

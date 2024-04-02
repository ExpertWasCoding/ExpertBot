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


def debugger(func):
    def debugger_func(*args, **kwargs):
        print("starting debugger")
        print(f"running {debugger_func.__name__} with args {args}, {kwargs}")
        print("function ended")
        return func(*args, **kwargs)

    return debugger_func

import random as rand


def random_numbers(n, _range=53):
    list_of_rand_nums = []
    for i in range(n):
        nums = rand.randint(0, _range)
        list_of_rand_nums.append(nums)
    return list_of_rand_nums


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

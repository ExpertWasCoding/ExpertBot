import random as rand

b = []


def two_random_numbers():
    for i in range(2):
        c = rand.randint(0, 53)
        b.append(c)


two_random_numbers()
print(b)

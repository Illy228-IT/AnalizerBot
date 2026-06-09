import random

from scanner.coin_list import TOP_ALTCOINS

used_coins = []


def get_next_coin():
    global used_coins

    available = [
        coin
        for coin in TOP_ALTCOINS
        if coin not in used_coins
    ]

    if not available:
        used_coins = []
        available = TOP_ALTCOINS.copy()

    coin = random.choice(available)

    used_coins.append(coin)

    return coin

from scanner.coin_selector import get_next_coin
from analyzers.coin_analyzer import CoinAnalyzer


class CoinScanner:
    def __init__(self):
        self.coin_analyzer = CoinAnalyzer()

    def scan_next_coin(self) -> dict:
        symbol = get_next_coin()
        return self.coin_analyzer.analyze(symbol)
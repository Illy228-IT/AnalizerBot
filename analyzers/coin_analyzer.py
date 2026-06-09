import random

from data.bybit_client import BybitClient
from config import TIMEFRAMES

from smc.structure import MarketStructure
from smc.liquidity import LiquidityAnalyzer
from smc.ranges import RangeDetector
from smc.premium_discount import PremiumDiscount
from smc.fvg import FVGAnalyzer
from smc.order_blocks import OrderBlockAnalyzer


class CoinAnalyzer:
    def __init__(self):
        self.client = BybitClient()

        self.structure = MarketStructure()
        self.liquidity = LiquidityAnalyzer()
        self.ranges = RangeDetector()
        self.premium_discount = PremiumDiscount()
        self.fvg = FVGAnalyzer()
        self.order_blocks = OrderBlockAnalyzer()

    def analyze(self, symbol: str) -> dict:
        try:
            df_4h = self.client.get_klines(
                symbol,
                TIMEFRAMES["4H"]
            )

            df_1h = self.client.get_klines(
                symbol,
                TIMEFRAMES["1H"]
            )

            df_15m = self.client.get_klines(
                symbol,
                TIMEFRAMES["15M"]
            )

            return {
                "symbol": symbol,
                "price": round(
                    float(df_15m["close"].iloc[-1]),
                    6
                ),

                "4H": self._analyze_timeframe(df_4h),
                "1H": self._analyze_timeframe(df_1h),
                "15M": self._analyze_timeframe(df_15m)
            }

        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e)
            }

    def _analyze_timeframe(self, df) -> dict:
        structure = self.structure.analyze(df)

        return {
            "market_structure": structure,
            "range": self.ranges.analyze(df),
            "premium_discount": self.premium_discount.analyze(df),
            "liquidity": self.liquidity.analyze(df),
            "fvg": self.fvg.analyze(df),
            "order_blocks": self.order_blocks.analyze(df)
        }

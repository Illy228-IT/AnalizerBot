from data.bybit_client import BybitClient
from config import TIMEFRAMES

from smc.structure import MarketStructure
from smc.ranges import RangeDetector
from smc.premium_discount import PremiumDiscount
from smc.liquidity import LiquidityAnalyzer


class BTCAnalyzer:
    def __init__(self):
        self.client = BybitClient()

        self.structure = MarketStructure()
        self.ranges = RangeDetector()
        self.premium_discount = PremiumDiscount()
        self.liquidity = LiquidityAnalyzer()

    def analyze(self) -> dict:
        try:
            df_4h = self.client.get_klines("BTCUSDT", TIMEFRAMES["4H"])
            df_1h = self.client.get_klines("BTCUSDT", TIMEFRAMES["1H"])
            df_15m = self.client.get_klines("BTCUSDT", TIMEFRAMES["15M"])

            btc_4h = self._analyze_timeframe(df_4h)
            btc_1h = self._analyze_timeframe(df_1h)
            btc_15m = self._analyze_timeframe(df_15m)

            bias = self._detect_btc_bias(btc_4h, btc_1h, btc_15m)

            return {
                "symbol": "BTCUSDT",
                "price": round(float(df_15m["close"].iloc[-1]), 2),
                "4H": btc_4h,
                "1H": btc_1h,
                "15M": btc_15m,
                "bias": bias,
                "summary": self._build_summary(bias)
            }

        except Exception as e:
            return {
                "symbol": "BTCUSDT",
                "error": str(e),
                "bias": "UNKNOWN",
                "summary": "BTC context unavailable."
            }

    def _analyze_timeframe(self, df) -> dict:
        return {
            "market_structure": self.structure.analyze(df),
            "range": self.ranges.analyze(df),
            "premium_discount": self.premium_discount.analyze(df),
            "liquidity": self.liquidity.analyze(df)
        }

    def _detect_btc_bias(self, btc_4h: dict, btc_1h: dict, btc_15m: dict) -> str:
        trend_4h = btc_4h["market_structure"]["trend"]
        trend_1h = btc_1h["market_structure"]["trend"]
        trend_15m = btc_15m["market_structure"]["trend"]

        if trend_4h == "BULLISH" and trend_1h == "BULLISH":
            return "BULLISH"

        if trend_4h == "BEARISH" and trend_1h == "BEARISH":
            return "BEARISH"

        if trend_4h == "RANGE" or trend_1h == "RANGE":
            return "RANGE"

        if trend_4h == "BULLISH" and trend_1h == "BEARISH":
            return "PULLBACK_OR_REVERSAL"

        if trend_4h == "BEARISH" and trend_1h == "BULLISH":
            return "CORRECTION_AGAINST_TREND"

        if trend_15m == "RANGE":
            return "CHOPPY"

        return "MIXED"

    def _build_summary(self, bias: str) -> str:
        summaries = {
            "BULLISH": "BTC bullish — ринок підтримує LONG-сценарії по альтах.",
            "BEARISH": "BTC bearish — по альтах краще шукати SHORT або WAIT.",
            "RANGE": "BTC у range — потрібна обережність, не входити без сильного підтвердження.",
            "PULLBACK_OR_REVERSAL": "BTC 4H bullish, але 1H bearish — можливий pullback. LONG тільки після підтвердження.",
            "CORRECTION_AGAINST_TREND": "BTC 4H bearish, але 1H bullish — це може бути корекція. SHORT після підтвердження.",
            "CHOPPY": "BTC на 15M у шумі/range — краще не брати слабкі альт-сигнали.",
            "MIXED": "BTC має змішаний контекст — сигнали по альтах треба фільтрувати жорсткіше.",
            "UNKNOWN": "BTC context unavailable."
        }

        return summaries.get(bias, "BTC context unclear.")

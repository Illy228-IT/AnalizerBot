from data.tradingview_client import TradingViewClient

from smc.structure import MarketStructure
from smc.ranges import RangeDetector


class BTCDAnalyzer:
    def __init__(self):
        self.client = TradingViewClient()

        self.structure = MarketStructure()
        self.ranges = RangeDetector()

    def analyze(self) -> dict:
        df = self.client.get_btcd_1h()

        if df is None or len(df) < 50:
            return {
                "symbol": "BTC.D",
                "last_close": None,
                "trend": "UNKNOWN",
                "pressure": "NEUTRAL",
                "description": "BTC.D не вдалося отримати."
            }

        structure = self.structure.analyze(df)
        range_data = self.ranges.analyze(df)

        last_close = float(df["close"].iloc[-1])
        prev_close = float(df["close"].iloc[-24])

        change_percent = (
            (last_close - prev_close)
            / prev_close
        ) * 100

        trend = structure["trend"]

        bos = structure["bos"]
        choch = structure["choch"]

        pressure = self._detect_alt_pressure(
            trend,
            bos,
            choch,
            range_data
        )

        return {
            "symbol": "BTC.D",

            "last_close": round(
                last_close,
                4
            ),

            "change_percent": round(
                change_percent,
                2
            ),

            "trend": trend,

            "market_phase": structure[
                "market_phase"
            ],

            "bos": bos,

            "choch": choch,

            "range": range_data,

            "pressure": pressure,

            "description": self._build_description(
                pressure,
                trend
            )
        }

    def _detect_alt_pressure(
        self,
        trend,
        bos,
        choch,
        range_data
    ):
        if choch["detected"]:
            return "REVERSAL_WARNING"

        if trend == "BULLISH":
            return "NEGATIVE_FOR_ALTS"

        if trend == "BEARISH":
            return "POSITIVE_FOR_ALTS"

        if range_data["state"] in [
            "RANGE",
            "RANGE_MIDDLE"
        ]:
            return "NEUTRAL"

        return "MIXED"

    def _build_description(
        self,
        pressure,
        trend
    ):
        descriptions = {
            "NEGATIVE_FOR_ALTS":
                "BTC.D має bullish структуру. Гроші заходять у BTC, альтам важче рости.",

            "POSITIVE_FOR_ALTS":
                "BTC.D має bearish структуру. Капітал частіше перетікає в альткоїни.",

            "REVERSAL_WARNING":
                "На BTC.D є CHOCH. Можлива зміна ринкового режиму для альтів.",

            "NEUTRAL":
                "BTC.D знаходиться у range. Явної переваги ні для BTC, ні для альтів немає.",

            "MIXED":
                "Контекст BTC.D змішаний."
        }

        return descriptions.get(
            pressure,
            "Контекст BTC.D невизначений."
        )

from data.tradingview_client import TradingViewClient


class BTCDAnalyzer:
    def __init__(self):
        self.client = TradingViewClient()

    def analyze(self) -> dict:
        df = self.client.get_btcd_1h()

        if df is None:
            return {
                "symbol": "BTC.D",
                "last_close": None,
                "change_percent": None,
                "trend": "UNKNOWN",
                "pressure": "NEUTRAL",
                "description": "BTC.D не вдалося отримати. Аналіз робиться без домінації."
            }

        last_close = float(df["close"].iloc[-1])
        prev_close = float(df["close"].iloc[-20])

        change_percent = ((last_close - prev_close) / prev_close) * 100

        if change_percent > 0.35:
            trend = "RISING"
            pressure = "NEGATIVE_FOR_ALTS"
            description = "BTC.D росте — альткоїнам важче рости."
        elif change_percent < -0.35:
            trend = "FALLING"
            pressure = "POSITIVE_FOR_ALTS"
            description = "BTC.D падає — альткоїнам легше показувати силу."
        else:
            trend = "SIDEWAYS"
            pressure = "NEUTRAL"
            description = "BTC.D у боковику — сильного тиску на альти немає."

        return {
            "symbol": "BTC.D",
            "last_close": round(last_close, 4),
            "change_percent": round(change_percent, 2),
            "trend": trend,
            "pressure": pressure,
            "description": description
        }
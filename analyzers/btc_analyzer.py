from data.bybit_client import BybitClient
from config import TIMEFRAMES
from smc.structure import MarketStructure


class BTCAnalyzer:
    def __init__(self):
        self.client = BybitClient()
        self.structure = MarketStructure()

    def analyze(self) -> dict:
        df_4h = self.client.get_klines("BTCUSDT", TIMEFRAMES["4H"])
        df_1h = self.client.get_klines("BTCUSDT", TIMEFRAMES["1H"])

        structure_4h = self.structure.analyze(df_4h)
        structure_1h = self.structure.analyze(df_1h)

        return {
            "symbol": "BTCUSDT",
            "price": round(float(df_1h["close"].iloc[-1]), 2),
            "4h": structure_4h,
            "1h": structure_1h,
            "summary": self._build_summary(structure_4h, structure_1h)
        }

    def _build_summary(self, structure_4h: dict, structure_1h: dict) -> str:
        if structure_4h["trend"] == "BULLISH" and structure_1h["trend"] == "BULLISH":
            return "BTC bullish — ринок підтримує LONG-сценарії по альтах."

        if structure_4h["trend"] == "BEARISH" and structure_1h["trend"] == "BEARISH":
            return "BTC bearish — по альтах краще шукати SHORT або WAIT."

        if structure_4h["trend"] == "RANGE":
            return "BTC у range — потрібна обережність, не входити без підтвердження."

        return "BTC має змішаний контекст — сигнали по альтах треба фільтрувати жорсткіше."
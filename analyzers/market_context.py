from analyzers.btc_analyzer import BTCAnalyzer
from analyzers.btcd_analyzer import BTCDAnalyzer


class MarketContextAnalyzer:
    def __init__(self):
        self.btc_analyzer = BTCAnalyzer()
        self.btcd_analyzer = BTCDAnalyzer()

    def analyze(self) -> dict:
        btc = self.btc_analyzer.analyze()
        btcd = self.btcd_analyzer.analyze()

        return {
            "btc": btc,
            "btcd": btcd,
            "summary": self._build_summary(btc, btcd)
        }

    def _build_summary(self, btc: dict, btcd: dict) -> str:
        btc_trend = btc["4h"]["trend"]
        btcd_pressure = btcd["pressure"]

        if btc_trend == "BULLISH" and btcd_pressure == "POSITIVE_FOR_ALTS":
            return "BTC bullish + BTC.D падає — найкращий фон для LONG по сильних альтах."

        if btc_trend == "BEARISH" and btcd_pressure == "NEGATIVE_FOR_ALTS":
            return "BTC bearish + BTC.D росте — небезпечний фон для альтів, краще SHORT або WAIT."

        if btc_trend == "BULLISH" and btcd_pressure == "NEGATIVE_FOR_ALTS":
            return "BTC росте, але BTC.D теж росте — альти можуть рости слабше BTC."

        if btc_trend == "BEARISH" and btcd_pressure == "POSITIVE_FOR_ALTS":
            return "BTC падає, BTC.D падає — ринок слабкий, альти можуть бути нестабільні."

        return "Ринковий фон змішаний — потрібна обережність і підтвердження на 15M."
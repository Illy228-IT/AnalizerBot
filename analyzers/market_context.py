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
            "summary": self._build_summary(
                btc,
                btcd
            )
        }

    def _build_summary(
        self,
        btc: dict,
        btcd: dict
    ) -> str:

        try:
            btc_bias = btc.get(
                "bias",
                "UNKNOWN"
            )

            btcd_pressure = btcd.get(
                "pressure",
                "NEUTRAL"
            )

            if (
                btc_bias == "BULLISH"
                and btcd_pressure == "POSITIVE_FOR_ALTS"
            ):
                return (
                    "BTC bullish + BTC.D bearish. "
                    "Найкращий фон для LONG по сильних альтах."
                )

            if (
                btc_bias == "BEARISH"
                and btcd_pressure == "NEGATIVE_FOR_ALTS"
            ):
                return (
                    "BTC bearish + BTC.D bullish. "
                    "Небезпечний фон для альтів. "
                    "SHORT або WAIT."
                )

            if (
                btc_bias == "BULLISH"
                and btcd_pressure == "NEGATIVE_FOR_ALTS"
            ):
                return (
                    "BTC росте, але домінація теж росте. "
                    "Альти можуть відставати від BTC."
                )

            if (
                btc_bias == "BEARISH"
                and btcd_pressure == "POSITIVE_FOR_ALTS"
            ):
                return (
                    "BTC слабкий, BTC.D падає. "
                    "Ринок нестабільний, потрібне підтвердження."
                )

            if btc_bias == "RANGE":
                return (
                    "BTC знаходиться у range. "
                    "Для входів потрібні сильні підтвердження."
                )

            if btc_bias == "MIXED":
                return (
                    "Контекст BTC змішаний. "
                    "Фільтрація сигналів повинна бути жорсткою."
                )

            if btc_bias == "PULLBACK_OR_REVERSAL":
                return (
                    "BTC може бути в pullback або розвороті. "
                    "Краще чекати підтвердження."
                )

            if btc_bias == "CORRECTION_AGAINST_TREND":
                return (
                    "BTC показує корекцію проти старшого тренду."
                )

            return (
                "Ринковий фон змішаний. "
                "Потрібно підтвердження на 15M."
            )

        except Exception as e:
            return f"Market context error: {e}"

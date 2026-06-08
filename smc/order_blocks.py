class OrderBlockAnalyzer:
    def analyze(self, df) -> dict:
        recent = df.tail(120).reset_index(drop=True)

        return {
            "bullish_ob": self._find_bullish_ob(recent),
            "bearish_ob": self._find_bearish_ob(recent)
        }

    def _find_bullish_ob(self, df):
        for i in range(len(df) - 6, 5, -1):
            candle = df.iloc[i]
            next_candle = df.iloc[i + 1]

            is_down_candle = float(candle["close"]) < float(candle["open"])
            strong_bullish_displacement = (
                float(next_candle["close"]) > float(next_candle["open"])
                and float(next_candle["close"]) > float(candle["high"])
            )

            if is_down_candle and strong_bullish_displacement:
                return {
                    "type": "BULLISH_ORDER_BLOCK",
                    "low": round(float(candle["low"]), 6),
                    "high": round(float(candle["high"]), 6),
                    "open": round(float(candle["open"]), 6),
                    "close": round(float(candle["close"]), 6),
                    "time": str(candle["timestamp"]),
                    "displacement_time": str(next_candle["timestamp"]),
                    "description": "Последняя bearish свеча перед сильным движением вверх."
                }

        return None

    def _find_bearish_ob(self, df):
        for i in range(len(df) - 6, 5, -1):
            candle = df.iloc[i]
            next_candle = df.iloc[i + 1]

            is_up_candle = float(candle["close"]) > float(candle["open"])
            strong_bearish_displacement = (
                float(next_candle["close"]) < float(next_candle["open"])
                and float(next_candle["close"]) < float(candle["low"])
            )

            if is_up_candle and strong_bearish_displacement:
                return {
                    "type": "BEARISH_ORDER_BLOCK",
                    "low": round(float(candle["low"]), 6),
                    "high": round(float(candle["high"]), 6),
                    "open": round(float(candle["open"]), 6),
                    "close": round(float(candle["close"]), 6),
                    "time": str(candle["timestamp"]),
                    "displacement_time": str(next_candle["timestamp"]),
                    "description": "Последняя bullish свеча перед сильным движением вниз."
                }

        return None
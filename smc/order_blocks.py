class OrderBlockAnalyzer:
    def analyze(self, df) -> dict:
        recent = df.tail(150).reset_index(drop=True)

        if len(recent) < 30:
            return {
                "bullish_ob": None,
                "bearish_ob": None
            }

        return {
            "bullish_ob": self._find_bullish_ob(recent),
            "bearish_ob": self._find_bearish_ob(recent)
        }

    def _find_bullish_ob(self, df):
        for i in range(len(df) - 8, 5, -1):
            candle = df.iloc[i]
            next_candles = df.iloc[i + 1:i + 4]

            open_price = float(candle["open"])
            close_price = float(candle["close"])
            high = float(candle["high"])
            low = float(candle["low"])

            is_down_candle = close_price < open_price

            displacement_high = float(next_candles["high"].max())
            displacement_close = float(next_candles.iloc[-1]["close"])

            strong_bullish_displacement = (
                displacement_high > high
                and displacement_close > high
                and self._has_strong_body(next_candles, "bullish")
            )

            if is_down_candle and strong_bullish_displacement:
                ob = {
                    "type": "BULLISH_ORDER_BLOCK",
                    "direction": "LONG",
                    "low": round(low, 6),
                    "high": round(high, 6),
                    "mid": round((low + high) / 2, 6),
                    "open": round(open_price, 6),
                    "close": round(close_price, 6),
                    "time": str(candle["timestamp"]),
                    "displacement_time": str(next_candles.iloc[-1]["timestamp"]),
                    "mitigated": self._is_bullish_ob_mitigated(df, i, low, high),
                    "strength": self._classify_ob_strength(low, high, displacement_high),
                    "description": "Bullish OB: последняя bearish свеча перед сильным импульсом вверх."
                }

                return ob

        return None

    def _find_bearish_ob(self, df):
        for i in range(len(df) - 8, 5, -1):
            candle = df.iloc[i]
            next_candles = df.iloc[i + 1:i + 4]

            open_price = float(candle["open"])
            close_price = float(candle["close"])
            high = float(candle["high"])
            low = float(candle["low"])

            is_up_candle = close_price > open_price

            displacement_low = float(next_candles["low"].min())
            displacement_close = float(next_candles.iloc[-1]["close"])

            strong_bearish_displacement = (
                displacement_low < low
                and displacement_close < low
                and self._has_strong_body(next_candles, "bearish")
            )

            if is_up_candle and strong_bearish_displacement:
                ob = {
                    "type": "BEARISH_ORDER_BLOCK",
                    "direction": "SHORT",
                    "low": round(low, 6),
                    "high": round(high, 6),
                    "mid": round((low + high) / 2, 6),
                    "open": round(open_price, 6),
                    "close": round(close_price, 6),
                    "time": str(candle["timestamp"]),
                    "displacement_time": str(next_candles.iloc[-1]["timestamp"]),
                    "mitigated": self._is_bearish_ob_mitigated(df, i, low, high),
                    "strength": self._classify_ob_strength(low, high, displacement_low),
                    "description": "Bearish OB: последняя bullish свеча перед сильным импульсом вниз."
                }

                return ob

        return None

    def _has_strong_body(self, candles, direction: str) -> bool:
        strong_count = 0

        for _, candle in candles.iterrows():
            open_price = float(candle["open"])
            close_price = float(candle["close"])
            high = float(candle["high"])
            low = float(candle["low"])

            body = abs(close_price - open_price)
            full_range = high - low

            if full_range <= 0:
                continue

            body_ratio = body / full_range

            if direction == "bullish":
                if close_price > open_price and body_ratio >= 0.55:
                    strong_count += 1

            if direction == "bearish":
                if close_price < open_price and body_ratio >= 0.55:
                    strong_count += 1

        return strong_count >= 1

    def _is_bullish_ob_mitigated(self, df, ob_index: int, low: float, high: float) -> bool:
        future = df.iloc[ob_index + 4:]

        for _, candle in future.iterrows():
            candle_low = float(candle["low"])
            candle_close = float(candle["close"])

            if candle_low <= high and candle_close >= low:
                return True

        return False

    def _is_bearish_ob_mitigated(self, df, ob_index: int, low: float, high: float) -> bool:
        future = df.iloc[ob_index + 4:]

        for _, candle in future.iterrows():
            candle_high = float(candle["high"])
            candle_close = float(candle["close"])

            if candle_high >= low and candle_close <= high:
                return True

        return False

    def _classify_ob_strength(self, low: float, high: float, displacement_price: float) -> str:
        ob_range = abs(high - low)

        if ob_range <= 0:
            return "UNKNOWN"

        displacement = abs(displacement_price - high)

        ratio = displacement / ob_range

        if ratio >= 3:
            return "STRONG"
        if ratio >= 1.5:
            return "MEDIUM"

        return "WEAK"

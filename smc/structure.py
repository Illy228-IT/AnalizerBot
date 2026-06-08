class MarketStructure:
    def analyze(self, df) -> dict:
        swings = self._find_swings(df)

        trend = self._detect_trend(swings)
        bos = self._detect_bos(df, swings)
        choch = self._detect_choch(bos, trend)

        return {
            "trend": trend["trend"],
            "trend_score": trend["score"],
            "trend_reason": trend["reason"],
            "swings": swings,
            "bos": bos,
            "choch": choch
        }

    def _find_swings(self, df, left: int = 3, right: int = 3) -> dict:
        highs = []
        lows = []

        for i in range(left, len(df) - right):
            candle = df.iloc[i]

            window_high = df["high"].iloc[i - left:i + right + 1].max()
            window_low = df["low"].iloc[i - left:i + right + 1].min()

            if float(candle["high"]) == float(window_high):
                highs.append({
                    "type": "SWING_HIGH",
                    "price": round(float(candle["high"]), 6),
                    "time": str(candle["timestamp"])
                })

            if float(candle["low"]) == float(window_low):
                lows.append({
                    "type": "SWING_LOW",
                    "price": round(float(candle["low"]), 6),
                    "time": str(candle["timestamp"])
                })

        return {
            "last_highs": highs[-6:],
            "last_lows": lows[-6:]
        }

    def _detect_trend(self, swings: dict) -> dict:
        highs = swings["last_highs"]
        lows = swings["last_lows"]

        if len(highs) < 3 or len(lows) < 3:
            return {
                "trend": "UNKNOWN",
                "score": 0,
                "reason": "Недостаточно swing-точек"
            }

        lower_highs = 0
        higher_highs = 0

        for i in range(1, len(highs)):
            if highs[i]["price"] < highs[i - 1]["price"]:
                lower_highs += 1
            elif highs[i]["price"] > highs[i - 1]["price"]:
                higher_highs += 1

        lower_lows = 0
        higher_lows = 0

        for i in range(1, len(lows)):
            if lows[i]["price"] < lows[i - 1]["price"]:
                lower_lows += 1
            elif lows[i]["price"] > lows[i - 1]["price"]:
                higher_lows += 1

        bearish_score = lower_highs + lower_lows
        bullish_score = higher_highs + higher_lows

        if bearish_score >= bullish_score + 2:
            return {
                "trend": "BEARISH",
                "score": bearish_score,
                "reason": f"Больше LH/LL: bearish_score={bearish_score}, bullish_score={bullish_score}"
            }

        if bullish_score >= bearish_score + 2:
            return {
                "trend": "BULLISH",
                "score": bullish_score,
                "reason": f"Больше HH/HL: bullish_score={bullish_score}, bearish_score={bearish_score}"
            }

        return {
            "trend": "RANGE",
            "score": max(bearish_score, bullish_score),
            "reason": f"Нет явного преимущества: bearish_score={bearish_score}, bullish_score={bullish_score}"
        }

    def _detect_bos(self, df, swings: dict) -> dict:
        last_close = float(df["close"].iloc[-1])
        last_time = str(df["timestamp"].iloc[-1])

        highs = swings["last_highs"]
        lows = swings["last_lows"]

        if highs:
            last_swing_high = highs[-1]

            if last_close > last_swing_high["price"]:
                return {
                    "detected": True,
                    "type": "BULLISH_BOS",
                    "broken_level": last_swing_high["price"],
                    "broken_level_time": last_swing_high["time"],
                    "break_time": last_time,
                    "close_price": round(last_close, 6)
                }

        if lows:
            last_swing_low = lows[-1]

            if last_close < last_swing_low["price"]:
                return {
                    "detected": True,
                    "type": "BEARISH_BOS",
                    "broken_level": last_swing_low["price"],
                    "broken_level_time": last_swing_low["time"],
                    "break_time": last_time,
                    "close_price": round(last_close, 6)
                }

        return {
            "detected": False,
            "type": None
        }

    def _detect_choch(self, bos: dict, trend: dict) -> dict:
        if not bos["detected"]:
            return {
                "detected": False,
                "type": None
            }

        current_trend = trend["trend"]

        if current_trend == "BEARISH" and bos["type"] == "BULLISH_BOS":
            return {
                **bos,
                "type": "BULLISH_CHOCH"
            }

        if current_trend == "BULLISH" and bos["type"] == "BEARISH_BOS":
            return {
                **bos,
                "type": "BEARISH_CHOCH"
            }

        return {
            "detected": False,
            "type": None
        }
class MarketStructure:
    def analyze(self, df) -> dict:
        recent = df.tail(200).reset_index(drop=True)

        if len(recent) < 30:
            return {
                "trend": "UNKNOWN",
                "trend_score": 0,
                "trend_reason": "Недостаточно данных",
                "market_phase": "UNKNOWN",
                "swings": {
                    "last_highs": [],
                    "last_lows": [],
                    "structure_points": []
                },
                "bos": self._empty_bos(),
                "choch": self._empty_choch()
            }

        swings = self._find_swings(recent)

        trend = self._detect_trend(swings)
        bos = self._detect_bos(recent, swings, trend)
        choch = self._detect_choch(bos, trend)
        market_phase = self._detect_market_phase(trend, bos, choch)

        return {
            "trend": trend["trend"],
            "trend_score": trend["score"],
            "trend_reason": trend["reason"],
            "market_phase": market_phase,
            "swings": swings,
            "bos": bos,
            "choch": choch
        }

    def _find_swings(self, df, left: int = 3, right: int = 3) -> dict:
        highs = []
        lows = []

        for i in range(left, len(df) - right):
            candle = df.iloc[i]

            current_high = float(candle["high"])
            current_low = float(candle["low"])

            window_high = float(df["high"].iloc[i - left:i + right + 1].max())
            window_low = float(df["low"].iloc[i - left:i + right + 1].min())

            if current_high == window_high:
                highs.append({
                    "type": "SWING_HIGH",
                    "price": round(current_high, 6),
                    "time": str(candle["timestamp"]),
                    "index": i
                })

            if current_low == window_low:
                lows.append({
                    "type": "SWING_LOW",
                    "price": round(current_low, 6),
                    "time": str(candle["timestamp"]),
                    "index": i
                })

        highs = self._label_highs(highs)
        lows = self._label_lows(lows)

        structure_points = sorted(
            highs + lows,
            key=lambda x: x["index"]
        )[-12:]

        return {
            "last_highs": highs[-8:],
            "last_lows": lows[-8:],
            "structure_points": structure_points
        }

    def _label_highs(self, highs: list) -> list:
        labeled = []

        for i, high in enumerate(highs):
            item = high.copy()

            if i == 0:
                item["structure"] = "HIGH"
            else:
                previous = highs[i - 1]["price"]

                if high["price"] > previous:
                    item["structure"] = "HH"
                elif high["price"] < previous:
                    item["structure"] = "LH"
                else:
                    item["structure"] = "EQH"

            labeled.append(item)

        return labeled

    def _label_lows(self, lows: list) -> list:
        labeled = []

        for i, low in enumerate(lows):
            item = low.copy()

            if i == 0:
                item["structure"] = "LOW"
            else:
                previous = lows[i - 1]["price"]

                if low["price"] > previous:
                    item["structure"] = "HL"
                elif low["price"] < previous:
                    item["structure"] = "LL"
                else:
                    item["structure"] = "EQL"

            labeled.append(item)

        return labeled

    def _detect_trend(self, swings: dict) -> dict:
        highs = swings["last_highs"]
        lows = swings["last_lows"]

        if len(highs) < 3 or len(lows) < 3:
            return {
                "trend": "UNKNOWN",
                "score": 0,
                "reason": "Недостаточно swing-точек"
            }

        recent_highs = highs[-5:]
        recent_lows = lows[-5:]

        hh_count = sum(1 for h in recent_highs if h.get("structure") == "HH")
        lh_count = sum(1 for h in recent_highs if h.get("structure") == "LH")
        hl_count = sum(1 for l in recent_lows if l.get("structure") == "HL")
        ll_count = sum(1 for l in recent_lows if l.get("structure") == "LL")

        bullish_score = hh_count + hl_count
        bearish_score = lh_count + ll_count

        if bullish_score >= bearish_score + 2 and hl_count >= 1:
            return {
                "trend": "BULLISH",
                "score": bullish_score,
                "reason": f"Преобладают HH/HL: HH={hh_count}, HL={hl_count}, LH={lh_count}, LL={ll_count}"
            }

        if bearish_score >= bullish_score + 2 and lh_count >= 1:
            return {
                "trend": "BEARISH",
                "score": bearish_score,
                "reason": f"Преобладают LH/LL: LH={lh_count}, LL={ll_count}, HH={hh_count}, HL={hl_count}"
            }

        return {
            "trend": "RANGE",
            "score": max(bullish_score, bearish_score),
            "reason": f"Нет чистой структуры: HH={hh_count}, HL={hl_count}, LH={lh_count}, LL={ll_count}"
        }

    def _detect_bos(self, df, swings: dict, trend: dict) -> dict:
        last_close = float(df["close"].iloc[-1])
        last_high = float(df["high"].iloc[-1])
        last_low = float(df["low"].iloc[-1])
        last_time = str(df["timestamp"].iloc[-1])

        highs = swings["last_highs"]
        lows = swings["last_lows"]

        if highs:
            last_swing_high = highs[-1]

            if last_close > last_swing_high["price"]:
                return {
                    "detected": True,
                    "type": "BULLISH_BOS",
                    "direction": "LONG",
                    "broken_level": last_swing_high["price"],
                    "broken_level_time": last_swing_high["time"],
                    "break_time": last_time,
                    "close_price": round(last_close, 6),
                    "break_high": round(last_high, 6),
                    "confirmed_by_close": True,
                    "description": "Цена закрылась выше последнего swing high."
                }

        if lows:
            last_swing_low = lows[-1]

            if last_close < last_swing_low["price"]:
                return {
                    "detected": True,
                    "type": "BEARISH_BOS",
                    "direction": "SHORT",
                    "broken_level": last_swing_low["price"],
                    "broken_level_time": last_swing_low["time"],
                    "break_time": last_time,
                    "close_price": round(last_close, 6),
                    "break_low": round(last_low, 6),
                    "confirmed_by_close": True,
                    "description": "Цена закрылась ниже последнего swing low."
                }

        return self._empty_bos()

    def _detect_choch(self, bos: dict, trend: dict) -> dict:
        if not bos["detected"]:
            return self._empty_choch()

        current_trend = trend["trend"]

        if current_trend == "BEARISH" and bos["type"] == "BULLISH_BOS":
            return {
                **bos,
                "type": "BULLISH_CHOCH",
                "description": "CHOCH вверх: цена сломала bearish structure. Возможный разворот в LONG."
            }

        if current_trend == "BULLISH" and bos["type"] == "BEARISH_BOS":
            return {
                **bos,
                "type": "BEARISH_CHOCH",
                "description": "CHOCH вниз: цена сломала bullish structure. Возможный разворот в SHORT."
            }

        return self._empty_choch()

    def _detect_market_phase(self, trend: dict, bos: dict, choch: dict) -> str:
        if choch["detected"]:
            return "REVERSAL_POSSIBLE"

        if bos["detected"] and trend["trend"] == "BULLISH":
            return "BULLISH_CONTINUATION"

        if bos["detected"] and trend["trend"] == "BEARISH":
            return "BEARISH_CONTINUATION"

        if trend["trend"] == "RANGE":
            return "CONSOLIDATION"

        if trend["trend"] == "UNKNOWN":
            return "UNKNOWN"

        return "TRENDING"

    def _empty_bos(self) -> dict:
        return {
            "detected": False,
            "type": None,
            "direction": None
        }

    def _empty_choch(self) -> dict:
        return {
            "detected": False,
            "type": None,
            "direction": None
        }

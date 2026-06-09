class LiquidityAnalyzer:
    def analyze(self, df) -> dict:
        recent = df.tail(120).reset_index(drop=True)

        if len(recent) < 25:
            return {
                "equal_highs": self._empty_equal_result("EQH"),
                "equal_lows": self._empty_equal_result("EQL"),
                "buy_side_liquidity_sweep": self._empty_sweep_result("BUY_SIDE_LIQUIDITY_SWEEP"),
                "sell_side_liquidity_sweep": self._empty_sweep_result("SELL_SIDE_LIQUIDITY_SWEEP")
            }

        equal_highs = self._detect_equal_levels(recent, "high")
        equal_lows = self._detect_equal_levels(recent, "low")

        buy_side_sweep = self._detect_buy_side_sweep(recent)
        sell_side_sweep = self._detect_sell_side_sweep(recent)

        return {
            "equal_highs": equal_highs,
            "equal_lows": equal_lows,
            "buy_side_liquidity_sweep": buy_side_sweep,
            "sell_side_liquidity_sweep": sell_side_sweep
        }

    def _detect_equal_levels(self, df, column: str) -> dict:
        recent = df.tail(60).reset_index(drop=True)

        if column == "high":
            swings = self._find_swing_highs(recent)
            level_type = "EQH"
        else:
            swings = self._find_swing_lows(recent)
            level_type = "EQL"

        if len(swings) < 2:
            return self._empty_equal_result(level_type)

        avg_price = float(recent[column].mean())
        tolerance = avg_price * 0.001

        matches = []

        for i in range(len(swings) - 1):
            for j in range(i + 1, len(swings)):
                first = swings[i]
                second = swings[j]

                distance = abs(first["price"] - second["price"])

                if distance <= tolerance:
                    matches.append({
                        "type": level_type,
                        "detected": True,
                        "level": round((first["price"] + second["price"]) / 2, 6),
                        "first_time": first["time"],
                        "second_time": second["time"],
                        "touches": 2,
                        "distance": round(distance, 6),
                        "description": (
                            "Equal Highs: потенциальная buy-side ликвидность над рынком."
                            if level_type == "EQH"
                            else "Equal Lows: потенциальная sell-side ликвидность под рынком."
                        )
                    })

        if not matches:
            return self._empty_equal_result(level_type)

        return {
            "detected": True,
            "type": level_type,
            "levels": matches[-3:]
        }

    def _detect_buy_side_sweep(self, df) -> dict:
        previous = df.iloc[-25:-1].reset_index(drop=True)
        last = df.iloc[-1]

        if previous.empty:
            return self._empty_sweep_result("BUY_SIDE_LIQUIDITY_SWEEP")

        previous_high = float(previous["high"].max())
        previous_high_row = previous.loc[previous["high"].idxmax()]

        last_high = float(last["high"])
        last_close = float(last["close"])
        last_open = float(last["open"])

        wick_size = last_high - max(last_open, last_close)

        if last_high > previous_high and last_close < previous_high:
            return {
                "detected": True,
                "type": "BUY_SIDE_LIQUIDITY_SWEEP",
                "direction_after_sweep": "BEARISH_REACTION",
                "liquidity_level": round(previous_high, 6),
                "liquidity_time": str(previous_high_row["timestamp"]),
                "sweep_time": str(last["timestamp"]),
                "sweep_high": round(last_high, 6),
                "close_price": round(last_close, 6),
                "wick_size": round(wick_size, 6),
                "strength": self._classify_sweep_strength(wick_size, previous_high),
                "description": "Цена сняла buy-side ликвидность над high и закрылась обратно ниже. Возможная SHORT-реакция."
            }

        return self._empty_sweep_result("BUY_SIDE_LIQUIDITY_SWEEP")

    def _detect_sell_side_sweep(self, df) -> dict:
        previous = df.iloc[-25:-1].reset_index(drop=True)
        last = df.iloc[-1]

        if previous.empty:
            return self._empty_sweep_result("SELL_SIDE_LIQUIDITY_SWEEP")

        previous_low = float(previous["low"].min())
        previous_low_row = previous.loc[previous["low"].idxmin()]

        last_low = float(last["low"])
        last_close = float(last["close"])
        last_open = float(last["open"])

        wick_size = min(last_open, last_close) - last_low

        if last_low < previous_low and last_close > previous_low:
            return {
                "detected": True,
                "type": "SELL_SIDE_LIQUIDITY_SWEEP",
                "direction_after_sweep": "BULLISH_REACTION",
                "liquidity_level": round(previous_low, 6),
                "liquidity_time": str(previous_low_row["timestamp"]),
                "sweep_time": str(last["timestamp"]),
                "sweep_low": round(last_low, 6),
                "close_price": round(last_close, 6),
                "wick_size": round(wick_size, 6),
                "strength": self._classify_sweep_strength(wick_size, previous_low),
                "description": "Цена сняла sell-side ликвидность под low и закрылась обратно выше. Возможная LONG-реакция."
            }

        return self._empty_sweep_result("SELL_SIDE_LIQUIDITY_SWEEP")

    def _find_swing_highs(self, df) -> list:
        swings = []

        for i in range(2, len(df) - 2):
            current = float(df["high"].iloc[i])

            if (
                current > float(df["high"].iloc[i - 1])
                and current > float(df["high"].iloc[i - 2])
                and current > float(df["high"].iloc[i + 1])
                and current > float(df["high"].iloc[i + 2])
            ):
                swings.append({
                    "price": current,
                    "time": str(df["timestamp"].iloc[i])
                })

        return swings

    def _find_swing_lows(self, df) -> list:
        swings = []

        for i in range(2, len(df) - 2):
            current = float(df["low"].iloc[i])

            if (
                current < float(df["low"].iloc[i - 1])
                and current < float(df["low"].iloc[i - 2])
                and current < float(df["low"].iloc[i + 1])
                and current < float(df["low"].iloc[i + 2])
            ):
                swings.append({
                    "price": current,
                    "time": str(df["timestamp"].iloc[i])
                })

        return swings

    def _classify_sweep_strength(self, wick_size: float, price: float) -> str:
        if price <= 0:
            return "UNKNOWN"

        wick_percent = wick_size / price

        if wick_percent >= 0.004:
            return "STRONG"
        if wick_percent >= 0.002:
            return "MEDIUM"

        return "WEAK"

    def _empty_equal_result(self, level_type: str) -> dict:
        return {
            "detected": False,
            "type": level_type,
            "levels": []
        }

    def _empty_sweep_result(self, sweep_type: str) -> dict:
        return {
            "detected": False,
            "type": sweep_type
        }

class LiquidityAnalyzer:
    def analyze(self, df) -> dict:
        recent = df.tail(100).reset_index(drop=True)

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
        recent = df.tail(40).reset_index(drop=True)
        tolerance = float(recent[column].mean()) * 0.0015

        matches = []

        for i in range(len(recent) - 1):
            for j in range(i + 1, len(recent)):
                first = float(recent[column].iloc[i])
                second = float(recent[column].iloc[j])

                if abs(first - second) <= tolerance:
                    matches.append({
                        "level": round((first + second) / 2, 6),
                        "first_time": str(recent["timestamp"].iloc[i]),
                        "second_time": str(recent["timestamp"].iloc[j])
                    })

        if not matches:
            return {
                "detected": False,
                "type": "EQH" if column == "high" else "EQL",
                "levels": []
            }

        return {
            "detected": True,
            "type": "EQH" if column == "high" else "EQL",
            "levels": matches[-3:]
        }

    def _detect_buy_side_sweep(self, df) -> dict:
        previous = df.iloc[-20:-1]
        last = df.iloc[-1]

        previous_high = float(previous["high"].max())
        previous_high_row = previous.loc[previous["high"].idxmax()]

        last_high = float(last["high"])
        last_close = float(last["close"])

        if last_high > previous_high and last_close < previous_high:
            return {
                "detected": True,
                "type": "BUY_SIDE_LIQUIDITY_SWEEP",
                "liquidity_level": round(previous_high, 6),
                "liquidity_time": str(previous_high_row["timestamp"]),
                "sweep_time": str(last["timestamp"]),
                "sweep_high": round(last_high, 6),
                "close_price": round(last_close, 6),
                "description": "Цена сняла ликвидность над high и закрылась обратно ниже."
            }

        return {
            "detected": False,
            "type": "BUY_SIDE_LIQUIDITY_SWEEP"
        }

    def _detect_sell_side_sweep(self, df) -> dict:
        previous = df.iloc[-20:-1]
        last = df.iloc[-1]

        previous_low = float(previous["low"].min())
        previous_low_row = previous.loc[previous["low"].idxmin()]

        last_low = float(last["low"])
        last_close = float(last["close"])

        if last_low < previous_low and last_close > previous_low:
            return {
                "detected": True,
                "type": "SELL_SIDE_LIQUIDITY_SWEEP",
                "liquidity_level": round(previous_low, 6),
                "liquidity_time": str(previous_low_row["timestamp"]),
                "sweep_time": str(last["timestamp"]),
                "sweep_low": round(last_low, 6),
                "close_price": round(last_close, 6),
                "description": "Цена сняла ликвидность под low и закрылась обратно выше."
            }

        return {
            "detected": False,
            "type": "SELL_SIDE_LIQUIDITY_SWEEP"
        }
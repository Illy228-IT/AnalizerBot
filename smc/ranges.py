class RangeDetector:
    def analyze(self, df) -> dict:
        recent = df.tail(50)

        high = float(recent["high"].max())
        low = float(recent["low"].min())
        close = float(recent["close"].iloc[-1])

        range_percent = ((high - low) / close) * 100

        if range_percent < 4:
            state = "TIGHT_RANGE"
            tradable = False
        elif low < close < high:
            state = "RANGE"
            tradable = True
        else:
            state = "BREAKOUT"
            tradable = True

        return {
            "state": state,
            "high": round(high, 6),
            "low": round(low, 6),
            "range_percent": round(range_percent, 2),
            "tradable": tradable
        }
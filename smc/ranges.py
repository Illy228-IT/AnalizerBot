class RangeDetector:
    def analyze(self, df) -> dict:
        recent = df.tail(60).reset_index(drop=True)

        if len(recent) < 20:
            return {
                "state": "UNKNOWN",
                "tradable": False
            }

        range_high = float(recent["high"].max())
        range_low = float(recent["low"].min())

        current_close = float(recent.iloc[-1]["close"])

        range_size = range_high - range_low

        if range_size <= 0:
            return {
                "state": "UNKNOWN",
                "tradable": False
            }

        range_percent = (range_size / current_close) * 100

        range_mid = (range_high + range_low) / 2

        distance_to_high = abs(range_high - current_close)
        distance_to_low = abs(current_close - range_low)

        near_high = distance_to_high <= range_size * 0.15
        near_low = distance_to_low <= range_size * 0.15

        breakout_up = current_close > range_high * 0.998
        breakout_down = current_close < range_low * 1.002

        if range_percent < 3:
            state = "TIGHT_RANGE"
            tradable = False

        elif breakout_up:
            state = "BREAKOUT_UP"
            tradable = True

        elif breakout_down:
            state = "BREAKOUT_DOWN"
            tradable = True

        elif near_high:
            state = "RANGE_PREMIUM"
            tradable = False

        elif near_low:
            state = "RANGE_DISCOUNT"
            tradable = False

        else:
            state = "RANGE_MIDDLE"
            tradable = False

        return {
            "state": state,
            "high": round(range_high, 6),
            "low": round(range_low, 6),
            "mid": round(range_mid, 6),
            "range_percent": round(range_percent, 2),
            "distance_to_high": round(distance_to_high, 6),
            "distance_to_low": round(distance_to_low, 6),
            "tradable": tradable
        }

class FVGAnalyzer:
    def analyze(self, df) -> dict:
        recent = df.tail(120).reset_index(drop=True)

        bullish_fvgs = []
        bearish_fvgs = []

        if len(recent) < 3:
            return {
                "last_bullish_fvg": None,
                "last_bearish_fvg": None,
                "active_bullish_fvg": None,
                "active_bearish_fvg": None,
                "bullish_fvg_count": 0,
                "bearish_fvg_count": 0
            }

        for i in range(2, len(recent)):
            candle_1 = recent.iloc[i - 2]
            candle_2 = recent.iloc[i - 1]
            candle_3 = recent.iloc[i]

            c1_high = float(candle_1["high"])
            c1_low = float(candle_1["low"])
            c2_open = float(candle_2["open"])
            c2_close = float(candle_2["close"])
            c2_body = abs(c2_close - c2_open)
            c3_high = float(candle_3["high"])
            c3_low = float(candle_3["low"])

            if c2_body <= 0:
                continue

            if c1_high < c3_low:
                bullish_fvgs.append({
                    "type": "BULLISH_FVG",
                    "low": round(c1_high, 6),
                    "high": round(c3_low, 6),
                    "mid": round((c1_high + c3_low) / 2, 6),
                    "gap_size": round(c3_low - c1_high, 6),
                    "start_time": str(candle_1["timestamp"]),
                    "middle_time": str(candle_2["timestamp"]),
                    "end_time": str(candle_3["timestamp"]),
                    "description": "Bullish FVG: imbalance вверх, зона интереса для LONG после отката."
                })

            if c1_low > c3_high:
                bearish_fvgs.append({
                    "type": "BEARISH_FVG",
                    "low": round(c3_high, 6),
                    "high": round(c1_low, 6),
                    "mid": round((c3_high + c1_low) / 2, 6),
                    "gap_size": round(c1_low - c3_high, 6),
                    "start_time": str(candle_1["timestamp"]),
                    "middle_time": str(candle_2["timestamp"]),
                    "end_time": str(candle_3["timestamp"]),
                    "description": "Bearish FVG: imbalance вниз, зона интереса для SHORT после отката."
                })

        last_close = float(recent.iloc[-1]["close"])

        active_bullish = [
            fvg for fvg in bullish_fvgs
            if last_close >= fvg["low"]
        ]

        active_bearish = [
            fvg for fvg in bearish_fvgs
            if last_close <= fvg["high"]
        ]

        return {
            "last_bullish_fvg": bullish_fvgs[-1] if bullish_fvgs else None,
            "last_bearish_fvg": bearish_fvgs[-1] if bearish_fvgs else None,
            "active_bullish_fvg": active_bullish[-1] if active_bullish else None,
            "active_bearish_fvg": active_bearish[-1] if active_bearish else None,
            "bullish_fvg_count": len(bullish_fvgs),
            "bearish_fvg_count": len(bearish_fvgs)
        }

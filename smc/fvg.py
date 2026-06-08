class FVGAnalyzer:
    def analyze(self, df) -> dict:
        recent = df.tail(120).reset_index(drop=True)

        bullish_fvgs = []
        bearish_fvgs = []

        for i in range(2, len(recent)):
            candle_1 = recent.iloc[i - 2]
            candle_2 = recent.iloc[i - 1]
            candle_3 = recent.iloc[i]

            if float(candle_1["high"]) < float(candle_3["low"]):
                bullish_fvgs.append({
                    "type": "BULLISH_FVG",
                    "low": round(float(candle_1["high"]), 6),
                    "high": round(float(candle_3["low"]), 6),
                    "start_time": str(candle_1["timestamp"]),
                    "middle_time": str(candle_2["timestamp"]),
                    "end_time": str(candle_3["timestamp"]),
                    "description": "Bullish FVG: high первой свечи ниже low третьей свечи."
                })

            if float(candle_1["low"]) > float(candle_3["high"]):
                bearish_fvgs.append({
                    "type": "BEARISH_FVG",
                    "low": round(float(candle_3["high"]), 6),
                    "high": round(float(candle_1["low"]), 6),
                    "start_time": str(candle_1["timestamp"]),
                    "middle_time": str(candle_2["timestamp"]),
                    "end_time": str(candle_3["timestamp"]),
                    "description": "Bearish FVG: low первой свечи выше high третьей свечи."
                })

        return {
            "last_bullish_fvg": bullish_fvgs[-1] if bullish_fvgs else None,
            "last_bearish_fvg": bearish_fvgs[-1] if bearish_fvgs else None,
            "bullish_fvg_count": len(bullish_fvgs),
            "bearish_fvg_count": len(bearish_fvgs)
        }
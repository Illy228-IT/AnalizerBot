class PremiumDiscount:
    def analyze(self, df) -> dict:
        recent = df.tail(120).reset_index(drop=True)

        swing_high_row = recent.loc[recent["high"].idxmax()]
        swing_low_row = recent.loc[recent["low"].idxmin()]

        swing_high = float(swing_high_row["high"])
        swing_low = float(swing_low_row["low"])
        current_price = float(recent["close"].iloc[-1])

        equilibrium = (swing_high + swing_low) / 2

        if current_price > equilibrium:
            zone = "PREMIUM"
        elif current_price < equilibrium:
            zone = "DISCOUNT"
        else:
            zone = "EQUILIBRIUM"

        return {
            "swing_high": round(swing_high, 6),
            "swing_high_time": str(swing_high_row["timestamp"]),
            "swing_low": round(swing_low, 6),
            "swing_low_time": str(swing_low_row["timestamp"]),
            "equilibrium": round(equilibrium, 6),
            "current_price": round(current_price, 6),
            "zone": zone
        }
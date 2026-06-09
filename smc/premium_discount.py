class PremiumDiscount:
    def analyze(self, df) -> dict:
        recent = df.tail(150).reset_index(drop=True)

        if len(recent) < 20:
            return {
                "zone": "UNKNOWN",
                "tradable": False,
                "reason": "Недостаточно данных"
            }

        swing_high_row = recent.loc[recent["high"].idxmax()]
        swing_low_row = recent.loc[recent["low"].idxmin()]

        swing_high = float(swing_high_row["high"])
        swing_low = float(swing_low_row["low"])
        current_price = float(recent["close"].iloc[-1])

        dealing_range = swing_high - swing_low

        if dealing_range <= 0:
            return {
                "zone": "UNKNOWN",
                "tradable": False,
                "reason": "Некорректный dealing range"
            }

        equilibrium = (swing_high + swing_low) / 2

        premium_level = swing_low + dealing_range * 0.75
        discount_level = swing_low + dealing_range * 0.25

        price_position_percent = ((current_price - swing_low) / dealing_range) * 100

        if current_price >= premium_level:
            zone = "DEEP_PREMIUM"
            preferred_direction = "SHORT"
            tradable = True
        elif current_price > equilibrium:
            zone = "PREMIUM"
            preferred_direction = "SHORT"
            tradable = True
        elif current_price <= discount_level:
            zone = "DEEP_DISCOUNT"
            preferred_direction = "LONG"
            tradable = True
        elif current_price < equilibrium:
            zone = "DISCOUNT"
            preferred_direction = "LONG"
            tradable = True
        else:
            zone = "EQUILIBRIUM"
            preferred_direction = None
            tradable = False

        return {
            "swing_high": round(swing_high, 6),
            "swing_high_time": str(swing_high_row["timestamp"]),
            "swing_low": round(swing_low, 6),
            "swing_low_time": str(swing_low_row["timestamp"]),
            "equilibrium": round(equilibrium, 6),
            "premium_level": round(premium_level, 6),
            "discount_level": round(discount_level, 6),
            "current_price": round(current_price, 6),
            "price_position_percent": round(price_position_percent, 2),
            "zone": zone,
            "preferred_direction": preferred_direction,
            "tradable": tradable,
            "description": self._get_description(zone)
        }

    def _get_description(self, zone: str) -> str:
        descriptions = {
            "DEEP_PREMIUM": "Цена находится высоко в premium. Для SMC лучше искать SHORT после подтверждения.",
            "PREMIUM": "Цена выше equilibrium. Приоритет SHORT, если структура и ликвидность подтверждают.",
            "EQUILIBRIUM": "Цена около середины dealing range. Лучше не входить.",
            "DISCOUNT": "Цена ниже equilibrium. Приоритет LONG, если структура и ликвидность подтверждают.",
            "DEEP_DISCOUNT": "Цена находится низко в discount. Для SMC лучше искать LONG после подтверждения.",
            "UNKNOWN": "Недостаточно данных для определения premium/discount."
        }

        return descriptions.get(zone, "Нет описания.")

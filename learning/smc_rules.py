SMC_RULES = """
SMC RULES:

1. Buy-side liquidity:
- находится над локальными high
- если цена пробила high и закрылась обратно ниже — это BUY_SIDE_LIQUIDITY_SWEEP

2. Sell-side liquidity:
- находится под локальными low
- если цена пробила low и закрылась обратно выше — это SELL_SIDE_LIQUIDITY_SWEEP

3. Нельзя называть пробой low buy-side liquidity.
4. Нельзя называть пробой high sell-side liquidity.

5. BOS:
- bullish BOS = цена закрылась выше предыдущего значимого swing high
- bearish BOS = цена закрылась ниже предыдущего значимого swing low

6. CHoCH:
- bullish CHoCH = после bearish структуры цена ломает последний lower high
- bearish CHoCH = после bullish структуры цена ломает последний higher low

7. FVG:
- bullish FVG = high свечи 1 ниже low свечи 3
- bearish FVG = low свечи 1 выше high свечи 3

8. Premium / Discount:
- premium = цена выше 50% диапазона swing high / swing low
- discount = цена ниже 50% диапазона
- equilibrium = зона около 50%

9. Order Block:
- bullish OB = последняя bearish свеча перед сильным импульсом вверх
- bearish OB = последняя bullish свеча перед сильным импульсом вниз

10. OpenAI не имеет права придумывать уровни.
11. OpenAI обязан использовать только SMC-сигналы, которые передал код.
"""
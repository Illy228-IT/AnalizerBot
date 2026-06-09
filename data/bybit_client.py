import pandas as pd

from tvDatafeed import TvDatafeed, Interval
from config import CANDLE_LIMIT


class BybitClient:
    def __init__(self):
        self.tv = TvDatafeed()

    def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = CANDLE_LIMIT
    ) -> pd.DataFrame:
        tv_interval = self._convert_interval_to_tradingview(interval)

        tv_symbol = symbol.replace("USDT", "USDT.P")

        df = self.tv.get_hist(
            symbol=tv_symbol,
            exchange="BINANCE",
            interval=tv_interval,
            n_bars=limit
        )

        if df is None or df.empty:
            raise RuntimeError(f"TradingView не повернув дані для {symbol}")

        df = df.reset_index()

        df = df.rename(
            columns={
                "datetime": "timestamp",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume"
            }
        )

        df["turnover"] = 0.0

        df = df[
            [
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover"
            ]
        ]

        return self._normalize_df(df)

    def _normalize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        for column in [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover"
        ]:
            df[column] = df[column].astype(float)

        return df.reset_index(drop=True)

    def _convert_interval_to_tradingview(self, interval: str):
        intervals = {
            "1": Interval.in_1_minute,
            "3": Interval.in_3_minute,
            "5": Interval.in_5_minute,
            "15": Interval.in_15_minute,
            "30": Interval.in_30_minute,
            "60": Interval.in_1_hour,
            "120": Interval.in_2_hour,
            "240": Interval.in_4_hour,
            "D": Interval.in_daily,
            "W": Interval.in_weekly,
            "M": Interval.in_monthly
        }

        if interval not in intervals:
            raise ValueError(f"Unsupported TradingView interval: {interval}")

        return intervals[interval]

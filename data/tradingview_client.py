import pandas as pd

from tvDatafeed import TvDatafeed, Interval


class TradingViewClient:
    def __init__(self):
        try:
            self.tv = TvDatafeed()
        except Exception:
            self.tv = None

    def get_btcd_1h(self, bars: int = 200):
        if self.tv is None:
            return None

        try:
            df = self.tv.get_hist(
                symbol="BTC.D",
                exchange="CRYPTOCAP",
                interval=Interval.in_1_hour,
                n_bars=bars
            )

            if df is None or df.empty:
                return None

            df = df.reset_index()

            if "datetime" in df.columns:
                df = df.rename(columns={"datetime": "timestamp"})
            elif "index" in df.columns:
                df = df.rename(columns={"index": "timestamp"})
            elif "timestamp" not in df.columns:
                df = df.rename(columns={df.columns[0]: "timestamp"})

            df["timestamp"] = pd.to_datetime(df["timestamp"])

            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            df = df.dropna().reset_index(drop=True)

            return df

        except Exception:
            return None

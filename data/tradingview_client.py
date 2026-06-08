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

            return df

        except Exception:
            return None
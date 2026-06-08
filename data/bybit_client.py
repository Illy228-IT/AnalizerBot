import time
import requests
import pandas as pd

from config import BYBIT_BASE_URL, CANDLE_LIMIT


class BybitClient:
    def __init__(self):
        self.bybit_base_url = BYBIT_BASE_URL
        self.binance_base_url = "https://fapi.binance.com"

        self.session = requests.Session()

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
            "Connection": "keep-alive"
        }

    def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = CANDLE_LIMIT
    ) -> pd.DataFrame:
        try:
            return self._get_bybit_klines(symbol, interval, limit)

        except Exception as bybit_error:
            print(f"[WARN] Bybit failed for {symbol}: {bybit_error}")
            print(f"[INFO] Trying Binance Futures for {symbol}")

            try:
                return self._get_binance_klines(symbol, interval, limit)

            except Exception as binance_error:
                raise RuntimeError(
                    f"Не вдалося отримати дані для {symbol}. "
                    f"Bybit error: {bybit_error}. "
                    f"Binance error: {binance_error}"
                )

    def _get_bybit_klines(
        self,
        symbol: str,
        interval: str,
        limit: int
    ) -> pd.DataFrame:
        url = f"{self.bybit_base_url}/v5/market/kline"

        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        last_error = None

        for _ in range(3):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=20,
                    headers=self.headers
                )

                if response.status_code == 403:
                    raise RuntimeError(
                        f"Bybit 403 Forbidden. Response: {response.text[:300]}"
                    )

                response.raise_for_status()

                data = response.json()

                if data.get("retCode") != 0:
                    raise RuntimeError(
                        f"Bybit API error for {symbol}: {data.get('retMsg')}"
                    )

                candles = data["result"]["list"]

                if not candles:
                    raise RuntimeError(f"No Bybit candles returned for {symbol}")

                candles.reverse()

                df = pd.DataFrame(
                    candles,
                    columns=[
                        "timestamp",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "turnover"
                    ]
                )

                return self._normalize_df(df)

            except Exception as error:
                last_error = error
                time.sleep(2)

        raise RuntimeError(last_error)

    def _get_binance_klines(
        self,
        symbol: str,
        interval: str,
        limit: int
    ) -> pd.DataFrame:
        url = f"{self.binance_base_url}/fapi/v1/klines"

        params = {
            "symbol": symbol,
            "interval": self._convert_interval_to_binance(interval),
            "limit": limit
        }

        last_error = None

        for _ in range(3):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=20,
                    headers=self.headers
                )

                response.raise_for_status()

                data = response.json()

                if not data:
                    raise RuntimeError(f"No Binance candles returned for {symbol}")

                df = pd.DataFrame(
                    data,
                    columns=[
                        "timestamp",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "close_time",
                        "quote_asset_volume",
                        "number_of_trades",
                        "taker_buy_base_volume",
                        "taker_buy_quote_volume",
                        "ignore"
                    ]
                )

                df = df[
                    [
                        "timestamp",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume"
                    ]
                ]

                df["turnover"] = 0.0

                return self._normalize_df(df)

            except Exception as error:
                last_error = error
                time.sleep(2)

        raise RuntimeError(last_error)

    def _normalize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"].astype("int64"),
            unit="ms"
        )

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

    def _convert_interval_to_binance(self, interval: str) -> str:
        intervals = {
            "1": "1m",
            "3": "3m",
            "5": "5m",
            "15": "15m",
            "30": "30m",
            "60": "1h",
            "120": "2h",
            "240": "4h",
            "360": "6h",
            "720": "12h",
            "D": "1d",
            "W": "1w",
            "M": "1M"
        }

        if interval not in intervals:
            raise ValueError(f"Unsupported interval for Binance: {interval}")

        return intervals[interval]

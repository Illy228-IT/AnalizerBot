import time
import requests
import pandas as pd

from config import BYBIT_BASE_URL, CANDLE_LIMIT


class BybitClient:
    def __init__(self):
        self.base_url = BYBIT_BASE_URL
        self.session = requests.Session()

    def get_klines(self, symbol: str, interval: str, limit: int = CANDLE_LIMIT) -> pd.DataFrame:
        url = f"{self.base_url}/v5/market/kline"

        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        last_error = None

        for attempt in range(3):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=20,
                    headers={
                        "User-Agent": "Mozilla/5.0"
                    }
                )

                response.raise_for_status()
                data = response.json()

                if data.get("retCode") != 0:
                    raise RuntimeError(f"Bybit API error for {symbol}: {data.get('retMsg')}")

                candles = data["result"]["list"]

                if not candles:
                    raise RuntimeError(f"No candles returned for {symbol}")

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

                df["timestamp"] = pd.to_datetime(
                    df["timestamp"].astype("int64"),
                    unit="ms"
                )

                for column in ["open", "high", "low", "close", "volume", "turnover"]:
                    df[column] = df[column].astype(float)

                return df

            except Exception as error:
                last_error = error
                time.sleep(2)

        raise RuntimeError(f"Не вдалося отримати дані Bybit для {symbol}: {last_error}")
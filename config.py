import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

BYBIT_BASE_URL = "https://api.bybit.com"

TIMEFRAMES = {
    "4H": "240",
    "1H": "60",
    "15M": "15"
}

CANDLE_LIMIT = 200

MIN_RR = 2.0

COMMAND_NEXT = ["дальше", "далі", "дали", "next"]
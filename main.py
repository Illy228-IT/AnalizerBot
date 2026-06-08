from telegram_bot import TelegramBot
from utils.logger import setup_logger


def main():
    setup_logger()

    bot = TelegramBot()
    bot.run()


if __name__ == "__main__":
    main()
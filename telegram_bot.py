from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from learning.feedback_store import FeedbackStore
from config import TELEGRAM_BOT_TOKEN, COMMAND_NEXT
from analyzers.market_context import MarketContextAnalyzer
from scanner.coin_scanner import CoinScanner
from openai_client import OpenAIClient
from utils.formatter import (
    start_message,
    loading_message,
    unknown_command_message
)


class TelegramBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        self.market_context_analyzer = MarketContextAnalyzer()
        self.coin_scanner = CoinScanner()
        self.openai_client = OpenAIClient()
        self.feedback_store = FeedbackStore()

        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(start_message())

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text.lower().strip()

        if user_text.startswith("запомни:"):
            feedback = update.message.text.split(":", 1)[1].strip()

            self.feedback_store.add_feedback(feedback)

            await update.message.reply_text(
                "✅ Запомнил правило."
            )

            return

        if user_text not in COMMAND_NEXT:
            await update.message.reply_text(unknown_command_message())
            return

        await update.message.reply_text(loading_message())

        try:
            market_context = self.market_context_analyzer.analyze()
            coin_data = self.coin_scanner.scan_next_coin()

            analysis = self.openai_client.generate_analysis(
                market_context=market_context,
                coin_data=coin_data
            )

            await update.message.reply_text(analysis)

        except Exception as error:
            import traceback

            error_text = traceback.format_exc()

            await update.message.reply_text(
                f"❌ Ошибка во время анализа:\n\n{error}"
            )

            print(error_text)

    def run(self):
        print("SMC AI BOT STARTED")
        self.app.run_polling()
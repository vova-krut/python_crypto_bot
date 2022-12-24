from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


class TelegramBot:
    def __init__(self, tg_token: str) -> None:
        self.app = ApplicationBuilder().token(tg_token).build()

    async def _hello(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'Hello {update.effective_user.full_name}')

    def run(self):
        self.app.add_handler(CommandHandler('hello', self._hello))

        self.app.run_polling()

    def stop(self):
        self.app.stop()

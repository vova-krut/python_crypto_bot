from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db_connection import DbConnection


class TelegramBot:
    def __init__(self, tg_token: str) -> None:
        self._app = ApplicationBuilder().token(tg_token).build()
        self._db_connection = DbConnection().get_connection()

    async def _hello(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'Hello {update.effective_user.full_name}')

    def run(self):
        self._app.add_handler(CommandHandler('hello', self._hello))

        self._app.run_polling()

    def stop(self):
        self._app.stop()

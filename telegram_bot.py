from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db_connection import DbConnection

class TelegramBot:
    def __init__(self, tg_token: str) -> None:
        self._app = ApplicationBuilder().token(tg_token).build()
        self._db_connection = DbConnection().get_connection()

    @staticmethod
    async def _hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Create the buttons
        button1 = KeyboardButton("Button 1")
        button2 = KeyboardButton("Button 2")
        button3 = KeyboardButton("Button 3")

        # Create the keyboard
        keyboard = [[button1, button2], [button3]]

        # Create the ReplyKeyboardMarkup object
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        # Send the message with the buttons
        await update.message.reply_text(f'Suck my cock {update.effective_user.full_name}', reply_markup=markup)

    def run(self):
        self._app.add_handler(CommandHandler('hello', self._hello))

        self._app.run_polling()

    def stop(self):
        self._app.stop()
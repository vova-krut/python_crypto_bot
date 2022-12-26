from telegram import Update, ReplyKeyboardMarkup
from src.db_connection import DbConnection
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)


class TelegramBot:
    BUY_CRYPTO, SELECT_CRYPTO, SELECT_AMOUNT = range(3)

    def __init__(self, tg_token: str) -> None:
        self._app = ApplicationBuilder().token(tg_token).build()
        self._db_connection = DbConnection().get_connection()

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'Welcome to our tutorial bot!')
        await update.message.reply_text(f'It can help you to learn how to earn money trading crypto')
        await update.message.reply_text(f'You can emulate buying some coins and see if you made a good decision!')
        await update.message.reply_text(f'Here are some options: ', reply_markup=self._create_keyboard())

    def _create_keyboard(self):
        keyboard = [['Buy crypto', 'Make a transaction'], ['Check balance']]

        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True)

    async def _buy_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'Sure! Which cryptocurrency do you want to buy?')

        return self.SELECT_CRYPTO

    async def _select_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        crypto = update.message.text
        context.user_data['crypto'] = crypto

        await update.message.reply_text(f'Got it, you want to buy {crypto}.')
        await update.message.reply_text(f'How much do you want to buy?')

        return self.SELECT_AMOUNT

    async def _select_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        amount = update.message.text
        crypto = context.user_data['crypto']

        await update.message.reply_text(f'You want to buy {amount} of {crypto}.')

        return ConversationHandler.END

    async def _cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Okay, lets go back')
        return ConversationHandler.END

    def run(self):
        buy_crypto_handler = ConversationHandler(
            entry_points=[MessageHandler(
                filters.Text('Buy crypto'), self._buy_crypto)],
            states={
                self.SELECT_CRYPTO: [MessageHandler(
                    filters.TEXT, self._select_crypto)],
                self.SELECT_AMOUNT: [MessageHandler(
                    filters.TEXT, self._select_amount)]
            },
            fallbacks=[CommandHandler('cancel', self._cancel)],
            allow_reentry=True
        )

        self._app.add_handler(CommandHandler('start', self._start))
        self._app.add_handler(buy_crypto_handler)

        self._app.run_polling()

    def stop(self):
        self._app.stop()

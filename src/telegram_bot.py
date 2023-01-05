from src.user_repository import UserRepository
from src.currency_repository import CurrencyRepository
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

class TelegramBot:
    SELECT_CRYPTO, SELECT_AMOUNT = range(2)

    def __init__(self, tg_token: str) -> None:
        self._app = ApplicationBuilder().token(tg_token).build()
        self._user_repository = UserRepository()
        self._curr_repository = CurrencyRepository()

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        db_user = self._user_repository.find_user(user.id)

        if not db_user:
            self._user_repository.create_user(user.id)
            await self._send_greetings(update)
        else:
            await update.message.reply_text(f'Welcome again!', reply_markup=self._create_keyboard())

    async def _send_greetings(self, update: Update):
        await update.message.reply_text(f'Welcome to our tutorial bot!')
        await update.message.reply_text(f'It can help you to learn how to earn money trading crypto')
        await update.message.reply_text(f'You can emulate buying some coins and see if you made a good decision!')
        await update.message.reply_text(f'Here are some options: ', reply_markup=self._create_keyboard())

    def _create_keyboard(self):
        keyboard = [['Buy crypto', 'Make a transaction'], ['Check balance']]

        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True)

    async def _buy_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        currencies = self._curr_repository.get_currencies()
        currencies_names = [x[1] for x in currencies]
        buttons = [InlineKeyboardButton(x, callback_data=x) for x in currencies_names]

        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

        markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f'Sure! Which cryptocurrency do you want to buy?', reply_markup=markup)

        return self.SELECT_CRYPTO

    async def _select_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        crypto = update.callback_query.data
        context.user_data['crypto'] = crypto

        await update.callback_query.edit_message_text(f'Got it, now enter the amount of {crypto} you want to buy.')

        return self.SELECT_AMOUNT

    async def _select_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        amount = update.message.text
        crypto = context.user_data['crypto']
        user_id = update.message.from_user.id

        self._curr_repository.buy_currency_for_user(user_id, crypto, amount)

        await update.message.reply_text(f'You want to buy {amount} of {crypto}.', reply_markup=self._create_keyboard())

        return ConversationHandler.END

    async def _cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Okay, lets go back')
        return ConversationHandler.END

    def run(self):
        buy_crypto_handler = ConversationHandler(
            entry_points=[MessageHandler(
                filters.Text('Buy crypto'), self._buy_crypto)],
            states={
                self.SELECT_CRYPTO: [CallbackQueryHandler(self._select_crypto)],
                self.SELECT_AMOUNT: [MessageHandler(filters.TEXT, self._select_amount)]
            },
            fallbacks=[CommandHandler('cancel', self._cancel)],
            allow_reentry=True
        )

        self._app.add_handler(CommandHandler('start', self._start))
        self._app.add_handler(buy_crypto_handler)

        self._app.run_polling()

    def stop(self):
        self._app.stop()


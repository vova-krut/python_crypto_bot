import telegram

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
    SELECT_CRYPTO, SELECT_AMOUNT, SELECT_RECEIVER_ID, PRINT_TRANSACTION_CRYPTO, SELECT_TRANSACTION_CRYPTO, SELECT_TRANSACTION_AMOUNT = range(
        6)

    def __init__(self, tg_token: str) -> None:
        self._messages = []
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
        greeting_texts = [
            "Welcome to our tutorial bot!",
            "It can help you to learn how to earn money trading crypto",
            "You can emulate buying some coins and see if you made a good decision!"
        ]

        self._messages.extend(await self._send_messages(update, greeting_texts))
        self._messages.extend(await self._send_messages(update, "Here are some options: ", reply_markup=self._create_keyboard()))

    async def _buy_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self._messages = await self._clear_messages(update, self._messages)

        await self._send_messages(update, "Sure! Which cryptocurrency do you want to buy?", reply_markup=self._get_crypto_buttons_markup())

        return self.SELECT_CRYPTO

    async def _select_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        crypto = update.callback_query.data
        context.user_data['crypto'] = crypto

        await update.callback_query.edit_message_text(f'Got it, now enter the amount of {crypto} you want to buy.')

        return self.SELECT_AMOUNT

    async def _select_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            amount = update.message.text
            crypto = context.user_data['crypto']
            user_id = update.message.from_user.id

            self._curr_repository.buy_currency_for_user(
                user_id, crypto, amount)

            await update.message.reply_text(f'You have successfully bought {amount} of {crypto}.', reply_markup=self._create_keyboard())

            return ConversationHandler.END
        except ValueError as e:
            await update.message.reply_text(str(e), reply_markup=self._create_keyboard())
            return ConversationHandler.END

    async def _make_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._send_messages("Enter the receiver ID.")
        return self.PRINT_TRANSACTION_CRYPTO

    async def _print_transaction_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        receiver_id = update.message.text
        context.user_data['receiver_id'] = receiver_id

        await self._send_messages("Good! Which cryptocurrency do you want to send?", reply_markup=self._get_crypto_buttons_markup())

        return self.SELECT_TRANSACTION_CRYPTO

    async def _select_transaction_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        crypto = update.callback_query.data
        context.user_data['crypto'] = crypto

        await update.callback_query.edit_message_text(f'Got it, now enter the amount of {crypto} you want to send.')

        return self.SELECT_TRANSACTION_AMOUNT

    async def _select_transaction_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            amount = update.message.text
            crypto = context.user_data['crypto']
            receiver_id = context.user_data['receiver_id']
            sender_id = update.message.from_user.id

            self._curr_repository.send_crypto_to_user(
                sender_id, receiver_id, crypto, amount)

            await update.message.reply_text(f'You have successfully sent {amount} of {crypto} to {receiver_id}.', reply_markup=self._create_keyboard())

            return ConversationHandler.END
        except ValueError as e:
            await update.message.reply_text(str(e), reply_markup=self._create_keyboard())
            return ConversationHandler.END

    async def _cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Okay, lets go back', reply_markup=self._create_keyboard())
        return ConversationHandler.END

    def run(self):
        buy_crypto_handler = ConversationHandler(
            entry_points=[MessageHandler(
                filters.Text('Buy crypto'), self._buy_crypto)],
            states={
                self.SELECT_CRYPTO: [CallbackQueryHandler(self._select_crypto)],
                self.SELECT_AMOUNT: [MessageHandler(
                    filters.TEXT, self._select_amount)]
            },
            fallbacks=[CommandHandler('cancel', self._cancel)],
            allow_reentry=True
        )

        send_crypto_handler = ConversationHandler(
            entry_points=[MessageHandler(
                filters.Text('Make a transaction'), self._make_transaction)],
            states={
                self.PRINT_TRANSACTION_CRYPTO: [MessageHandler(filters.TEXT, self._print_transaction_crypto)],
                self.SELECT_TRANSACTION_CRYPTO: [CallbackQueryHandler(self._select_transaction_crypto)],
                self.SELECT_TRANSACTION_AMOUNT: [MessageHandler(
                    filters.TEXT, self._select_transaction_amount)]
            },
            fallbacks=[CommandHandler('cancel', self._cancel)],
            allow_reentry=True
        )

        self._app.add_handler(CommandHandler('start', self._start))
        self._app.add_handler(buy_crypto_handler)
        self._app.add_handler(send_crypto_handler)

        self._app.run_polling()

    async def _send_messages(self, update: Update, messages: list[str], reply_markup=None):
        if isinstance(messages, str):
            messages = [messages]
        sent_messages = []
        for message in messages:
            sent_messages.append(await update.get_bot().send_message(chat_id=update.message.from_user.id, text=message, reply_markup=reply_markup))
        return sent_messages

    async def _clear_messages(self, update: Update, messages):
        for message in messages:
            await update.get_bot().deleteMessage(chat_id=update.message.from_user.id, message_id=message.message_id)
        return []

    def _get_crypto_buttons_markup(self):
        currencies = self._curr_repository.get_currencies()
        currencies_names = [x[1] for x in currencies]
        buttons = [InlineKeyboardButton(x, callback_data=x)
                   for x in currencies_names]

        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        markup = InlineKeyboardMarkup(keyboard)

        return markup

    def _create_keyboard(self):
        keyboard = [['Buy crypto', 'Make a transaction'], ['Check balance']]

        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True)

    def stop(self):
        self._app.stop()

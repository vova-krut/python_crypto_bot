from src.repositories.user_repository import UserRepository
from src.repositories.currency_repository import CurrencyRepository
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
    SELECT_CRYPTO, SELECT_AMOUNT, SELECT_RECEIVER_ID, PRINT_TRANSACTION_CRYPTO, SELECT_TRANSACTION_CRYPTO, SELECT_TRANSACTION_AMOUNT, SELECT_CRYPTO_TO_SELL, SELECT_AMOUNT_TO_SELL = range(
        8)

    def __init__(self, tg_token: str) -> None:
        self._app = ApplicationBuilder().token(tg_token).build()
        self._user_repository = UserRepository()
        self._curr_repository = CurrencyRepository()

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["all_messages"] = [update.message]

        user = update.message.from_user
        db_user = self._user_repository.find_user(user.id)

        if not db_user:
            self._user_repository.create_user(user.id)
            await self._send_greetings(update, context)
        else:
            await self._send_messages(update, context, f'Welcome again!', self._create_keyboard())

    async def _send_greetings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        greeting_texts = [
            "Welcome to our tutorial bot!",
            "It can help you to learn how to earn money trading crypto",
            "You can emulate buying some coins and see if you made a good decision!"
        ]

        await self._send_messages(update, context, greeting_texts)
        await self._send_messages(update, context, "Here are some options: ", self._create_keyboard())

    async def _buy_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["all_messages"].append(update.message)
        context.user_data["all_messages"] = await self._clear_messages(update, context.user_data["all_messages"])

        await self._send_messages(update, context, "Sure! Which cryptocurrency do you want to buy?", self._get_crypto_buttons_markup())

        return self.SELECT_CRYPTO

    async def _select_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        crypto = update.callback_query.data
        context.user_data['crypto'] = crypto

        await self._send_messages(update, context, f"Got it, now enter the amount of {crypto} you want to buy.")

        return self.SELECT_AMOUNT

    async def _select_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["all_messages"].append(update.message)
        context.user_data["all_messages"] = await self._clear_messages(update, context.user_data["all_messages"])

        try:
            amount = update.message.text
            crypto = context.user_data['crypto']
            user_id = update.message.from_user.id

            self._curr_repository.buy_currency_for_user(
                user_id, crypto, amount)

            await self._send_messages(update, context, f"You have successfully bought {amount} of {crypto}.", self._create_keyboard())

            return ConversationHandler.END
        except ValueError as e:
            await self._send_messages(update, context, str(e), self._create_keyboard())
            return ConversationHandler.END

    async def _sell_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["all_messages"].append(update.message)
        await self._send_messages(update, context, "Sure! Which cryptocurrency do you want to sell?", self._get_crypto_buttons_markup())

        return self.SELECT_CRYPTO_TO_SELL

    async def _select_crypto_to_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        crypto = update.callback_query.data
        context.user_data['crypto'] = crypto

        await self._send_messages(update, context, f"Got it, now enter the amount of {crypto} you want to sell.")

        return self.SELECT_AMOUNT_TO_SELL

    async def _select_amount_to_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["all_messages"].append(update.message)
        amount = update.message.text
        crypto = context.user_data['crypto']
        sender_id = update.message.from_user.id

        await self._send_messages(update, context, f'You have successfully sold {amount} of {crypto} for ENTER BLYAT AMOUNT.', self._create_keyboard())

        return ConversationHandler.END

    async def _make_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["all_messages"].append(update.message)
        await self._send_messages(update, context, "Enter the receiver ID.")
        return self.PRINT_TRANSACTION_CRYPTO

    async def _print_transaction_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["all_messages"].append(update.message)
        receiver_id = update.message.text
        context.user_data['receiver_id'] = receiver_id

        await self._send_messages(update, context, "Good! Which cryptocurrency do you want to send?", reply_markup=self._get_crypto_buttons_markup())

        return self.SELECT_TRANSACTION_CRYPTO

    async def _select_transaction_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        crypto = update.callback_query.data
        context.user_data['crypto'] = crypto

        await self._send_messages(update, context, f"Got it, now enter the amount of {crypto} you want to send.")

        return self.SELECT_TRANSACTION_AMOUNT

    async def _get_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        currency_balance, usd_balance = self._user_repository.get_balance(
            update.message.from_user.id)
        try:
            currency_vs_balance = [
                f"{currency_name}: {balance}" for currency_name, balance in currency_balance.items()]
            currency_balance_table = "\n".join(currency_vs_balance)
        except:
            currency_balance_table = "You don't have any currency available."
        await self._send_messages(update, context, [f"Currency balance:\n{currency_balance_table}", f"USD balance: {usd_balance}"], reply_markup=self._create_keyboard())

    async def _select_transaction_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["all_messages"].append(update.message)
        try:
            amount = update.message.text
            crypto = context.user_data['crypto']
            receiver_id = context.user_data['receiver_id']
            sender_id = update.message.from_user.id

            self._curr_repository.send_crypto_to_user(
                sender_id, receiver_id, crypto, amount)

            await self._send_messages(update, context, f"You have successfully sent {amount} of {crypto} to {receiver_id}.", self._create_keyboard())

            return ConversationHandler.END
        except ValueError as e:
            await self._send_messages(update, context, str(e), self._create_keyboard())
            return ConversationHandler.END

    async def _cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._send_messages(update, context, "Okay, lets go back", self._create_keyboard())
        #context.user_data["all_messages"] = self._clear_messages(update, context.user_data["all_messages"])
        return ConversationHandler.END

    async def _send_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE, messages: list[str], reply_markup=None):
        if isinstance(messages, str):
            messages = [messages]
        sent_messages = []
        for message in messages:
            sent_messages.append(await update.get_bot().send_message(chat_id=self._get_chat_id(update), text=message, reply_markup=reply_markup))

        context.user_data["all_messages"].extend(sent_messages)


    async def _clear_messages(self, update: Update, messages):

        for message in messages:
            await update.get_bot().deleteMessage(chat_id=update.message.from_user.id, message_id=message.message_id)
        return []

    def _get_chat_id(self, update: Update):
        chat_id = None
        if update.message is not None:
            chat_id = update.message.chat.id
        elif update.channel_post is not None:
            chat_id = update.channel_post.chat.id
        elif update.inline_query is not None:
            chat_id = update.inline_query.from_user.id
        elif update.chosen_inline_result is not None:
            chat_id = update.chosen_inline_result.from_user.id
        elif update.callback_query is not None:
            chat_id = update.callback_query.from_user.id
        return chat_id

    def _get_crypto_buttons_markup(self):
        currencies = self._curr_repository.get_currencies()
        currencies_names = [x[1] for x in currencies]
        buttons = [InlineKeyboardButton(x, callback_data=x)
                   for x in currencies_names]

        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        markup = InlineKeyboardMarkup(keyboard)

        return markup

    def _create_keyboard(self):
        keyboard = [['Buy crypto', 'Sell crypto'], ['Make a transaction', 'Check balance'], ['Check history']]

        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True)

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

        sell_crypto_handler = ConversationHandler(
            entry_points=[MessageHandler(
                filters.Text('Sell crypto'), self._sell_crypto)],
            states={
                self.SELECT_CRYPTO_TO_SELL: [CallbackQueryHandler(self._select_crypto_to_sell)],
                self.SELECT_AMOUNT_TO_SELL: [MessageHandler(filters.TEXT, self._select_amount_to_sell)]
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

        get_balance = MessageHandler(filters.Text("Check balance"), self._get_balance)

        self._app.add_handler(CommandHandler('start', self._start))
        self._app.add_handler(buy_crypto_handler)
        self._app.add_handler(sell_crypto_handler)
        self._app.add_handler(send_crypto_handler)
        self._app.add_handler(get_balance)

        self._app.run_polling()

    def stop(self):
        self._app.stop()

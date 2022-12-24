from telegram_bot import TelegramBot
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')

    tg_bot = TelegramBot(bot_token)

    tg_bot.run()


if __name__ == '__main__':
    main()

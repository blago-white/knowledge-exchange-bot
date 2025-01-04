import logging
import asyncio

from dotenv import load_dotenv

load_dotenv()

import os

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import loggers


async def main():
    dp = Dispatcher()

    bot = Bot(
        token=os.environ.get("BOT_TOKEN"),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    logging.getLogger('aiogram').addHandler(loggers.ConsoleDebugLogger())

    asyncio.run(main())

import logging
import asyncio
import redis

import loggers

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from handlers import ROUTERS

load_dotenv()

import os


async def main():
    dp = Dispatcher()

    dp.include_routers(*ROUTERS)

    bot = Bot(
        token=os.environ.get("BOT_TOKEN"),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    logging.getLogger('aiogram').addHandler(loggers.ConsoleDebugLogger())

    asyncio.run(main())

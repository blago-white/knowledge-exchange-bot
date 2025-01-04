import logging
import asyncio
import redis

import loggers

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

load_dotenv()

import os


async def main():
    dp = Dispatcher(storage=RedisStorage(
        redis=redis.Redis.from_url(
            "redis://knowledgeredis:6379/0/"
        )
    ))

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

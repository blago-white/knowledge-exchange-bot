import logging
import asyncio
import redis

import loggers

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from handlers import ROUTERS
from models import DBSessionAccesObject

load_dotenv()

import os


async def run_bot():
    dp = Dispatcher()

    dp.include_routers(*ROUTERS)

    bot = Bot(
        token=os.environ.get("BOT_TOKEN"),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    )

    await dp.start_polling(bot)


async def init_db_connection():
    engine = create_async_engine(
        url="postgresql+asyncpg://vmerinov:270407020104$sPg%Gettr_5o0e@localhost:5432/jackdropdb",
        # url=("postgresql+asyncpg://"
        #      f"{os.environ.get('POSTGRES_USER')}:"
        #      f"{os.environ.get('POSTGRES_PASSWORD')}@"
        #      f"{os.environ.get('POSTGRES_HOST')}/"
        #      f"{os.environ.get('POSTGRES_DB')}"),
        echo=True,
        hide_parameters=False
    )

    ao = DBSessionAccesObject()
    ao.sessionmaker = async_sessionmaker(engine)

    from repositories import test

    await test.init_data(engine=engine, initialize_models=True, initialize_data=True)


async def main():
    await init_db_connection()

    await run_bot()


if __name__ == '__main__':
    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    logging.getLogger('aiogram').addHandler(loggers.ConsoleDebugLogger())

    asyncio.run(main())

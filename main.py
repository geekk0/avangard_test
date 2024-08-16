import asyncio
from loguru import logger
from aiogram import Dispatcher

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot_setup import bot, dp
from handlers import message_router, form_router
from utils import check_prices


async def on_startup(dispatcher: Dispatcher):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_prices, 'interval', seconds=15)
    scheduler.start()
    logger.info("Scheduler started")


async def main():
    dp.include_router(message_router)
    dp.include_router(form_router)
    logger.info("Routers included")
    dp.startup.register(on_startup)
    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

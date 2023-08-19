"""Main module to run the bot"""
import asyncio
import logging

from telegram.client import dispatcher, telegram_bot
from telegram.handler import router
from twitter.cron import cron_tweet
from twitter.parser import process_login

logging.basicConfig(level=logging.INFO)


async def process_bot():
    """Start the bot"""
    dispatcher.include_router(router)
    await telegram_bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(telegram_bot)


async def process_cron():
    while True:
        await cron_tweet()


async def run_tasks():
    task1 = asyncio.create_task(process_bot())
    task2 = asyncio.create_task(process_cron())
    await task1
    await task2


if __name__ == "__main__":
    process_login()
    asyncio.run(run_tasks())

import asyncio
import logging

from telegram.client import dp, bot
from telegram.handler import tweet
from twitter.cron import cron_tweet

logging.basicConfig(level=logging.INFO)


async def main():
    dp.include_routers(tweet.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def job_every_10_seconds():
    while True:
        await cron_tweet()


async def run_tasks():
    task1 = asyncio.create_task(main())
    task2 = asyncio.create_task(job_every_10_seconds())
    await task1
    await task2


if __name__ == "__main__":
    asyncio.run(run_tasks())

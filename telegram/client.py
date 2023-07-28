import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession


bot_token = os.getenv('BOT_TOKEN')
bot = Bot(token=bot_token, session=AiohttpSession())
dp = Dispatcher()


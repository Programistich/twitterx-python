from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from config_reader import config

bot = Bot(token=config.bot_token.get_secret_value(), session=AiohttpSession())
dp = Dispatcher()


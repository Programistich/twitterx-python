"""Telegram client module."""
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

telegram_bot = Bot(token=os.getenv('BOT_TOKEN'), session=AiohttpSession())
dispatcher = Dispatcher()

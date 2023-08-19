"""Start processor module"""
from telegram.sender import telegram_sender


async def start_processor(chat_id: int):
    """Start processor."""
    await telegram_sender.send_message(chat_id=chat_id, text="Start command")

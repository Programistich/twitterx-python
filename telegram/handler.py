"""Telegram handler module."""
import logging
import re
from typing import Optional

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineQuery, ErrorEvent

from telegram.processors.get_tweets import get_tweets_processor
from telegram.processors.start_command import start_processor
from telegram.processors.tweet_inline import get_tweet_inline_processor

# objects
router = Router()
logger = logging.getLogger("telegram.handler")

# block regex
TWEET_REGEX = "https://(mobile.)?twitter.com/([a-zA-Z0-9_]+)/status/([0-9]+)?(.*)"
TWEET_ID_GROUP = 3
USERNAME_GROUP = 2
tweet_pattern = re.compile(TWEET_REGEX)


@router.errors
async def error_handler(event: ErrorEvent):
    """Error handler."""
    logger.error("Error occurred in Telegram handler: %s", event)


@router.message(Command("start"))
async def start(message: Message):
    """Start command handler."""
    await start_processor(chat_id=message.chat.id)


@router.message(lambda message: tweet_pattern.match(message.text) is not None)
async def get_tweets_by_link(message: Message):
    """Get tweets by link."""
    tweet_id = tweet_pattern.match(message.text).group(TWEET_ID_GROUP)
    username = tweet_pattern.match(message.text).group(USERNAME_GROUP)
    reply_id = process_reply(message)

    await get_tweets_processor(
        chat_id=message.chat.id,
        reply_id=reply_id,
        tweet_id=tweet_id,
        username=username,
        from_user=message.from_user,
        message_id = message.message_id
    )


@router.inline_query()
async def get_tweet_by_link_inline(inline: InlineQuery):
    """Get tweet by link inline."""
    try:
        text = inline.query.strip()
        tweet_id = tweet_pattern.match(text).group(TWEET_ID_GROUP)
        username = tweet_pattern.match(text).group(USERNAME_GROUP)
        await get_tweet_inline_processor(tweet_id=tweet_id, username=username, inline=inline)
    except Exception:
        pass


def process_reply(message: Message) -> Optional[int]:
    """Process reply message."""
    if message.reply_to_message is None:
        return None
    return message.reply_to_message.message_id

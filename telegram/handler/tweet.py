import re

from aiogram import types, Router
from aiogram.filters import Command

from telegram.sender.tweet_send import send_single_tweet
from utils import get_text_from_bot_command

router = Router()

tweet_regex = "https://(mobile.)?twitter.com/([a-zA-Z0-9_]+)/status/([0-9]+)?(.*)"
tweet_id_group = 3
tweet_pattern = re.compile(tweet_regex)


@router.message(lambda message: tweet_pattern.match(message.text) is not None)
async def get_single_tweet_by_link(message: types.Message):
    tweet_id = tweet_pattern.match(message.text).group(tweet_id_group)
    await send_single_tweet(tweet_id, message)

    # delete message with link
    await message.delete()


@router.message(Command("full"))
async def get_branch_tweets_by_link(message: types.Message):
    message_text = get_text_from_bot_command(message)

    is_tweet_link = tweet_pattern.match(message_text) is not None
    if is_tweet_link:
        tweet_id = tweet_pattern.match(message_text).group(tweet_id_group)
        await message.answer("It is tweet with id: " + tweet_id)

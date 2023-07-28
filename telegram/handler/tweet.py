import re

from aiogram import types, Router
from aiogram.filters import Command

import telegram.client
from telegram.sender.tweet_send import send_single_tweet, send_tweets
from utils import get_text_from_bot_command

router = Router()

TWEET_REGEX = "https://(mobile.)?twitter.com/([a-zA-Z0-9_]+)/status/([0-9]+)?(.*)"
TWEET_ID_GROUP = 3
tweet_pattern = re.compile(TWEET_REGEX)


@telegram.client.dp.message(lambda message: tweet_pattern.match(message.text) is not None)
async def get_tweets_by_link(message: types.Message):
    tweet_id = tweet_pattern.match(message.text).group(TWEET_ID_GROUP)

    if message.reply_to_message is None:
        reply_to_message_id = None
    else:
        reply_to_message_id = message.reply_to_message.message_id

    await send_tweets(tweet_id, message, reply_to_message_id)

    # delete message with link
    await message.delete()

#
# @telegram.client.dp.message(Command("full"))
# async def get_branch_tweets_by_link(message: types.Message):
#     message_text = get_text_from_bot_command(message)
#
#     is_tweet_link = tweet_pattern.match(message_text) is not None
#     if not is_tweet_link:
#         return
#
#     if message.reply_to_message is None:
#         reply_to_message_id = None
#     else:
#         reply_to_message_id = message.reply_to_message.message_id
#
#     tweet_id = tweet_pattern.match(message_text).group(TWEET_ID_GROUP)
#     await send_tweets(tweet_id, message, reply_to_message_id)
#
#     # delete message with link
#     await message.delete()

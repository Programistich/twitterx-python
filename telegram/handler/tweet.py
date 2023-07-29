import re

from aiogram import types, Router

import telegram.client
from telegram.sender.tweet_send import  send_tweets

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

import re

from aiogram import types, Router
from aiogram.filters import Command, CommandObject
from aiogram.handlers import inline_query

import telegram.client
from telegram.sender.tweet_inline import send_inline_tweet
from telegram.sender.tweet_send import send_tweets, send_tweet, send_single_tweet

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

    await message.delete()
    await send_tweets(tweet_id, message, reply_to_message_id)


@telegram.client.dp.message(Command("single"))
async def get_tweet_by_link(message: types.Message, command: CommandObject):
    text = command.args.strip()
    tweet_id = tweet_pattern.match(text).group(TWEET_ID_GROUP)
    if tweet_id is None:
        return

    if message.reply_to_message is None:
        reply_to_message_id = None
    else:
        reply_to_message_id = message.reply_to_message.message_id

    await message.delete()
    await send_single_tweet(tweet_id, message, reply_to_message_id)


@telegram.client.dp.inline_query()
async def get_tweet_by_link_inline(inline: types.InlineQuery):
    try:
        text = inline.query.strip()
        tweet_match = tweet_pattern.match(text)
        if tweet_match is None:
            return
        tweet_id = tweet_match.group(TWEET_ID_GROUP)
        if tweet_id is None:
            return
        await send_inline_tweet(tweet_id, inline)
    except Exception as e:
        print(e)

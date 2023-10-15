"""Get tweets processor module."""
import asyncio
import logging

from aiogram.types import User

import cache.client
from telegram.sender import telegram_sender
from twitter.client import get_tweet_branch
from twitter.models import Tweet

logger = logging.getLogger("telegram.processor.get_tweets")
redis = cache.client.redis_client


async def get_tweets_processor(
        chat_id: int,
        tweet_id: str,
        username: str,
        from_user: User,
        reply_id: int,
):
    """Get tweets processor."""
    await telegram_sender.send_action_typing(chat_id)
    already_reply_id = await redis.get_message_id(chat_id, tweet_id)
    if already_reply_id is not None:
        await telegram_sender.send_message(chat_id, text = "Твит уже был отправлен ранее", reply_to_message_id=already_reply_id)
        return

    try:
        tweets_branch = await get_tweet_branch(username=username, tweet_id=tweet_id)
        current_reply_message_id = reply_id
        for index, tweet in enumerate(tweets_branch):
            if index == len(tweets_branch) - 1:
                user = from_user
            else:
                user = None
            current_reply_message_id = await send_tweet(
                chat_id=chat_id,
                reply_message_id=current_reply_message_id,
                tweet=tweet,
                user=user
            )
            await asyncio.sleep(5)

    except Exception as e:
        await telegram_sender.send_message(
            chat_id = chat_id,
            text = f"Произошла ошибка при отправке цепочки <a href='https://fxtwitter.com/{username}/status/{tweet_id}'>твитов</a>"
        )
        logger.error("error %s %s %s", chat_id, tweet_id, e)


async def send_tweet(chat_id, reply_message_id, tweet: Tweet, user: User) -> int:
    """Send tweet."""
    # if tweet already sent
    exist_message_id = await redis.get_message_id(chat_id, tweet.id)
    if exist_message_id is not None:
        return exist_message_id

    try:
        message_id = await telegram_sender.send_tweet(tweet, chat_id, reply_message_id, user)
        await redis.set_message_id(chat_id, tweet.id, message_id)
    except Exception as e:
        logger.error("error %s %s %s", chat_id, tweet.id, e)
        try:
            await asyncio.sleep(5)
            url = tweet.get_tweet_url().replace("twitter.com", "fxtwitter.com")
            message_id = await telegram_sender.send_message(
                chat_id=chat_id,
                text=f"Ошибка при отправке твита {url}",
                reply_to_message_id=reply_message_id,
            )
        except Exception as e:
            logger.error("error %s %s %s", chat_id, tweet.id, e)
            message_id = None
    return message_id

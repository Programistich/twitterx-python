import asyncio
import logging

from aiogram.types import URLInputFile

from cache.client import set_message_id, get_message_id
from telegram.client import bot as telegram_bot
from twitter.model import TweetModel
from twitter.tweets import get_tweet_by_id, translate_tweet_text, find_tweet_branch, get_tweet_body

log = logging.getLogger(__name__)


async def send_tweets(tweet_id: str, chat_id: str) -> int:
    await telegram_bot.send_chat_action(chat_id=chat_id, action="typing")
    exist_message_id = await get_message_id(chat_id, tweet_id)
    if exist_message_id is not None:
        return exist_message_id

    tweets_branch = find_tweet_branch(tweet_id)
    current_reply_message_id = None
    for tweet_branch_id in reversed(tweets_branch):
        current_reply_message_id = await send_many_tweet(
            tweet_id=tweet_branch_id,
            chat_id=chat_id,
            reply_message_id=current_reply_message_id
        )
    return current_reply_message_id


async def send_many_tweet(
        tweet_id: str,
        chat_id: str,
        reply_message_id: int
) -> int:
    tweet = get_tweet_by_id(tweet_id)
    exist_message_id = await get_message_id(chat_id, tweet.id_str)
    if exist_message_id is not None:
        return exist_message_id

    try:
        message_id = await send_tweet(chat_id, reply_message_id, tweet)
    except Exception as e:
        log.error("error send_tweet %s %s %s", chat_id, tweet.id_str, e)
        await asyncio.sleep(10)
        try:
            result = await telegram_bot.send_message(
                text=f"Ошибка при отправке твита {tweet.get_tweet_url()} от {tweet.user.screen_name}",
                chat_id=chat_id,
                reply_to_message_id=reply_message_id,
                disable_web_page_preview=False
            )
            message_id = result.message_id
        except Exception as e:
            log.error("error send_message %s %s %s", chat_id, tweet.id_str, e)
            message_id = None

    await set_message_id(chat_id, tweet.id_str, message_id)
    return message_id


async def send_tweet(chat_id: str, reply_message_id: int, tweet):
    message_head = get_tweet_header(tweet)
    message_tweet = get_tweet_body(tweet)
    message_text = f"{message_head}\n\n{message_tweet}".strip()
    if tweet.is_single_photo():
        await telegram_bot.send_chat_action(chat_id=chat_id, action="upload_photo")
        photo_file = URLInputFile(url=tweet.single_media().url, bot=telegram_bot)
        message = await telegram_bot.send_photo(
            chat_id=chat_id,
            photo=photo_file,
            caption=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id
        )
        message_id = message.message_id

    elif tweet.is_single_video():
        await telegram_bot.send_chat_action(chat_id=chat_id, action="upload_video")
        video_file = URLInputFile(url=tweet.single_media().url, bot=telegram_bot)
        message = await telegram_bot.send_video(
            chat_id=chat_id,
            video=video_file,
            caption=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id
        )
        message_id = message.message_id

    elif tweet.is_multi_media():
        await telegram_bot.send_chat_action(chat_id=chat_id, action="upload_photo")
        result = tweet.get_telegram_media(telegram_bot, message_text)

        message = await telegram_bot.send_media_group(
            chat_id=chat_id,
            media=result,
            reply_to_message_id=reply_message_id
        )
        message_id = message[0].message_id

    else:
        await telegram_bot.send_chat_action(chat_id=chat_id, action="typing")
        hide_link = tweet.get_hide_link()
        message = await telegram_bot.send_message(
            text=hide_link + message_text,
            parse_mode="HTML",
            chat_id=chat_id,
            reply_to_message_id=reply_message_id,
            disable_web_page_preview=hide_link == ""
        )
        message_id = message.message_id
    return message_id


def get_tweet_header(tweet: TweetModel):
    return f"<a href='{tweet.get_tweet_url()}'>Твит</a> от {tweet.user.get_url_html()}"


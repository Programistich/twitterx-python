import asyncio
import logging

from aiogram import types
from aiogram.types import URLInputFile

from cache.client import set_message_id, get_message_id
from telegram.client import bot as telegram_bot
from twitter.model import TweetModel
from twitter.tweets import get_tweet_by_id, translate_tweet_text, find_tweet_branch, get_tweet_body

log = logging.getLogger(__name__)


async def send_single_tweet(tweet_id: str, message: types.Message, reply_message_id=None) -> int:
    await telegram_bot.send_chat_action(chat_id=message.chat.id, action="typing")
    exist_message_id = await get_message_id(message.chat.id, tweet_id)
    if exist_message_id is not None:
        await message.answer(
            text="Твит уже был отправлен ранее",
            parse_mode="HTML",
            reply_to_message_id=exist_message_id,
            disable_web_page_preview=False
        )
        return exist_message_id

    await send_many_tweet(tweet_id, message, reply_message_id, True)


async def send_tweets(tweet_id: str, message: types.Message, reply_message_id=None) -> int:
    await telegram_bot.send_chat_action(chat_id=message.chat.id, action="typing")
    exist_message_id = await get_message_id(message.chat.id, tweet_id)
    if exist_message_id is not None:
        await message.answer(
            text="Твит уже был отправлен ранее",
            parse_mode="HTML",
            reply_to_message_id=exist_message_id,
            disable_web_page_preview=False
        )
        return exist_message_id

    tweets_branch = find_tweet_branch(tweet_id)
    current_reply_message_id = reply_message_id
    for index, tweet_branch_id in enumerate(reversed(tweets_branch)):
        is_main_tweet = index == len(tweets_branch) - 1
        current_reply_message_id = await send_many_tweet(tweet_branch_id, message, current_reply_message_id,
                                                         is_main_tweet)
    return current_reply_message_id


async def send_many_tweet(
        tweet_id: str,
        message: types.Message,
        reply_message_id: int,
        is_main_tweet: bool
) -> int:
    tweet = get_tweet_by_id(tweet_id)
    exist_message_id = await get_message_id(message.chat.id, tweet.id_str)
    if exist_message_id is not None:
        return exist_message_id

    chat_id = message.chat.id

    try:
        message_id = await send_tweet(is_main_tweet, message, reply_message_id, tweet)
        await set_message_id(chat_id, tweet.id_str, message_id)
    except Exception as e:
        log.error("error %s %s %s", chat_id, tweet.id_str, e)
        try:
            await asyncio.sleep(10)
            result = await message.answer(
                text=f"Ошибка при отправке твита {tweet.get_tweet_url()}",
                parse_mode="HTML",
                reply_to_message_id=reply_message_id,
                disable_web_page_preview=False
            )
            message_id = result.message_id
        except Exception as e:
            log.error("error %s %s %s", chat_id, tweet.id_str, e)
            message_id = None
    await asyncio.sleep(5)
    return message_id


async def send_tweet(is_main_tweet, message, reply_message_id, tweet):
    message_head = get_tweet_header(tweet, message.from_user, is_main_tweet)
    message_tweet = get_tweet_body(tweet)
    message_text = f"{message_head}\n\n{message_tweet}".strip()
    if tweet.is_single_photo():
        await telegram_bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
        photo_file = URLInputFile(url=tweet.single_media().url, bot=telegram_bot)
        message = await message.answer_photo(
            photo=photo_file,
            caption=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id
        )
        message_id = message.message_id

    elif tweet.is_single_video():
        await telegram_bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
        video_file = URLInputFile(url=tweet.single_media().url, bot=telegram_bot)
        message = await message.answer_video(
            video=video_file,
            caption=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id
        )
        message_id = message.message_id

    elif tweet.is_multi_media():
        await telegram_bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
        result = tweet.get_telegram_media(telegram_bot, message_text)

        message = await message.answer_media_group(
            media=result,
            caption=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id
        )
        message_id = message[0].message_id

    else:
        await telegram_bot.send_chat_action(chat_id=message.chat.id, action="typing")
        hide_link = tweet.get_hide_link()
        message = await message.answer(
            text=hide_link + message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id,
            disable_web_page_preview=hide_link == ""
        )
        message_id = message.message_id
    return message_id


def get_tweet_header(tweet: TweetModel, telegram_user, is_main_tweet):
    if is_main_tweet:
        return f"<a href='{tweet.get_tweet_url()}'>Твит</a> от {tweet.user.get_url_html()} by {telegram_user.full_name}"
    else:
        return f"<a href='{tweet.get_tweet_url()}'>Твит</a> от {tweet.user.get_url_html()}"

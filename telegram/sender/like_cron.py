import asyncio

from aiogram.types import URLInputFile

from telegram.client import bot as telegram_bot
from twitter.model import TweetModel, UserModel
from twitter.tweets import get_tweet_by_id, translate_tweet_text


async def send_error_like(chat_id: str, user: UserModel, tweet_id: str):
    await telegram_bot.send_message(
        text=f"Ошибка при отправке лайка от {user.screen_name} на твит {tweet_id}",
        parse_mode="HTML",
        chat_id=chat_id
    )


async def send_like(chat_id: str, tweet_id, user: UserModel):
    tweet = get_tweet_by_id(tweet_id)
    message_head = get_tweet_header(tweet, user)
    message_tweet = get_tweet_body(tweet)
    message_text = f"{message_head}\n\n{message_tweet}".strip()
    if tweet.is_single_photo():
        photo_file = URLInputFile(url=tweet.single_media().url, bot=telegram_bot)
        message = await telegram_bot.send_photo(
            chat_id=chat_id,
            photo=photo_file,
            caption=message_text,
            parse_mode="HTML",
        )
        message_id = message.message_id

    elif tweet.is_single_video():
        video_file = URLInputFile(url=tweet.single_media().url, bot=telegram_bot)
        message = await telegram_bot.send_video(
            chat_id=chat_id,
            video=video_file,
            caption=message_text,
            parse_mode="HTML",
        )
        message_id = message.message_id

    elif tweet.is_multi_media():
        result = tweet.get_telegram_media(telegram_bot, message_text)

        message = await telegram_bot.send_media_group(
            chat_id=chat_id,
            media=result,
            parse_mode="HTML",
        )
        message_id = message[0].message_id

    else:
        hide_link = tweet.get_hide_link()
        message = await telegram_bot.send_message(
            text=hide_link + message_text,
            parse_mode="HTML",
            chat_id=chat_id,
            disable_web_page_preview=hide_link == ""
        )
        message_id = message.message_id
    await asyncio.sleep(10)
    return message_id


def get_tweet_header(tweet: TweetModel, user: UserModel):
    return f"<a href='{tweet.get_tweet_url()}'>Лайк</a> от {user.get_url_html()} на твит от {tweet.user.get_url_html()}"


def get_tweet_body(tweet: TweetModel):
    tweet_text = tweet.text
    translate_tweet = translate_tweet_text(tweet_text, tweet.lang)

    if translate_tweet.dest == translate_tweet.src:
        return tweet_text

    else:
        return f"[{translate_tweet.src.upper()}] {tweet_text}\n\n[{translate_tweet.dest.upper()}] {translate_tweet.text}"

from aiogram.types import URLInputFile

from cache.client import set_message_id, get_message_id
from telegram.client import bot as telegram_bot
from twitter.model import TweetModel
from twitter.tweets import get_tweet_by_id, translate_tweet_text, find_tweet_branch


async def send_tweets(tweet_id: str, chat_id: str) -> int:
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

    message_id = await send_tweet(chat_id, reply_message_id, tweet)
    result = await set_message_id(chat_id, tweet.id_str, message_id)
    print(f"Set message_id: {result}")
    return message_id


async def send_tweet(chat_id: str, reply_message_id: int, tweet):
    message_head = get_tweet_header(tweet)
    message_tweet = get_tweet_body(tweet)
    message_text = f"{message_head}\n\n{message_tweet}".strip()
    if tweet.is_single_photo():
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
        result = tweet.get_telegram_media(telegram_bot, message_text)

        message = await telegram_bot.send_media_group(
            chat_id=chat_id,
            media=result,
            caption=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id
        )
        message_id = message[0].message_id

    else:
        message = await telegram_bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id,
            disable_web_page_preview=False
        )
        message_id = message.message_id
    return message_id


def get_tweet_header(tweet: TweetModel):
    hide_link = tweet.get_hide_link()
    return f"{hide_link}<a href='{tweet.get_tweet_url()}'>Твит</a> от {tweet.user.get_url_html()}"


def get_tweet_body(tweet: TweetModel):
    tweet_text = tweet.text
    translate_tweet = translate_tweet_text(tweet_text, tweet.lang)

    if translate_tweet.dest == translate_tweet.src:
        return tweet_text

    else:
        return f"[{translate_tweet.src.upper()}] {tweet_text}\n\n[{translate_tweet.dest.upper()}] {translate_tweet.text}"

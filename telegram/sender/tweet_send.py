from aiogram import types
from aiogram.types import URLInputFile

from telegram.client import bot as telegram_bot
from twitter.model import TweetModel
from twitter.tweets import get_tweet_by_id, translate_tweet_text


async def send_single_tweet(tweet_id: str, message: types.Message, reply_message_id=None) -> int:
    tweet = get_tweet_by_id(tweet_id)

    message_head = get_tweet_header(tweet, message.from_user)
    message_tweet = get_tweet_body(tweet)
    message_text = f"{message_head}\n\n{message_tweet}".strip()

    if tweet.is_single_photo():
        photo_file = URLInputFile(url=tweet.single_media().url, bot=telegram_bot)
        await message.answer_photo(
            photo=photo_file,
            caption=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id,
            disable_web_page_preview=True
        )

    elif tweet.is_single_video():
        video_file = URLInputFile(url=tweet.single_media().url, bot=telegram_bot)
        await message.answer_video(
            video=video_file,
            caption=message_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    elif tweet.is_multi_media():
        result = []
        for index, media in enumerate(tweet.media):
            file = URLInputFile(url=media.url, bot=telegram_bot)

            if media.type.value == "photo":
                if index == 0:
                    result.append(types.InputMediaPhoto(media=file, caption=message_text, parse_mode="HTML"))
                else:
                    result.append(types.InputMediaPhoto(media=file))
            elif media.type.value == "video":
                if index == 0:
                    result.append(types.InputMediaVideo(media=file, caption=message_text, parse_mode="HTML"))
                else:
                    result.append(types.InputMediaVideo(media=file))

        await message.answer_media_group(
            media=result,
            caption=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id,
            disable_web_page_preview=True
        )

    else:
        await message.answer(
            text=message_text,
            parse_mode="HTML",
            reply_to_message_id=reply_message_id,
            disable_web_page_preview=True
        )

    return -1


def get_tweet_header(tweet: TweetModel, telegram_user):
    return f"<a href='{tweet.get_tweet_url()}'>Твит</a> от {tweet.user.get_url_html()} by {telegram_user.full_name}"


def get_tweet_body(tweet: TweetModel):
    tweet_text = tweet.text
    translate_tweet = translate_tweet_text(tweet_text, tweet.lang)

    if translate_tweet.dest == translate_tweet.src:
        return tweet_text

    else:
        return f"[{translate_tweet.src.upper()}] {tweet_text}\n\n[{translate_tweet.dest.upper()}] {translate_tweet.text}"


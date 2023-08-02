from aiogram import types
from aiogram.types import InlineQueryResultArticle, InlineQueryResultCachedPhoto, InlineQueryResultPhoto

from twitter.model import TweetModel
from twitter.tweets import get_tweet_by_id, get_tweet_body


async def send_inline_tweet(tweet_id: str, inline: types.InlineQuery):
    tweet = get_tweet_by_id(tweet_id)

    if tweet.is_single_photo():
        image_url = tweet.media[0].url
    else:
        image_url = None

    result = InlineQueryResultArticle(
        id=tweet.id_str,
        title=tweet.user.name,
        description=tweet.text,
        url=tweet.get_tweet_url(),
        thumb_url=image_url,
        input_message_content=types.InputTextMessageContent(
            message_text=get_tweet_text(tweet),
            parse_mode="HTML"
        )
    )

    await inline.answer([result], is_personal=True, cache_time=0)


def get_tweet_text(tweet: TweetModel) -> str:
    message_tweet = get_tweet_body(tweet)
    message_head = f"<a href='{tweet.get_tweet_url()}'>Твит</a> от {tweet.user.get_url_html()}"
    return f"{message_head}\n\n{message_tweet}"

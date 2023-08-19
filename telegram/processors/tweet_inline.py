import logging

from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.markdown import hide_link

from twitter.client import get_tweet
from twitter.models import Tweet
from twitter.translate import translate_tweet_text, get_emoji_by_lang, get_translated_tweet_body, \
    get_translated_tweet_header

logger = logging.getLogger("tweet_inline_processor")

variants = [
    "en",
    "ru",
    "uk"
]


async def get_tweet_inline_processor(tweet_id: str, username: str, inline: InlineQuery):
    try:
        tweet = await get_tweet(tweet_id=tweet_id, username=username)
        result = list(map(lambda variant: get_result_article(tweet, variant), variants))

        await inline.answer(result, is_personal=True, cache_time=0)
    except Exception as e:
        logger.error(e)


def get_result_article(tweet: Tweet, variant: str) -> InlineQueryResultArticle:
    image_url = tweet.get_mosaic()

    if image_url is None:
        image_url_hide = ""
    else:
        image_url_hide = f"{hide_link(tweet.get_mosaic())}"

    translated_text = translate_tweet_text(tweet, variant)
    emoji = get_emoji_by_lang(variant)
    input_text = image_url_hide + get_translated_tweet_header(tweet, None, variant) + "\n\n" + get_translated_tweet_body(tweet, variant)

    return InlineQueryResultArticle(
        id=tweet.id + "_" + variant,
        title=tweet.author.name,
        description=f"{emoji} {translated_text.text}",
        thumb_url=image_url,
        input_message_content=InputTextMessageContent(
            message_text=input_text,
            parse_mode="HTML",
            disable_web_page_preview=image_url is None
        )
    )
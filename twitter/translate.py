import emojiflag
from googletrans import Translator, LANGUAGES
from googletrans.models import Translated

from twitter.models import Tweet

translator = Translator()


def translate_tweet_text(tweet: Tweet, to_lang: str = "en") -> Translated:
    tweet_lang = tweet.lang or "auto"
    if tweet_lang not in LANGUAGES:
        tweet_lang = "auto"

    return translator.translate(tweet.text, src=tweet_lang, dest=to_lang)


def get_emoji_by_lang(lang: str) -> str:
    if lang.lower() == "uk":
        lang = "ua"
    return f"[{lang.upper()}]"


def get_translated_tweet_body(tweet: Tweet, to_lang="en"):
    translate = translate_tweet_text(tweet, to_lang)

    if translate.src == translate.dest:
        return tweet.text

    src_flag = get_emoji_by_lang(translate.src)
    dest_flag = get_emoji_by_lang(translate.dest)

    return f"{src_flag} {tweet.text}\n\n{dest_flag} {translate.text}"


def get_translated_tweet_header(tweet: Tweet, telegram_user, variant = "en"):
    header = get_tweet_header(variant, tweet)
    if telegram_user is not None:
        return header + " by " + telegram_user.full_name
    else:
        return header


def get_tweet_header(variant: str, tweet: Tweet):
    if variant == "ru":
        tweet_link = f"<a href='{tweet.url}'>Твит</a> от <a href='{tweet.author.url}'>{tweet.author.name}</a>"
    elif variant == "uk":
        tweet_link = f"<a href='{tweet.url}'>Твіт</a> від <a href='{tweet.author.url}'>{tweet.author.name}</a>"
    else:
        tweet_link = f"<a href='{tweet.url}'>Tweet</a> by <a href='{tweet.author.url}'>{tweet.author.name}</a>"

    return tweet_link


from twitter.client import twitter
from twitter.model import TweetModel
from googletrans import Translator, LANGUAGES

translator = Translator()


def get_tweet_by_id(tweet_id) -> TweetModel:
    status = twitter.get_status(
        id=tweet_id,
        tweet_mode="extended",
        include_entities=True,
        include_ext_alt_text=False
    )

    return TweetModel(status)


def find_tweet_branch(tweet_id) -> [str]:
    tweet = get_tweet_by_id(tweet_id)
    if tweet.reply_tweet_id is None:
        return [tweet_id]

    return [tweet_id] + find_tweet_branch(tweet.reply_tweet_id)


def translate_tweet_text(text: str, lang: str):
    if lang not in LANGUAGES:
        lang = "auto"

    return translator.translate(text, src=lang, dest="ru")

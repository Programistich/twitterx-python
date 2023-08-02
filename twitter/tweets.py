from twitter.client import twitter
from twitter.model import TweetModel, UserModel
from googletrans import Translator, LANGUAGES
from aiogram import html as aiogram_html

translator = Translator()


def get_tweet_by_id(tweet_id) -> TweetModel:
    status = twitter.get_status(
        id=tweet_id,
        tweet_mode="extended",
        include_entities=True,
        include_ext_alt_text=False
    )

    return TweetModel(status)


def get_user_by_id(user_id):
    user = twitter.get_user(user_id=user_id)
    return UserModel(user)


def find_tweet_branch(tweet_id) -> [str]:
    tweet = get_tweet_by_id(tweet_id)
    if tweet.reply_tweet_id is None:
        return [tweet_id]

    return [tweet_id] + find_tweet_branch(tweet.reply_tweet_id)


def translate_tweet_text(text: str, lang: str):
    if lang not in LANGUAGES:
        lang = "auto"

    return translator.translate(text, src=lang, dest="ru")


def get_tweet_body(tweet: TweetModel):
    tweet_text = tweet.text
    translate_tweet = translate_tweet_text(tweet_text, tweet.lang)

    if translate_tweet.dest == translate_tweet.src:
        return tweet_text

    else:
        return f"[{translate_tweet.src.upper()}] {tweet_text}\n\n[{translate_tweet.dest.upper()}] {translate_tweet.text}"

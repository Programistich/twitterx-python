from twitter.models import Tweet
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))


class Translated:
    def __init__(self, text, src, dest):
        self.text = text
        self.src = src
        self.dest = dest


def translate_text(text, target_language):
    if text.strip() == "":
        return ""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Translate the following text into {target_language}: {text}\n In additional, ignore urls and mentions in translation."
            }
        ]
    )
    return response.choices[0].message.content


def translate_tweet_text(tweet: Tweet, to_lang: str = "en") -> Translated:
    return Translated(
        text=translate_text(tweet.text, to_lang),
        src=tweet.lang,
        dest=to_lang
    )


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


def get_translated_tweet_header(tweet: Tweet, telegram_user, variant="en"):
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


LANGUAGES = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'or': 'odia',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu',
}
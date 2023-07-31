import re
from enum import Enum

from aiogram import types
from aiogram.types import URLInputFile
from aiogram.utils.markdown import hide_link


class MediaType(Enum):
    PHOTO = "photo"
    VIDEO = "video"
    GIF = "gif"


class Media:
    def __init__(self, media_type: MediaType, url: str):
        self.url = url
        self.type = media_type


class UserModel:
    def __init__(self, user):
        self.id = user.id_str
        self.name = user.name
        self.screen_name = user.screen_name

    def get_url_html(self):
        return f"<a href='https://twitter.com/{self.screen_name}'>{self.name}</a>"


class TweetModel:

    def __init__(self, status):
        self.id_str = status.id_str
        self.created_at = status.created_at
        self.retweeted = status.retweeted
        self.user = UserModel(status.user)
        self.status = status
        self.lang = status.lang
        self.reply_tweet_id = self.__parse_reply__()
        self.media = self.__parse_media__()
        self.text = self.__parse_text__()

    def get_tweet_url(self):
        return f"https://twitter.com/{self.user.screen_name}/status/{self.id_str}"

    def is_single_photo(self):
        filter_photo = list(filter(lambda media: media.type == MediaType.PHOTO, self.media))
        return len(filter_photo) == 1

    def single_media(self) -> Media:
        return self.media[0]

    def is_single_video(self):
        filter_photo = list(filter(lambda media: media.type == MediaType.VIDEO, self.media))
        return len(filter_photo) == 1

    def is_multi_media(self):
        return len(self.media) > 1

    def __parse_text__(self):
        text = self.status.full_text

        media_entity = self.status.entities.get("media", [])
        media_urls = list(map(lambda media: media["url"], media_entity))
        for media_url in media_urls:
            text = text.replace(media_url, "")

        user_mentions = self.status.entities.get("user_mentions", [])
        for user_mention in user_mentions:
            screen_name = user_mention["screen_name"]
            url = f"https://twitter.com/{screen_name}"
            text = text.replace(f"@{screen_name}", f"<a href='{url}'>@{screen_name}</a>")

        urls_hide = self.status.entities.get("urls", [])
        for url_hide in urls_hide:
            url = url_hide["url"]
            expanded_url = url_hide["expanded_url"]

            if self.reply_tweet_id is None:
                text = text.replace(url, expanded_url)
                continue

            tweet_regex = f'https://(mobile.)?twitter.com/([a-zA-Z0-9_]+)/status/{self.reply_tweet_id}?(.*)'
            tweet_pattern = re.compile(tweet_regex)
            if tweet_pattern.match(expanded_url) is not None:
                text = text.replace(url, "")
            else:
                text = text.replace(url, expanded_url)

        if text is None:
            return ""

        else:
            return text.strip()

    def get_hide_link(self):
        urls_hide = self.status.entities.get("urls", [])
        # filter expanded_url not have twitter.com
        urls_hide = list(filter(lambda url_hide: "twitter.com" not in url_hide["expanded_url"], urls_hide))

        if len(urls_hide) == 0:
            return ""
        return hide_link(urls_hide[0]["expanded_url"])

    def __parse_media__(self) -> [Media]:
        status = self.status
        media = []
        if not hasattr(status, "extended_entities"):
            return media
        for media_item in status.extended_entities.get("media", []):
            if media_item["type"] == "photo":
                photo_url = media_item["media_url_https"]
                media.append(Media(MediaType.PHOTO, photo_url))
            elif media_item["type"] == "video":
                best_bitrate = 0
                best_video_url = None
                for variant in media_item["video_info"]["variants"]:
                    video_url = variant["url"]
                    video_bitrate = variant.get("bitrate", 0)
                    if best_video_url is None or video_bitrate > best_bitrate:
                        best_bitrate = video_bitrate
                        best_video_url = video_url
                if best_video_url is not None:
                    media.append(Media(MediaType.VIDEO, best_video_url))
        return media

    def __parse_reply__(self):
        if self.status.in_reply_to_status_id_str is not None:
            return self.status.in_reply_to_status_id_str

        if self.status.is_quote_status:
            return self.status.quoted_status_id_str

        return None

    def get_telegram_media(self, telegram_bot, message_text):
        result = []
        for index, media in enumerate(self.media):
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

        return result

from enum import Enum


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
        self.reply_tweet_id = status.in_reply_to_status_id_str
        self.created_at = status.created_at
        self.retweeted = status.retweeted
        self.user = UserModel(status.user)
        self.status = status
        self.lang = status.lang
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
        media_entity = self.status.entities.get("media", [])
        media_urls = list(map(lambda media: media["url"], media_entity))

        text = self.status.full_text

        for media_url in media_urls:
            text = text.replace(media_url, "")

        if text is None:
            return ""

        else:
            return text.strip()

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
                    print("best_video_url", best_video_url, "best_bitrate", best_bitrate)
                    media.append(Media(MediaType.VIDEO, best_video_url))
        return media

from typing import List


class Author:
    name: str
    screen_name: str
    url: str

    def __init__(self, author_json):
        self.name = author_json.get("name")
        self.screen_name = author_json.get("screen_name")
        self.url = "https://twitter.com/" + self.screen_name


class Video:
    url: str
    type: str

    def __init__(self, video_json):
        self.url = video_json.get("url")
        self.type = video_json.get("type")


class Photo:
    url: str
    type: str

    def __init__(self, photo_json):
        self.type = photo_json.get("type")
        self.url = photo_json.get("url")


class Mosaic:
    url_jpeg: str

    def __new__(cls, mosaic_json):
        if mosaic_json is None:
            return None

        instance = super(Mosaic, cls).__new__(cls)
        instance.url_jpeg = mosaic_json.get("formats").get("jpeg")
        return instance


class Media:
    videos: List[Video]
    photos: List[Photo]
    mosaic: Mosaic

    def __new__(cls, media_json):
        if media_json is None:
            return None

        instance = super(Media, cls).__new__(cls)

        videos_json = media_json.get("videos")
        if videos_json is None:
            instance.videos = []
        else:
            instance.videos = [Video(video_json) for video_json in videos_json]

        photos_json = media_json.get("photos")
        if photos_json is None:
            instance.photos = []
        else:
            instance.photos = [Photo(photo_json) for photo_json in media_json.get("photos")]

        mosaic_json = Mosaic(media_json.get("mosaic"))
        if mosaic_json is None:
            instance.mosaic = None
        else:
            instance.mosaic = mosaic_json

        return instance


class PollChoice:
    label: str

    def __new__(cls, poll_choice_json):
        if poll_choice_json is None:
            return None

        instance = super(PollChoice, cls).__new__(cls)
        instance.label = poll_choice_json.get("label")
        return instance


class Poll:
    choices: List[PollChoice]

    def __new__(cls, poll_json):
        if poll_json is None:
            return None

        instance = super(Poll, cls).__new__(cls)
        instance.choices = [PollChoice(poll_choice_json) for poll_choice_json in poll_json.get("choices")]
        return instance


class Tweet:
    id: str
    url: str
    text: str
    created_timestamp: int
    author: Author
    lang: str
    replying_to: str
    replying_to_status: str
    media: Media
    poll: Poll

    def __init__(self, tweet_json):
        self.id = tweet_json.get("id")
        self.url = tweet_json.get("url")
        self.text = tweet_json.get("text")
        self.created_timestamp = tweet_json.get("created_timestamp")
        self.author = Author(tweet_json.get("author"))
        self.lang = tweet_json.get("lang")
        self.replying_to = tweet_json.get("replying_to")
        self.replying_to_status = tweet_json.get("replying_to_status")
        self.media = Media(tweet_json.get("media"))
        self.poll = Poll(tweet_json.get("poll"))

        # case with quote
        quote = tweet_json.get("quote")
        if quote is not None:
            self.replying_to_status = quote.get("id")
            self.replying_to = quote.get("author").get("screen_name")

    def is_reply(self) -> bool:
        return self.replying_to is not None and self.replying_to_status is not None

    def get_mosaic(self):
        if self.media is None:
            return None

        if self.media.mosaic is not None:
            return self.media.mosaic.url_jpeg

        photos = self.media.photos

        if len(photos) == 0:
            return None

        return photos[0].url

    def get_tweet_url(self):
        return f"https://twitter.com/{self.author.screen_name}/status/{self.id}"

    def get_single_photo(self):
        if self.media is None:
            return None

        if len(self.media.photos) == 1 and len(self.media.videos) == 0:
            return self.media.photos[0]

        return None

    def get_single_video(self):
        if self.media is None:
            return None

        if len(self.media.videos) == 1 and len(self.media.photos) == 0:
            return self.media.videos[0]

        return None

    def get_multi_media(self):
        if self.media is None:
            return None

        return self.media.videos + self.media.photos

    def get_poll(self):
        if self.poll is None:
            return None

        # get labels from choices
        return [choice.label for choice in self.poll.choices]


class TweetData:
    code: int
    message: str
    tweet: Tweet

    def __init__(self, tweet_data_json):
        self.code = tweet_data_json.get("code")
        self.message = tweet_data_json.get("message")
        self.tweet = Tweet(tweet_data_json.get("tweet"))

"""Twitter client."""
from typing import List

import aiohttp
import unittest

from twitter.models import TweetData, Tweet


async def get_tweet(tweet_id: str, username: str) -> Tweet:
    url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json = await response.json()
            tweet_data = TweetData(json)
            return tweet_data.tweet


async def get_tweet_branch(tweet_id: str, username: str) -> List[Tweet]:
    root = await get_tweet(tweet_id, username)
    if root.is_reply():
        return await get_tweet_branch(root.replying_to_status, root.replying_to) + [root]
    else:
        return [root]


class TestGetTweet(unittest.IsolatedAsyncioTestCase):
    username = "elonmusk"

    async def test_tweet_only_text(self):
        tweet_id = "1692431966849921527"

        # tweet
        tweet = await get_tweet(tweet_id, self.username)
        self.assertEqual(tweet.text, "We need to make this interface far more beautiful")
        self.assertEqual(tweet.url, f"https://twitter.com/{self.username}/status/{tweet_id}")

        # author
        author = tweet.author
        self.assertEqual(author.screen_name, self.username)

        # media
        media = tweet.media
        self.assertEqual(media, None)

        # poll
        poll = tweet.poll
        self.assertEqual(poll, None)

    async def test_tweet_with_photo(self):
        tweet_id = "1690889882174971904"
        tweet = await get_tweet(tweet_id, self.username)

        # media
        media = tweet.media
        self.assertNotEquals(media, None)

        # photos
        photos = media.photos
        self.assertEqual(len(photos), 1)
        single_photo = photos[0]
        self.assertEqual(single_photo.url, "https://pbs.twimg.com/media/F3c_YtaXwAEAKWE.jpg")

    async def test_tweet_with_video(self):
        tweet_id = "1692325844570833386"
        tweet = await get_tweet(tweet_id, self.username)

        # media
        media = tweet.media
        self.assertNotEquals(media, None)

        # photos
        videos = media.videos
        self.assertEqual(len(videos), 1)
        single_videos = videos[0]
        self.assertEqual(single_videos.url, "https://video.twimg.com/tweet_video/F3xZUvlbUAAbZ_E.mp4")

    async def test_tweet_with_poll(self):
        tweet_id = "1604617643973124097"
        tweet = await get_tweet(tweet_id, self.username)

        # poll
        poll = tweet.poll
        self.assertNotEquals(poll, None)
        poll_choices = poll.choices
        self.assertEqual(len(poll_choices), 2)

        # poll choice
        poll_choices_values = [poll_choice.label for poll_choice in poll_choices]
        self.assertEqual(poll_choices_values, ["Yes", "No"])

    async def test_tweet_with_medias(self):
        tweet_id = "1664330035530964996"
        tweet = await get_tweet(tweet_id, self.username)

        # media
        media = tweet.media
        self.assertNotEquals(media, None)

        # photos
        photos = media.photos
        self.assertEqual(len(photos), 2)
        photos_urls = [photo.url for photo in photos]
        print(photos_urls)
        self.assertEqual(photos_urls, ['https://pbs.twimg.com/media/FxjjWHpX0AAqr11.jpg',
                                       'https://pbs.twimg.com/media/FxjjWIGWIAQ9Ply.jpg'])

    async def test_tweet_with_reply(self):
        tweet_id = "1692505523977957817"
        tweet = await get_tweet(tweet_id, self.username)

        self.assertEqual(tweet.replying_to, "elonmusk")
        self.assertEqual(tweet.replying_to_status, "1692486041989517670")

    async def test_tweet_with_quote(self):
        tweet_id = "1692432631382852066"
        tweet = await get_tweet(tweet_id, self.username)

        self.assertEqual(tweet.replying_to, "VivekGRamaswamy")
        self.assertEqual(tweet.replying_to_status, "1692267994490060817")

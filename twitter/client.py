import tweepy

from config_reader import config

auth = tweepy.OAuth2BearerHandler(config.twitter_bearer.get_secret_value())
twitter = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(bearer_token=config.twitter_bearer.get_secret_value())

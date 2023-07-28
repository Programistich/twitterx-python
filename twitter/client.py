import os

import tweepy


twitter_bearer = os.getenv('TWITTER_BEARER')

auth = tweepy.OAuth2BearerHandler(twitter_bearer)
twitter = tweepy.API(auth, wait_on_rate_limit=True)


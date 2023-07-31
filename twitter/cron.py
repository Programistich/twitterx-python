import asyncio
import logging

from cache.client import get_user_last_tweet, set_user_last_tweet, get_user_last_like, set_user_last_like
from telegram.sender.like_cron import send_like
from telegram.sender.tweet_cron import send_tweets
from twitter.client import twitter
from twitter.tweets import get_user_by_id

chat_ids = ["2107708834", "-1001488807577"]
twitter_ids = [44196397]

log = logging.getLogger(__name__)


async def cron_tweet():
    log.info("Job executed")
    log.info("Job executed")
    for twitter_id in twitter_ids:
        await process_tweet(twitter_id)
        await process_like(twitter_id)

    await asyncio.sleep(120)


async def process_tweet(user_id):
    log.info("process_tweet")
    # get last 10 tweet
    statuses = twitter.user_timeline(user_id=user_id, count=10, tweet_mode="extended", include_rts=False)
    log.info("statuses len: ", len(statuses))
    log.info("statuses ids: ", [status.id for status in statuses])

    # get statuses where id more than last_tweet_id, but if last_tweet_id is None, get last status
    last_tweet_id = await get_user_last_tweet(user_id)
    log.info("last_tweet_id: ", last_tweet_id)
    if last_tweet_id is None:
        filter_statuses = [statuses[0]]
    else:
        filter_statuses = [status for status in statuses if status.id > int(last_tweet_id)]
    log.info("filter_statuses len: ", len(filter_statuses))

    if len(filter_statuses) == 0:
        log.info("no new tweet")
        return

    for filter_status in filter_statuses:
        for chat_id in chat_ids:
            try:
                await send_tweets(tweet_id=filter_status.id, chat_id=chat_id)
            except Exception as e:
                log.info(f"error: {chat_id} {filter_status.id}", e)

    # save last status id
    last_status = filter_statuses[0]
    log.info("last_status: ", last_status)
    result_save = await set_user_last_tweet(user_id, last_status.id)
    log.info("result_save: ", result_save)


async def process_like(user_id):
    log.info("process_like")
    statuses = twitter.get_favorites(user_id=user_id, count=10)
    log.info("statuses len: ", len(statuses))
    log.info("statuses ids: ", [status.id for status in statuses])

    user = get_user_by_id(user_id=user_id)

    # get statuses where id more than last_tweet_id, but if last_tweet_id is None, get last status
    last_tweet_id = await get_user_last_like(user_id)
    log.info("last_tweet_id: ", last_tweet_id)
    if last_tweet_id is None:
        filter_statuses = [statuses[0]]
    else:
        filter_statuses = [status for status in statuses if status.id > int(last_tweet_id)]
    log.info("filter_statuses len: ", len(filter_statuses))

    if len(filter_statuses) == 0:
        log.info("no new tweet")
        return

    for filter_status in filter_statuses:
        for chat_id in chat_ids:
            try:
                await send_like(tweet_id=filter_status.id, chat_id=chat_id, user=user)
            except Exception as e:
                log.info(f"error: {chat_id} {filter_status.id}", e)

    # save last status id
    last_status = filter_statuses[0]
    log.info("last_status: ", last_status)
    result_save = await set_user_last_like(user_id, last_status.id)
    log.info("result_save: ", result_save)

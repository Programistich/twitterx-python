import asyncio
import logging

import cache.client
from telegram.processors.get_tweets import get_tweets_processor
from twitter.parser import get_last_tweets

chat_ids = ["241629528", "-1001488807577"]
twitter_usernames = ["elonmusk"]

log = logging.getLogger(__name__)


async def cron_tweet():
    for twitter_username in twitter_usernames:
        await process_tweet(twitter_username)
    await asyncio.sleep(10)


async def process_tweet(username):
    log.info("process_tweet")
    last_tweets = get_last_tweets(username=username)
    log.info("statuses ids %s", last_tweets)
    log.info("statuses len %s", len(last_tweets))
    if not last_tweets:
        return

    # get statuses where id more than last_tweet_id, but if last_tweet_id is None, get last status
    last_tweet_id = await cache.client.redis_client.get_user_last_tweet(user_id = username)
    log.info("last_tweet_id %s", last_tweet_id)
    if last_tweet_id is None:
        filter_statuses = [last_tweets[0]]
    else:
        filter_statuses = [status for status in last_tweets if int(status) > int(last_tweet_id)]
    log.info("filter_statuses len: %s", len(filter_statuses))

    if len(filter_statuses) == 0:
        log.info("no new tweet")
        return

    for filter_status in filter_statuses:
        for chat_id in chat_ids:
            try:
                await get_tweets_processor(
                    chat_id=int(chat_id),
                    tweet_id=filter_status,
                    username=username,
                    from_user=None,
                    reply_id=None,
                )
                await asyncio.sleep(5)
            except Exception as e:
                log.error("error %s %s %s",chat_id, filter_status, e)

    # save last status id
    last_status = filter_statuses[0]
    log.info("last_status: %s", last_status)
    result_save = await cache.client.redis_client.set_user_last_tweet(user_id = username, tweet_id = last_status)
    log.info("result_save: %s", result_save)


# async def process_like(user_id):
#     log.info("process_like")
#     statuses = twitter.get_favorites(user_id=user_id, count=10)
#     log.info("statuses len %s", len(statuses))
#     log.info("statuses ids %s", [status.id for status in statuses])
#
#     user = get_user_by_id(user_id=user_id)
#
#     # get statuses where id more than last_tweet_id, but if last_tweet_id is None, get last status
#     last_tweet_id = await get_user_last_like(user_id)
#     log.info("last_tweet_id %s", last_tweet_id)
#     if last_tweet_id is None:
#         filter_statuses = [statuses[0]]
#     else:
#         filter_statuses = [status for status in statuses if status.id > int(last_tweet_id)]
#     log.info("filter_statuses len: %s", len(filter_statuses))
#
#     if len(filter_statuses) == 0:
#         log.info("no new tweet")
#         return
#
#     for filter_status in filter_statuses:
#         for chat_id in chat_ids:
#             try:
#                 await send_like(tweet_id=filter_status.id, chat_id=chat_id, user=user)
#                 await asyncio.sleep(5)
#             except Exception as e:
#                 try:
#                     log.error("error %s %s %s", chat_id, filter_status.id, e)
#                     await send_error_like(chat_id=chat_id, user=user, tweet_id=filter_status.id)
#                 except Exception as e:
#                     log.error("error send_error_like %s %s %s", chat_id, filter_status.id, e)
#
#
#     # save last status id
#     last_status = filter_statuses[0]
#     log.info("last_status: %s", last_status)
#     result_save = await set_user_last_like(user_id, last_status.id)
#     log.info("result_save: %s", result_save)

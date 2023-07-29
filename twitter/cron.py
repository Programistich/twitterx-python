import asyncio

from cache.client import get_user_last_tweet, set_user_last_tweet
from telegram.sender.tweet_cron import send_tweets
from twitter.client import twitter

chat_ids = ["2107708834", "-1001488807577"]
twitter_ids = [44196397]


async def cron_tweet():
    print("Job executed")
    for twitter_id in twitter_ids:
        await process_user(twitter_id)

    await asyncio.sleep(10)


async def process_user(user_id):
    # get last 10 tweet
    statuses = twitter.user_timeline(user_id=user_id, count=10, tweet_mode="extended", include_rts=False)
    print("statuses len: ", len(statuses))
    print("statuses ids: ", [status.id for status in statuses])

    # get statuses where id more than last_tweet_id, but if last_tweet_id is None, get last status
    last_tweet_id = await get_user_last_tweet(user_id)
    print("last_tweet_id: ", last_tweet_id)
    if last_tweet_id is None:
        filter_statuses = [statuses[0]]
    else:
        filter_statuses = [status for status in statuses if status.id > int(last_tweet_id)]
    print("filter_statuses len: ", len(filter_statuses))

    if len(filter_statuses) == 0:
        print("no new tweet")
        return

    for filter_status in filter_statuses:
        for chat_id in chat_ids:
            try:
                await send_tweets(tweet_id = filter_status.id, chat_id = chat_id)
            except Exception as e:
                print(f"error: {chat_id} {filter_status.id}", e)

    # save last status id
    last_status = filter_statuses[0]
    print("last_status: ", last_status)
    result_save = await set_user_last_tweet(user_id, last_status.id)
    print("result_save: ", result_save)
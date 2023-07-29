import os

from redis.asyncio.client import Redis

redis_host = os.getenv('REDIS_HOST')
client = Redis(host=redis_host, port=6379, decode_responses=True)


async def get_message_id(chat_id, tweet_id):
    return await client.get(f'{chat_id}:{tweet_id}')


async def set_message_id(chat_id, tweet_id, message_id):
    return await client.set(f'{chat_id}:{tweet_id}', message_id)


async def get_user_last_tweet(user_id):
    return await client.get(user_id)

async def set_user_last_tweet(user_id, tweet_id):
    return await client.set(user_id, tweet_id)
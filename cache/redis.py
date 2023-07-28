from redis.asyncio.client import Redis

redis = Redis(host='localhost', port=6381, decode_responses=True)


async def get_message_id(chat_id, tweet_id):
    return await redis.get(f'{chat_id}:{tweet_id}')


async def set_message_id(chat_id, tweet_id, message_id):
    return await redis.set(f'{chat_id}:{tweet_id}', message_id)

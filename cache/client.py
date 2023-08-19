"""Cache client for caching"""
import os

from redis.asyncio.client import Redis


class RedisClient:
    """Redis client for caching"""

    def __init__(self):
        """Init redis client"""
        self.client = Redis(host=os.getenv('REDIS_HOST'), port=6379, decode_responses=True)

    async def get_message_id(self, chat_id, tweet_id):
        """Get message id from redis cache"""
        return await self.client.get(f'{chat_id}:{tweet_id}')

    async def set_message_id(self, chat_id, tweet_id, message_id):
        """Set message id to redis cache"""
        return await self.client.set(f'{chat_id}:{tweet_id}', message_id)

    async def get_user_last_tweet(self, user_id):
        """Get user last tweet id from redis cache"""
        return await self.client.get(f"{user_id}:tweet")

    async def set_user_last_tweet(self, user_id, tweet_id):
        """Set user last tweet id to redis cache"""
        return await self.client.set(f"{user_id}:tweet", tweet_id)

    async def get_user_last_like(self, user_id):
        """Get user last like id from redis cache"""
        return await self.client.get(f"{user_id}:like")

    async def set_user_last_like(self, user_id, tweet_id):
        """Set user last like id to redis cache"""
        return await self.client.set(f"{user_id}:like", tweet_id)


redis_client = RedisClient()
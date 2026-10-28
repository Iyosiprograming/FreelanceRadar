from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from redis.asyncio import Redis

from app.core.logger import logger
from app.core.redis import redis_client
from app.model.filter_model import Filter


class RedisService:
    def __init__(self, redis: Redis = redis_client):
        self.redis = redis

    # 1. Save user to keywords (e.g. user_1 -> "python", "fastapi")
    async def save_user_keywords(self, user_id: UUID | str, keywords: list[str]) -> None:
        valid_keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
        for kw in valid_keywords:
            key = f"skill:{kw}"
            await self.redis.sadd(key, str(user_id))
        logger.info(f"Saved {len(valid_keywords)} keyword(s) for user: {user_id}")

    # 2. Delete user from keywords
    async def delete_user_keywords(self, user_id: UUID | str, keywords: list[str]) -> None:
        valid_keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
        for kw in valid_keywords:
            key = f"skill:{kw}"
            await self.redis.srem(key, str(user_id))
        logger.info(f"Deleted {len(valid_keywords)} keyword(s) for user: {user_id}")

    # 3. Update keywords: Remove old ones, then add new ones
    async def update_user_keywords(
        self, 
        user_id: UUID | str, 
        old_keywords: list[str], 
        new_keywords: list[str]
    ) -> None:
        await self.delete_user_keywords(user_id, old_keywords)
        await self.save_user_keywords(user_id, new_keywords)
        logger.info(f"Updated keywords for user: {user_id}")

    # 4. Find all users matching a scraped job's skills
    async def get_users_by_keywords(self, keywords: list[str]) -> set[str]:
        keys = [f"skill:{kw.strip().lower()}" for kw in keywords if kw.strip()]
        if not keys:
            return set()
        matched_users = await self.redis.sunion(*keys)
        logger.debug(f"Matched {len(matched_users)} user(s) for skills: {keywords}")
        return matched_users

    # 5. On server restart: Clear Redis and reload all users from the database
    async def rebuild_cache_from_db(self, db: Session) -> None:
        logger.info("Rebuilding Redis keyword index from database...")
        await self.redis.flushdb()  # Wipes any old/stale keys
        filters = db.scalars(select(Filter)).all()
        for f in filters:
            await self.save_user_keywords(f.user_id, f.skills)
        logger.info(f"Redis cache rebuild complete: Indexed {len(filters)} filter(s).")

import json
from dataclasses import asdict
from redis.asyncio import Redis

from app.core.redis import redis_client
from app.service.matching_service import MatchResult

QUEUE_KEY = "queue:telegram"


class AlertQueue:
    def __init__(self, redis: Redis | None = None):
        self.redis = redis or redis_client

    async def push_alert(self, match: MatchResult) -> int:
        """Pushes a single MatchResult into the Redis alert queue."""
        data = asdict(match)
        data["user_id"] = str(data["user_id"])
        data["job_id"] = str(data["job_id"])
        payload = json.dumps(data)
        return await self.redis.rpush(QUEUE_KEY, payload)

    async def push_alerts(self, matches: list[MatchResult]) -> int:
        """Pushes multiple MatchResults in a single Redis call."""
        if not matches:
            return 0
        payloads = []
        for match in matches:
            data = asdict(match)
            data["user_id"] = str(data["user_id"])
            data["job_id"] = str(data["job_id"])
            payloads.append(json.dumps(data))
        return await self.redis.rpush(QUEUE_KEY, *payloads)

    async def pop_alert(self, timeout: int = 0) -> dict | None:
        """
        Pops the next alert from the Redis queue.
        If timeout > 0, blocks up to timeout seconds (blpop).
        If timeout == 0, pops immediately (lpop).
        """
        if timeout > 0:
            result = await self.redis.blpop(QUEUE_KEY, timeout=timeout)
            if not result:
                return None
            _, payload = result
        else:
            payload = await self.redis.lpop(QUEUE_KEY)
            if not payload:
                return None

        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        return json.loads(payload)

    async def get_queue_length(self) -> int:
        """Returns the number of pending alerts in the queue."""
        return await self.redis.llen(QUEUE_KEY)


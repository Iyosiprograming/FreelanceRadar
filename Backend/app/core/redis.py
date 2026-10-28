from redis.asyncio import Redis, ConnectionPool
from typing import AsyncGenerator
from app.core.config import settings

# 1. Reusable connection pool with timeouts and auto-decoding
pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20,
    socket_connect_timeout=5.0,  # 5s timeout on connecting
    socket_timeout=5.0,          # 5s timeout on operations
)

redis_client = Redis(connection_pool=pool)


# 2. FastAPI Dependency (for use with Depends(get_redis))
async def get_redis() -> AsyncGenerator[Redis, None]:
    """Provides an async Redis client instance to FastAPI routes."""
    yield redis_client
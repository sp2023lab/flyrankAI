from __future__ import annotations

from uuid import UUID
import hashlib
from redis.asyncio import Redis
from app.rate_limit.base import RateLimitDecision

_LUA = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


class RedisRateLimiter:
    def __init__(self, redis: Redis, *, ip_limit: int, widget_limit: int, window_seconds: int = 60):
        self.redis = redis
        self.ip_limit = ip_limit
        self.widget_limit = widget_limit
        self.window_seconds = window_seconds

    async def _increment(self, key: str) -> tuple[int, int]:
        current, ttl = await self.redis.eval(_LUA, 1, key, self.window_seconds)
        return int(current), max(int(ttl), 1)

    async def check(self, widget_id: UUID, ip_address: str) -> RateLimitDecision:
        ip_token = hashlib.sha256(ip_address.encode("utf-8")).hexdigest()
        ip_key = f"rate:submission:widget:{widget_id}:ip:{ip_token}"
        widget_key = f"rate:submission:widget:{widget_id}:total"
        ip_count, ip_ttl = await self._increment(ip_key)
        widget_count, widget_ttl = await self._increment(widget_key)
        if ip_count > self.ip_limit or widget_count > self.widget_limit:
            return RateLimitDecision(False, max(ip_ttl, widget_ttl))
        return RateLimitDecision(True, 0)

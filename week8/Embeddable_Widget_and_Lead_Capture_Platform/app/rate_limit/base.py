from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(slots=True)
class RateLimitDecision:
    allowed: bool
    retry_after: int = 0


class RateLimiter(Protocol):
    async def check(self, widget_id: UUID, ip_address: str) -> RateLimitDecision: ...

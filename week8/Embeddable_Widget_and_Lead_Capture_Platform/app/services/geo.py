from __future__ import annotations

import logging
from typing import Protocol
from app.domain.types import GeoLocation

log = logging.getLogger(__name__)


class GeoProvider(Protocol):
    name: str
    async def locate(self, ip_address: str) -> GeoLocation | None: ...


class GeoEnrichmentService:
    def __init__(self, providers: list[GeoProvider]):
        self.providers = providers

    async def enrich(self, ip_address: str) -> GeoLocation | None:
        for provider in self.providers:
            try:
                result = await provider.locate(ip_address)
                if result:
                    result.provider = provider.name
                    return result
            except Exception as exc:  # adapter boundary: degradation is intentional
                log.warning("geo_provider_failed provider=%s error=%s", provider.name, type(exc).__name__)
        return None

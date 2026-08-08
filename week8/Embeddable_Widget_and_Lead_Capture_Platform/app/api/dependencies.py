from __future__ import annotations

import httpx
from fastapi import Header, HTTPException
from redis.asyncio import Redis
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_api_key
from app.db.models import Tenant
from app.db.session import SessionFactory
from app.integrations.geo_providers import IpApiCoProvider, IpApiProvider
from app.rate_limit.redis_limiter import RedisRateLimiter
from app.repositories.submission_store import SqlAlchemySubmissionStore
from app.services.geo import GeoEnrichmentService
from app.services.submissions import SubmissionService

settings = get_settings()
_redis = Redis.from_url(settings.redis_url, decode_responses=True)


def get_submission_store():
    return SqlAlchemySubmissionStore(SessionFactory)


def get_rate_limiter():
    return RedisRateLimiter(
        _redis,
        ip_limit=settings.rate_limit_ip_per_minute,
        widget_limit=settings.rate_limit_widget_per_minute,
    )


def get_geo_service():
    client = httpx.AsyncClient(timeout=settings.geo_request_timeout_seconds)
    providers = []
    if settings.geo_provider_a_enabled: providers.append(IpApiProvider(client))
    if settings.geo_provider_b_enabled: providers.append(IpApiCoProvider(client))
    return GeoEnrichmentService(providers)


def get_submission_service():
    return SubmissionService(
        store=get_submission_store(), rate_limiter=get_rate_limiter(),
        geo_service=get_geo_service(), ip_hash_salt=settings.ip_hash_salt,
    )


async def require_tenant_id(x_api_key: str = Header(..., alias="X-API-Key")):
    key_hash = hash_api_key(x_api_key)
    async with SessionFactory() as session:
        tenant_id = await session.scalar(select(Tenant.id).where(Tenant.api_key_hash == key_hash))
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return tenant_id

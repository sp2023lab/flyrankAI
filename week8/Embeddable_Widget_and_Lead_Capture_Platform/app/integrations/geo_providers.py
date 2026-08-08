from __future__ import annotations

import httpx
from app.domain.types import GeoLocation


class IpApiProvider:
    name = "ip-api"
    def __init__(self, client: httpx.AsyncClient): self.client = client

    async def locate(self, ip_address: str) -> GeoLocation | None:
        r = await self.client.get(
            f"http://ip-api.com/json/{ip_address}",
            params={"fields": "status,message,country,countryCode,city"},
        )
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "success": return None
        return GeoLocation(country_code=data.get("countryCode"), country=data.get("country"), city=data.get("city"))


class IpApiCoProvider:
    name = "ipapi.co"
    def __init__(self, client: httpx.AsyncClient): self.client = client

    async def locate(self, ip_address: str) -> GeoLocation | None:
        r = await self.client.get(f"https://ipapi.co/{ip_address}/json/")
        r.raise_for_status()
        data = r.json()
        if data.get("error"): return None
        return GeoLocation(country_code=data.get("country_code"), country=data.get("country_name"), city=data.get("city"))

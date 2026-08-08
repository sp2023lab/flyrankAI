import pytest
from app.domain.types import GeoLocation
from app.services.geo import GeoEnrichmentService

class Provider:
    def __init__(self, name, result=None, error=None): self.name=name; self.result=result; self.error=error; self.calls=0
    async def locate(self, ip):
        self.calls += 1
        if self.error: raise self.error
        return self.result

@pytest.mark.asyncio
async def test_falls_back_to_second_provider():
    a=Provider("a", error=TimeoutError())
    b=Provider("b", result=GeoLocation(country_code="GB", country="United Kingdom", city="Reading"))
    result=await GeoEnrichmentService([a,b]).enrich("8.8.8.8")
    assert result.provider == "b" and result.country_code == "GB"
    assert a.calls == b.calls == 1

@pytest.mark.asyncio
async def test_all_providers_down_degrades_to_none():
    result=await GeoEnrichmentService([Provider("a", error=TimeoutError()), Provider("b", error=RuntimeError())]).enrich("8.8.8.8")
    assert result is None

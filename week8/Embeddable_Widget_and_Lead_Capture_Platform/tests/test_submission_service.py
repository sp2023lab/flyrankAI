from uuid import uuid4
import pytest
from app.core.errors import OriginDenied, RateLimitExceeded
from app.domain.types import GeoLocation, PublicWidget, StoredSubmission
from app.rate_limit.base import RateLimitDecision
from app.services.geo import GeoEnrichmentService
from app.services.submissions import SubmissionService

class FakeStore:
    def __init__(self): self.existing=None; self.saved=[]
    async def get_existing(self, widget_id, key): return self.existing
    async def store_submission_and_job(self, **kwargs):
        row=StoredSubmission(id=uuid4(), widget_id=kwargs['widget'].id, tenant_id=kwargs['widget'].tenant_id,
            idempotency_key=kwargs['idempotency_key'], payload=kwargs['payload'],
            country_code=kwargs['geo'].country_code if kwargs['geo'] else None)
        self.saved.append(kwargs); return row, False

class Limiter:
    def __init__(self, allowed=True): self.allowed=allowed; self.calls=0
    async def check(self, widget_id, ip): self.calls+=1; return RateLimitDecision(self.allowed, 17)

class Geo:
    name="geo"
    async def locate(self, ip): return GeoLocation(country_code="GB", country="United Kingdom", city="Reading")

@pytest.fixture
def widget():
    return PublicWidget(id=uuid4(), public_id=uuid4(), tenant_id=uuid4(), widget_type="contact_form",
        title="Contact", description=None, button_text="Send",
        fields=[{"name":"email","type":"email","required":True,"max_length":254}], display_options={},
        allowed_origins=["http://localhost:5500"])

@pytest.mark.asyncio
async def test_valid_submission_is_enriched_and_stored(widget):
    store=FakeStore(); limiter=Limiter()
    service=SubmissionService(store=store, rate_limiter=limiter, geo_service=GeoEnrichmentService([Geo()]), ip_hash_salt="salt")
    result=await service.submit(widget=widget, origin="http://localhost:5500", client_ip="8.8.8.8", user_agent="test",
        idempotency_key=uuid4(), submitted_fields={"email":"a@example.com"})
    assert result.status == "stored" and result.submission.country_code == "GB"
    assert len(store.saved) == 1

@pytest.mark.asyncio
async def test_honeypot_is_not_stored_or_enriched(widget):
    store=FakeStore(); limiter=Limiter()
    service=SubmissionService(store=store, rate_limiter=limiter, geo_service=GeoEnrichmentService([Geo()]), ip_hash_salt="salt")
    result=await service.submit(widget=widget, origin="http://localhost:5500", client_ip="8.8.8.8", user_agent=None,
        idempotency_key=uuid4(), submitted_fields={"email":"bot@example.com"}, honeypot="spam.example")
    assert result.status == "accepted_spam_drop" and store.saved == []

@pytest.mark.asyncio
async def test_disallowed_origin_is_rejected(widget):
    service=SubmissionService(store=FakeStore(), rate_limiter=Limiter(), geo_service=GeoEnrichmentService([Geo()]), ip_hash_salt="salt")
    with pytest.raises(OriginDenied):
        await service.submit(widget=widget, origin="https://evil.example", client_ip="8.8.8.8", user_agent=None,
            idempotency_key=uuid4(), submitted_fields={"email":"a@example.com"})

@pytest.mark.asyncio
async def test_rate_limit_rejected(widget):
    service=SubmissionService(store=FakeStore(), rate_limiter=Limiter(False), geo_service=GeoEnrichmentService([Geo()]), ip_hash_salt="salt")
    with pytest.raises(RateLimitExceeded) as exc:
        await service.submit(widget=widget, origin="http://localhost:5500", client_ip="8.8.8.8", user_agent=None,
            idempotency_key=uuid4(), submitted_fields={"email":"a@example.com"})
    assert exc.value.retry_after == 17

@pytest.mark.asyncio
async def test_idempotent_retry_does_not_store_again(widget):
    store=FakeStore(); key=uuid4()
    store.existing=StoredSubmission(id=uuid4(), widget_id=widget.id, tenant_id=widget.tenant_id, idempotency_key=key, payload={"email":"a@example.com"})
    limiter=Limiter()
    service=SubmissionService(store=store, rate_limiter=limiter, geo_service=GeoEnrichmentService([Geo()]), ip_hash_salt="salt")
    result=await service.submit(widget=widget, origin="http://localhost:5500", client_ip="8.8.8.8", user_agent=None,
        idempotency_key=key, submitted_fields={"email":"a@example.com"})
    assert result.duplicate is True and store.saved == [] and limiter.calls == 0

class DownGeo:
    name = "down"
    async def locate(self, ip):
        raise TimeoutError()

@pytest.mark.asyncio
async def test_all_geo_providers_down_still_stores(widget):
    store=FakeStore(); limiter=Limiter()
    service=SubmissionService(store=store, rate_limiter=limiter, geo_service=GeoEnrichmentService([DownGeo()]), ip_hash_salt="salt")
    result=await service.submit(widget=widget, origin="http://localhost:5500", client_ip="8.8.8.8", user_agent=None,
        idempotency_key=uuid4(), submitted_fields={"email":"a@example.com"})
    assert result.status == "stored"
    assert result.submission.country_code is None
    assert len(store.saved) == 1

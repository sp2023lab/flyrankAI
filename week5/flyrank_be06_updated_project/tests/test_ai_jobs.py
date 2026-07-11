from unittest.mock import AsyncMock, patch

import pytest
from celery.exceptions import Retry

from app.ai.base import AICompletion, AIProviderError
from app.database import SessionLocal
from app.models import AIJob
from app.tasks import generate_ai_summary

TEXT = "Revenue rose 18 percent. Refunds fell 7 percent. Mobile is 61 percent of sales."
RESULT_JSON = '{"bullets":["Revenue rose 18 percent.","Refunds fell 7 percent.","Mobile is 61 percent of sales."]}'


class SuccessfulProvider:
    def __init__(self) -> None:
        self.complete = AsyncMock(
            return_value=AICompletion(
                content=RESULT_JSON,
                input_tokens=20,
                output_tokens=30,
                model="test-model",
            )
        )


class RetryableProvider:
    def __init__(self) -> None:
        self.complete = AsyncMock(
            side_effect=AIProviderError("temporary outage", retryable=True)
        )


def enqueue(client, key: str = "request-123"):
    with patch("app.routers.summarize.generate_ai_summary.delay") as delay:
        response = client.post(
            "/api/v1/summarize",
            json={"text": TEXT},
            headers={"Idempotency-Key": key},
        )
    return response, delay


def test_submit_returns_202_and_status_url_without_running_ai(client):
    response, delay = enqueue(client)
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "queued"
    assert body["attempts"] == 0
    assert body["result"] is None
    assert response.headers["location"].endswith(f"/api/v1/ai-jobs/{body['id']}")
    delay.assert_called_once_with(body["id"])


def test_idempotency_key_reuses_original_job_and_enqueues_once(client):
    with patch("app.routers.summarize.generate_ai_summary.delay") as delay:
        first = client.post(
            "/api/v1/summarize",
            json={"text": TEXT},
            headers={"Idempotency-Key": "duplicate-123"},
        )
        second = client.post(
            "/api/v1/summarize",
            json={"text": "Different text must not create another job."},
            headers={"Idempotency-Key": "duplicate-123"},
        )
    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["id"] == second.json()["id"]
    delay.assert_called_once()


def test_worker_completes_job_and_status_returns_result(client):
    response, _ = enqueue(client, "complete-123")
    job_id = response.json()["id"]
    provider = SuccessfulProvider()
    with patch("app.tasks.get_ai_provider", return_value=provider):
        result = generate_ai_summary.run(job_id)
    assert result["bullets"][0] == "Revenue rose 18 percent."
    status_response = client.get(f"/api/v1/ai-jobs/{job_id}")
    assert status_response.status_code == 200
    body = status_response.json()
    assert body["status"] == "completed"
    assert body["attempts"] == 1
    assert body["result"]["bullets"][2] == "Mobile is 61 percent of sales."


def test_completed_job_is_idempotent_when_delivered_twice(client):
    response, _ = enqueue(client, "worker-duplicate")
    job_id = response.json()["id"]
    provider = SuccessfulProvider()
    with patch("app.tasks.get_ai_provider", return_value=provider):
        first = generate_ai_summary.run(job_id)
        second = generate_ai_summary.run(job_id)
    assert first == second
    assert provider.complete.await_count == 1


def test_retryable_failure_sets_retrying_state(client):
    response, _ = enqueue(client, "retry-123")
    job_id = response.json()["id"]
    with (
        patch("app.tasks.get_ai_provider", return_value=RetryableProvider()),
        patch.object(generate_ai_summary, "retry", side_effect=Retry("scheduled")),
        pytest.raises(Retry),
    ):
        generate_ai_summary.run(job_id)
    body = client.get(f"/api/v1/ai-jobs/{job_id}").json()
    assert body["status"] == "retrying"
    assert body["attempts"] == 1
    assert "temporary outage" in body["error"]


def test_exhausted_job_fails_and_alerts(client):
    response, _ = enqueue(client, "failed-123")
    job_id = response.json()["id"]
    with SessionLocal() as db:
        job = db.get(AIJob, job_id)
        assert job is not None
        job.max_attempts = 1
        db.commit()
    with (
        patch("app.tasks.get_ai_provider", return_value=RetryableProvider()),
        patch("app.tasks.alert_permanent_ai_failure") as alert,
        pytest.raises(AIProviderError),
    ):
        generate_ai_summary.run(job_id)
    body = client.get(f"/api/v1/ai-jobs/{job_id}").json()
    assert body["status"] == "failed"
    assert body["attempts"] == 1
    alert.assert_called_once()


def test_unknown_ai_job_returns_404(client):
    response = client.get("/api/v1/ai-jobs/not-a-real-job")
    assert response.status_code == 404

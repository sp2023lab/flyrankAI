from unittest.mock import patch

from app.tasks import generate_sales_report


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_complete_report_pipeline(client):
    seed_response = client.post("/api/v1/demo/orders/seed", json={"count": 24})
    assert seed_response.status_code == 200
    assert seed_response.json()["inserted"] == 24

    with patch("app.routers.reports.generate_sales_report.delay"):
        create_response = client.post(
            "/api/v1/reports",
            json={"report_type": "sales_summary", "title": "FlyRank Test Report"},
        )
    assert create_response.status_code == 202
    job = create_response.json()
    assert job["status"] == "queued"

    report_id = generate_sales_report.run(job["id"])
    assert report_id

    job_response = client.get(f"/api/v1/jobs/{job['id']}")
    assert job_response.status_code == 200
    completed_job = job_response.json()
    assert completed_job["status"] == "completed"
    assert completed_job["report_id"] == report_id
    assert completed_job["download_url"].endswith(f"/api/v1/reports/{report_id}/download")

    download_response = client.get(f"/api/v1/reports/{report_id}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
    assert download_response.content.startswith(b"%PDF")
    assert len(download_response.content) > 1000


def test_missing_job_returns_404(client):
    response = client.get("/api/v1/jobs/not-a-real-job")
    assert response.status_code == 404

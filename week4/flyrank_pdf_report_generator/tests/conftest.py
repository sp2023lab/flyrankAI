import os
from pathlib import Path

TEST_DB = Path("test_report_generator.db")
TEST_ARTIFACTS = Path("test_artifacts")

os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB}"
os.environ["ARTIFACTS_DIR"] = str(TEST_ARTIFACTS)
os.environ["CELERY_BROKER_URL"] = "memory://"
os.environ["CELERY_RESULT_BACKEND"] = "cache+memory://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    TEST_ARTIFACTS.mkdir(exist_ok=True)
    for pdf in TEST_ARTIFACTS.glob("*.pdf"):
        pdf.unlink()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

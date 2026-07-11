from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ReportArtifact


class ReportRepository:
    @staticmethod
    def add(db: Session, report: ReportArtifact) -> ReportArtifact:
        db.add(report)
        db.flush()
        return report

    @staticmethod
    def get(db: Session, report_id: str) -> ReportArtifact | None:
        return db.get(ReportArtifact, report_id)

    @staticmethod
    def list_recent(db: Session, limit: int = 50) -> list[ReportArtifact]:
        statement = (
            select(ReportArtifact).order_by(ReportArtifact.created_at.desc()).limit(limit)
        )
        return list(db.scalars(statement))

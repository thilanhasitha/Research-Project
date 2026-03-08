from typing import Iterable

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.report import SecurityReport


class ReportRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_many(self, security_id: int, kind: str, items: Iterable[dict]) -> list[SecurityReport]:
        saved: list[SecurityReport] = []
        for item in items:
            path = item.get("path")
            if not path:
                continue
            existing = self.session.scalar(
                select(SecurityReport).where(
                    and_(SecurityReport.security_id == security_id, SecurityReport.kind == kind, SecurityReport.path == path)
                )
            )
            if existing:
                existing.file_text = item.get("fileText")
                existing.manual_date = _ts_to_dt(item.get("manualDate"))
                existing.uploaded_date = _ts_to_dt(item.get("uploadedDate"))
                existing.authorized_date = _ts_to_dt(item.get("authorizedDate"))
                saved.append(existing)
                continue

            report = SecurityReport(
                security_id=security_id,
                kind=kind,
                path=path,
                file_text=item.get("fileText"),
                manual_date=_ts_to_dt(item.get("manualDate")),
                uploaded_date=_ts_to_dt(item.get("uploadedDate")),
                authorized_date=_ts_to_dt(item.get("authorizedDate")),
            )
            self.session.add(report)
            saved.append(report)
        return saved


def _ts_to_dt(value):
    if not value:
        return None
    try:
        # API returns ms epoch
        from datetime import datetime, timezone

        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).replace(tzinfo=None)
    except Exception:
        return None

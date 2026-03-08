from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SecurityReport(Base):
    __tablename__ = "security_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    security_id: Mapped[int] = mapped_column(ForeignKey("securities.id", ondelete="CASCADE"), index=True)

    # "annual" or "quarterly"
    kind: Mapped[str] = mapped_column(String(16), index=True)

    # Path from API (e.g., "cmt/upload_report_file/389_1747616410421.pdf")
    path: Mapped[str] = mapped_column(String(512))
    file_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    manual_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    uploaded_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    authorized_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    security: Mapped["Security"] = relationship(back_populates="reports")

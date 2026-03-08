from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import Date, DateTime, Float, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Security(Base):
    __tablename__ = "securities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity_issued: Mapped[int | None] = mapped_column(Integer, nullable=True)
    established_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    business_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sector: Mapped[str | None] = mapped_column(String(255), nullable=True)
    board_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    market_cap: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    market_cap_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    previous_close: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    previous_close_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closing_price: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    closing_price_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    reports: Mapped[list["SecurityReport"]] = relationship(
        back_populates="security",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

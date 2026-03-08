from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyListItem(BaseModel):
    """Simple company info from CSE API (not from database)."""
    id: int
    symbol: str
    name: str


class ReportRead(BaseModel):
    kind: str
    url: str | None = None
    path: str | None = None
    file_text: str | None = None
    manual_date: datetime | None = None
    uploaded_date: datetime | None = None
    authorized_date: datetime | None = None


class SecurityBase(BaseModel):
    symbol: str
    name: str
    logo_url: str | None = None
    issue_date: date | None = None
    quantity_issued: int | None = None
    established_year: int | None = None
    business_summary: str | None = None
    sector: str | None = None
    board_type: str | None = None
    market_cap: float | None = None
    market_cap_percentage: float | None = None
    previous_close: float | None = None
    previous_close_updated_at: datetime | None = None
    closing_price: float | None = None
    closing_price_updated_at: datetime | None = None


class SecurityCreate(SecurityBase):
    pass


class SecurityRead(SecurityBase):
    id: int
    annual_reports: list[ReportRead] = Field(default_factory=list)
    quarterly_reports: list[ReportRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

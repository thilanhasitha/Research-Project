from typing import List

from datetime import datetime
from sqlalchemy.orm import Session

from app.clients.cse_client import CSEClient
from app.repositories.report_repository import ReportRepository
from app.repositories.security_repository import SecurityRepository
from app.schemas.security import ReportRead, SecurityCreate, SecurityRead


CDN_LOGO_BASE = "https://cdn.cse.lk/cmt/"
CDN_REPORT_BASE = "https://cdn.cse.lk/"


class CSEService:
    def __init__(self, session: Session, client: CSEClient):
        self.session = session
        self.client = client
        self.repo = SecurityRepository(session)
        self.report_repo = ReportRepository(session)

    async def fetch_available_companies(self) -> list[dict]:
        """Fetch list of available companies from CSE without storing in database."""
        raw_items = await self.client.fetch_all_securities()
        return [{"id": item.get("id"), "symbol": item.get("symbol"), "name": item.get("name")} for item in raw_items]

    async def sync_basic_list(self) -> list[SecurityRead]:
        raw_items = await self.client.fetch_all_securities()
        if not raw_items:
            return []

        saved: List[SecurityRead] = []
        for item in raw_items:
            symbol = item.get("symbol")
            name = item.get("name")
            if not symbol or not name:
                continue
            payload = SecurityCreate(symbol=symbol.strip(), name=name.strip())
            entity = self.repo.upsert(payload)
            saved.append(SecurityRead.model_validate(entity))

        self.session.commit()
        return saved

    async def sync_details_for_symbol(self, symbol: str) -> SecurityRead | None:
        # ensure basic exists
        base = SecurityCreate(symbol=symbol, name=symbol)
        entity = self.repo.upsert(base)

        info = await self.client.fetch_company_info_summery(symbol)
        profile = await self.client.fetch_company_profile(symbol)
        financials = await self.client.fetch_financials(symbol)

        # Extract info from companyInfoSummery
        logo_path = (info.get("reqLogo") or {}).get("path")
        logo_url = f"{CDN_LOGO_BASE}{logo_path}" if logo_path else None

        req_symbol = info.get("reqSymbolInfo") or {}
        issue_date_str = (req_symbol.get("issueDate") or "").strip() or None
        quantity_issued = req_symbol.get("quantityIssued")
        previous_close = req_symbol.get("previousClose")
        closing_price = req_symbol.get("closingPrice")
        market_cap = req_symbol.get("marketCap")
        market_cap_pct = req_symbol.get("marketCapPercentage")
        name = req_symbol.get("name") or entity.name

        # Extract profile details
        com_sum = None
        if isinstance(profile.get("reqComSumInfo"), list) and profile["reqComSumInfo"]:
            com_sum = profile["reqComSumInfo"][0]

        established = (com_sum or {}).get("established")
        established_year = None
        if established:
            try:
                established_year = int(str(established).strip())
            except Exception:
                established_year = None

        sector = (com_sum or {}).get("sector")
        board_type = (com_sum or {}).get("boardType")

        # Business summary location (best-effort)
        business_summary = None
        if isinstance(profile.get("infoCompanyBusinessSummary"), list) and profile["infoCompanyBusinessSummary"]:
            first = profile["infoCompanyBusinessSummary"][0]
            business_summary = first.get("body") or first.get("summary")

        # Parse dates
        issue_date = _parse_issue_date(issue_date_str)
        now = datetime.utcnow()

        payload = SecurityCreate(
            symbol=symbol,
            name=name,
            logo_url=logo_url,
            issue_date=issue_date,
            quantity_issued=quantity_issued,
            established_year=established_year,
            business_summary=business_summary,
            sector=sector,
            board_type=board_type,
            market_cap=float(market_cap) if market_cap is not None else None,
            market_cap_percentage=float(market_cap_pct) if market_cap_pct is not None else None,
            previous_close=float(previous_close) if previous_close is not None else None,
            previous_close_updated_at=now if previous_close is not None else None,
            closing_price=float(closing_price) if closing_price is not None else None,
            closing_price_updated_at=now if closing_price is not None else None,
        )

        entity = self.repo.upsert(payload)

        # Reports
        annual = financials.get("infoAnnualData") or []
        quarterly = financials.get("infoQuarterlyData") or []
        self.report_repo.upsert_many(entity.id, "annual", annual)
        self.report_repo.upsert_many(entity.id, "quarterly", quarterly)

        self.session.commit()
        return self._to_read(entity)

    async def sync_all_details(self) -> list[SecurityRead]:
        items = await self.client.fetch_all_securities()
        results: list[SecurityRead] = []
        for row in items:
            symbol = row.get("symbol")
            name = row.get("name") or symbol
            if not symbol:
                continue
            # ensure base record first
            base = SecurityCreate(symbol=symbol, name=name)
            self.repo.upsert(base)
            # then fill details
            read = await self.sync_details_for_symbol(symbol)
            if read:
                results.append(read)
        return results

    def list_cached(self) -> list[SecurityRead]:
        items = self.repo.list_all()
        return [self._to_read(obj) for obj in items]

    def get_by_symbol(self, symbol: str) -> SecurityRead | None:
        """Get a single security with full details from database by symbol."""
        from sqlalchemy import select
        from app.models.security import Security
        
        entity = self.session.scalar(select(Security).where(Security.symbol == symbol))
        if not entity:
            return None
        return self._to_read(entity)

    def _to_read(self, entity) -> SecurityRead:
        # Transform reports into two lists with full URLs
        annual: list[ReportRead] = []
        quarterly: list[ReportRead] = []
        for r in getattr(entity, "reports", []) or []:
            url = f"{CDN_REPORT_BASE}{r.path}" if r.path else None
            data = ReportRead(
                kind=r.kind,
                url=url,
                path=r.path,
                file_text=r.file_text,
                manual_date=r.manual_date,
                uploaded_date=r.uploaded_date,
                authorized_date=r.authorized_date,
            )
            (annual if r.kind == "annual" else quarterly).append(data)

        obj = SecurityRead.model_validate(entity)
        obj.annual_reports = annual
        obj.quarterly_reports = quarterly
        return obj


def _parse_issue_date(value: str | None):
    if not value:
        return None
    # Examples: "07/JAN/2026"
    s = value.strip()
    try:
        from datetime import datetime

        return datetime.strptime(s, "%d/%b/%Y").date()
    except Exception:
        pass
    try:
        from datetime import datetime

        return datetime.strptime(s, "%d/%B/%Y").date()
    except Exception:
        pass
    try:
        # Manual map for uppercase months
        day, mon, year = s.split("/")
        months = {
            "JAN": 1,
            "FEB": 2,
            "MAR": 3,
            "APR": 4,
            "MAY": 5,
            "JUN": 6,
            "JUL": 7,
            "AUG": 8,
            "SEP": 9,
            "SEPT": 9,
            "OCT": 10,
            "NOV": 11,
            "DEC": 12,
        }
        m = months.get(mon.upper())
        if not m:
            return None
        return datetime(int(year), m, int(day)).date()
    except Exception:
        return None

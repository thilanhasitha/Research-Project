from typing import Any

import httpx

from app.core.config import get_settings


class CSEClient:
    """Lightweight HTTP client for CSE endpoints."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: int | None = None):
        settings = get_settings()
        self.base_url = base_url or settings.cse_base_url
        self.api_key = api_key or settings.cse_api_key
        self.timeout = timeout or settings.http_timeout_seconds

    def _headers(self) -> dict[str, str]:
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        return headers

    async def fetch_all_securities(self) -> list[dict[str, Any]]:
        """GET list of {id, name, symbol} from /api/allSecurityCode."""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            resp = await client.get("/api/allSecurityCode", headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else []

    async def fetch_company_info_summery(self, symbol: str) -> dict[str, Any]:
        """POST form-data to /api/companyInfoSummery with {symbol}."""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            resp = await client.post("/api/companyInfoSummery", headers=self._headers(), data={"symbol": symbol})
            resp.raise_for_status()
            return resp.json() or {}

    async def fetch_financials(self, symbol: str) -> dict[str, Any]:
        """POST form-data to /api/financials with {symbol}."""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            resp = await client.post("/api/financials", headers=self._headers(), data={"symbol": symbol})
            resp.raise_for_status()
            return resp.json() or {}

    async def fetch_company_profile(self, symbol: str) -> dict[str, Any]:
        """POST form-data to /api/companyProfile with {symbol}."""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            resp = await client.post("/api/companyProfile", headers=self._headers(), data={"symbol": symbol})
            resp.raise_for_status()
            return resp.json() or {}

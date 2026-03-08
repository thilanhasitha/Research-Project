from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_cse_service
from app.schemas.security import CompanyListItem, SecurityRead
from app.services.cse_service import CSEService

router = APIRouter(prefix="/cse", tags=["cse"])


@router.get("/available", response_model=list[CompanyListItem], summary="List available companies from CSE (no database storage)")
async def get_available_companies(service: CSEService = Depends(get_cse_service)) -> list[CompanyListItem]:
    """Fetch the list of available companies from CSE API without storing in database.
    User can choose from this list and then sync specific company."""
    return await service.fetch_available_companies()


@router.post("/sync-basic", response_model=list[SecurityRead], summary="Pull security codes and names from CSE and store")
async def sync_basic(service: CSEService = Depends(get_cse_service)) -> list[SecurityRead]:
    return await service.sync_basic_list()


@router.post("/sync-details", response_model=list[SecurityRead], summary="Pull details for all securities (slow)")
async def sync_all_details(service: CSEService = Depends(get_cse_service)) -> list[SecurityRead]:
    return await service.sync_all_details()


@router.post("/sync-symbol", response_model=SecurityRead | None, summary="Sync a single symbol with details")
async def sync_symbol(symbol: str = Query(..., description="Symbol like DIAL.N0000"), service: CSEService = Depends(get_cse_service)):
    return await service.sync_details_for_symbol(symbol)


@router.get("/securities", response_model=list[SecurityRead], summary="List cached securities")
def list_securities(service: CSEService = Depends(get_cse_service)) -> list[SecurityRead]:
    return service.list_cached()


@router.get("/securities/{symbol}", response_model=SecurityRead, summary="Get full details of a security from database")
def get_security_details(
    symbol: str,
    service: CSEService = Depends(get_cse_service)
) -> SecurityRead:
    """Retrieve full details including reports for a specific security from database.
    If not found, returns 404. Use POST /sync-symbol first to fetch and store data."""
    result = service.get_by_symbol(symbol)
    if not result:
        raise HTTPException(status_code=404, detail=f"Security {symbol} not found in database")
    return result

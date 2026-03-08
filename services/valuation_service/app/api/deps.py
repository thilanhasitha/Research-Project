from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.cse_client import CSEClient
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.services.cse_service import CSEService


def get_settings_dep() -> Settings:
    return get_settings()


def get_cse_client(settings: Settings = Depends(get_settings_dep)) -> CSEClient:
    return CSEClient(
        base_url=settings.cse_base_url,
        api_key=settings.cse_api_key,
        timeout=settings.http_timeout_seconds,
    )


def get_cse_service(
    db: Session = Depends(get_db_session),
    client: CSEClient = Depends(get_cse_client),
) -> CSEService:
    return CSEService(session=db, client=client)

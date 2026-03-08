from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_application()

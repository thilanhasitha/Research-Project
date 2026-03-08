"""Helper to create tables during early development.
Use migrations (e.g., Alembic) for production deployments."""

from app.db.base import Base
from app.db.session import engine
from app.models import security  # noqa: F401 - ensure models are imported
from app.models import report  # noqa: F401 - ensure models are imported


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security import Security
from app.schemas.security import SecurityCreate


class SecurityRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert(self, payload: SecurityCreate) -> Security:
        existing = self.session.scalar(select(Security).where(Security.symbol == payload.symbol))
        if existing:
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(existing, field, value)
            self.session.flush()
            return existing

        instance = Security(**payload.model_dump())
        self.session.add(instance)
        self.session.flush() 
        return instance

    def list_all(self) -> list[Security]:
        return list(self.session.scalars(select(Security)))

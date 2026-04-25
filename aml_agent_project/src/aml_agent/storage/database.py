"""Инициализация SQLite и CRUD-функции suspicious DB + audit log."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from aml_agent.storage.models import AuditLog, Base, SuspiciousCounterparty


def make_session_factory(db_url: str = "sqlite:///aml_agent.db") -> sessionmaker:
    """Создает фабрику SQLAlchemy-сессий и таблицы."""

    engine = create_engine(db_url, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


def lookup_suspicious(session: Session, counterparty: str) -> SuspiciousCounterparty | None:
    """Возвращает контрагента из suspicious DB по точному имени."""

    stmt = select(SuspiciousCounterparty).where(SuspiciousCounterparty.counterparty == counterparty)
    return session.execute(stmt).scalar_one_or_none()


def search_suspicious(session: Session, query: str) -> list[SuspiciousCounterparty]:
    """Ищет контрагентов по подстроке."""

    stmt = select(SuspiciousCounterparty).where(SuspiciousCounterparty.counterparty.ilike(f"%{query}%"))
    return list(session.execute(stmt).scalars())


def upsert_suspicious(session: Session, counterparty: str, risk_level: str, reason: str) -> SuspiciousCounterparty:
    """Upsert записи в suspicious_counterparties."""

    row = lookup_suspicious(session, counterparty)
    if row is None:
        row = SuspiciousCounterparty(
            counterparty=counterparty,
            risk_level=risk_level,
            reason=reason,
            updated_at=datetime.utcnow(),
        )
        session.add(row)
    else:
        row.risk_level = risk_level
        row.reason = reason
        row.updated_at = datetime.utcnow()
    session.commit()
    return row


def write_audit_rows(session: Session, rows: list[dict]) -> None:
    """Пакетная запись аудита."""

    for r in rows:
        session.add(AuditLog(**r))
    session.commit()

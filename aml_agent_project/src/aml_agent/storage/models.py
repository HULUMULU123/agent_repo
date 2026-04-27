"""SQLAlchemy-модели хранилища suspicious counterparties и audit log."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SuspiciousCounterparty(Base):
    """Таблица подозрительных контрагентов."""

    __tablename__ = "suspicious_counterparties"
    id = Column(Integer, primary_key=True)
    counterparty = Column(String, index=True, nullable=False, unique=True)
    risk_level = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class AuditLog(Base):
    """Таблица аудита прохождения операций через пайплайн."""

    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    operation_id = Column(String, index=True, nullable=False)
    cluster_id = Column(Integer, nullable=True)
    selected_for_llm = Column(Boolean, nullable=False)
    iso_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    propagation_confidence = Column(Float, nullable=True)
    used_tools = Column(JSON, nullable=True)

"""Pydantic-схемы для валидации итоговых решений и evidence ledger."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EvidenceModel(BaseModel):
    """Схема строки evidence ledger."""

    evidence_id: str
    operation_id: str
    source: str
    fact: str
    confidence: float = Field(ge=0, le=1)
    supports_risk: bool
    timestamp: datetime


class FinalDecisionModel(BaseModel):
    """Схема финального решения AML."""

    operation_id: str
    cluster_id: int
    risk_level: Literal["low", "medium", "high"]
    risk_score: float = Field(ge=0, le=1)
    decision: str
    reason: str
    evidence_summary: str
    used_tools: list[str]
    recommended_action: str
    can_propagate: bool
    propagation_rules: dict

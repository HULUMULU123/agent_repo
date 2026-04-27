"""Общие типы состояния и доменных объектов для пайплайна AML-агента."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, TypedDict


class Operation(TypedDict, total=False):
    """Нормализованная банковская операция."""

    operation_id: str
    client: str
    counterparty: str
    date: str
    purpose: str
    debit_amount: float
    credit_amount: float
    court_claim_date: str | None


class Evidence(TypedDict):
    """Запись evidence ledger."""

    evidence_id: str
    operation_id: str
    source: str
    fact: str
    confidence: float
    supports_risk: bool
    timestamp: str


class FinalDecision(TypedDict, total=False):
    """Решение финализатора по операции."""

    operation_id: str
    cluster_id: int
    risk_level: Literal["low", "medium", "high"]
    risk_score: float
    decision: str
    reason: str
    evidence_summary: str
    used_tools: list[str]
    recommended_action: str
    can_propagate: bool
    propagation_rules: dict[str, Any]


class AMLState(TypedDict, total=False):
    """Состояние LangGraph-графа на всех этапах пайплайна."""

    input_path: str
    operations: list[Operation]
    manual_review_rows: list[dict[str, Any]]
    sampled_operations: list[Operation]
    low_risk_operations: list[Operation]
    high_risk_operations: list[Operation]
    evidence_ledger: list[Evidence]
    investigator_tools_catalog: list[dict[str, str]]
    final_decisions: list[FinalDecision]
    propagated_decisions: list[FinalDecision]
    suspicious_to_write: list[dict[str, Any]]
    audit_log_rows: list[dict[str, Any]]
    processing_started_at: str
    processing_finished_at: str

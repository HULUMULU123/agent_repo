"""Нормализация операций к единой схеме AML-пайплайна."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

REQUIRED_FIELDS = [
    "operation_id",
    "client",
    "counterparty",
    "date",
    "purpose",
    "debit_amount",
    "credit_amount",
    "court_claim_date",
]


def normalize_operations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Нормализует даты и суммы, добавляет отсутствующие обязательные поля."""

    norm_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        out = {k: row.get(k) for k in REQUIRED_FIELDS}
        out["operation_id"] = str(out.get("operation_id") or f"op-{idx}")
        out["date"] = _normalize_date(out.get("date"))
        out["court_claim_date"] = _normalize_date(out.get("court_claim_date"))
        out["debit_amount"] = _to_float(out.get("debit_amount"))
        out["credit_amount"] = _to_float(out.get("credit_amount"))
        for text_key in ["client", "counterparty", "purpose"]:
            out[text_key] = str(out.get(text_key) or "").strip()
        norm_rows.append(out)
    return norm_rows


def _normalize_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    dt = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(dt):
        return None
    return dt.strftime("%Y-%m-%d")


def _to_float(value: Any) -> float:
    try:
        if value in (None, ""):
            return 0.0
        return float(str(value).replace(" ", "").replace(",", "."))
    except ValueError:
        return 0.0

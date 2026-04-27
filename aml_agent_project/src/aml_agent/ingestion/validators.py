"""Валидаторы входных и промежуточных данных операций."""

from __future__ import annotations

from typing import Any

KEY_FIELDS = ["operation_id", "date", "purpose"]


def validate_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Разделяет строки на валидные и требующие manual review."""

    valid, manual = [], []
    for row in rows:
        has_missing = any(row.get(k) in (None, "") for k in KEY_FIELDS)
        (manual if has_missing else valid).append(row)
    return valid, manual

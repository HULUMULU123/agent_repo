"""Pydantic-схемы API слоя FastAPI для AML анализа."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    """Ответ API после прохождения полного AML-пайплайна."""

    operations_total: int = Field(description="Количество валидных операций после validation")
    manual_review_rows: int = Field(description="Количество строк, ушедших в ручную проверку")
    sampled_for_llm: int = Field(description="Количество операций в representative sampling")
    suspicious_written: int = Field(description="Количество подозрительных операций, записанных в БД")
    audit_rows: int = Field(description="Количество строк audit log")
    result: dict[str, Any] = Field(description="Полный итоговый state пайплайна")

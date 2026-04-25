"""Роутер extraction-логики по типам входных файлов (csv/xlsx/pdf/image)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from aml_agent.ingestion.image_parser import parse_image
from aml_agent.ingestion.llm_parser import parse_with_llm
from aml_agent.ingestion.pdf_parser import parse_pdf


def _df_to_ops(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Унифицирует DataFrame в список операций стандартного формата."""

    return df.fillna("").to_dict(orient="records")


def extract_operations(file_path: str) -> list[dict[str, Any]]:
    """Извлекает операции из файла с fallback-стратегиями."""

    suffix = Path(file_path).suffix.lower()
    if suffix == ".csv":
        return _df_to_ops(pd.read_csv(file_path))
    if suffix in {".xlsx", ".xls"}:
        return _df_to_ops(pd.read_excel(file_path))
    if suffix == ".pdf":
        parsed = parse_pdf(file_path)
        if parsed is not None:
            return parsed
        with open(file_path, "rb") as f:
            return parse_with_llm(f.read(), "pdf")
    if suffix in {".png", ".jpg", ".jpeg"}:
        return parse_image(file_path)
    raise ValueError(f"Unsupported file type: {suffix}")

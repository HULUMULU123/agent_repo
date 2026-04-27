"""PDF-парсер с двухэтапной логикой: pdfplumber -> pymupdf, затем fallback."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import fitz
import pandas as pd
import pdfplumber


_DATE_RE = re.compile(r"\b\d{2}[./-]\d{2}[./-]\d{4}\b")
_AMOUNT_RE = re.compile(r"-?\d+[\s,]\d{2}|-?\d+\.\d{2}")


def _rows_quality(rows: list[dict], min_rows: int = 3) -> bool:
    """Проверяет качество распознанных операций: даты, суммы, количество строк."""

    if len(rows) < min_rows:
        return False
    joined = " ".join(str(v) for r in rows for v in r.values())
    return bool(_DATE_RE.search(joined) and _AMOUNT_RE.search(joined))


def _table_to_ops(df: pd.DataFrame) -> list[dict]:
    """Преобразует табличный DataFrame в список операций с общей схемой ключей."""

    df = df.fillna("")
    cols = [c.lower().strip() for c in df.columns]
    df.columns = cols
    ops = []
    for idx, row in df.iterrows():
        ops.append(
            {
                "operation_id": str(row.get("operation_id") or row.get("id") or f"pdf-{idx}"),
                "client": str(row.get("client", "")),
                "counterparty": str(row.get("counterparty", "")),
                "date": str(row.get("date", "")),
                "purpose": str(row.get("purpose", "")),
                "debit_amount": row.get("debit_amount") or row.get("debit") or 0,
                "credit_amount": row.get("credit_amount") or row.get("credit") or 0,
                "court_claim_date": row.get("court_claim_date") or None,
            }
        )
    return ops


def parse_pdf(file_path: str) -> Optional[list[dict]]:
    """Парсит PDF: сначала таблицы pdfplumber, затем сырой текст pymupdf.

    Returns None, если качество извлечения неудовлетворительное.
    """

    path = Path(file_path)

    # Этап 1: pdfplumber таблицы
    table_rows: list[dict] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if not table or len(table) < 2:
                    continue
                header, *data = table
                df = pd.DataFrame(data, columns=header)
                table_rows.extend(_table_to_ops(df))
    if _rows_quality(table_rows):
        return table_rows

    # Этап 2: pymupdf текст
    text_rows: list[dict] = []
    doc = fitz.open(path)
    for page in doc:
        text = page.get_text("text")
        for i, line in enumerate(text.splitlines()):
            if _DATE_RE.search(line) and _AMOUNT_RE.search(line):
                text_rows.append(
                    {
                        "operation_id": f"pdf-txt-{i}",
                        "client": "",
                        "counterparty": "",
                        "date": _DATE_RE.search(line).group(0) if _DATE_RE.search(line) else "",
                        "purpose": line,
                        "debit_amount": 0,
                        "credit_amount": 0,
                        "court_claim_date": None,
                    }
                )
    if _rows_quality(text_rows):
        return text_rows

    return None

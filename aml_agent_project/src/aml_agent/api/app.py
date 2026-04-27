"""FastAPI-приложение для загрузки выписок и возврата итогов AML-анализа."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from aml_agent.api.schemas import AnalyzeResponse
from aml_agent.pipeline.service import run_pipeline

ALLOWED_SUFFIXES = {".csv", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"}

app = FastAPI(title="AML Agent API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Проверка доступности API сервиса."""

    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_statement(
    file: UploadFile = File(...),
    db_url: str = Form("sqlite:///aml_agent.db"),
) -> AnalyzeResponse:
    """Принимает файл выписки, запускает полный анализ и возвращает итоговый результат."""

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = run_pipeline(input_path=tmp_path, output_path=None, db_url=db_url)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return AnalyzeResponse(
        operations_total=len(result.get("operations", [])),
        manual_review_rows=len(result.get("manual_review_rows", [])),
        sampled_for_llm=len(result.get("sampled_operations", [])),
        suspicious_written=len(result.get("suspicious_to_write", [])),
        audit_rows=len(result.get("audit_log_rows", [])),
        result=result,
    )

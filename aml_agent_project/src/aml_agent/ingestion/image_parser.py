"""Парсер изображений выписок: в MVP сразу отправляет файл в LLM-парсер."""

from __future__ import annotations

from typing import Any

from aml_agent.ingestion.llm_parser import parse_with_llm


def parse_image(file_path: str) -> list[dict[str, Any]]:
    """Читает изображение и извлекает операции через LLM (без локального OCR)."""

    with open(file_path, "rb") as f:
        return parse_with_llm(f.read(), "image")

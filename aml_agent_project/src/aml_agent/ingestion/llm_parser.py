"""LLM-парсер документов, когда классический парсинг не дал результата."""

from __future__ import annotations

import json
from typing import Any

from aml_agent.llm.gigachat_client import GigaChatClient


def parse_with_llm(file_bytes: bytes, file_type: str) -> list[dict[str, Any]]:
    """Парсит бинарное содержимое файла через GigaChat и возвращает операции."""

    client = GigaChatClient()
    response = client.parse_document(file_bytes=file_bytes, file_type=file_type)
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        return [response]
    try:
        # Fallback: если по какой-то причине вернулась строка JSON.
        parsed = json.loads(str(response))
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        return []

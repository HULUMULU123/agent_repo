"""LLM-парсер документов, когда классический парсинг не дал результата."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from aml_agent.llm.gigachat_client import get_gigachat_llm
from aml_agent.prompts.prompts import LLM_DOCUMENT_PARSER_PROMPT


def parse_with_llm(file_bytes: bytes, file_type: str) -> list[dict[str, Any]]:
    """Парсит бинарное содержимое файла через GigaChat и возвращает операции."""

    llm = get_gigachat_llm()
    prompt = (
        f"Тип файла: {file_type}. Содержимое (первые 20k байт, utf-8 с заменой ошибок):\n"
        f"{file_bytes[:20000].decode('utf-8', errors='replace')}"
    )
    response = llm.invoke([SystemMessage(content=LLM_DOCUMENT_PARSER_PROMPT), HumanMessage(content=prompt)])
    content = response.content if isinstance(response.content, str) else str(response.content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return []

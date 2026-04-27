"""Клиентский класс для GigaChat с методами под все LLM-модули AML-пайплайна."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

from aml_agent.prompts.prompts import (
    FINALIZER_PROMPT,
    INVESTIGATOR_PROMPT,
    LLM_DOCUMENT_PARSER_PROMPT,
    LOW_RISK_REVIEWER_PROMPT,
    REPAIR_PROMPT,
)


class GigaChatClient:
    """Унифицированный клиент GigaChat для всех LLM-этапов AML.

    Зачем:
    - централизовать работу с моделью;
    - дать отдельные методы под каждый LLM-модуль;
    - поддержать отправку файлов в LLM-контекст.
    """

    def __init__(self, temperature: float = 0.0) -> None:
        """Инициализирует базовый chat-модель клиент из `.env`."""

        load_dotenv()
        credentials = os.getenv("GIGACHAT_CREDENTIALS", "")
        scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
        self.llm = GigaChat(
            credentials=credentials,
            scope=scope,
            verify_ssl_certs=False,
            temperature=temperature,
        )

    def send_file(self, file_bytes: bytes, file_type: str, instruction: str = "") -> str:
        """Отправляет файл в LLM-контекст как текстовый payload.

        Примечание: в MVP payload формируется из первых 20k байт с безопасным decode.
        """

        payload = (
            f"Тип файла: {file_type}\n"
            f"Инструкция: {instruction or 'нет'}\n"
            f"Содержимое (первые 20k байт):\n"
            f"{file_bytes[:20000].decode('utf-8', errors='replace')}"
        )
        return self._invoke_text(system_prompt="Ты помощник по обработке файлов.", user_prompt=payload)

    def parse_document(self, file_bytes: bytes, file_type: str) -> list[dict[str, Any]]:
        """LLM-модуль document parser: извлекает операции из документа."""

        payload = self.send_file(file_bytes, file_type, instruction="Извлеки банковские операции в JSON")
        return self._invoke_json(LLM_DOCUMENT_PARSER_PROMPT, payload, default=[])

    def review_low_risk(self, operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """LLM-модуль low risk reviewer: проверяет упущенные риски и эскалацию."""

        return self._invoke_json(LOW_RISK_REVIEWER_PROMPT, json.dumps(operations, ensure_ascii=False), default=[])

    def investigate(self, operations: list[dict[str, Any]], tools_catalog: list[dict[str, str]]) -> list[dict[str, Any]]:
        """LLM-модуль investigator: формирует факты и оценку риска с учетом tools."""

        payload = json.dumps(
            {
                "tools_catalog": tools_catalog,
                "operations": operations,
            },
            ensure_ascii=False,
        )
        return self._invoke_json(INVESTIGATOR_PROMPT, payload, default=[])

    def finalize(self, operation_payload: dict[str, Any]) -> dict[str, Any]:
        """LLM-модуль finalizer: возвращает итоговое AML-решение по схеме."""

        return self._invoke_json(FINALIZER_PROMPT, json.dumps(operation_payload, ensure_ascii=False), default={})

    def repair(self, payload: dict[str, Any]) -> dict[str, Any]:
        """LLM-модуль repair: исправляет пустые/некорректные поля без выдумки фактов."""

        return self._invoke_json(REPAIR_PROMPT, json.dumps(payload, ensure_ascii=False), default={})

    def _invoke_text(self, system_prompt: str, user_prompt: str) -> str:
        """Низкоуровневый текстовый вызов GigaChat."""

        response = self.llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        return response.content if isinstance(response.content, str) else str(response.content)

    def _invoke_json(self, system_prompt: str, user_prompt: str, default: Any) -> Any:
        """Низкоуровневый JSON-вызов GigaChat c fallback на default."""

        content = self._invoke_text(system_prompt=system_prompt, user_prompt=user_prompt)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return default


def get_gigachat_llm() -> GigaChat:
    """Совместимость со старым API: возвращает объект chat-модели."""

    return GigaChatClient().llm

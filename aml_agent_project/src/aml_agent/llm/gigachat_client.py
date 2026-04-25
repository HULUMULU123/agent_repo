"""Инициализация клиента GigaChat для использования в узлах LangChain/LangGraph."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_gigachat.chat_models import GigaChat


def get_gigachat_llm() -> GigaChat:
    """Создает LLM-клиент GigaChat из переменных окружения.

    Returns:
        Готовый к вызовам объект GigaChat.
    """

    load_dotenv()
    credentials = os.getenv("GIGACHAT_CREDENTIALS", "")
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    return GigaChat(credentials=credentials, scope=scope, verify_ssl_certs=False, temperature=0.0)

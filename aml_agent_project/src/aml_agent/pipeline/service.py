"""Сервисный слой запуска AML workflow для CLI и API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aml_agent.graph.workflow import build_workflow
from aml_agent.storage.database import make_session_factory


def run_pipeline(input_path: str, output_path: str | None = None, db_url: str = "sqlite:///aml_agent.db") -> dict[str, Any]:
    """Запускает полный AML workflow и возвращает финальное состояние.

    Args:
        input_path: Путь к входному файлу выписки.
        output_path: Необязательный путь для сохранения state в JSON.
        db_url: SQLAlchemy URL для SQLite/другой БД.
    """

    app = build_workflow()
    session_factory = make_session_factory(db_url)
    final_state = app.invoke({"input_path": input_path, "session_factory": session_factory})

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_state, f, ensure_ascii=False, indent=2, default=str)

    return final_state

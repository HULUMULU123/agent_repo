"""CLI-точка входа: загрузка файла, запуск графа, сохранение результата и summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aml_agent.graph.workflow import build_workflow
from aml_agent.storage.database import make_session_factory


def run_pipeline(input_path: str, output_path: str, db_url: str) -> dict:
    """Запускает полный AML workflow и возвращает конечное состояние."""

    app = build_workflow()
    session_factory = make_session_factory(db_url)
    final_state = app.invoke({"input_path": input_path, "session_factory": session_factory})

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_state, f, ensure_ascii=False, indent=2, default=str)

    print("=== AML SUMMARY ===")
    print(f"Operations total: {len(final_state.get('operations', []))}")
    print(f"Manual review rows: {len(final_state.get('manual_review_rows', []))}")
    print(f"Sampled for LLM: {len(final_state.get('sampled_operations', []))}")
    print(f"Suspicious written: {len(final_state.get('suspicious_to_write', []))}")
    print(f"Audit rows: {len(final_state.get('audit_log_rows', []))}")
    print(f"Result saved: {output_path}")
    return final_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AML agent for bank statements")
    parser.add_argument("--input", required=True, help="Path to statement file")
    parser.add_argument("--output", default="data/result.json", help="Where to save resulting state JSON")
    parser.add_argument("--db-url", default="sqlite:///aml_agent.db", help="SQLAlchemy database URL")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.input, args.output, args.db_url)

"""CLI-точка входа: загрузка файла, запуск графа, сохранение результата и summary."""

from __future__ import annotations

import argparse

from aml_agent.pipeline.service import run_pipeline


def parse_args() -> argparse.Namespace:
    """Парсит аргументы командной строки для запуска AML анализа."""

    parser = argparse.ArgumentParser(description="AML agent for bank statements")
    parser.add_argument("--input", required=True, help="Path to statement file")
    parser.add_argument("--output", default="data/result.json", help="Where to save resulting state JSON")
    parser.add_argument("--db-url", default="sqlite:///aml_agent.db", help="SQLAlchemy database URL")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    final_state = run_pipeline(args.input, args.output, args.db_url)
    print("=== AML SUMMARY ===")
    print(f"Operations total: {len(final_state.get('operations', []))}")
    print(f"Manual review rows: {len(final_state.get('manual_review_rows', []))}")
    print(f"Sampled for LLM: {len(final_state.get('sampled_operations', []))}")
    print(f"Suspicious written: {len(final_state.get('suspicious_to_write', []))}")
    print(f"Audit rows: {len(final_state.get('audit_log_rows', []))}")
    print(f"Result saved: {args.output}")

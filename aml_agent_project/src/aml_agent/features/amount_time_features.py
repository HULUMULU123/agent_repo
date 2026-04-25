"""Расчет числовых AML-признаков по суммам, времени и повторяемости операций."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_amount_time_features(rows: list[dict]) -> list[dict]:
    """Добавляет признаки: abs/net/direction, frequency, velocity и court proximity."""

    df = pd.DataFrame(rows)
    if df.empty:
        return rows
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["court_claim_date"] = pd.to_datetime(df.get("court_claim_date"), errors="coerce")
    df["debit_amount"] = pd.to_numeric(df["debit_amount"], errors="coerce").fillna(0.0)
    df["credit_amount"] = pd.to_numeric(df["credit_amount"], errors="coerce").fillna(0.0)

    df["abs_amount"] = (df["debit_amount"] - df["credit_amount"]).abs()
    df["net_amount"] = df["credit_amount"] - df["debit_amount"]
    df["direction"] = np.where(df["net_amount"] >= 0, "in", "out")
    df["days_from_court_claim"] = (df["date"] - df["court_claim_date"]).dt.days

    # Частотные и velocity признаки
    daily_counts = df.groupby(df["date"].dt.date)["operation_id"].transform("count")
    df["frequency_feature"] = daily_counts.fillna(0)
    df = df.sort_values(["counterparty", "date"])
    diff = df.groupby("counterparty")["date"].diff().dt.days
    df["velocity_days"] = diff.fillna(999)
    df["repeated_amount"] = df.groupby(["counterparty", "abs_amount"])["operation_id"].transform("count") > 1
    df["court_proximity"] = (df["days_from_court_claim"].abs() <= 30).astype(int)

    return df.to_dict(orient="records")

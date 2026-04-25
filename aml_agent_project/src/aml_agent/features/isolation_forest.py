"""Аномалия-скоринг операций через Isolation Forest для sampling и propagation."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest


def apply_isolation_forest(rows: list[dict]) -> list[dict]:
    """Добавляет iso_score, iso_rank, is_iso_anomaly."""

    df = pd.DataFrame(rows)
    if df.empty:
        return rows
    feature_cols = ["abs_amount", "frequency_feature", "velocity_days", "repeated_amount", "court_proximity"]
    x = df[feature_cols].astype(float)

    model = IsolationForest(contamination=0.1, random_state=42)
    preds = model.fit_predict(x)
    score = -model.score_samples(x)

    df["iso_score"] = score
    df["iso_rank"] = df["iso_score"].rank(pct=True)
    df["is_iso_anomaly"] = preds == -1
    return df.to_dict(orient="records")

"""Representative sampling внутри кластера для экономии LLM-бюджета."""

from __future__ import annotations

import pandas as pd


def representative_sampling(rows: list[dict], per_cluster: int = 6) -> list[dict]:
    """Выбирает репрезентативные операции по формуле приоритета."""

    df = pd.DataFrame(rows)
    if df.empty:
        return rows

    df["purpose_distance_rank"] = df["distance_to_center"].rank(pct=True)
    df["amount_rank"] = df["abs_amount"].rank(pct=True)
    df["rarity_score"] = 1 / df["cluster_size"].clip(lower=1)
    df["sampling_priority"] = (
        0.30 * df["iso_rank"]
        + 0.25 * df["purpose_distance_rank"]
        + 0.20 * df["court_proximity"]
        + 0.15 * df["amount_rank"]
        + 0.10 * df["rarity_score"]
    )

    samples = []
    for _, cluster_df in df.groupby("cluster_id"):
        chosen = cluster_df.sort_values("sampling_priority", ascending=False).head(per_cluster)
        samples.append(chosen)
    return pd.concat(samples).drop_duplicates(subset=["operation_id"]).to_dict(orient="records")

"""Кластеризация по purpose-эмбеддингам с расчетом позиции в кластере."""

from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans


def cluster_purposes(rows: list[dict], embeddings: np.ndarray, n_clusters: int = 4) -> list[dict]:
    """Добавляет cluster_id, distance_to_center, cluster_size, purpose_position."""

    if len(rows) == 0:
        return rows
    k = min(n_clusters, len(rows))
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = model.fit_predict(embeddings)
    centers = model.cluster_centers_

    for i, row in enumerate(rows):
        label = int(labels[i])
        dist = float(np.linalg.norm(embeddings[i] - centers[label]))
        cluster_mask = labels == label
        cluster_dists = np.linalg.norm(embeddings[cluster_mask] - centers[label], axis=1)
        q25, q75 = np.quantile(cluster_dists, [0.25, 0.75])
        if dist <= q25:
            position = "center"
        elif dist >= q75:
            position = "boundary"
        else:
            position = "middle"
        row["cluster_id"] = label
        row["distance_to_center"] = dist
        row["cluster_size"] = int(cluster_mask.sum())
        row["purpose_position"] = position
    return rows

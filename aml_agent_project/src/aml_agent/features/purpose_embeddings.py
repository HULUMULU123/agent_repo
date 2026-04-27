"""Векторизация назначений платежей для кластеризации и propagation similarity."""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class PurposeEmbedder:
    """Простая embed-модель на TF-IDF для purpose-поля (MVP)."""

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(max_features=256, ngram_range=(1, 2))

    def fit_transform(self, purposes: list[str]) -> np.ndarray:
        """Обучает векторизатор и возвращает dense-эмбеддинги."""

        mat = self.vectorizer.fit_transform(purposes)
        return mat.toarray()
